from flask import Flask, render_template
from models import db
from routes import routes
from flask_cors import CORS


app = Flask(
    __name__, 
    static_folder='../frontend/static',   # onde ficam css, js, imagens
    template_folder='../frontend'         # onde fica index.html
)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(routes)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/verificar')
def verificar():
    return render_template('verificar.html')

@app.route('/historico')
def historico():
    return render_template('historico.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
