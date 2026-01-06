import re
from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource, reqparse
import mongoengine as me
from mongoengine import NotUniqueError, connect

app = Flask(__name__)
api = Api(app)

# -------------------------
# MongoDB Connection
# -------------------------
connect(
    db='users',
    host='mongodb',
    port=27017,
    username='admin',
    password='admin',
    authentication_source='admin',
)

# -------------------------
# Helpers
# -------------------------
def normalize_cpf(cpf: str) -> str:
    return re.sub(r'\D', '', cpf)

def validate_cpf(cpf: str) -> bool:
    cpf = normalize_cpf(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    digito1 = 0 if digito1 == 10 else digito1

    if digito1 != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    digito2 = 0 if digito2 == 10 else digito2

    return digito2 == int(cpf[10])

# -------------------------
# Request Parser
# -------------------------
user_parser = reqparse.RequestParser()
user_parser.add_argument('first_name', type=str, required=True)
user_parser.add_argument('last_name', type=str, required=True)
user_parser.add_argument('cpf', type=str, required=True)
user_parser.add_argument('email', type=str, required=True)
user_parser.add_argument('birth_date', type=str, required=True)

# -------------------------
# Model
# -------------------------
class UserModel(me.Document):
    cpf = me.StringField(required=True, unique=True)
    first_name = me.StringField(required=True)
    last_name = me.StringField(required=True)
    email = me.EmailField(required=True)
    birth_date = me.DateTimeField(required=True)

    meta = {'collection': 'users'}

    def to_dict(self):
        return {
            'cpf': self.cpf,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'birth_date': self.birth_date.strftime('%Y-%m-%d')
        }

# -------------------------
# Resources
# -------------------------
class Users(Resource):
    def get(self):
        users = UserModel.objects()
        return [user.to_dict() for user in users], 200


class User(Resource):

    def post(self):
        data = user_parser.parse_args()

        if not validate_cpf(data['cpf']):
            return {'message': 'CPF inválido'}, 400

        data['cpf'] = normalize_cpf(data['cpf'])

        try:
            data['birth_date'] = datetime.strptime(
                data['birth_date'], '%Y-%m-%d'
            )
            UserModel(**data).save()
            return {'message': 'Usuário criado com sucesso'}, 201

        except ValueError:
            return {'message': 'Formato de data inválido (YYYY-MM-DD)'}, 400

        except NotUniqueError:
            return {'message': 'CPF já existente'}, 400


    def get(self, cpf):
        cpf = normalize_cpf(cpf)

        user = UserModel.objects(cpf=cpf).first()
        if not user:
            return {'message': 'Usuário não encontrado'}, 404

        return user.to_dict(), 200

# -------------------------
# Routes
# -------------------------
api.add_resource(Users, '/users')
api.add_resource(User, '/user', '/user/<string:cpf>')

# -------------------------
# Main
# -------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
