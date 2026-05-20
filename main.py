import sqlite3
from datetime import datetime

BANCO = "remanso.db"
ARQUIVO_ALERTAS = "alertas.txt"


def conectar():
    return sqlite3.connect(BANCO)


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            estoque_minimo INTEGER NOT NULL,
            especificacoes TEXT,
            criado_em TEXT NOT NULL
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
            observacao TEXT,
            saldo_apos INTEGER NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            mensagem TEXT NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    conexao.commit()
    conexao.close()


def ler_inteiro(texto):
    while True:
        try:
            valor = int(input(texto))
            if valor < 0:
                print("Digite um número maior ou igual a zero.")
                continue
            return valor
        except ValueError:
            print("Valor inválido. Digite um número inteiro.")


def ler_decimal(texto):
    while True:
        try:
            valor = float(input(texto).replace(",", "."))
            if valor < 0:
                print("Digite um valor maior ou igual a zero.")
                continue
            return valor
        except ValueError:
            print("Valor inválido. Digite um número decimal.")


def data_atual():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def cadastrar_produto():
    print("\n--- CADASTRO DE PRODUTO ---")
    nome = input("Nome do produto: ").strip()
    categoria = input("Categoria: ").strip()
    preco = ler_decimal("Preço unitário: R$ ")
    quantidade = ler_inteiro("Quantidade inicial: ")
    estoque_minimo = ler_inteiro("Estoque mínimo para alerta: ")
    especificacoes = input("Especificações técnicas: ").strip()

    if not nome or not categoria:
        print("Nome e categoria são obrigatórios.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO produtos
        (nome, categoria, preco, quantidade, estoque_minimo, especificacoes, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, categoria, preco, quantidade, estoque_minimo, especificacoes, data_atual()))

    conexao.commit()
    produto_id = cursor.lastrowid
    conexao.close()

    print(f"Produto cadastrado com sucesso. Código: {produto_id}")
    verificar_alerta_produto(produto_id)


def buscar_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, categoria, preco, quantidade, estoque_minimo, especificacoes
        FROM produtos
        WHERE id = ?
    """, (produto_id,))

    produto = cursor.fetchone()
    conexao.close()
    return produto


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, categoria, preco, quantidade, estoque_minimo, especificacoes
        FROM produtos
        ORDER BY nome
    """)

    produtos = cursor.fetchall()
    conexao.close()
    return produtos


def consultar_estoque():
    print("\n--- CONSULTA EM TEMPO REAL DO ESTOQUE ---")
    produtos = listar_produtos()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print("-" * 95)
    print(f"{'ID':<4} {'Produto':<22} {'Categoria':<15} {'Preço':<12} {'Qtd':<8} {'Mínimo':<8} {'Situação':<12}")
    print("-" * 95)

    for produto in produtos:
        produto_id, nome, categoria, preco, quantidade, estoque_minimo, especificacoes = produto
        situacao = "CRÍTICO" if quantidade <= estoque_minimo else "OK"
        print(f"{produto_id:<4} {nome:<22} {categoria:<15} R$ {preco:<9.2f} {quantidade:<8} {estoque_minimo:<8} {situacao:<12}")

    print("-" * 95)


def registrar_movimentacao():
    print("\n--- REGISTRO DE MOVIMENTAÇÕES ---")
    consultar_estoque()

    produto_id = ler_inteiro("\nDigite o ID do produto: ")
    produto = buscar_produto(produto_id)

    if produto is None:
        print("Produto não encontrado.")
        return

    print("\nTipo de movimentação:")
    print("1 - Entrada")
    print("2 - Saída")
    opcao_tipo = input("Escolha: ").strip()

    if opcao_tipo == "1":
        tipo = "ENTRADA"
        motivos_validos = ["compra", "devolução"]
    elif opcao_tipo == "2":
        tipo = "SAÍDA"
        motivos_validos = ["venda", "transferência", "perda"]
    else:
        print("Opção inválida.")
        return

    print("\nMotivos disponíveis:")
    for indice, motivo in enumerate(motivos_validos, start=1):
        print(f"{indice} - {motivo.capitalize()}")

    escolha_motivo = ler_inteiro("Escolha o motivo: ")

    if escolha_motivo < 1 or escolha_motivo > len(motivos_validos):
        print("Motivo inválido.")
        return

    motivo = motivos_validos[escolha_motivo - 1]
    quantidade_mov = ler_inteiro("Quantidade movimentada: ")
    observacao = input("Observação: ").strip()

    if quantidade_mov == 0:
        print("A quantidade precisa ser maior que zero.")
        return

    quantidade_atual = produto[4]

    if tipo == "SAÍDA" and quantidade_mov > quantidade_atual:
        print("Não é possível registrar a saída. Quantidade maior que o saldo atual.")
        return

    if tipo == "ENTRADA":
        novo_saldo = quantidade_atual + quantidade_mov
    else:
        novo_saldo = quantidade_atual - quantidade_mov

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE produtos
        SET quantidade = ?
        WHERE id = ?
    """, (novo_saldo, produto_id))

    cursor.execute("""
        INSERT INTO movimentacoes
        (produto_id, tipo, motivo, quantidade, data, observacao, saldo_apos)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (produto_id, tipo, motivo, quantidade_mov, data_atual(), observacao, novo_saldo))

    conexao.commit()
    conexao.close()

    print("Movimentação registrada com sucesso.")
    print(f"Saldo atual do produto: {novo_saldo} unidades")

    verificar_alerta_produto(produto_id)


