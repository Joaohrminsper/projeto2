# Projeto 2 - API de Imóveis

## IP DO DEPLOY DA AWS: *13.58.217.10/imoveis*
API REST desenvolvida em Flask para consultar e gerenciar imóveis armazenados
em um banco de dados MySQL. O projeto foi desenvolvido para a disciplina de
Programação Eficaz.

## Funcionalidades

- listar todos os imóveis;
- consultar um imóvel pelo ID;
- filtrar imóveis por tipo ou cidade;
- cadastrar, atualizar e remover imóveis;
- retornar respostas em JSON;
- criar automaticamente o banco, a tabela e a carga inicial de dados.

## Requisitos

- Python 3.10 ou superior;
- MySQL acessível pela aplicação;
- permissão do usuário MySQL para criar o banco configurado em `DB_NAME`.

As dependências Python estão em [requirements.txt](requirements.txt).

## Configuração

1. Crie e ative um ambiente virtual:

	```powershell
	python -m venv env
	.\env\Scripts\Activate.ps1
	```

	No Linux ou macOS, use `source env/bin/activate`.

2. Instale as dependências:

	```bash
	pip install -r requirements.txt
	```

3. Copie `.env.example` para `.env` e ajuste os valores da sua conexão MySQL:

	```powershell
	Copy-Item .env.example .env
	```

	| Variável | Obrigatória | Descrição |
	| --- | --- | --- |
	| `DB_HOST` | Sim | Host do servidor MySQL |
	| `DB_PORT` | Não | Porta do MySQL; padrão `3306` |
	| `DB_USER` | Sim | Usuário da conexão |
	| `DB_PASSWORD` | Sim | Senha da conexão |
	| `DB_NAME` | Sim | Nome do banco a ser criado ou utilizado |
	| `DB_SSL_CA` | Não | Caminho do certificado CA para conexões SSL |

	Não compartilhe o arquivo `.env`. O arquivo `.env.example` serve apenas como
	modelo e deve ser atualizado com credenciais próprias antes do uso.

## Banco de dados

Ao importar `app.py`, a aplicação:

1. valida as variáveis obrigatórias;
2. cria o banco definido em `DB_NAME`, caso ele não exista;
3. cria a tabela `imoveis`, caso ela não exista;
4. executa a carga de [imoveis.sql](imoveis.sql) somente quando a tabela está
	vazia.

O usuário configurado precisa ter permissão para criar bancos e tabelas. A
tabela possui os campos `id`, `logradouro`, `tipo_logradouro`, `bairro`,
`cidade`, `cep`, `tipo`, `valor` e `data_aquisicao`.

## Executar a aplicação

Com o ambiente virtual ativado e o `.env` configurado:

```bash
python app.py
```

O servidor Flask ficará disponível, por padrão, em `http://127.0.0.1:5000`.

## Testes

Os testes usam o cliente de testes do Flask, mas continuam dependendo de um
MySQL configurado e acessível, pois a aplicação inicializa o banco ao ser
importada.

```bash
pytest
```

## Endpoints

Todas as respostas são JSON. Os filtros de tipo e cidade não diferenciam letras
maiúsculas de minúsculas.

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/imoveis` | Lista todos os imóveis |
| `GET` | `/imoveis/<id>` | Busca um imóvel pelo ID |
| `GET` | `/imoveis/tipo/<tipo>` | Lista imóveis de um tipo |
| `GET` | `/imoveis/cidade/<cidade>` | Lista imóveis de uma cidade |
| `POST` | `/imoveis` | Cadastra um imóvel |
| `PATCH` | `/imoveis/<id>` | Atualiza um ou mais campos |
| `DELETE` | `/imoveis/<id>` | Remove um imóvel |

### Exemplos

Listar imóveis:

```bash
curl http://127.0.0.1:5000/imoveis
```

Buscar por cidade:

```bash
curl "http://127.0.0.1:5000/imoveis/cidade/Sao%20Paulo"
```

Cadastrar um imóvel:

```bash
curl -X POST http://127.0.0.1:5000/imoveis \
  -H "Content-Type: application/json" \
  -d '{
	 "logradouro": "Rua do Teste",
	 "tipo_logradouro": "Rua",
	 "bairro": "Centro",
	 "cidade": "Sao Paulo",
	 "cep": "01000-000",
	 "tipo": "casa",
	 "valor": 250000.00,
	 "data_aquisicao": "2026-09-11"
  }'
```

Atualizar somente o bairro de um imóvel:

```bash
curl -X PATCH http://127.0.0.1:5000/imoveis/1 \
  -H "Content-Type: application/json" \
  -d '{"bairro": "Novo bairro"}'
```

Remover um imóvel:

```bash
curl -X DELETE http://127.0.0.1:5000/imoveis/1
```

O `POST` exige todos os campos do imóvel, exceto `id`. O `PATCH` aceita apenas
campos da tabela e preserva os campos que não forem enviados. IDs inexistentes
retornam `404`; requisições com JSON inválido ou campos inválidos retornam
`400`.

## Estrutura do projeto

```text
app.py            Aplicação Flask e endpoints da API
conftest.py       Fixture do cliente de testes
imoveis.sql       Estrutura e carga inicial da tabela
requirements.txt  Dependências Python
test_app.py       Testes dos endpoints
```
