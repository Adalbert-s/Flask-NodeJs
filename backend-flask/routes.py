from flask import Blueprint, request, jsonify
from difflib import SequenceMatcher
from models import db, Usuario, Verificacao

routes = Blueprint('routes', __name__)

@routes.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json()
    if Usuario.query.filter_by(email=dados.get('email')).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400
    usuario = Usuario(nome=dados['nome'], email=dados['email'], senha=dados['senha'])
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado', 'id': usuario.id}), 201


# Outras rotas de usuário e verificações...

