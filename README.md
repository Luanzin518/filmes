# CineLista — Catálogo de Filmes

Sistema web CRUD desenvolvido com Python, Flask, SQLite, HTML e Jinja2 para a atividade prática UC32.

## Funcionalidades

- **Cadastrar:** título, gênero, ano de lançamento e nota de 1 a 10.
- **Listar:** exibe os filmes cadastrados em cartões.
- **Editar:** atualiza os dados de um filme.
- **Excluir:** remove um filme com confirmação.
- **Banco automático:** cria a pasta `instance/`, o banco `catalogo.db` e a tabela na primeira inicialização.
- **Validação:** valida campos obrigatórios, tamanho do título/gênero, ano e nota.

## Requisitos

- Python 3.10 ou mais recente (recomendado Python 3.12 para este projeto).
- pip.

## Executar no Windows

1. Extraia o ZIP para uma pasta, por exemplo `C:\Projetos\catalogo-filmes`.
2. Abra essa pasta no VS Code ou abra o PowerShell nela.
3. Crie e ative um ambiente virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Se o comando `py` não estiver disponível, use `python` no lugar.
4. Instale as dependências:

   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Inicie a aplicação:

   ```powershell
   python app.py
   ```
6. Abra no navegador: http://127.0.0.1:5000

O arquivo `instance/catalogo.db` é criado automaticamente. Não precisa criar o banco manualmente.

## Publicar no GitHub

1. Crie um repositório novo no GitHub, por exemplo `catalogo-filmes`.
2. Abra um terminal dentro da pasta do projeto e execute:

   ```bash
   git init
   git add .
   git commit -m "Cria catálogo de filmes com Flask e SQLite"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/catalogo-filmes.git
   git push -u origin main
   ```

3. Troque `SEU-USUARIO` pelo seu nome de usuário do GitHub. Use a URL real do repositório que você criou.

## Publicar no Render

1. Entre em https://render.com/ e conecte sua conta do GitHub.
2. Selecione **New + → Web Service** e escolha o repositório `catalogo-filmes`.
3. Configure:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Crie o serviço e aguarde o deploy terminar.
5. Abra o endereço `onrender.com` que o Render mostrar e teste cadastro, edição e exclusão.

## Observação sobre SQLite no Render

Sem disco persistente configurado, o sistema de arquivos do serviço pode ser substituído durante deploys/reinicializações e os dados do SQLite podem ser perdidos. Isso é aceitável para uma demonstração escolar, conforme o enunciado. Para manter os dados no Render, configure um disco persistente e a variável de ambiente `DATABASE_PATH` apontando para um arquivo dentro do caminho montado pelo disco. Consulte a documentação atual do Render antes de configurar armazenamento persistente.

## Rotas principais

| Método | Caminho | Operação |
|---|---|---|
| GET | `/` | Lista filmes |
| GET, POST | `/filmes/novo` | Cadastra filme |
| GET, POST | `/filmes/<id>/editar` | Edita filme |
| POST | `/filmes/<id>/excluir` | Exclui filme |

## Estrutura

```text
catalogo-filmes/
├── app.py
├── requirements.txt
├── Procfile
├── .gitignore
├── README.md
├── instance/              # criada automaticamente; não vai para o Git
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── form.html
    └── 404.html
```