def verificar_alerta_produto(produto_id):
    produto = buscar_produto(produto_id)

    if produto is None:
        return

    _, nome, categoria, preco, quantidade, estoque_minimo, especificacoes = produto

    if quantidade <= estoque_minimo:
        mensagem = (
            f"SMS REMANSO: Atenção! O estoque de {nome} está crítico. "
            f"Saldo atual: {quantidade} unidade(s). Estoque mínimo: {estoque_minimo}. "
            f"É necessário realizar reposição."
        )

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO alertas (produto_id, mensagem, data)
            VALUES (?, ?, ?)
        """, (produto_id, mensagem, data_atual()))

        conexao.commit()
        conexao.close()

        with open(ARQUIVO_ALERTAS, "a", encoding="utf-8") as arquivo:
            arquivo.write(f"[{data_atual()}] {mensagem}\n")

        print("\n--- ALERTA INTELIGENTE ---")
        print(mensagem)
        print("Alerta salvo no arquivo alertas.txt")


def verificar_todos_alertas():
    print("\n--- ALERTAS INTELIGENTES ---")
    produtos = listar_produtos()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    encontrou_alerta = False

    for produto in produtos:
        produto_id, nome, categoria, preco, quantidade, estoque_minimo, especificacoes = produto
        if quantidade <= estoque_minimo:
            encontrou_alerta = True
            mensagem = (
                f"SMS REMANSO: Estoque crítico de {nome}. "
                f"Quantidade atual: {quantidade}. Reposição recomendada."
            )
            print(mensagem)

    if not encontrou_alerta:
        print("Nenhum produto está com estoque crítico.")


def historico_movimentacoes():
    print("\n--- HISTÓRICO DE MOVIMENTAÇÕES ---")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT m.id, p.nome, m.tipo, m.motivo, m.quantidade, m.data, m.saldo_apos, m.observacao
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        ORDER BY m.id DESC
    """)

    movimentacoes = cursor.fetchall()
    conexao.close()

    if not movimentacoes:
        print("Nenhuma movimentação registrada.")
        return

    print("-" * 110)
    print(f"{'ID':<4} {'Produto':<22} {'Tipo':<10} {'Motivo':<15} {'Qtd':<8} {'Saldo':<8} {'Data':<20} {'Obs'}")
    print("-" * 110)

    for mov in movimentacoes:
        mov_id, produto, tipo, motivo, quantidade, data, saldo_apos, observacao = mov
        print(f"{mov_id:<4} {produto:<22} {tipo:<10} {motivo:<15} {quantidade:<8} {saldo_apos:<8} {data:<20} {observacao}")

    print("-" * 110)


