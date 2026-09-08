from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    return jsonify([])


if __name__ == "__main__":
    app.run(debug=True)