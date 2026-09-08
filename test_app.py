def test_listar_imoveis_retorna_200(client):
    response = client.get("/imoveis")
    assert response.status_code == 200

def test_listar_imoveis_retorna_lista_vazia(client):
    response = client.get("/imoveis")
    assert response.get_json() == []