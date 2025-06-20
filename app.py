from flask import Flask, render_template
from models import db
from routes import routes

app = Flask(
    __name__, 
    static_folder='../frontend/static',   # onde ficam css, js, imagens
    template_folder='../frontend'         # onde fica index.html
)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
