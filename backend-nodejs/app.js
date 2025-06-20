const readline = require('readline');
const axios = require('axios');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let tokenJWT = null;
let nomeLogado = null;

function perguntar(pergunta) {
  return new Promise(resolve => rl.question(pergunta, resolve));
}

async function menuPrincipal() {
  console.log('\n--- MENU PRINCIPAL ---');
  console.log('1 - Login');
  console.log('2 - Cadastrar');
  console.log('3 - Tentar Deletar para dar Erro');
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
  console.log(`\n--- MENU DO USUÁRIO: ${nomeLogado} ---`);
  console.log('1 - Verificar Plágio');
  console.log('2 - Logout');
  console.log('3 - Deletar usuário');

  const opcao = await perguntar('Escolha uma opção: ');

  switch (opcao) {
    case '1':
      await verificarPlagio();
      break;
    case '2':
      tokenJWT = null;
      nomeLogado = null;
      console.log('Logout realizado com sucesso.');
      return;
    case '3':
      await deletarUsuario();
      break;
    default:
      console.log('Opção inválida!');
  }

  await menuLogado();
}

async function fazerLogin() {
  const email = await perguntar('Email: ');
  const senha = await perguntar('Senha: ');

  try {
    // Primeiro verificamos se o usuário existe, usando GET /usuarios
    const respostaUsuarios = await axios.get('http://localhost:5000/usuarios');
    const usuario = respostaUsuarios.data.find(u => u.email === email);

    if (!usuario) {
      console.error('Usuário não existe.');
      return;
    }

    // Se usuário existe, tentamos autenticar pelo POST /login
    try {
      const respostaLogin = await axios.post('http://localhost:5000/login', { email, senha });

      nomeLogado = usuario.nome;
      emailLogado = email;
      tokenJWT = respostaLogin.data.token;

      console.log('Login realizado com sucesso!');
      await menuLogado();
    } catch (erroLogin) {
      // Se deu erro no login, significa senha incorreta ou algo assim
      if (erroLogin.response && erroLogin.response.status === 401) {
        console.error('Email ou senha incorretos.');
      } else {
        console.error('Erro ao fazer login:', erroLogin.message);
      }
    }

  } catch (erro) {
    console.error('Erro ao buscar usuários:', erro.response?.data?.erro || erro.message);
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
  if (!tokenJWT) {
    console.log('Você precisa estar logado para deletar sua conta.');
    return;
  }

  const confirmacao = await perguntar('Tem certeza que deseja deletar sua conta? (s/n): ');
  if (confirmacao.toLowerCase() !== 's') {
    console.log('Operação cancelada.');
    return;
  }

  try {
    const resposta = await axios.delete('http://localhost:5000/usuarios', {
      headers: {
        Authorization: `Bearer ${tokenJWT}`
      }
    });

    console.log(resposta.data.mensagem);
    tokenJWT = null;
    nomeLogado = null;
  } catch (erro) {
    console.error('Erro ao deletar usuário:', erro.response?.data?.erro || erro.message);
  }
}


async function verificarPlagio() {
  const texto1 = await perguntar('Digite o texto produzido: ');
  const texto2 = await perguntar('Digite o texto para comparação: ');

  try {
    const resposta = await axios.post('http://localhost:5000/verificacoes', {
      texto1,
      texto2
    }, {
      headers: {
        Authorization: `Bearer ${tokenJWT}`
      }
    });

    console.log('\n--- Resultado ---');
    console.log(`Similaridade: ${resposta.data.porcentagem_plagio}%`);
    console.log(resposta.data.mensagem);
  } catch (erro) {
    console.error('Erro ao verificar plágio:', erro.response?.data?.erro || erro.message);
  }
}

menuPrincipal();
