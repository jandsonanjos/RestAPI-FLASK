from flask import Flask
from flask_restful import Resource, Api, reqparse
import mongoengine as me
from mongoengine import connect

app = Flask(__name__)

# Connect to MongoDB
connect(
    db='users',
    host='mongodb',
    port=27017,
    username='admin',
    password='admin',
    authentication_source='admin'
)

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('first_name', 
        type=str, 
        required=True, 
        help='First name is required')
_user_parser.add_argument('last_name', 
        type=str, 
        required=True, 
        help='Last name is required')
_user_parser.add_argument('cpf', 
        type=str, 
        required=True, 
        help='CPF is required')
_user_parser.add_argument('email', 
        type=str, 
        required=True, 
        help='Email is required')
_user_parser.add_argument('birth_date', 
        type=str, 
        required=True, 
        help='Birth date is required')

api = Api(app)


class UserModel(me.Document):
    cpf = me.StringField(required=True, unique=True)
    first_name = me.StringField()
    last_name = me.StringField()
    email = me.EmailField(required=True)
    birth_date = me.DateTimeField(required=True)
    
    meta = {
        'collection': 'users'
    }


class Users(Resource):
    def get(self):
        data = _user_parser.parse_args()
        UserModel(**data).save()
        return data
    print("Salvo")


class User(Resource):
    def post(self):
        data = _user_parser.parse_args()
        return data

    def get(self, cpf):
        return {"message": "CPF"}


api.add_resource(Users, '/users')
api.add_resource(User, '/user', '/user/<string:cpf>')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
