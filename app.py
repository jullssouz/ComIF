import sqlite3

from flask import Flask, redirect, render_template, request, url_for

import bd

app = Flask(__name__)
DATABASE = "comif.db"

bd.init_db()


def get_db_connection():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


@app.route("/")
def index():
    conexao = get_db_connection()
    refeicoes = conexao.execute(
        "SELECT * FROM refeicao ORDER BY categoria, nome_prato"
    ).fetchall()
    conexao.close()

    return render_template("index.html", refeicoes=refeicoes)


@app.route("/cardapio")
def cardapio():
    conexao = get_db_connection()
    refeicoes = conexao.execute(
        "SELECT * FROM refeicao ORDER BY categoria, nome_prato"
    ).fetchall()
    conexao.close()

    return render_template("cardapio.html", refeicoes=refeicoes)


@app.route("/adicionar-refeicao", methods=["GET", "POST"])
def adicionar_refeicao():
    if request.method == "POST":
        nome_prato = (request.form.get("nome_prato") or "").strip()
        categoria = (request.form.get("categoria") or "").strip()
        ingredientes = (request.form.get("ingredientes") or "").strip()
        observacao = (request.form.get("observacao") or "").strip()

        if not nome_prato or not categoria or not ingredientes:
            return redirect(url_for("adicionar_refeicao"))

        conexao = get_db_connection()
        conexao.execute(
            "INSERT INTO refeicao (nome_prato, categoria, ingredientes, observacao) VALUES (?, ?, ?, ?)",
            (nome_prato, categoria, ingredientes, observacao),
        )
        conexao.commit()
        conexao.close()

        return redirect(url_for("cardapio"))

    return render_template("cardapio_add.html")


@app.route("/ver-refeicao/<int:id_refeicao>")
def ver_refeicao(id_refeicao):
    conexao = get_db_connection()
    refeicao = conexao.execute(
        "SELECT * FROM refeicao WHERE id_refeicao = ?",
        (id_refeicao,),
    ).fetchone()
    conexao.close()

    if not refeicao:
        return redirect(url_for("cardapio"))

    return render_template("cardapio_ver.html", refeicao=refeicao, id_refeicao=id_refeicao)


@app.route("/editar-refeicao/<int:id_refeicao>", methods=["GET", "POST"])
def editar_refeicao(id_refeicao):
    conexao = get_db_connection()
    refeicao = conexao.execute(
        "SELECT * FROM refeicao WHERE id_refeicao = ?",
        (id_refeicao,),
    ).fetchone()

    if request.method == "POST":
        nome_prato = (request.form.get("nome_prato") or "").strip()
        categoria = (request.form.get("categoria") or "").strip()
        ingredientes = (request.form.get("ingredientes") or "").strip()
        observacao = (request.form.get("observacao") or "").strip()

        if not nome_prato or not categoria or not ingredientes:
            return redirect(url_for("editar_refeicao", id_refeicao=id_refeicao))

        conexao.execute(
            "UPDATE refeicao SET nome_prato = ?, categoria = ?, ingredientes = ?, observacao = ? WHERE id_refeicao = ?",
            (nome_prato, categoria, ingredientes, observacao, id_refeicao),
        )
        conexao.commit()
        conexao.close()
        return redirect(url_for("ver_refeicao", id_refeicao=id_refeicao))

    conexao.close()
    return render_template("cardapio_edit.html", refeicao=refeicao, id_refeicao=id_refeicao)


@app.route("/deletar-refeicao/<int:id_refeicao>", methods=["POST"])
def deletar_refeicao(id_refeicao):
    conexao = get_db_connection()
    conexao.execute("DELETE FROM refeicao WHERE id_refeicao = ?", (id_refeicao,))
    conexao.commit()
    conexao.close()
    return redirect(url_for("cardapio"))


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


if __name__ == "__main__":
    bd.init_db()
    app.run(debug=True)
