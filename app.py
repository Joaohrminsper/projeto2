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


if __name__ == "__main__":
    app.run(debug=True)