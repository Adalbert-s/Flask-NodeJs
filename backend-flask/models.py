from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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
