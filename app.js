const readline = require('readline');
const axios = require('axios');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let texto1 = '';
let texto2 = '';

rl.question('Escreva o texto produzido: ', function(resposta1) {
  texto1 = resposta1;

  rl.question('Escreva o texto para comparação: ', async function(resposta2) {
    texto2 = resposta2;

    try {
      const resposta = await axios.post('http://localhost:5000/verificar-plagio', {
        texto1: texto1,
        texto2: texto2
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('\n--- Resultado vindo do Flask ---');
      console.log(`Plágio: ${resposta.data.mensagem}`);
      console.log(`Similaridade: ${resposta.data.porcentagem_plagio}%`);
    } catch (erro) {
      console.error('Erro ao enviar para o Flask:', erro.response?.data || erro.message);
    }

    rl.close();
  });
});
