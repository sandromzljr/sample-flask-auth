from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin@127.0.0.1:3306/flask-crud"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    request_json = request.json
    username = request_json.get("username")
    password = request_json.get("password")

    if username and password:
        user = User.query.filter_by(username = username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
                login_user(user)
                return jsonify({"message": "AUTENTICAÇÃO REALIZADA COM SUCESSO"})

    return jsonify({"message": "CREDÊNCIAS INVÁLIDAS"}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
     logout_user()
     return jsonify({"message": "LOGOUT REALIZADO COM SUCESSO!"})

@app.route("/user", methods=["POST"])
def create_user():
    request_json = request.json
    username = request_json.get("username")
    password = request_json.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username = username, password = hashed_password, role="user")
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "CADASTRO REALIZADO COM SUCESSO"})

    return jsonify({"message": "DADOS INVÁLIDOS"}), 400

@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}

    return jsonify({"message": "USUÁRIO NÃO ENCONTRADO"}), 404

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    user = User.query.get(id_user)
    request_json = request.json

    if id_user != current_user.id and current_user.role == "user":
        return jsonify({"message": "OPERAÇÃO NÃO PERMITIDA"}), 403

    if user and request_json.get("password"):
        user.password = request_json.get("password")
        db.session.commit()

        return jsonify({"message": f"USUÁRIO {id_user} ATUALIZADO COM SUCESSO!"})

    return jsonify({"message": "USUÁRIO NÃO ENCONTRADO"}), 404

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != "admin":
        return jsonify({"message": "OPERAÇÃO NÃO PERMITIDA"}), 403

    if id_user == current_user.id:
        return jsonify({"message": f"DELEÇÃO NÃO PERMITIDA"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"USUÁRIO {id_user} APAGADO COM SUCESSO!"})

    return jsonify({"message": "USUÁRIO NÃO ENCONTRADO"}), 404
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)
