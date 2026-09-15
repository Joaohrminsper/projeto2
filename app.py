from flask import *
import mysql.connector
import os
import re
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()


CONFIGURACAO_SERVIDOR = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
NOME_BANCO = os.getenv("DB_NAME")


def inicializar_banco_de_dados():
    variaveis_obrigatorias = {
        "DB_HOST": CONFIGURACAO_SERVIDOR["host"],
        "DB_USER": CONFIGURACAO_SERVIDOR["user"],
        "DB_PASSWORD": CONFIGURACAO_SERVIDOR["password"],
        "DB_NAME": NOME_BANCO,
    }
    variaveis_ausentes = [
        nome
        for nome, valor in variaveis_obrigatorias.items()
        if valor is None
    ]

    if variaveis_ausentes:
        raise RuntimeError(
            "Variáveis ausentes no .env: "
            + ", ".join(variaveis_ausentes)
        )

    if not re.fullmatch(r"[A-Za-z0-9_]+", NOME_BANCO):
        raise RuntimeError("DB_NAME deve conter apenas letras, números e _")

    conexao_servidor = mysql.connector.connect(**CONFIGURACAO_SERVIDOR)
    cursor_servidor = conexao_servidor.cursor()
    cursor_servidor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{NOME_BANCO}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor_servidor.close()
    conexao_servidor.close()

    conexao_banco = mysql.connector.connect(
        **CONFIGURACAO_SERVIDOR,
        database=NOME_BANCO,
    )
    cursor_banco = conexao_banco.cursor()
    cursor_banco.execute("""
        CREATE TABLE IF NOT EXISTS imoveis (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            logradouro TEXT NOT NULL,
            tipo_logradouro TEXT,
            bairro TEXT,
            cidade TEXT NOT NULL,
            cep TEXT,
            tipo TEXT,
            valor REAL,
            data_aquisicao TEXT
        )
    """)
    cursor_banco.close()
    conexao_banco.close()


inicializar_banco_de_dados()


CONFIGURACAO_BANCO = {
    **CONFIGURACAO_SERVIDOR,
    "database": NOME_BANCO,
}


@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conexao = mysql.connector.connect(**CONFIGURACAO_BANCO)
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM imoveis")
    imoveis = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(imoveis)


@app.route("/imoveis/tipo/<string:tipo>", methods=["GET"])
def buscar_imoveis_por_tipo(tipo):
    conexao = mysql.connector.connect(**CONFIGURACAO_BANCO)
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM imoveis WHERE LOWER(tipo) = LOWER(%s)",
        (tipo,),
    )
    imoveis = cursor.fetchall()

    if not imoveis:
        cursor.execute("""
            SELECT DISTINCT tipo
            FROM imoveis
            WHERE tipo IS NOT NULL AND TRIM(tipo) != ''
        """)
        tipos_disponiveis = sorted(
            resultado["tipo"]
            for resultado in cursor.fetchall()
        )

        cursor.close()
        conexao.close()

        return jsonify({
            "erro": "Nenhum imóvel encontrado para o tipo informado",
            "tipos_disponiveis": tipos_disponiveis,
        }), 404

    cursor.close()
    conexao.close()

    return jsonify(imoveis), 200


@app.route("/imoveis/cidade/<string:cidade>", methods=["GET"])
def buscar_imoveis_por_cidade(cidade):
    conexao = mysql.connector.connect(**CONFIGURACAO_BANCO)
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM imoveis WHERE LOWER(cidade) = LOWER(%s)",
        (cidade,),
    )
    imoveis = cursor.fetchall()

    if not imoveis:
        cursor.execute("""
            SELECT DISTINCT cidade
            FROM imoveis
            WHERE cidade IS NOT NULL AND TRIM(cidade) != ''
        """)
        cidades_disponiveis = sorted(
            resultado["cidade"]
            for resultado in cursor.fetchall()
        )

        cursor.close()
        conexao.close()

        return jsonify({
            "erro": "Nenhum imóvel encontrado para a cidade informada",
            "cidades_disponiveis": cidades_disponiveis,
        }), 404

    cursor.close()
    conexao.close()

    return jsonify(imoveis), 200


@app.route("/imoveis/<int:id>", methods=["GET"])
def listar_imovel_por_id(id):
    conexao = mysql.connector.connect(**CONFIGURACAO_BANCO)
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

    conexao = mysql.connector.connect(**CONFIGURACAO_BANCO)
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

    conexao = mysql.connector.connect(**CONFIGURACAO_BANCO)
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


@app.route("/imoveis/<int:id>", methods=["DELETE"])
def remover_imovel(id):
    conexao = mysql.connector.connect(**CONFIGURACAO_BANCO)
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM imoveis WHERE id = %s",
        (id,),
    )

    imovel_encontrado = cursor.rowcount > 0

    if imovel_encontrado:
        conexao.commit()

    cursor.close()
    conexao.close()

    if not imovel_encontrado:
        return jsonify({
            "erro": "Imóvel não encontrado"
        }), 404

    return jsonify({
        "mensagem": "Imóvel removido com sucesso"
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
