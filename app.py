from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:senhasecreta123@db.xfzdbuxmtmaltnmjcceb.supabase.co:5432/postgres'

db = SQLAlchemy(app)

class User(db.Model):
    rg = db.Column(db.Integer, primary_key= True, nullable=False)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {"rg": self.rg, "name": self.name, "email": self.email, "cpf": self.cpf, "age": self.age}

def func_response(status, content_name, content, message=False):
    body = {}
    body[content_name] = content

    if(message):
        body["message"] = message
    
    return Response(json.dumps(body), status=status, mimetype="application/json")
@app.route("/users", methods=["GET"])
def select_all_users(): # consulta ao banco de dados na tabela Usuario
    obj_users = User.query.all()
    users_json = [user.to_json() for user in obj_users]
    
    return func_response(200, "users", users_json)

@app.route("/users/<rg>", methods=["GET"])
def select_user(rg):
    obj_user = User.query.filter_by(rg=rg).first()
    users_json = obj_user.to_json()

    return func_response(200, "user", users_json)

@app.route("/users", methods=["POST"])
def cria_usuario():
    body = request.get_json()

    try:
        user = User(rg=body["rg"], name=body["name"], email= body["email"],password= body["password"],cpf= body["cpf"], age= body["age"])
        if (user.age >= 18):
            db.session.add(user)
            db.session.commit()      
        else:
            return func_response(400, "usuario", {}, "Erro ao cadastrar")
        return func_response(201, "usuario", user.to_json(), "Criado com sucesso")
    except Exception as e:
        print(e)
        return func_response(400, "usuario", {}, "Erro ao cadastrar")

@app.route("/users/<rg>", methods=["DELETE"])
def deleta_usuario(rg):
    obj_user = User.query.filter_by(rg=rg).first()

    try:
        db.session.delete(obj_user)
        db.session.commit()

        return func_response(200, "usuario", obj_user.to_json(), "deletado com sucesso")
    except Exception as e:
        print("Erro", e)
        return func_response(400, "usuario", {}, "Erro ao deletar")

@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    user = User.query.filter_by(cpf=body.cpf)
    if (user.password == body["password"]):
        return user
    else:
        return func_response(400, "usuario", {}, "Senha invalida")
app.run()




