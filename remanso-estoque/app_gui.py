import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import backend


CORES = {
    "fundo": "#f5f7fb",
    "painel": "#ffffff",
    "texto": "#172033",
    "muted": "#5c667a",
    "primaria": "#2563eb",
    "perigo": "#dc2626",
    "sucesso": "#15803d",
    "borda": "#d8dee9",
}

CATEGORIAS = ("Cerveja", "Energetico", "Refrigerante")
MOVIMENTACOES = {
    "Entrada por compra": ("entrada", "compra"),
    "Saida por venda": ("saida", "venda"),
    "Saida por transferencia": ("saida", "transferencia"),
}


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


class RemansoEstoqueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        backend.criar_banco()

        self.title("Sistema de Estoque Remanso Bebidas")
        self.geometry("1180x720")
        self.minsize(980, 620)
        self.configure(bg=CORES["fundo"])

        self.produtos_por_id = {}
        self.produto_selecionado = tk.IntVar(value=0)

        self._configurar_estilos()
        self._montar_tela()
        self.atualizar_tudo()

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=CORES["fundo"])
        estilo.configure("Card.TFrame", background=CORES["painel"], relief="solid", borderwidth=1)
        estilo.configure("TLabel", background=CORES["fundo"], foreground=CORES["texto"], font=("Segoe UI", 10))
        estilo.configure("Card.TLabel", background=CORES["painel"], foreground=CORES["texto"], font=("Segoe UI", 10))
        estilo.configure("Title.TLabel", background=CORES["fundo"], foreground=CORES["texto"], font=("Segoe UI", 18, "bold"))
        estilo.configure("Metric.TLabel", background=CORES["painel"], foreground=CORES["texto"], font=("Segoe UI", 16, "bold"))
        estilo.configure("Muted.TLabel", background=CORES["painel"], foreground=CORES["muted"], font=("Segoe UI", 9))
        estilo.configure("TButton", font=("Segoe UI", 10), padding=(10, 7))
        estilo.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 7))
        estilo.configure("Treeview", rowheight=28, font=("Segoe UI", 9), fieldbackground=CORES["painel"])
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _montar_tela(self):
        container = ttk.Frame(self, padding=18)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(1, weight=1)

        topo = ttk.Frame(container)
        topo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        topo.columnconfigure(0, weight=1)

        ttk.Label(topo, text="Sistema de Estoque Remanso Bebidas", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(topo, text="Atualizar", command=self.atualizar_tudo).grid(row=0, column=1, sticky="e")

        self._montar_estoque(container)
        self._montar_painel_lateral(container)

    def _montar_estoque(self, container):
        area = ttk.Frame(container, style="Card.TFrame", padding=12)
        area.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        area.rowconfigure(1, weight=1)
        area.columnconfigure(0, weight=1)

        ttk.Label(area, text="Estoque atual", style="Card.TLabel", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))

        colunas = ("id", "nome", "categoria", "preco", "quantidade", "status")
        self.tabela = ttk.Treeview(area, columns=colunas, show="headings", selectmode="browse")
        self.tabela.heading("id", text="ID")
        self.tabela.heading("nome", text="Produto")
        self.tabela.heading("categoria", text="Categoria")
        self.tabela.heading("preco", text="Preco")
        self.tabela.heading("quantidade", text="Qtd")
        self.tabela.heading("status", text="Status")
        self.tabela.column("id", width=55, anchor="center")
        self.tabela.column("nome", width=280)
        self.tabela.column("categoria", width=110)
        self.tabela.column("preco", width=90, anchor="e")
        self.tabela.column("quantidade", width=70, anchor="center")
        self.tabela.column("status", width=95, anchor="center")
        self.tabela.grid(row=1, column=0, sticky="nsew")
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar_produto)

        barra = ttk.Scrollbar(area, orient="vertical", command=self.tabela.yview)
        barra.grid(row=1, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=barra.set)

        botoes = ttk.Frame(area, style="Card.TFrame")
        botoes.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(botoes, text="Remover selecionado", command=self.remover_produto).pack(side="left")

    def _montar_painel_lateral(self, container):
        abas = ttk.Notebook(container)
        abas.grid(row=1, column=1, sticky="nsew")

        self.aba_cadastro = ttk.Frame(abas, padding=12)
        self.aba_movimento = ttk.Frame(abas, padding=12)
        self.aba_relatorios = ttk.Frame(abas, padding=12)
        abas.add(self.aba_cadastro, text="Cadastro")
        abas.add(self.aba_movimento, text="Movimentacao")
        abas.add(self.aba_relatorios, text="Relatorios")

        self._montar_cadastro()
        self._montar_movimentacao()
        self._montar_relatorios()

    def _montar_cadastro(self):
        self.nome_var = tk.StringVar()
        self.categoria_var = tk.StringVar(value=CATEGORIAS[0])
        self.preco_var = tk.StringVar()
        self.quantidade_var = tk.StringVar(value="0")

        self._campo(self.aba_cadastro, "Nome do produto", self.nome_var, 0)
        ttk.Label(self.aba_cadastro, text="Categoria").grid(row=2, column=0, sticky="w", pady=(8, 2))
        ttk.Combobox(self.aba_cadastro, textvariable=self.categoria_var, values=CATEGORIAS, state="readonly").grid(row=3, column=0, sticky="ew")
        self._campo(self.aba_cadastro, "Preco", self.preco_var, 4)
        self._campo(self.aba_cadastro, "Quantidade inicial", self.quantidade_var, 6)
        ttk.Button(self.aba_cadastro, text="Cadastrar produto", style="Primary.TButton", command=self.cadastrar_produto).grid(row=8, column=0, sticky="ew", pady=(14, 0))
        self.aba_cadastro.columnconfigure(0, weight=1)

    def _montar_movimentacao(self):
        self.produto_mov_var = tk.StringVar()
        self.tipo_mov_var = tk.StringVar(value=list(MOVIMENTACOES.keys())[0])
        self.quantidade_mov_var = tk.StringVar()

        ttk.Label(self.aba_movimento, text="Produto").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.combo_produtos = ttk.Combobox(self.aba_movimento, textvariable=self.produto_mov_var, state="readonly")
        self.combo_produtos.grid(row=1, column=0, sticky="ew")

        ttk.Label(self.aba_movimento, text="Tipo de movimentacao").grid(row=2, column=0, sticky="w", pady=(8, 2))
        ttk.Combobox(self.aba_movimento, textvariable=self.tipo_mov_var, values=list(MOVIMENTACOES.keys()), state="readonly").grid(row=3, column=0, sticky="ew")
        self._campo(self.aba_movimento, "Quantidade", self.quantidade_mov_var, 4)
        ttk.Button(self.aba_movimento, text="Registrar", style="Primary.TButton", command=self.registrar_movimentacao).grid(row=6, column=0, sticky="ew", pady=(14, 0))
        self.aba_movimento.columnconfigure(0, weight=1)

    def _montar_relatorios(self):
        cards = ttk.Frame(self.aba_relatorios)
        cards.pack(fill="x", pady=(0, 10))
        cards.columnconfigure((0, 1), weight=1)

        self.lbl_produtos = self._card_metrica(cards, "Produtos", 0, 0)
        self.lbl_itens = self._card_metrica(cards, "Itens em estoque", 0, 1)
        self.lbl_valor = self._card_metrica(cards, "Valor total", 1, 0)
        self.lbl_criticos = self._card_metrica(cards, "Estoque critico", 1, 1)

        ttk.Label(self.aba_relatorios, text="Alertas e movimentacoes", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.texto_relatorio = tk.Text(self.aba_relatorios, height=18, wrap="word", font=("Segoe UI", 9), bd=1, relief="solid")
        self.texto_relatorio.pack(fill="both", expand=True, pady=(6, 0))

    def _campo(self, pai, texto, variavel, linha):
        ttk.Label(pai, text=texto).grid(row=linha, column=0, sticky="w", pady=(8, 2))
        ttk.Entry(pai, textvariable=variavel).grid(row=linha + 1, column=0, sticky="ew")

    def _card_metrica(self, pai, titulo, linha, coluna):
        card = ttk.Frame(pai, style="Card.TFrame", padding=10)
        card.grid(row=linha, column=coluna, sticky="ew", padx=4, pady=4)
        ttk.Label(card, text=titulo, style="Muted.TLabel").pack(anchor="w")
        valor = ttk.Label(card, text="0", style="Metric.TLabel")
        valor.pack(anchor="w")
        return valor

    def atualizar_tudo(self):
        self.atualizar_estoque()
        self.atualizar_relatorios()

    def atualizar_estoque(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        produtos = backend.listar_produtos()
        self.produtos_por_id = {}
        opcoes = []

        for produto_id, nome, categoria, preco, quantidade in produtos:
            status = "CRITICO" if quantidade <= backend.ESTOQUE_MINIMO else "OK"
            self.produtos_por_id[produto_id] = nome
            opcoes.append(f"{produto_id} - {nome}")
            self.tabela.insert("", "end", iid=str(produto_id), values=(produto_id, nome, categoria, moeda(preco), quantidade, status))

        self.combo_produtos.configure(values=opcoes)
        if opcoes and self.produto_mov_var.get() not in opcoes:
            self.produto_mov_var.set(opcoes[0])

    def atualizar_relatorios(self):
        relatorio = backend.relatorio_gerencial()
        self.lbl_produtos.configure(text=str(relatorio["total_produtos"]))
        self.lbl_itens.configure(text=str(relatorio["total_itens"]))
        self.lbl_valor.configure(text=moeda(relatorio["valor_total"]))
        self.lbl_criticos.configure(text=str(relatorio["produtos_criticos"]))

        linhas = ["ALERTAS"]
        alertas = backend.listar_alertas()
        if alertas:
            for nome, quantidade in alertas:
                linhas.append(f"- {nome}: apenas {quantidade} unidades")
        else:
            linhas.append("- Nenhum produto com estoque critico")

        linhas.append("\nMOVIMENTACOES RECENTES")
        movimentacoes = backend.listar_movimentacoes()
        if movimentacoes:
            for mov_id, produto, tipo, motivo, quantidade, data in movimentacoes[:12]:
                linhas.append(f"- {data} | {produto} | {tipo} por {motivo} | Qtd: {quantidade}")
        else:
            linhas.append("- Nenhuma movimentacao registrada")

        self.texto_relatorio.configure(state="normal")
        self.texto_relatorio.delete("1.0", "end")
        self.texto_relatorio.insert("1.0", "\n".join(linhas))
        self.texto_relatorio.configure(state="disabled")

    def _selecionar_produto(self, _evento=None):
        selecao = self.tabela.selection()
        if selecao:
            self.produto_selecionado.set(int(selecao[0]))

    def cadastrar_produto(self):
        nome = self.nome_var.get().strip()
        categoria = self.categoria_var.get()

        try:
            preco = float(self.preco_var.get().replace(",", "."))
            quantidade = int(self.quantidade_var.get())
            backend.cadastrar_produto(nome, categoria, preco, quantidade)
        except ValueError as erro:
            messagebox.showerror("Dados invalidos", str(erro))
            return
        except sqlite3.IntegrityError:
            messagebox.showerror("Produto duplicado", "Ja existe um produto com esse nome.")
            return

        self.nome_var.set("")
        self.preco_var.set("")
        self.quantidade_var.set("0")
        self.atualizar_tudo()
        messagebox.showinfo("Cadastro", "Produto cadastrado com sucesso.")

    def remover_produto(self):
        produto_id = self.produto_selecionado.get()
        if not produto_id:
            messagebox.showwarning("Selecao obrigatoria", "Selecione um produto na tabela.")
            return

        produto = backend.buscar_produto(produto_id)
        if produto is None:
            messagebox.showerror("Produto", "Produto nao encontrado.")
            self.atualizar_tudo()
            return

        if not messagebox.askyesno("Remover produto", f"Tem certeza que deseja remover {produto[1]}?"):
            return

        backend.remover_produto(produto_id)
        self.produto_selecionado.set(0)
        self.atualizar_tudo()
        messagebox.showinfo("Remocao", "Produto removido com sucesso.")

    def registrar_movimentacao(self):
        produto_texto = self.produto_mov_var.get()
        if not produto_texto:
            messagebox.showwarning("Produto", "Selecione um produto.")
            return

        try:
            produto_id = int(produto_texto.split(" - ", 1)[0])
            quantidade = int(self.quantidade_mov_var.get())
        except ValueError:
            messagebox.showerror("Dados invalidos", "Informe uma quantidade inteira valida.")
            return

        tipo, motivo = MOVIMENTACOES[self.tipo_mov_var.get()]
        mensagem = backend.registrar_movimentacao(produto_id, tipo, motivo, quantidade)
        self.quantidade_mov_var.set("")
        self.atualizar_tudo()

        produto = backend.buscar_produto(produto_id)
        if produto and produto[4] <= backend.ESTOQUE_MINIMO:
            mensagem += f"\n\nALERTA: estoque critico de {produto[1]}."

        messagebox.showinfo("Movimentacao", mensagem)


def abrir():
    app = RemansoEstoqueApp()
    app.mainloop()


if __name__ == "__main__":
    abrir()
