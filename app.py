from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods=["GET"])
def hello_world_get():
    return jsonify({"message": "Tudo certo!"}), 200

@app.route('/test', methods=["DELETE"])
def hello_world_delete():
    req_data = request.get_json()

    if ("name" not in req_data):
        return jsonify({"message": "Erro!"}), 400

    return jsonify({"message": f"Olá {req_data['name']}!"}), 200

@app.route('/test', methods=["PUT"])
def hello_world_put():
    req_data = request.get_json()

    if ("name" not in req_data):
        return jsonify({"message": "Erro!"}), 400

    return jsonify({"message": f"Olá {req_data['name']}!"}), 200

@app.route('/test', methods=["POST"])
def hello_world_post():
    req_data = request.get_json()

    if ("name" not in req_data):
        return jsonify({"message": "Erro!"}), 400

    return jsonify({"message": f"Olá {req_data['name']}!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5500)