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

@app.route("/imoveis/<int:id>", methods=["PATCH"])
def atualizar_imovel(id):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict) or not dados:
        return jsonify({
            "erro": "O corpo deve conter um JSON válido"
        }), 400

    campos_permitidos = {
        "logradouro",
        "tipo_logradouro",
        "bairro",
        "cidade",
        "cep",
        "tipo",
        "valor",
        "data_aquisicao",
    }

    campos_invalidos = set(dados) - campos_permitidos

    if campos_invalidos:
        return jsonify({
            "erro": "Campos inválidos",
            "campos": sorted(campos_invalidos),
        }), 400

    campos_texto = {
        "logradouro",
        "tipo_logradouro",
        "bairro",
        "cidade",
        "cep",
        "tipo",
        "data_aquisicao",
    }

    for campo in campos_texto:
        if campo in dados:
            if (
                not isinstance(dados[campo], str)
                or not dados[campo].strip()
            ):
                return jsonify({
                    "erro": f"O campo '{campo}' deve ser uma string válida"
                }), 400

    if "valor" in dados:
        valor = dados["valor"]

        if (
            not isinstance(valor, (int, float))
            or isinstance(valor, bool)
            or valor < 0
        ):
            return jsonify({
                "erro": "O campo 'valor' deve ser um número não negativo"
            }), 400

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM imoveis WHERE id = %s",
        (id,),
    )

    imovel = cursor.fetchone()

    if imovel is None:
        cursor.close()
        conexao.close()

        return jsonify({
            "erro": "Imóvel não encontrado"
        }), 404

    campos_para_atualizar = list(dados.keys())

    clausula_set = ", ".join(
        f"{campo} = %s"
        for campo in campos_para_atualizar
    )


    valores = [
        dados[campo]
        for campo in campos_para_atualizar
    ]

    cursor.execute(
        f"UPDATE imoveis SET {clausula_set} WHERE id = %s",
        (*valores, id),
    )

    conexao.commit()

    cursor.execute(
        "SELECT * FROM imoveis WHERE id = %s",
        (id,),
    )

    imovel_atualizado = cursor.fetchone()

    cursor.close()
    conexao.close()

    return jsonify(imovel_atualizado), 200


if __name__ == "__main__":
    app.run(debug=True)