def relatorio_gerencial():
    print("\n--- RELATÓRIOS GERENCIAIS ---")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*), SUM(quantidade), SUM(preco * quantidade) FROM produtos")
    total_produtos, total_unidades, valor_total = cursor.fetchone()

    total_produtos = total_produtos or 0
    total_unidades = total_unidades or 0
    valor_total = valor_total or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM produtos
        WHERE quantidade <= estoque_minimo
    """)
    produtos_criticos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT tipo, SUM(quantidade)
        FROM movimentacoes
        GROUP BY tipo
    """)
    totais_movimentacao = cursor.fetchall()

    cursor.execute("""
        SELECT p.nome, COUNT(m.id) AS total
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        GROUP BY p.nome
        ORDER BY total DESC
        LIMIT 1
    """)
    produto_mais_movimentado = cursor.fetchone()

    cursor.execute("""
        SELECT categoria, SUM(preco * quantidade) AS valor
        FROM produtos
        GROUP BY categoria
        ORDER BY valor DESC
    """)
    valor_por_categoria = cursor.fetchall()

    cursor.execute("""
        SELECT p.nome, 
               SUM(CASE WHEN m.tipo = 'ENTRADA' THEN m.quantidade ELSE 0 END) AS entradas,
               SUM(CASE WHEN m.tipo = 'SAÍDA' THEN m.quantidade ELSE 0 END) AS saidas
        FROM produtos p
        LEFT JOIN movimentacoes m ON p.id = m.produto_id
        GROUP BY p.id, p.nome
        ORDER BY p.nome
    """)
    analise_produtos = cursor.fetchall()

    conexao.close()

    print(f"Total de produtos cadastrados: {total_produtos}")
    print(f"Total de unidades em estoque: {total_unidades}")
    print(f"Valorização total do estoque: R$ {valor_total:.2f}")
    print(f"Produtos em situação crítica: {produtos_criticos}")

    if produto_mais_movimentado:
        print(f"Produto com maior número de movimentações: {produto_mais_movimentado[0]} ({produto_mais_movimentado[1]} registros)")
    else:
        print("Produto com maior número de movimentações: ainda não há movimentações.")

    print("\nMovimentações por tipo:")
    if totais_movimentacao:
        for tipo, quantidade in totais_movimentacao:
            print(f"- {tipo}: {quantidade} unidade(s)")
    else:
        print("- Nenhuma movimentação registrada.")

    print("\nValorização por categoria:")
    if valor_por_categoria:
        for categoria, valor in valor_por_categoria:
            print(f"- {categoria}: R$ {valor:.2f}")
    else:
        print("- Nenhuma categoria cadastrada.")

    print("\nIndicadores por produto:")
    print("-" * 70)
    print(f"{'Produto':<25} {'Entradas':<12} {'Saídas':<12} {'Saldo final'}")
    print("-" * 70)

    for nome, entradas, saidas in analise_produtos:
        entradas = entradas or 0
        saidas = saidas or 0
        produto = buscar_produto_por_nome(nome)
        saldo = produto[4] if produto else 0
        print(f"{nome:<25} {entradas:<12} {saidas:<12} {saldo}")

    print("-" * 70)


def buscar_produto_por_nome(nome):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, categoria, preco, quantidade, estoque_minimo, especificacoes
        FROM produtos
        WHERE nome = ?
        LIMIT 1
    """, (nome,))

    produto = cursor.fetchone()
    conexao.close()
    return produto


def inserir_dados_exemplo():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    quantidade_produtos = cursor.fetchone()[0]

    if quantidade_produtos > 0:
        conexao.close()
        print("Os dados de exemplo não foram inseridos porque já existem produtos cadastrados.")
        return

    produtos = [
        ("Água Mineral 500ml", "Água", 2.50, 40, 10, "Garrafa plástica sem gás"),
        ("Refrigerante Cola 2L", "Refrigerante", 8.90, 20, 5, "Garrafa PET 2 litros"),
        ("Suco de Laranja 1L", "Suco", 7.50, 8, 6, "Caixa longa vida 1 litro"),
        ("Energético 473ml", "Energético", 10.00, 4, 5, "Lata 473ml"),
        ("Cerveja Pilsen 350ml", "Cerveja", 4.20, 30, 12, "Lata 350ml")
    ]

    for produto in produtos:
        cursor.execute("""
            INSERT INTO produtos
            (nome, categoria, preco, quantidade, estoque_minimo, especificacoes, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (*produto, data_atual()))

    conexao.commit()
    conexao.close()

    print("Dados de exemplo inseridos com sucesso.")


def menu():
    criar_tabelas()

    while True:
        print("\n========== SISTEMA DE ESTOQUE REMANSO ==========")
        print("1 - Cadastrar produto")
        print("2 - Registrar movimentação")
        print("3 - Consultar estoque em tempo real")
        print("4 - Verificar alertas inteligentes")
        print("5 - Relatórios gerenciais")
        print("6 - Histórico de movimentações")
        print("7 - Inserir dados de exemplo")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            registrar_movimentacao()
        elif opcao == "3":
            consultar_estoque()
        elif opcao == "4":
            verificar_todos_alertas()
        elif opcao == "5":
            relatorio_gerencial()
        elif opcao == "6":
            historico_movimentacoes()
        elif opcao == "7":
            inserir_dados_exemplo()
        elif opcao == "0":
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
