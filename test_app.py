import pytest


@pytest.mark.dependency()
def test_listar_imoveis_retorna_200(client):
    response = client.get("/imoveis")
    assert response.status_code == 200


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_listar_imoveis_retorna_lista_nao_vazia(client):
    response = client.get("/imoveis")
    assert len(response.get_json()) > 0


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_listar_imoveis_retorna_dicionarios_com_chaves_esperadas(client):
    response = client.get("/imoveis")
    imoveis = response.get_json()
    chaves_esperadas = {
        "bairro",
        "cep",
        "cidade",
        "data_aquisicao",
        "id",
        "logradouro",
        "tipo",
        "tipo_logradouro",
        "valor",
    }

    assert len(imoveis) > 0
    assert all(set(imovel.keys()) == chaves_esperadas for imovel in imoveis)


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_listar_imovel_por_id_retorna_todos_os_atributos(client):
    imoveis = client.get("/imoveis").get_json()
    imovel_esperado = imoveis[0]

    response = client.get(f"/imoveis/{imovel_esperado['id']}")

    assert response.status_code == 200
    assert response.get_json() == imovel_esperado

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_listar_imoveis_retorna_content_type_json(client):
    response = client.get("/imoveis")
    content_type = response.headers["Content-Type"]

    assert "application/json" in content_type 

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_buscar_imovel_por_id_retorna_content_type_json(client):
    imoveis = client.get("/imoveis").get_json()
    imovel_esperado = imoveis[0]

    response = client.get(f"/imoveis/{imovel_esperado['id']}")
    content_type = response.headers["Content-Type"]
    
    assert "application/json" in content_type 