from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="241207",
        database="imobiliaria"
    )


@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM imoveis")
    imoveis = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(imoveis)


@app.route("/imoveis/<int:id>", methods=["GET"])
def listar_imovel_por_id(id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (id,))
    imovel = cursor.fetchone()

    cursor.close()
    conexao.close()

    if imovel is None:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    return jsonify(imovel)


if __name__ == "__main__":
    app.run(debug=True)
