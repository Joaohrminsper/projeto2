import pytest
from urllib.parse import quote


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

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_imovel_id_nao_existe(client):
    imoveis = client.get("/imoveis").get_json()
    id_inexistente = max(imovel["id"] for imovel in imoveis) + 1

    response = client.get(f"/imoveis/{id_inexistente}")

    assert response.status_code == 404

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_adicionar_imovel_retorna_201_e_id(client):
    imovel = {
        "logradouro": "Rua do Teste da Rota POST",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "Sao Paulo",
        "cep": "01000-000",
        "tipo": "casa",
        "valor": 250000.00,
        "data_aquisicao": "2026-09-11",
    }

    response = client.post("/imoveis", json=imovel)

    assert response.status_code == 201
    assert response.get_json()["id"] is not None
    assert response.get_json()["logradouro"] == imovel["logradouro"]
    assert response.get_json()["tipo_logradouro"] == imovel["tipo_logradouro"]
    assert response.get_json()["bairro"] == imovel["bairro"]
    assert response.get_json()["cidade"] == imovel["cidade"]
    assert response.get_json()["cep"] == imovel["cep"]
    assert response.get_json()["tipo"] == imovel["tipo"]
    assert response.get_json()["valor"] == imovel["valor"]
    assert response.get_json()["data_aquisicao"] == imovel["data_aquisicao"]

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_adicionar_imovel_retorna_400_sem_campos_obrigatorios(client):
    response = client.post("/imoveis", json={})

    assert response.status_code == 400
    assert response.get_json()["campos"] == [
        "bairro",
        "cep",
        "cidade",
        "data_aquisicao",
        "logradouro",
        "tipo",
        "tipo_logradouro",
        "valor",
    ]

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_atualizar_dados_com_sucesso(client):
    imoveis = client.get("/imoveis").get_json()
    imovel_esperado = imoveis[0]

    nova_info = {"bairro": "valor_novo"}
    response = client.patch(f"/imoveis/{imovel_esperado['id']}", json=nova_info)

    imoveis_atualizados = client.get("/imoveis").get_json()
    imovel_atualizado = next(
        (
            imovel
            for imovel in imoveis_atualizados
            if imovel['id'] == imovel_esperado['id']
        ),
        None,
    )

    assert response.status_code == 200
    assert imovel_atualizado is not None
    assert imovel_atualizado["bairro"] == nova_info["bairro"]

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])                          
def test_atualizar_preserva_campos_nao_enviados(client):
    imovel_antes = client.get("/imoveis").get_json()[0]

    response = client.patch(
        f"/imoveis/{imovel_antes['id']}",
        json={"bairro": "Novo bairro"},
    )

    imovel_depois = next(
        imovel
        for imovel in client.get("/imoveis").get_json()
        if imovel["id"] == imovel_antes["id"]
    )

    assert response.status_code == 200
    assert imovel_depois["bairro"] == "Novo bairro"

    assert imovel_depois["valor"] == imovel_antes["valor"]

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"]) 
def test_atualizar_imovel_inexistente_retorna_404(client):
    response = client.patch(
        "/imoveis/999999",
        json={"bairro": "Novo bairro"},
    )

    assert response.status_code == 404

@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"]) 
def test_atualizar_imovel_com_dados_invalidos_retorna_400(client):
    imovel = client.get("/imoveis").get_json()[0]

    response = client.patch(
        f"/imoveis/{imovel['id']}",
        json={"bairro": 123},
    )

    assert response.status_code == 400


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_remover_imovel_com_sucesso(client):
    novo_imovel = {
        "logradouro": "Rua do Teste da Rota DELETE",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "Sao Paulo",
        "cep": "01000-000",
        "tipo": "casa",
        "valor": 250000.00,
        "data_aquisicao": "2026-09-14",
    }
    imovel_id = client.post("/imoveis", json=novo_imovel).get_json()["id"]

    response = client.delete(f"/imoveis/{imovel_id}")

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel removido com sucesso"}
    assert client.get(f"/imoveis/{imovel_id}").status_code == 404


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_remover_imovel_inexistente_retorna_404(client):
    response = client.delete("/imoveis/999999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_buscar_imoveis_por_tipo_retorna_todos_os_atributos(client):
    imoveis = client.get("/imoveis").get_json()
    tipo = imoveis[0]["tipo"]
    imoveis_esperados = [
        imovel
        for imovel in imoveis
        if imovel["tipo"] == tipo
    ]
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

    response = client.get(f"/imoveis/tipo/{quote(tipo, safe='')}")
    imoveis_encontrados = response.get_json()

    assert response.status_code == 200
    assert imoveis_encontrados == imoveis_esperados
    assert all(
        set(imovel.keys()) == chaves_esperadas
        for imovel in imoveis_encontrados
    )


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_buscar_tipo_inexistente_retorna_tipos_disponiveis(client):
    imoveis = client.get("/imoveis").get_json()
    tipos_disponiveis = sorted({
        imovel["tipo"]
        for imovel in imoveis
        if imovel["tipo"]
    })

    response = client.get("/imoveis/tipo/tipo-inexistente")

    assert response.status_code == 404
    assert response.get_json() == {
        "erro": "Nenhum imóvel encontrado para o tipo informado",
        "tipos_disponiveis": tipos_disponiveis,
    }


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_buscar_imoveis_por_cidade_retorna_todos_os_atributos(client):
    imoveis = client.get("/imoveis").get_json()
    cidade = imoveis[0]["cidade"]
    imoveis_esperados = [
        imovel
        for imovel in imoveis
        if imovel["cidade"] == cidade
    ]
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

    response = client.get(f"/imoveis/cidade/{quote(cidade, safe='')}")
    imoveis_encontrados = response.get_json()

    assert response.status_code == 200
    assert imoveis_encontrados == imoveis_esperados
    assert all(
        set(imovel.keys()) == chaves_esperadas
        for imovel in imoveis_encontrados
    )


@pytest.mark.dependency(depends=["test_listar_imoveis_retorna_200"])
def test_buscar_cidade_inexistente_retorna_cidades_disponiveis(client):
    imoveis = client.get("/imoveis").get_json()
    cidades_disponiveis = sorted({
        imovel["cidade"]
        for imovel in imoveis
        if imovel["cidade"]
    })

    response = client.get("/imoveis/cidade/cidade-inexistente")

    assert response.status_code == 404
    assert response.get_json() == {
        "erro": "Nenhum imóvel encontrado para a cidade informada",
        "cidades_disponiveis": cidades_disponiveis,
    }
