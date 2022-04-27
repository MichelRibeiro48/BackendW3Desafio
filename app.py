from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:senhasecreta123@db.xfzdbuxmtmaltnmjcceb.supabase.co:5432/postgres'

db = SQLAlchemy(app)

class Usuario(db.Model):
    rg = db.Column(db.Integer, primary_key= True, nullable=False)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    senha = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    idade = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {"rg": self.rg, "nome": self.nome, "email": self.email,"senha": self.senha, "cpf": self.cpf, "idade": self.idade}

def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem
    
    return Response(json.dumps(body), status=status, mimetype="application/json")
@app.route("/usuarios", methods=["GET"])
def seleciona_usuarios(): # consulta ao banco de dados na tabela Usuario
    usuarios_objetos = Usuario.query.all()
    usuarios_json = [usuario.to_json() for usuario in usuarios_objetos]
    
    return gera_response(200, "usuarios", usuarios_json)

@app.route("/usuarios/<rg>", methods=["GET"])
def seleciona_usuario(rg):
    usuarios_objetos = Usuario.query.filter_by(rg=rg).first()
    usuarios_json = usuarios_objetos.to_json()

    return gera_response(200, "usuarios", usuarios_json)

@app.route("/usuarios", methods=["POST"])
def cria_usuario():
    body = request.get_json()

    try:
        usuario = Usuario(rg=body["rg"], nome=body["nome"], email= body["email"],senha= body["senha"],cpf= body["cpf"], idade= body["idade"])
        if (usuario.idade >= 18):
            db.session.add(usuario)
            db.session.commit()      
        else:
            return gera_response(400, "usuario", {}, "Erro ao cadastrar")
        return gera_response(201, "usuario", usuario.to_json(), "Criado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "usuario", {}, "Erro ao cadastrar")

@app.route("/usuarios/<rg>", methods=["DELETE"])
def deleta_usuario(rg):
    usuario_objeto = Usuario.query.filter_by(rg=rg).first()

    try:
        db.session.delete(usuario_objeto)
        db.session.commit()

        return gera_response(200, "usuario", usuario_objeto.to_json(), "deletado com sucesso")
    except Exception as e:
        print("Erro", e)
        return gera_response(400, "usuario", {}, "Erro ao deletar")

@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    usuario = Usuario.query.filter_by(cpf=body.cpf)
    if (usuario.senha == body["password"]):
        return usuario
    else:
        return gera_response(400, "usuario", {}, "Senha invalida")
app.run()




