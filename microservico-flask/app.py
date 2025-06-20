from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # importante manter segredo

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
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

# Criar usuário com hash de senha
@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json()
    if Usuario.query.filter_by(email=dados.get('email')).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400
    senha_hash = generate_password_hash(dados['senha'])
    usuario = Usuario(nome=dados['nome'], email=dados['email'], senha_hash=senha_hash)
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado', 'id': usuario.id}), 201

# Login - retorna JWT se sucesso
@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    usuario = Usuario.query.filter_by(email=dados.get('email')).first()
    if not usuario or not check_password_hash(usuario.senha_hash, dados.get('senha')):
        return jsonify({'erro': 'Email ou senha incorretos'}), 401

    token = jwt.encode({
        'usuario_id': usuario.id,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token, 'mensagem': 'Login realizado com sucesso'})

# Decorador para proteger rotas
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.replace('Bearer ', '')

        if not token:
            return jsonify({'erro': 'Token é obrigatório'}), 401

        try:
            dados = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(dados['usuario_id'])
            if not current_user:
                raise
        except:
            return jsonify({'erro': 'Token inválido ou expirado'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# Exemplo de rota protegida para criar verificação
@app.route('/verificacoes', methods=['POST'])
@token_required
def criar_verificacao(current_user):
    dados = request.get_json()
    texto1 = dados.get('texto1')
    texto2 = dados.get('texto2')
    if not texto1 or not texto2:
        return jsonify({'erro': 'Campos obrigatórios ausentes'}), 400

    from difflib import SequenceMatcher
    palavras1 = texto1.lower().split()
    palavras2 = texto2.lower().split()
    porcentagem = SequenceMatcher(None, palavras1, palavras2).ratio() * 100

    verificacao = Verificacao(texto1=texto1, texto2=texto2, porcentagem=porcentagem, usuario=current_user)
    db.session.add(verificacao)
    db.session.commit()

    return jsonify({
        'id': verificacao.id,
        'porcentagem_plagio': round(porcentagem, 2),
        'mensagem': 'Plágio detectado' if porcentagem > 70 else 'Sem plágio aparente'
    }), 201

# Outros endpoints protegidos devem usar @token_required similarmente

if __name__ == '__main__':
    app.run(debug=True)
