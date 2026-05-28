# Sistema de Estoque Remanso Bebidas

Trabalho desenvolvido somente em **arquivos Python**, utilizando interface grafica com **Tkinter** e banco de dados **SQLite**. 
O sistema controla o estoque de bebidas da empresa ficticia **Remanso Bebidas**.

## Funcionalidades

- Cadastro de produtos.
- Remocao de produtos cadastrados.
- Registro de entrada por compra.
- Registro de saida por venda.
- Registro de saida por transferencia.
- Consulta do estoque em tempo real.
- Alertas quando o estoque esta baixo.
- Relatorio de movimentacoes.
- Relatorio gerencial com valor total do estoque.

## Tecnologias

- Python
- Tkinter
- SQLite
- Biblioteca `sqlite3`

Nao e necessario instalar frameworks como Flask, Django, FastAPI, Streamlit ou Node.js.

## Estrutura do projeto

- `abrir_app.py`: arquivo para abrir o sistema.
- `app_gui.py`: frontend grafico do sistema, feito em Python com Tkinter.
- `main.py`: menu do sistema e interacao com o usuario.
- `backend.py`: backend do sistema, com regras de negocio e acesso ao banco SQLite.
- `remanso_estoque.db`: banco de dados criado automaticamente.

## Como executar

Para abrir o app, execute:

```bash
py abrir_app.py
```

Tambem e possivel executar diretamente o frontend:

```bash
py app_gui.py
```

Se quiser usar a versao antiga pelo terminal, execute:

```bash
py main.py
```

Se o Python estiver configurado como programa padrao, voce tambem pode tentar abrir o arquivo `abrir_app.py` com dois cliques.

O banco de dados `remanso_estoque.db` sera criado automaticamente.

O sistema principal abre em uma janela grafica, diretamente pelos arquivos `.py`.

## Menu do sistema

```text
1 - Cadastrar produto
2 - Remover produto
3 - Registrar movimentacao
4 - Consultar estoque
5 - Ver alertas
6 - Relatorio de movimentacoes
7 - Relatorio gerencial
0 - Sair
```

## Produtos cadastrados

O sistema ja inicia com bebidas cadastradas, separadas por:

- Cerveja
- Energetico
- Refrigerante

Foram usados os precos informados para fardos, caixas e unidades.

Todos os produtos iniciais comecam com quantidade `0`. A quantidade real deve ser adicionada pelo usuario por meio da movimentacao de entrada por compra.

## Banco de dados

O sistema usa SQLite e cria duas tabelas:

### produtos

Guarda:

- id
- nome
- categoria
- preco
- quantidade

### movimentacoes

Guarda:

- id
- produto
- tipo da movimentacao
- motivo
- quantidade
- data

## Alertas

Quando um produto fica com quantidade menor ou igual a 5, o sistema mostra uma mensagem de alerta avisando que o estoque esta critico.

Exemplo:

```text
ALERTA: estoque critico de Skol 350ml - unidade! Necessidade de reposicao.
```
