from flask import Blueprint, request, jsonify
from difflib import SequenceMatcher
from models import db, Usuario, Verificacao
routes = Blueprint('routes', __name__)

@routes.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or usuario.senha != senha:
        return jsonify({'erro': 'Email ou senha inválidos'}), 401

    return jsonify({'mensagem': 'Login bem-sucedido', 'email': usuario.email}), 200

@routes.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return {"erro": "Usuário não encontrado"}, 404
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "senha": usuario.senha  # cuidado em enviar senha, só faça isso em ambiente controlado
    }

@routes.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = [{'id': u.id, 'nome': u.nome, 'email': u.email} for u in usuarios]
    return jsonify(resultado)

# Outras rotas de usuário e verificações...

@routes.route('/verificacoes', methods=['POST'])
def verificar_plagio():
    dados = request.get_json()
    texto1 = dados.get('texto1')
    texto2 = dados.get('texto2')

    if not texto1 or not texto2:
        return jsonify({'erro': 'Ambos os textos são obrigatórios'}), 400

    similaridade = SequenceMatcher(None, texto1, texto2).ratio()
    porcentagem = round(similaridade * 100, 2)

    return jsonify({
        'porcentagem_plagio': porcentagem,
        'mensagem': 'Verificação concluída.'
    }), 200

