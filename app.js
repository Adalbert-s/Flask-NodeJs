const readline = require('readline');
const axios = require('axios');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let usuarioLogado = null;

function perguntar(pergunta) {
  return new Promise(resolve => rl.question(pergunta, resolve));
}

async function menuPrincipal() {
  console.log('\n--- MENU PRINCIPAL ---');
  console.log('1 - Login');
  console.log('2 - Cadastrar');
  console.log('3 - Deletar usuário');
  console.log('0 - Sair');

  const opcao = await perguntar('Escolha uma opção: ');

  switch (opcao) {
    case '1':
      await fazerLogin();
      break;
    case '2':
      await cadastrarUsuario();
      break;
    case '3':
      await deletarUsuario();
      break;
    case '0':
      console.log('Saindo...');
      rl.close();
      return;
    default:
      console.log('Opção inválida!');
  }

  await menuPrincipal();
}

async function menuLogado() {
  console.log(`\n--- MENU DO USUÁRIO: ${usuarioLogado} ---`);
  console.log('1 - Verificar Plágio');
  console.log('2 - Logout');

  const opcao = await perguntar('Escolha uma opção: ');

  switch (opcao) {
    case '1':
      await verificarPlagio();
      break;
    case '2':
      usuarioLogado = null;
      console.log('Logout realizado com sucesso.');
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
    const resposta = await axios.get('http://localhost:5000/usuarios');
    const usuario = resposta.data.find(u => u.email === email);

    if (!usuario) {
      console.error('Usuário não encontrado.');
      return;
    }

    // Agora vamos buscar os dados completos do usuário para comparar a senha
    const usuarioDetalhado = await axios.get(`http://localhost:5000/usuarios/${usuario.id}`);

    if (usuarioDetalhado.data.senha !== senha) {
      console.error('Senha incorreta.');
      return;
    }

    console.log('Login realizado com sucesso!');
    emailLogado = email;
    await menuLogado();

  } catch (erro) {
    console.error('Erro ao fazer login:', erro.response?.data?.erro || erro.message);
  }
}

async function cadastrarUsuario() {
  const nome = await perguntar('Nome: ');
  const email = await perguntar('Email: ');
  const senha = await perguntar('Senha: ');

  try {
    const resposta = await axios.post('http://localhost:5000/usuarios', {
      nome,
      email,
      senha
    });

    console.log(resposta.data.mensagem || 'Usuário cadastrado com sucesso!');
  } catch (erro) {
    console.error('Erro ao cadastrar:', erro.response?.data?.erro || erro.message);
  }
}

async function deletarUsuario() {
  const usuario = await perguntar('Usuário: ');
  const senha = await perguntar('Senha: '); // Confirmação básica

  try {
    const resposta = await axios.delete(`http://localhost:5000/usuarios/${usuario}`, {
      data: { senha } // Envia no corpo da requisição
    });

    console.log(resposta.data.mensagem || 'Usuário deletado com sucesso!');
  } catch (erro) {
    console.error('Erro ao deletar usuário:', erro.response?.data?.erro || erro.message);
  }
}

async function verificarPlagio() {
  const texto1 = await perguntar('Digite o texto produzido: ');
  const texto2 = await perguntar('Digite o texto para comparação: ');

  try {
    const resposta = await axios.post('http://localhost:5000/verificar-plagio', {
      texto1,
      texto2
    });

    console.log('\n--- Resultado ---');
    console.log(`Similaridade: ${resposta.data.porcentagem_plagio}%`);
    console.log(resposta.data.mensagem);
  } catch (erro) {
    console.error('Erro ao verificar plágio:', erro.response?.data?.erro || erro.message);
  }
}

menuPrincipal();
