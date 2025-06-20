const readline = require('readline');
const axios = require('axios');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let token = null;

function perguntar(pergunta) {
  return new Promise(resolve => rl.question(pergunta, resolve));
}

async function menuPrincipal() {
  console.log('\n--- MENU PRINCIPAL ---');
  console.log('1 - Login');
  console.log('2 - Cadastrar');
  console.log('0 - Sair');

  const opcao = await perguntar('Escolha uma opção: ');

  switch (opcao) {
    case '1':
      await fazerLogin();
      break;
    case '2':
      await cadastrarUsuario();
      break;
    case '0':
      console.log('Saindo...');
      rl.close();
      return;
    default:
      console.log('Opção inválida!');
  }

  if (token) {
    await menuLogado();
  } else {
    await menuPrincipal();
  }
}

async function menuLogado() {
  console.log('\n--- MENU LOGADO ---');
  console.log('1 - Verificar Plágio');
  console.log('2 - Logout');

  const opcao = await perguntar('Escolha uma opção: ');

  switch (opcao) {
    case '1':
      await verificarPlagio();
      break;
    case '2':
      token = null;
      console.log('Logout realizado.');
      return;
    default:
      console.log('Opção inválida!');
  }

  await menuLogado();
}

async function fazerLogin() {
  const email = await perguntar('Email: ');
  const senha = await perguntar('Senha: ');

  try {
    const resposta = await axios.post('http://localhost:5000/login', { email, senha });
    token = resposta.data.token;
    console.log(resposta.data.mensagem);
  } catch (erro) {
    console.error('Erro no login:', erro.response?.data?.erro || erro.message);
  }
}

async function cadastrarUsuario() {
  const nome = await perguntar('Nome: ');
  const email = await perguntar('Email: ');
  const senha = await perguntar('Senha: ');

  try {
    const resposta = await axios.post('http://localhost:5000/usuarios', { nome, email, senha });
    console.log(resposta.data.mensagem || 'Usuário criado com sucesso!');
  } catch (erro) {
    console.error('Erro ao cadastrar:', erro.response?.data?.erro || erro.message);
  }
}

async function verificarPlagio() {
  if (!token) {
    console.log('Você precisa estar logado para verificar plágio.');
    return;
  }
  const texto1 = await perguntar('Texto produzido: ');
  const texto2 = await perguntar('Texto para comparar: ');

  try {
    const resposta = await axios.post('http://localhost:5000/verificacoes', 
      { texto1, texto2 }, 
      { headers: { Authorization: `Bearer ${token}` } }
    );

    console.log('\n--- Resultado ---');
    console.log(`Similaridade: ${resposta.data.porcentagem_plagio}%`);
    console.log(resposta.data.mensagem);
  } catch (erro) {
    console.error('Erro ao verificar plágio:', erro.response?.data?.erro || erro.message);
  }
}

menuPrincipal();
