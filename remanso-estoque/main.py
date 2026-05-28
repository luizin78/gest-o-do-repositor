import sqlite3

import backend


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def ler_inteiro(mensagem, minimo=None):
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Digite um numero inteiro valido.")
            continue

        if minimo is not None and valor < minimo:
            print(f"Digite um valor maior ou igual a {minimo}.")
            continue

        return valor


def ler_decimal(mensagem, minimo=None):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))
        except ValueError:
            print("Digite um valor numerico valido.")
            continue

        if minimo is not None and valor < minimo:
            print(f"Digite um valor maior ou igual a {minimo}.")
            continue

        return valor


def escolher_categoria():
    print("1 - Energetico")
    print("2 - Cerveja")
    print("3 - Refrigerante")
    opcao = input("Categoria: ")

    if opcao == "1":
        return "Energetico"
    if opcao == "2":
        return "Cerveja"
    if opcao == "3":
        return "Refrigerante"

    print("Categoria invalida. Usando Cerveja.")
    return "Cerveja"


def listar_produtos():
    produtos = backend.listar_produtos()

    print("\n--- ESTOQUE ATUAL ---")
    for produto in produtos:
        produto_id, nome, categoria, preco, quantidade = produto
        status = "CRITICO" if quantidade <= backend.ESTOQUE_MINIMO else "OK"
        print(f"{produto_id} - {nome} | {categoria} | {moeda(preco)} | Qtd: {quantidade} | {status}")


def cadastrar_produto():
    print("\n--- CADASTRAR PRODUTO ---")
    nome = input("Nome: ").strip()
    if not nome:
        print("O nome do produto nao pode ficar vazio.")
        return

    categoria = escolher_categoria()
    preco = ler_decimal("Preco: ", minimo=0)
    quantidade = ler_inteiro("Quantidade inicial: ", minimo=0)

    try:
        backend.cadastrar_produto(nome, categoria, preco, quantidade)
        print("Produto cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Ja existe um produto com esse nome.")


def remover_produto():
    print("\n--- REMOVER PRODUTO ---")
    listar_produtos()
    produto_id = ler_inteiro("\nDigite o ID do produto que deseja remover: ", minimo=1)
    produto = backend.buscar_produto(produto_id)

    if produto is None:
        print("Produto nao encontrado.")
        return

    confirmar = input(f"Tem certeza que deseja remover {produto[1]}? (s/n): ").lower()

    if confirmar == "s":
        backend.remover_produto(produto_id)
        print("Produto removido com sucesso!")
    else:
        print("Remocao cancelada.")


def registrar_movimentacao():
    print("\n--- REGISTRAR MOVIMENTACAO ---")
    listar_produtos()

    produto_id = ler_inteiro("\nDigite o ID do produto: ", minimo=1)
    print("\n1 - Entrada por compra")
    print("2 - Saida por venda")
    print("3 - Saida por transferencia")
    opcao = input("Escolha a movimentacao: ")
    quantidade = ler_inteiro("Quantidade: ", minimo=1)

    if opcao == "1":
        tipo = "entrada"
        motivo = "compra"
    elif opcao == "2":
        tipo = "saida"
        motivo = "venda"
    elif opcao == "3":
        tipo = "saida"
        motivo = "transferencia"
    else:
        print("Opcao invalida.")
        return

    mensagem = backend.registrar_movimentacao(produto_id, tipo, motivo, quantidade)
    print(mensagem)

    produto = backend.buscar_produto(produto_id)
    if produto and produto[4] <= backend.ESTOQUE_MINIMO:
        print(f"ALERTA: estoque critico de {produto[1]}! Necessidade de reposicao.")


def mostrar_alertas():
    alertas = backend.listar_alertas()

    print("\n--- ALERTAS INTELIGENTES ---")
    if not alertas:
        print("Nenhum produto com estoque critico.")
    else:
        for nome, quantidade in alertas:
            print(f"ALERTA: {nome} esta com apenas {quantidade} unidades. Fazer reposicao.")


def relatorio_movimentacoes():
    movimentacoes = backend.listar_movimentacoes()

    print("\n--- RELATORIO DE MOVIMENTACOES ---")
    if not movimentacoes:
        print("Nenhuma movimentacao registrada.")
    else:
        for mov in movimentacoes:
            print(f"{mov[0]} - {mov[1]} | {mov[2]} | {mov[3]} | Qtd: {mov[4]} | {mov[5]}")


def relatorio_gerencial():
    relatorio = backend.relatorio_gerencial()

    print("\n--- RELATORIO GERENCIAL ---")
    print(f"Produtos cadastrados: {relatorio['total_produtos']}")
    print(f"Quantidade total em estoque: {relatorio['total_itens']}")
    print(f"Valor total do estoque: {moeda(relatorio['valor_total'])}")
    print(f"Produtos com estoque critico: {relatorio['produtos_criticos']}")

    print("\nMovimentacoes:")
    if not relatorio["movimentacoes"]:
        print("Nenhuma movimentacao registrada.")
    else:
        for tipo, motivo, quantidade in relatorio["movimentacoes"]:
            print(f"{tipo} por {motivo}: {quantidade} itens")


def menu():
    backend.criar_banco()

    while True:
        print("\n=== SISTEMA DE ESTOQUE REMANSO ===")
        print("1 - Cadastrar produto")
        print("2 - Remover produto")
        print("3 - Registrar movimentacao")
        print("4 - Consultar estoque")
        print("5 - Ver alertas")
        print("6 - Relatorio de movimentacoes")
        print("7 - Relatorio gerencial")
        print("0 - Sair")

        try:
            opcao = input("Escolha uma opcao: ")
        except EOFError:
            print("\nSistema encerrado.")
            break

        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            remover_produto()
        elif opcao == "3":
            registrar_movimentacao()
        elif opcao == "4":
            listar_produtos()
        elif opcao == "5":
            mostrar_alertas()
        elif opcao == "6":
            relatorio_movimentacoes()
        elif opcao == "7":
            relatorio_gerencial()
        elif opcao == "0":
            print("Sistema encerrado.")
            break
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    menu()
