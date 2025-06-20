from flask import Blueprint, request, jsonify
from difflib import SequenceMatcher
from models import db, Usuario, Verificacao

routes = Blueprint('routes', __name__)

# Rota para login
@routes.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or usuario.senha != senha:
        return jsonify({'erro': 'Email ou senha inválidos'}), 401

    return jsonify({'mensagem': 'Login bem-sucedido', 'email': usuario.email}), 200

# Rota para listar usuários
@routes.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = [{'id': u.id, 'nome': u.nome, 'email': u.email} for u in usuarios]
    return jsonify(resultado)

# Rota para criar usuário (POST)
@routes.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado'}), 409

    novo_usuario = Usuario(nome=nome, email=email, senha=senha)
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso'}), 201

# Rota para verificação de plágio (POST)
@routes.route('/verificacoes', methods=['POST'])
def verificar_plagio():
    dados = request.get_json()
    texto1 = dados.get('texto1')
    texto2 = dados.get('texto2')
    email = dados.get('email')

    if not texto1 or not texto2 or not email:
        return jsonify({'erro': 'Campos texto1, texto2 e email são obrigatórios'}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    similaridade = SequenceMatcher(None, texto1, texto2).ratio()
    porcentagem = round(similaridade * 100, 2)

    # Salvar a verificação no banco
    verificacao = Verificacao(
        texto1=texto1,
        texto2=texto2,
        porcentagem=porcentagem,
        usuario=usuario
    )
    db.session.add(verificacao)
    db.session.commit()

    return jsonify({
        'porcentagem_plagio': porcentagem,
        'mensagem': 'Verificação concluída.'
    }), 200

# Rota para consultar histórico de verificações por email (GET)
@routes.route('/verificacoes', methods=['GET'])
def listar_verificacoes():
    email = request.args.get('email')
    if not email:
        return jsonify({'erro': 'Parâmetro email é obrigatório'}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    verificacoes = Verificacao.query.filter_by(usuario_id=usuario.id).all()
    resultado = [{
        'texto1': v.texto1,
        'texto2': v.texto2,
        'porcentagem': v.porcentagem,
        'data': v.data.isoformat()
    } for v in verificacoes]

    return jsonify(resultado)
