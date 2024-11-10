from pymongo.mongo_client import MongoClient
import uuid
import urllib

class db:
    def __init__(self):
        self.db=None
        self.Load_DB()

    def Load_DB(self):
        username = urllib.parse.quote_plus('Hassandaja')
        password = urllib.parse.quote_plus('Hassankhaleddaja')
        try:
            print("Connecting Database ***********")
            uri = f"mongodb+srv://{username}:{password}@hassanscluster.chtpttu.mongodb.net/?retryWrites=true&w=majority"
            # Create a new client and connect to the server
            client = MongoClient(uri)
            # Send a ping to confirm a successful connection

            db = client['HassansCluster']
            self.db=db
            self.db_status=True
            return True
        except Exception as e:
            self.db_status = False
            return False
    def student_signup(self,email, username, password, encodings,major):
        db=self.db
        try:
            # Check if username or email already exist
            query = {'$or': [{'username': username}, {'email': email}]}
            existing_student = db['student_info'].find_one(query)
            if existing_student:
                return 409  # Conflict: Username or email already exists
            # Insert student data into the database
            student_id = str(uuid.uuid4())  # Generate a unique ID
            encodings=[array for array in encodings]
            Student_data = {
                '_id': student_id,
                'email': email,
                'username': username,
                'password': password,
                'major':major,
                'Face_encodings': encodings
            }
            db['student_info'].insert_one(Student_data)
            return 200  # Success
        except Exception as e:
            print(e)
            return 500  # Internal server error

    def check_if_lecture_exist(self,lecture_id):
        db=self.db
        lecture=db.lecture_info.find_one({'_id':lecture_id})
        return lecture

    def add_lecture(self, lecture_id, lec_name, instructor):
        try:
            db = self.db

            # Check if lecture already exists
            if self.check_if_lecture_exist(lecture_id) is not None:
                return 409, 'Already exists'  # 409 Conflict: Resource already exists

            lecture_data = {
                '_id': lecture_id,
                'lecture_name': lec_name,
                'instructor': instructor,
            }

            db.lecture_info.insert_one(lecture_data)
            return 201  # 201 Created: Resource successfully created

        except Exception as e:
            print(e)
            return 500  # 500 Internal Server Error: Something went wrong on the server


    def add_student_to_lecture(self, student_id, lecture_id):
        try:
            db = self.db

            # Check if the student exists
            student_data = db.student_info.find_one({'_id': student_id})
            # Check if the student is already enrolled in the specific lecture
            if any(lecture['lec_id'] == lecture_id for lecture in student_data.get('lectures', [])):
                return 409  # Return conflict error code if the student is already enrolled in the lecture

            # Check if the student already has 'lectures' attribute
            if 'lectures' not in student_data:
                # If 'lectures' attribute doesn't exist, create it as an empty list
                db.student_info.update_one({'_id': student_id}, {'$set': {'lectures': []}})

            # Append the lecture information to the student's 'lectures' list with lecture_abs set to 0
            db.student_info.update_one({'_id': student_id},
                                       {'$addToSet': {'lectures': {'lec_id': lecture_id, 'lec_abs': 0}}})

            # Retrieve student face encodings
            student_encodings_cursor = db.student_info.find({'_id': student_id}, {'Face_encodings': 1})
            student_encodings = list(student_encodings_cursor)
            student_encodings = student_encodings[0]['Face_encodings']

            # Update the lecture document with student information
            db.lecture_info.update_one({'_id': lecture_id},
                                       {'$push': {'students_ids': student_id,
                                                  'students_encodings': {'$each': student_encodings}
                                                  }})
            return 200
        except Exception as e:
            print(e)
            return 500  # Return a different error code for general exceptions

    def get_faces_by_id(self,lecture_id):
        db = self.db
        students_encodings = db.lecture_info.find({'_id': lecture_id}, {'students_encodings': 1})
        return students_encodings

    def studentid_by_idx(self,lec_id,index):
        db =self.db
        students_ids = db.lecture_info.find({'_id': lec_id}, {'student_ids': 1})
        student_id=students_ids[index]
        return student_id

    def get_student_name(self, student_id):
        db = self.db

        # Retrieve the student information based on the student ID
        student_info = db.student_info.find_one({'_id': student_id}, {'username': 1})

        # Check if the student information was found
        if student_info:
            return student_info['username']
        else:
            # Handle the case where the student information is not found
            return None  # You might want to return a default value or raise an exception depending on your requirements
    def get_all_students_encodings(self,lec_id):
        db = self.db
        if not self.check_if_lecture_exist(lec_id):
            return 404
        students_encodings=db.lecture_info.find({'_id':lec_id},{'students_encodings':1})
        encodings=students_encodings[0]['students_encodings']
        return encodings
    def get_all_student_ids(self,lec_id):
        all_ids=self.get_student_ids_by_lecture(lec_id)
        return all_ids
    def get_all_students_info(self,lecture_id):
        print("Request_sent*************")
        ids=self.get_all_student_ids(lecture_id)
        encodings=self.get_all_students_encodings(lecture_id)
        return ids,encodings
    def get_student_ids_by_lecture(self,lec_id):
        db=self.db
        results=db.lecture_info.find({'_id':lec_id},{'students_ids':1})
        list_results=list(results)
        # Extract the 'students_ids' field from the first document (assuming there is only one)
        students_ids = list_results[0].get('students_ids', [])
        return students_ids
    def get_username_by_id(self,student_id):
        db=self.db
        result = self.db.student_info.find_one({"_id": student_id },{'username':1})
        if result:
            return result.get('username')
        else:
            return False


    def get_user_info(self, username, password):
        db = self.db
        # Check if the username exists
        user = db.student_info.find_one({'username': username})
        if user:
            # If the username exists, check if the password is correct
            if user['password'] == password:
                # If the password is correct, return user data
                user_data = {
                    'major': user.get('major', ''),
                    'email': user.get('email', ''),
                    'id':user.get('_id')
                }
                return True, user_data
            else:
                # If the password is incorrect, return False and None
                return False, None
        else:
            # If the username doesn't exist, return False and None
            return False, None

    def get_student_lectures(self, student_id):
        db = self.db
        try:
            # Check if the student exists
            student_data = db.student_info.find_one({'_id': student_id})
            if not student_data:
                return 404, []  # Return an error code if the student doesn't exist and an empty list of lectures

            # Get the list of lecture records the student is enrolled in
            student_lectures = student_data.get('lectures', [])

            # If student_lectures is empty, return an empty list of lectures
            if not student_lectures:
                return 200, []

            # Retrieve lecture information for each lecture record
            lectures_info = []
            for lecture_record in student_lectures:
                lecture_id = lecture_record.get('lec_id')
                lecture_info = db.lecture_info.find_one({'_id': lecture_id})
                if lecture_info:
                    lec_abs = lecture_record.get('lec_abs', 0)
                    lectures_info.append({
                        'lecture_id': lecture_id,
                        'lecture_name': lecture_info['lecture_name'],
                        'lec_abs': lec_abs
                    })

            return 200, lectures_info  # Return success code and list of student's lectures
        except Exception as e:
            return 500, []  # Return a different error code for general exceptions and an empty list of lectures

    def check_instructor_exists(self, username):
        # Check if an instructor with the given username already exists
        return self.db.instructors.find_one({'username': username}) is not None

    def add_instructor(self, username, password,email=None, lectures=None):
        try:
            # Check if the username already exists (additional safety check)
            if self.check_instructor_exists(username):
                return 400, None

            # Generate a unique _id for the instructor
            instructor_id = str(uuid.uuid4())
            if email:
                instructor_data = {'_id': instructor_id, 'username': username, "email":email,'password': password}
            else:
                # Insert new instructor document
                instructor_data = {'_id': instructor_id, 'username': username, 'password': password}
            if lectures is not None:
                instructor_data['lectures'] = lectures
            self.db.instructors.insert_one(instructor_data)
            return 200, instructor_id  # Success, return the generated instructor ID
        except Exception as e:
            print(e)
            return 500, None

    def get_lecture_name(self, lec_id):
        try:
            db = self.db

            # Find the lecture with the given lec_id
            lecture_info = db.lecture_info.find_one({'_id': lec_id})
            if lecture_info:
                lec_name = lecture_info.get('lecture_name')
                return lec_name
            else:
                return None  # Return None if lecture with given lec_id is not found

        except Exception as e:
            print(e)
            return None  # Return None in case of any exception

    def authenticate_instructor(self, username, password):
        try:
            # Check if instructor exists and password matches
            instructor = self.db.instructors.find_one({'username': username, 'password': password})
            if instructor:
                lectures = instructor.get('lectures', [])
                lecture_details = []
                for lecture_id in lectures:
                    lecture_name = self.get_lecture_name(lecture_id)
                    if lecture_name:
                        lecture_details.append({'lecture_id': lecture_id, 'lecture_name': lecture_name})
                return True, lecture_details  # Authentication successful, return True and list of lecture details
            else:
                return False, None  # Authentication failed or instructor not found
        except Exception as e:
            print(e)
            return False, None  # Internal server error

    def increment_absence_count(self, student_id, lec_id):
        try:
            db = self.db

            # Check if the student exists
            student_data = db.student_info.find_one({'_id': student_id})
            if not student_data:
                return 404  # Return an error code if the student doesn't exist

            # Find the lecture with the given lec_id
            lecture = next((lecture for lecture in student_data.get('lectures', []) if lecture.get('lec_id') == lec_id),
                           None)
            if not lecture:
                return 404  # Return an error code if the lecture doesn't exist for the student

            # Increment the absence count for the lecture
            lec_abs = lecture.get('lec_abs', 0)
            new_lec_abs = lec_abs + 1
            db.student_info.update_one({'_id': student_id, 'lectures.lec_id': lec_id},
                                       {'$set': {'lectures.$.lec_abs': new_lec_abs}})

            return 200  # Return success code
        except Exception as e:
            print(e)
            return 500

    def get_student_names_and_absences_by_ids(self, student_ids, lec_id):
        db = self.db
        student_info = {}

        for student_id in student_ids:
            username = self.get_username_by_id(student_id)
            status_code, lectures = self.get_student_lectures(student_id)

            print(f"Received lectures from API for student {student_id}: {lectures}")  # Debug statement

            if status_code == 200 and isinstance(lectures, list):
                for lecture in lectures:
                    print(
                        f"Student ID: {student_id}, Lecture ID: {lecture.get('lecture_id')}, Absences: {lecture.get('lec_abs')}")
                    if str(lecture.get('lecture_id')) == str(lec_id):
                        total_absences = lecture.get('lec_abs')
                        student_info[student_id] = {
                            'username': username,
                            'total_absences': total_absences
                        }
                        print(f"Added to student_info: {student_info}")  # Debug statement
                        break
            else:
                print(f"Warning: Lectures not found for student {student_id}. Status code: {status_code}")

        print(f"Final Student Info: {student_info}")  # Ensure this print statement captures correct data

        return student_info
if __name__=="__main__":
    pass
