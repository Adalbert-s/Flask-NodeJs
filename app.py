from flask import Flask, request, jsonify
from difflib import SequenceMatcher

app = Flask(__name__)

def calcular_similaridade_por_palavras(texto1, texto2):
    palavras1 = texto1.lower().split()
    palavras2 = texto2.lower().split()
    matcher = SequenceMatcher(None, palavras1, palavras2)
    return matcher.ratio() * 100  # porcentagem

@app.route('/verificar-plagio', methods=['POST'])
def verificar_plagio():
    dados = request.get_json()

    texto1 = dados.get('texto1')
    texto2 = dados.get('texto2')

    if not texto1 or not texto2:
        return jsonify({'erro': 'Ambos os textos devem ser fornecidos.'}), 400

    porcentagem = calcular_similaridade_por_palavras(texto1, texto2)

    return jsonify({
        'porcentagem_plagio': round(porcentagem, 2),
        'mensagem': 'Texto potencialmente plagiado' if porcentagem > 70 else 'Sem plágio aparente'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
