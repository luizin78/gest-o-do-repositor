import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
BANCO = BASE_DIR / "remanso_estoque.db"
ESTOQUE_MINIMO = 5


PRODUTOS_INICIAIS = [
    ("Skol 350ml - fardo", "Cerveja", 40.00),
    ("Brahma 350ml - fardo", "Cerveja", 45.00),
    ("Heineken 350ml - fardo", "Cerveja", 60.00),
    ("Corona 330ml - caixa", "Cerveja", 48.00),
    ("Corona longneck - caixa", "Cerveja", 180.00),
    ("Heineken longneck - caixa", "Cerveja", 140.00),
    ("Red Bull 250ml c/4", "Energetico", 40.00),
    ("Red Bull 250ml c/8", "Energetico", 80.00),
    ("Red Bull 250ml c/24", "Energetico", 180.00),
    ("Monster 473ml c/6", "Energetico", 60.00),
    ("Monster 473ml c/12", "Energetico", 120.00),
    ("TNT 269ml c/12", "Energetico", 65.00),
    ("TNT 473ml c/6", "Energetico", 55.00),
    ("Coca-Cola 2L c/6", "Refrigerante", 65.00),
    ("Coca-Cola lata 350ml c/12", "Refrigerante", 45.00),
    ("Guarana Antarctica 2L c/6", "Refrigerante", 50.00),
    ("Guarana Antarctica lata c/12", "Refrigerante", 35.00),
    ("Pepsi 2L c/6", "Refrigerante", 40.00),
    ("Skol 350ml - unidade", "Cerveja", 5.00),
    ("Brahma 350ml - unidade", "Cerveja", 5.00),
    ("Heineken - unidade", "Cerveja", 7.00),
    ("Heineken longneck - unidade", "Cerveja", 9.00),
    ("Corona 210ml - unidade", "Cerveja", 8.00),
    ("Corona longneck - unidade", "Cerveja", 10.00),
    ("Red Bull 250ml - unidade", "Energetico", 10.00),
    ("Monster 473ml - unidade", "Energetico", 10.00),
    ("TNT 269ml - unidade", "Energetico", 4.00),
    ("TNT 473ml - unidade", "Energetico", 6.00),
    ("Coca-Cola 2L - unidade", "Refrigerante", 10.00),
    ("Coca-Cola lata - unidade", "Refrigerante", 6.00),
    ("Guarana Antarctica 2L - unidade", "Refrigerante", 8.00),
    ("Guarana Antarctica lata - unidade", "Refrigerante", 5.00),
    ("Pepsi 2L - unidade", "Refrigerante", 7.00),
]


def conectar():
    return sqlite3.connect(BANCO)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            motivo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO produtos (nome, categoria, preco, quantidade)
            VALUES (?, ?, ?, 0)
        """, PRODUTOS_INICIAIS)

    conexao.commit()
    conexao.close()


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, categoria, preco, quantidade FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()
    conexao.close()
    return produtos


def cadastrar_produto(nome, categoria, preco, quantidade):
    if not nome.strip():
        raise ValueError("O nome do produto nao pode ficar vazio.")
    if preco < 0:
        raise ValueError("O preco nao pode ser negativo.")
    if quantidade < 0:
        raise ValueError("A quantidade nao pode ser negativa.")

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO produtos (nome, categoria, preco, quantidade)
        VALUES (?, ?, ?, ?)
    """, (nome, categoria, preco, quantidade))
    conexao.commit()
    conexao.close()


def remover_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()

    if produto is None:
        conexao.close()
        return None

    cursor.execute("DELETE FROM movimentacoes WHERE produto_id = ?", (produto_id,))
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conexao.commit()
    conexao.close()
    return produto[0]


def registrar_movimentacao(produto_id, tipo, motivo, quantidade):
    if quantidade <= 0:
        return "A quantidade deve ser maior que zero."

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()

    if produto is None:
        conexao.close()
        return "Produto nao encontrado."

    quantidade_atual = produto[0]

    if tipo == "entrada":
        nova_quantidade = quantidade_atual + quantidade
    elif tipo == "saida":
        if quantidade > quantidade_atual:
            conexao.close()
            return "Estoque insuficiente."
        nova_quantidade = quantidade_atual - quantidade
    else:
        conexao.close()
        return "Tipo invalido."

    cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto_id))
    cursor.execute("""
        INSERT INTO movimentacoes (produto_id, tipo, motivo, quantidade, data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        produto_id,
        tipo,
        motivo,
        quantidade,
        datetime.now().strftime("%d/%m/%Y %H:%M"),
    ))

    conexao.commit()
    conexao.close()
    return "Movimentacao registrada com sucesso."


def buscar_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, categoria, preco, quantidade FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    conexao.close()
    return produto


def listar_alertas():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, quantidade FROM produtos WHERE quantidade <= ? ORDER BY nome", (ESTOQUE_MINIMO,))
    alertas = cursor.fetchall()
    conexao.close()
    return alertas


def listar_movimentacoes():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT m.id, p.nome, m.tipo, m.motivo, m.quantidade, m.data
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        ORDER BY m.id DESC
    """)
    movimentacoes = cursor.fetchall()
    conexao.close()
    return movimentacoes


def relatorio_gerencial():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*), SUM(quantidade), SUM(preco * quantidade) FROM produtos")
    total_produtos, total_itens, valor_total = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= ?", (ESTOQUE_MINIMO,))
    produtos_criticos = cursor.fetchone()[0]

    cursor.execute("SELECT tipo, motivo, SUM(quantidade) FROM movimentacoes GROUP BY tipo, motivo")
    movimentacoes = cursor.fetchall()

    conexao.close()

    return {
        "total_produtos": total_produtos or 0,
        "total_itens": total_itens or 0,
        "valor_total": valor_total or 0,
        "produtos_criticos": produtos_criticos or 0,
        "movimentacoes": movimentacoes,
    }
