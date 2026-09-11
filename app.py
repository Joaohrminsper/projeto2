from flask import *
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


@app.route("/imoveis", methods=["POST"])   
def adicionar_imovel():
    req_data = request.get_json(silent=True)
    campos_obrigatorios = {"logradouro", "tipo_logradouro", "bairro", "cidade", "cep", "tipo", "valor", "data_aquisicao"}

    if not isinstance(req_data, dict):
        return jsonify({"erro": "O corpo da requisição deve ser um JSON"}), 400

    campos_faltantes = campos_obrigatorios - req_data.keys()
    if campos_faltantes:
        return jsonify({
            "erro": "Campos obrigatórios ausentes",
            "campos": sorted(campos_faltantes),
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()
    campos = (
        "logradouro",
        "tipo_logradouro",
        "bairro",
        "cidade",
        "cep",
        "tipo",
        "valor",
        "data_aquisicao",
    )
    valores = tuple(req_data.get(campo) for campo in campos)
    placeholders = ", ".join(["%s"] * len(campos))
    cursor.execute(
        f"INSERT INTO imoveis ({', '.join(campos)}) VALUES ({placeholders})",
        valores,
    )
    conexao.commit()
    imovel_id = cursor.lastrowid

    cursor.close()
    conexao.close()

    return jsonify({**req_data, "id": imovel_id}), 201

if __name__ == "__main__":
    app.run(debug=True)
