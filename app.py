import os
import sqlite3
from pathlib import Path
from datetime import datetime

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

# ==========================================
# CONFIGURAÇÃO DO PROJETO
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = os.environ.get(
    "DATABASE_PATH",
    str(INSTANCE_DIR / "catalogo.db"),
)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "chave-de-desenvolvimento-altere-no-render",
)

app.config["DATABASE"] = DATABASE_PATH


# ==========================================
# CONEXÃO COM O BANCO DE DADOS
# ==========================================

def get_db():
    """Obtém uma conexão SQLite para a requisição atual."""

    if "db" not in g:
        caminho_banco = Path(app.config["DATABASE"])
        caminho_banco.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        g.db = sqlite3.connect(
            str(caminho_banco),
            timeout=10,
        )

        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


@app.teardown_appcontext
def close_db(_erro=None):
    """Fecha a conexão ao terminar a requisição."""

    db = g.pop("db", None)

    if db is not None:
        db.close()


# ==========================================
# CRIAÇÃO AUTOMÁTICA DO BANCO
# ==========================================

def init_db():
    """Cria o banco e a tabela caso não existam."""

    caminho_banco = Path(app.config["DATABASE"])
    caminho_banco.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    db = sqlite3.connect(str(caminho_banco), timeout=10)

    try:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS filmes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                genero TEXT NOT NULL,
                ano INTEGER NOT NULL,
                nota REAL NOT NULL
                    CHECK (nota >= 1 AND nota <= 10),
                criado_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db.commit()

    finally:
        db.close()


# Inicializa o banco ao carregar o aplicativo.
# Funciona tanto localmente quanto no Render.
init_db()


# ==========================================
# VARIÁVEIS DISPONÍVEIS NOS TEMPLATES
# ==========================================

@app.context_processor
def inject_current_year():
    """Disponibiliza o ano atual para os templates."""

    return {
        "current_year": datetime.now().year
    }


# ==========================================
# VALIDAÇÃO DOS DADOS DOS FILMES
# ==========================================

def validar_filme(formulario):
    """Valida os dados recebidos do formulário."""

    titulo = formulario.get("titulo", "").strip()
    genero = formulario.get("genero", "").strip()
    ano_texto = formulario.get("ano", "").strip()

    nota_texto = (
        formulario.get("nota", "")
        .strip()
        .replace(",", ".")
    )

    if not titulo or not genero or not ano_texto or not nota_texto:
        return None, "Preencha todos os campos."

    if len(titulo) > 120:
        return None, "O título deve ter no máximo 120 caracteres."

    if len(genero) > 60:
        return None, "O gênero deve ter no máximo 60 caracteres."

    try:
        ano = int(ano_texto)

    except (TypeError, ValueError):
        return None, "Informe um ano válido."

    ano_atual = datetime.now().year

    if ano < 1888 or ano > ano_atual + 10:
        return None, (
            f"O ano deve estar entre 1888 e {ano_atual + 10}."
        )

    try:
        nota = float(nota_texto)

    except (TypeError, ValueError):
        return None, "A nota deve ser um número entre 1 e 10."

    if not 1 <= nota <= 10:
        return None, "A nota deve estar entre 1 e 10."

    filme = {
        "titulo": titulo,
        "genero": genero,
        "ano": ano,
        "nota": nota,
    }

    return filme, None


# ==========================================
# READ — LISTAR FILMES
# ==========================================

@app.route("/")
def index():
    """Exibe todos os filmes cadastrados."""

    with get_db() as db:
        filmes = db.execute(
            """
            SELECT id, titulo, genero, ano, nota
            FROM filmes
            ORDER BY titulo COLLATE NOCASE
            """
        ).fetchall()

    return render_template(
        "index.html",
        filmes=filmes,
    )


# ==========================================
# CREATE — CADASTRAR FILME
# ==========================================

@app.route("/filmes/novo", methods=["GET", "POST"])
def novo_filme():
    """Exibe o formulário e cadastra um filme."""

    if request.method == "POST":
        filme, erro = validar_filme(request.form)

        if erro:
            flash(erro, "erro")

            return render_template(
                "form.html",
                filme=request.form,
                modo="novo",
            ), 400

        with get_db() as db:
            db.execute(
                """
                INSERT INTO filmes (
                    titulo,
                    genero,
                    ano,
                    nota
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    filme["titulo"],
                    filme["genero"],
                    filme["ano"],
                    filme["nota"],
                ),
            )

        flash("Filme cadastrado com sucesso!", "sucesso")

        return redirect(url_for("index"))

    return render_template(
        "form.html",
        filme=None,
        modo="novo",
    )


# ==========================================
# UPDATE — EDITAR FILME
# ==========================================

@app.route(
    "/filmes/<int:filme_id>/editar",
    methods=["GET", "POST"],
)
def editar_filme(filme_id):
    """Edita um filme existente."""

    with get_db() as db:
        filme_atual = db.execute(
            "SELECT * FROM filmes WHERE id = ?",
            (filme_id,),
        ).fetchone()

    if filme_atual is None:
        abort(404)

    if request.method == "POST":
        filme, erro = validar_filme(request.form)

        if erro:
            flash(erro, "erro")

            dados = dict(request.form)
            dados["id"] = filme_id

            return render_template(
                "form.html",
                filme=dados,
                modo="editar",
            ), 400

        with get_db() as db:
            db.execute(
                """
                UPDATE filmes
                SET titulo = ?,
                    genero = ?,
                    ano = ?,
                    nota = ?
                WHERE id = ?
                """,
                (
                    filme["titulo"],
                    filme["genero"],
                    filme["ano"],
                    filme["nota"],
                    filme_id,
                ),
            )

        flash("Filme atualizado com sucesso!", "sucesso")

        return redirect(url_for("index"))

    return render_template(
        "form.html",
        filme=filme_atual,
        modo="editar",
    )


# ==========================================
# DELETE — EXCLUIR FILME
# ==========================================

@app.route(
    "/filmes/<int:filme_id>/excluir",
    methods=["POST"],
)
def excluir_filme(filme_id):
    """Exclui um filme pelo seu identificador."""

    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM filmes WHERE id = ?",
            (filme_id,),
        )

        apagado = cursor.rowcount

    if apagado == 0:
        abort(404)

    flash("Filme excluído com sucesso.", "sucesso")

    return redirect(url_for("index"))


# ==========================================
# PÁGINA NÃO ENCONTRADA
# ==========================================

@app.errorhandler(404)
def pagina_nao_encontrada(_erro):
    """Trata páginas ou filmes que não existem."""

    caminho_template = BASE_DIR / "templates" / "404.html"

    if caminho_template.exists():
        return render_template("404.html"), 404

    return "Página não encontrada.", 404


# ==========================================
# EXECUÇÃO LOCAL
# ==========================================

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", "5000"))
    modo_debug = os.environ.get("FLASK_DEBUG") == "1"

    app.run(
        host="0.0.0.0",
        port=porta,
        debug=modo_debug,
    )
