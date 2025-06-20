from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from difflib import SequenceMatcher
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    verificacoes = db.relationship('Verificacao', backref='usuario', lazy=True, cascade="all, delete")

class Verificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto1 = db.Column(db.Text, nullable=False)
    texto2 = db.Column(db.Text, nullable=False)
    porcentagem = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

with app.app_context():
    db.create_all()

# --- CRUD USUÁRIO ---

# Criar usuário
@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json()
    if Usuario.query.filter_by(email=dados.get('email')).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400
    usuario = Usuario(nome=dados['nome'], email=dados['email'], senha=dados['senha'])
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado', 'id': usuario.id}), 201

# Ler todos usuários
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = [{'id': u.id, 'nome': u.nome, 'email': u.email} for u in usuarios]
    return jsonify(resultado), 200

# Ler usuário específico
@app.route('/usuarios/<int:id>', methods=['GET'])
def buscar_usuario(id):
    u = Usuario.query.get(id)
    if not u:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    return jsonify({'id': u.id, 'nome': u.nome, 'email': u.email}), 200

# Atualizar usuário
@app.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    u = Usuario.query.get(id)
    if not u:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    dados = request.get_json()
    u.nome = dados.get('nome', u.nome)
    u.email = dados.get('email', u.email)
    u.senha = dados.get('senha', u.senha)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário atualizado'}), 200

# Deletar usuário
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    u = Usuario.query.get(id)
    if not u:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    db.session.delete(u)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário deletado'}), 200

# --- CRUD VERIFICAÇÕES (Histórico) ---

# Criar verificação (plágio)
@app.route('/verificacoes', methods=['POST'])
def criar_verificacao():
    dados = request.get_json()
    email = dados.get('email')
    texto1 = dados.get('texto1')
    texto2 = dados.get('texto2')
    if not email or not texto1 or not texto2:
        return jsonify({'erro': 'Campos obrigatórios ausentes'}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    palavras1 = texto1.lower().split()
    palavras2 = texto2.lower().split()
    porcentagem = SequenceMatcher(None, palavras1, palavras2).ratio() * 100

    verificacao = Verificacao(texto1=texto1, texto2=texto2, porcentagem=porcentagem, usuario=usuario)
    db.session.add(verificacao)
    db.session.commit()

    return jsonify({
        'id': verificacao.id,
        'porcentagem_plagio': round(porcentagem, 2),
        'mensagem': 'Plágio detectado' if porcentagem > 70 else 'Sem plágio aparente'
    }), 201

# Listar verificações de um usuário
@app.route('/verificacoes', methods=['GET'])
def listar_verificacoes():
    email = request.args.get('email')
    if not email:
        return jsonify({'erro': 'Parâmetro email é obrigatório'}), 400
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    verificacoes = Verificacao.query.filter_by(usuario_id=usuario.id).order_by(Verificacao.data.desc()).all()
    resultado = []
    for v in verificacoes:
        resultado.append({
            'id': v.id,
            'texto1': v.texto1,
            'texto2': v.texto2,
            'porcentagem': round(v.porcentagem, 2),
            'data': v.data.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(resultado), 200

# Buscar verificação específica
@app.route('/verificacoes/<int:id>', methods=['GET'])
def buscar_verificacao(id):
    v = Verificacao.query.get(id)
    if not v:
        return jsonify({'erro': 'Verificação não encontrada'}), 404
    return jsonify({
        'id': v.id,
        'texto1': v.texto1,
        'texto2': v.texto2,
        'porcentagem': round(v.porcentagem, 2),
        'data': v.data.strftime('%Y-%m-%d %H:%M:%S'),
        'usuario_id': v.usuario_id
    }), 200

# Atualizar verificação
@app.route('/verificacoes/<int:id>', methods=['PUT'])
def atualizar_verificacao(id):
    v = Verificacao.query.get(id)
    if not v:
        return jsonify({'erro': 'Verificação não encontrada'}), 404

    dados = request.get_json()
    texto1 = dados.get('texto1', v.texto1)
    texto2 = dados.get('texto2', v.texto2)

    palavras1 = texto1.lower().split()
    palavras2 = texto2.lower().split()
    porcentagem = SequenceMatcher(None, palavras1, palavras2).ratio() * 100

    v.texto1 = texto1
    v.texto2 = texto2
    v.porcentagem = porcentagem
    db.session.commit()

    return jsonify({'mensagem': 'Verificação atualizada'}), 200

# Deletar verificação
@app.route('/verificacoes/<int:id>', methods=['DELETE'])
def deletar_verificacao(id):
    v = Verificacao.query.get(id)
    if not v:
        return jsonify({'erro': 'Verificação não encontrada'}), 404
    db.session.delete(v)
    db.session.commit()
    return jsonify({'mensagem': 'Verificação deletada'}), 200


if __name__ == '__main__':
    app.run(debug=True)
