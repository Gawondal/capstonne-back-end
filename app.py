from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
import psycopg2

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kswkykvnmjgxom:d6dbb74956dea7edbb9536077aa9bd55e7cafa7ca82dd8fef5aa888ed88f0101@ec2-3-208-157-78.compute-1.amazonaws.com:5432/d4p434i4dt8p8v"
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

@app.route('/user/add', methods=['POST'])
def add_user():
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be JSON.")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    possible_duplicate = db.session.query(User).filter(User.username == username).first()

    if possible_duplicate is not None:
        return jsonify('Error: That username is Taken.')
    
    encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username, encrypted_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify('New user has been added.')

@app.route('/user/verify', methods=['POST'])
def verify_user():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be JSON.')

    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')

    user = db.session.query(User).filter(User.username == username).first()

    if user is None:
        return jsonify('User NOT verified.')

    if bcrypt.check_password_hash(user.password, password) == False:
        return jsonify('User NOT verified')

    return jsonify('User has been verified.')
    

@app.route('/user/get', methods=['GET'])
def get_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(all_users))

@app.route('/user/get/<id>', methods=['GET'])
def get_user_by_id(id):
    user = db.session.query(User).filter(User.id == id).first()
    return jsonify(user_schema.dump(user))

@app.route('/user/get/username/<username>', methods=['GET'])
def get_user_by_username(username):
    user = db.session.query(User).filter(User.username == username).first()
    return jsonify(user_schema.dump(user))

@app.route('/user/delete', methods=['DELETE'])
def delete_users():
    all_users = db.session.query(User).all()
    for user in all_users:
        db.session.delete(user)
    db.session.commit()
    return jsonify("All users have has been deleted.")

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False ) 
    treatment = db.Column(db.String, nullable=False)
    

    def __init__(self, name, date, time, treatment):
        self.name = name
        self.date = date
        self.time = time
        self.treatment = treatment


class AppointmentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'date', 'time', 'treatment')

appointment_schema = AppointmentSchema()
multiple_appointment_schema = AppointmentSchema(many=True)

@app.route("/appointment/add", methods=["POST"])
def add_appointment():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be JSON.")

    post_data = request.get_json()
    name = post_data.get('name')
    date = post_data.get('date')
    time = post_data.get('time')
    treatment = post_data.get('treatment')

    if name == None:
        return jsonify("Error: Data must have a 'name' key.")
    if date == None:
        return jsonify("Error: Data must have a 'date' key.")
    if time == None:
        return jsonify("Error: Data must have a 'time' key.")
    if treatment == None:
        return jsonify("Error: Data must have a 'treatment' key.")   

    new_appointment = Appointment(name, date, time, treatment)
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify("Good job on your appointment!")              

@app.route("/appointment/get", methods=["GET"])
def get_appointments():
    appointments = db.session.query(Appointment).all()
    return jsonify(multiple_appointment_schema.dump(appointments))

@app.route('/appointment/get/<id>', methods=['GET'])
def get_appointment_by_id(id):
    appointment = db.session.query(Appointment).filter(Appointment.id == id).first()
    return jsonify(appointment_schema.dump(appointment))

@app.route('/appointment/delete/<id>', methods=['DELETE'])
def delete_appointment_by_id(id):
    appointment = db.session.query(Appointment).filter(Appointment.id == id).first()
    db.session.delete(appointment)
    db.session.commit()
    return jsonify("Appointment has been canceled.")

@app.route('/appointment/update/<id>', methods=['PUT'])
def update_appointment_by_id(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be json")

    post_data = request.get_json()
    name = post_data.get('name')
    date = post_data.get('date')
    time = post_data.get('time') 
    treatment = post_data.get('treatment')

    appointment = db.session.query(Appointment).filter(Appointment.id == id).first()

    if name != None:
        appointment.name = name
    if date != None:
        appointment.date = date
    if time != None:
        appointment.time = time
    if treatment != None:
        appointment.treatment = treatment

    db.session.commit()
    return jsonify("Appointment Updated Successfully")

if __name__ == '__main__':
    app.run(debug=True)


    