import keras
import numpy
from PIL import Image,ImageOps
import numpy as np
from Face_detector import detect_faces
from keras.models import Model
from sklearn.metrics.pairwise import cosine_similarity
import requests
import keras

model=keras.models.load_model('./weights.h5')
model = Model(inputs=model.input, outputs=model.layers[-2].output)

def compute_cosine_similarity(embedding1, embedding2):

    # Reshape the embeddings to ensure they are 2D arrays
    embedding1 = np.array(embedding1).reshape(1, -1)
    embedding2 = np.array(embedding2).reshape(1, -1)

    # Compute the cosine similarity
    similarity_matrix = cosine_similarity(embedding1, embedding2)

    # Extract the similarity value from the matrix
    similarity = similarity_matrix[0][0]

    return similarity
def compute_similarity(query_feature,db_embedding):
    distance=cosine_similarity(query_feature,db_embedding)
    model=keras.models.load_model('BEST_SIA.h5')
    distance = model.predict(np.array([distance[0][0]]).reshape(1,-1))
    return distance
def calculate_cosine_similarity(query_feature, face_embeddings,thresh_hold=0.7):
    """
    Calculate cosine similarity between a query feature and a list of face embeddings.

    Parameters:
    - query_feature: NumPy array representing the feature vector of the query face.
    - face_embeddings: List of NumPy arrays, each representing a face embedding.

    Returns:
    - List of cosine similarities between the query feature and each face embedding.
    """
    classification=[]
    cosine_similarities = []

    # Convert the query feature to a 2D array if it's not already
    if len(query_feature.shape) == 1:
        query_feature = query_feature.reshape(1, -1)

    for embedding in face_embeddings:
        # Calculate the cosine similarity between the query feature and the current embedding
        similarity = cosine_similarity(query_feature, embedding.reshape(1, -1))
        classification.append(similarity[0][0]>thresh_hold)
        cosine_similarities.append(similarity[0][0])

    return cosine_similarities,classification
def preprocess_image(img):
    # Open the image using Pillow
    # Resize the image to 224x224 pixels
    img = img.resize((224, 224), Image.Resampling.LANCZOS)

    # Ensure the image has 3 channels (RGB)
    img = img.convert("RGB")
    #img = ImageOps.equalize(img)
    # Convert the image to a NumPy array if needed
    img_array = np.array(img)

    return img_array
def Feature_extactor(face_image:numpy.numarray,show_faces=True,add_preporcessing=True):
    image = Image.fromarray(face_image)
    if add_preporcessing:
        image = preprocess_image(image)
    if show_faces:
        #img=Image.fromarray(image)
        #img.show()
        pass
    processed = np.expand_dims(image, axis=0)
    embeddings = model.predict(processed)
    return embeddings
def get_faces(images):
    faces=detect_faces(images)
    if len(faces)==0:
        return False
    return faces
def get_faces_and_features(image,show_faces=False,add_preporcessing=True):
    faces=get_faces(image)
    embeddings=[]
    if faces is False:
        return False,'No faces detected'
    for face in faces:
        embeddings.append(Feature_extactor(face,show_faces,add_preporcessing=add_preporcessing))
    return faces,embeddings
def get_embeddings(image,show_faces=False):
    faces,embeddings=get_faces_and_features(image,show_faces=show_faces)
    if faces==False:
        return faces,embeddings
    return embeddings
######API
def image_for_same_person(embeddings,thresh_hold=0.6):
    matches=[]
    length=len(embeddings)
    if length==2:
        print(f'Distance between image {1} and image {2}')
        distance = compute_cosine_similarity(embeddings[0], embeddings[1])
        print(distance)
        matches.append(distance > thresh_hold)
        return all(matches)
    for i in range(2):
        for j in range(i+1,3):
            print(f'Distance between image {i} and image {j}')
            distance=compute_similarity(embeddings[i],embeddings[j])
            print(distance)
            matches.append(distance>thresh_hold)
    return all(matches)
def check_person_images(imgs,thresh_hold=0.6):
    embeddings=[]
    for img in imgs:
        embed=get_embeddings(img)
        if embed[0] is False:
            return embed
        embeddings.append(embed[0].tolist())
        ########handle if encoding not found
        print('Done')
    if not image_for_same_person(embeddings,thresh_hold):
        return False,"Faces don't belong to same person"
    return True,embeddings


def attendance_by_images(imgs, ids, encodings, thresh_hold=0.97):
    try:
        embeddings = []
        print("Initial IDs:", ids)
        for img in imgs:
            print('Started getting the embeddings for an image')
            embed = get_embeddings(img, show_faces=True)
            if embed[0] is False:
                return embed
            embeddings.extend(embed)  # Extend the embeddings list with the current image embeddings

        for emb in embeddings:
            distances = []
            for enc in encodings:
                print('Starting to calculate distance')
                distance = compute_similarity(emb.tolist(), enc)[0][0]  # Convert to list for compatibility
                print(f"Computed distance: {distance}")
                if distance > thresh_hold:
                    distances.append(distance)
                else:
                    distances.append(0)
            print("Distances:", distances)

            # Check if the distances list is all zeros
            if all(d == 0 for d in distances):
                print("All distances are zero, skipping this embedding")
                continue

            highest_value_index = distances.index(max(distances))
            print("Highest distance value index:", highest_value_index)
            idx = highest_value_index // 3
            print("ID corresponding to highest distance:", ids[idx])
            ids.pop(idx)
            for i in range(3):
                encodings.pop(idx * 3)  # Adjust index for popping encodings
            print("Updated IDs:", ids)

        print("Final IDs:", ids)
        return ids
    except Exception as e:
        print("Exception occurred:", e)


def get_students_enc_ids(lec_id):
    db_url = "http://127.0.0.1:5555"
    db_student_info_endpoint = '/Database/get_students_info/'
    url = db_url+db_student_info_endpoint+lec_id
    # Send a POST request to the API endpoint
    response = requests.get(url)
    response_json = response.json()
    # Extract status and message from the response
    ids = response_json.get('ids')
    encodings = response_json.get('Encodings')
    return ids, encodings

if __name__=='__main__':
    '''
    img1=Image.open('IMG_3498.jpg')
    img2=Image.open('IMG_3500.jpg')
    img3=Image.open('basel_2.jpg')
    imgs=[img1,img2,img3]
    print(check_person_images(imgs,thresh_hold=0.7)[0])
'''

    #query=get_embeddings(Image.open('test_img_2.png'))[0]
    query = get_embeddings(Image.open('img1.png'))
    db_embedding=get_embeddings(Image.open('yazeed.jpg'),show_faces=False)
    print(len(query[0]))
    print(len(query[0][0]))
    print(len(db_embedding[0][0]))
    print(compute_similarity(query[0][0].reshape(1,-1),db_embedding[0][0].reshape(1,-1)))
    print(compute_similarity(query[1][0].reshape(1,-1), db_embedding[0][0].reshape(1,-1)))
    print(compute_similarity(query[2][0].reshape(1,-1), db_embedding[0][0].reshape(1,-1)))



