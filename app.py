import re
from flask import Flask
from flask_restful import Api, Resource, reqparse
import mongoengine as me
from mongoengine import NotUniqueError
from mongoengine import connect


app = Flask(__name__)


# Connect to MongoDB
connect(
    db='users',
    host='mongodb',
    port=27017,
    username='admin',
    password='admin',
    authentication_source='admin',
)


_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    'first_name',
    type=str,
    required=True,
    help='First name is required',
)
_user_parser.add_argument(
    'last_name',
    type=str,
    required=True,
    help='Last name is required',
)
_user_parser.add_argument(
    'cpf',
    type=str,
    required=True,
    help='CPF is required',
)
_user_parser.add_argument(
    'email',
    type=str,
    required=True,
    help='Email is required',
)
_user_parser.add_argument(
    'birth_date',
    type=str,
    required=True,
    help='Birth date is required',
)


api = Api(app)


class UserModel(me.Document):
    cpf = me.StringField(required=True, unique=True)
    first_name = me.StringField()
    last_name = me.StringField()
    email = me.EmailField(required=True)
    birth_date = me.DateTimeField(required=True)

    meta = {
        'collection': 'users',
    }


class Users(Resource):
    def get(self):
        users = UserModel.objects()
        return users.to_json(), 200


class User(Resource):
    def validate_cpf(self, cpf: str) -> bool:
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            return False

        numbers = [int(digit) for digit in cpf if digit.isdigit()]

        if len(numbers) != 11:
            return False

        if numbers.count(numbers[0]) == 11:
            return False

        soma = sum(numbers[i] * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        digito1 = 0 if digito1 == 10 else digito1

        if digito1 != numbers[9]:
            return False

        soma = sum(numbers[i] * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        digito2 = 0 if digito2 == 10 else digito2

        if digito2 != numbers[10]:
            return False

        return True

    def post(self):
        data = _user_parser.parse_args()

        if not self.validate_cpf(data['cpf']):
            return {'message': 'CPF inválido'}, 400
        try:
            UserModel(**data).save()
            return {'message': 'Usuário %s criado com CPF válido' % data['cpf']}, 201
        except NotUniqueError:
            return {'message': 'CPF já existente no DB'}, 400

    def get(self, cpf):
        user = UserModel.objects(cpf=cpf).first()
        if not user:
            return {'message': 'Usuário não encontrado'}, 404

        return user.to_json(), 200


api.add_resource(Users, '/users')
api.add_resource(User, '/user', '/user/<string:cpf>')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
