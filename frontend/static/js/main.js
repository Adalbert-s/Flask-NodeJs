let emailLogado = null;

function login() {
  const email = document.getElementById('email').value;
  const senha = document.getElementById('senha').value;

  fetch('http://localhost:5000/usuarios')
    .then(res => res.json())
    .then(usuarios => {
      const usuario = usuarios.find(u => u.email === email);
      if (!usuario) return alert('Usuário não encontrado.');

      fetch(`http://localhost:5000/usuarios/${usuario.id}`)
        .then(res => res.json())
        .then(detalhes => {
          if (detalhes.senha !== senha) return alert('Senha incorreta.');
          emailLogado = email;
          alert('Login realizado com sucesso!');
        });
    });
}

function cadastrar() {
  const nome = document.getElementById('nome').value;
  const email = document.getElementById('novoEmail').value;
  const senha = document.getElementById('novaSenha').value;

  fetch('http://localhost:5000/usuarios', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, email, senha })
  })
    .then(res => res.json())
    .then(data => alert(data.mensagem || data.erro));
}

function verificarPlagio() {
  if (!emailLogado) return alert('Você precisa estar logado.');

  const texto1 = document.getElementById('texto1').value;
  const texto2 = document.getElementById('texto2').value;

  fetch('http://localhost:5000/verificacoes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: emailLogado, texto1, texto2 })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById('resultado').innerHTML =
        `<p>Similaridade: ${data.porcentagem_plagio?.toFixed(2) || '--'}%</p>
         <p>${data.mensagem || data.erro}</p>`;
    });
}
