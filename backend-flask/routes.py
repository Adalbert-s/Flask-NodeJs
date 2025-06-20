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

@routes.route('/verificacoes', methods=['GET', 'POST'])
def verificacoes():
    if request.method == 'POST':
        dados = request.get_json()
        email = dados.get('email')
        texto1 = dados.get('texto1')
        texto2 = dados.get('texto2')

        if not texto1 or not texto2:
            return jsonify({'erro': 'Ambos os textos são obrigatórios'}), 400

        similaridade = SequenceMatcher(None, texto1, texto2).ratio()
        porcentagem = round(similaridade * 100, 2)

        # Salvar no banco
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        nova_verificacao = Verificacao(
            texto1=texto1,
            texto2=texto2,
            porcentagem=porcentagem,
            usuario_id=usuario.id
        )
        db.session.add(nova_verificacao)
        db.session.commit()

        return jsonify({
            'porcentagem_plagio': porcentagem,
            'mensagem': 'Verificação concluída.'
        }), 200

    else:  # GET
        email = request.args.get('email')
        if not email:
            return jsonify({'erro': 'Email é obrigatório para buscar histórico'}), 400

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        verificacoes = Verificacao.query.filter_by(usuario_id=usuario.id).all()

        resultado = []
        for v in verificacoes:
            resultado.append({
                'texto1': v.texto1,
                'texto2': v.texto2,
                'porcentagem': v.porcentagem,
                'data': v.data.strftime('%d/%m/%Y %H:%M:%S')
            })

        return jsonify(resultado)


