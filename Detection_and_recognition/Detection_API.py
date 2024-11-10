from flask import Flask, request, jsonify
import sys
import os
os.chdir('Detection_and_recognition')

from detection_recognition_Methods import get_students_enc_ids,check_person_images,attendance_by_images
from flask_cors import CORS
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def test():
    return 'test'
@app.route('/check_person_images', methods=['POST'])
def check_images():
    data = request.json  # Expecting a JSON object with 'imgs' and 'threshold' keys
    if 'imgs' in data:
        imgs = data['imgs']
        print(type(imgs))
        threshold = data.get('threshold', 0.6)  # Default threshold is 0.6 if not provided
        Status,Data= check_person_images(imgs, threshold)
        print(Status)
        if Status==False:
            Status=Status
            Data=Data
        return jsonify({"Status":Status,"Data":Data})
    else:
        return jsonify({"error": "Missing 'imgs' key in the request."}), 400
@app.route('/get_attendance', methods=['POST'])
def get_attendance():
    data = request.json
    lec_id = data['lec_id']
    print(lec_id)
    try:
        ids,encodings=get_students_enc_ids(lec_id)
        all_ids=ids.copy()
        img=np.array(Image.open('New_test.jpeg'))
        imgs=[img]
        ids=attendance_by_images(imgs, ids, encodings)
        return jsonify({"ids": ids,'all_ids':all_ids})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({"error": error_message}), 400
if __name__ == '__main__':
    app.run(debug=False,port=9999)