from flask import Flask, jsonify,request
import Database_methods as Database
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
db=Database.db()
print(f"+++++++++++++{db.db_status}+++++++++++++++++")
@app.route('/Database/test', methods=['GET'])
def lol():
    return jsonify({'Value':1})
@app.route('/Database/authenticate_instructor', methods=['POST'])
def authenticate_instructor():
    # Extract username and password from request body
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Call authenticate_instructor method
    success, lecture_details = db.authenticate_instructor(username, password)

    # Return response based on success
    if success:
        return jsonify({'authenticated': True, 'lecture_details': lecture_details}), 200
    else:
        return jsonify({'authenticated': False, 'message': 'Authentication failed.'}), 401
@app.route('/Database/increment_absence_count', methods=['POST'])
def increment_abs():
    status=True
    data = request.json
    id=data['id']
    lec_id=int(data['lec_id'])
    status_code=db.increment_absence_count(id,lec_id)
    if status_code!=200:
        status=False
    print(status)
    return jsonify({"status":status})
@app.route('/Database/get_students_info/<int:lecture_id>', methods=['GET'])
def get_info(lecture_id):
    ids,encodings=db.get_all_students_info(lecture_id)
    return jsonify({'ids':ids,"Encodings":encodings})
@app.route('/Database/get_students_lec/<user_id>', methods=['GET'])
def get_student_lec(user_id):
    status_code,data=db.get_student_lectures(user_id)
    if status_code==200:
        return jsonify({'Data': data,"status":True})
    return jsonify({'Data': data,"status":False})
#    def student_signup(self,email, username, password, encodings):
@app.route('/Database/add_student_to_db',methods=['POST'])
def add_student_to_db():
    status=None
    message=None
    data=request.json
    email=data['email']
    username=data['username']
    password=data['password']
    encodings=data['encodings']
    major=data['major']
    results=db.student_signup(email,username,password,encodings,major)
    if results == 200:
        status = True
        message = 'Student has been added successfully.'
    elif results == 409:
        status = False
        message = 'Student already exists.'
    else:
        status = False
        message = 'An error occurred while adding the student to the database.'

    return jsonify({'status':status,'message':message})
@app.route('/Database/add_lec_to_db',methods=['POST'])
def add_lecture_to_db():
    data=request.json
    lec_id=data['lec_id']
    lec_name=data['lec_name']
    instructor_name=data['instructor_name']
    results=db.add_lecture(lec_id,lec_name,instructor_name)
    if results == 201:
        status = 'Success'
        message = 'Lecture has been added successfully.'
    elif results == 409:
        status = 'Error'
        message = 'lecture already exists.'
    else:
        status = 'Error'
        message = 'An error occurred while adding the lecture to the database.'
    return jsonify({'status': status, 'message': message})

@app.route('/Database/add_student_to_lec',methods=['POST'])
def add_student_to_lec():
    data=request.json
    lec_id=data['lec_id']
    student_id=data['student_id']
    results=db.add_student_to_lecture(student_id=student_id,lecture_id=lec_id)
    if results == 200:
        status = True
        message = f'Student has been added to lecture {lec_id} successfully.'
    elif results == 409:
        status = False
        message = "Student is already enrolled in this lecture."
    else:
        status = False
        message = f'An error occurred while adding the student to the Lecture {lec_id}.'
    return jsonify({'status': status, 'message': message})
@app.route('/Database/user_info', methods=['POST'])
def user_info():
    # Get username and password from the request
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Check if both username and password are provided
    if not username or not password:
        return jsonify({'status': False, 'message': 'Username and password are required'}), 400

    # Call the get_user_info method from your db class
    status, user_data = db.get_user_info(username, password)

    if status:
        # If status is True, user data is returned successfully
        return jsonify({'status': True, 'data': user_data}), 200
    else:
        # If status is False, either username or password is incorrect
        return jsonify({'status': False, 'message': 'Invalid username or password'}), 401
@app.route('/Database/add_instructor', methods=['POST'])
def add_instructor():
    # Extract username, password, and lectures from request body
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email=data.get('email')
    lectures = data.get('lectures', None)

    # Check if the username already exists
    user_exists = db.check_instructor_exists(username)

    if user_exists:
        return jsonify({'success': False, 'message': 'Instructor already exists.'}), 400

    # Call add_instructor method
    status, instructor_id = db.add_instructor(username, password, email,lectures)

    # Return response based on status
    if status == 200:
        return jsonify({'success': True, 'instructor_id': instructor_id}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to add instructor.'}), 500
@app.route('/Database/get_student_names_and_absences', methods=['POST'])
def get_student_names_and_absences():
    # Extract student_ids and lec_id from request body
    data = request.json
    student_ids = data.get('student_ids', [])
    lec_id = data.get('lec_id')

    # Call the get_student_names_and_absences_by_ids method
    student_info = db.get_student_names_and_absences_by_ids(student_ids, lec_id)

    return jsonify({'status': True, 'student_info': student_info}), 200
if __name__ == '__main__':
    app.run(debug=False,port=5555,host="0.0.0.0")