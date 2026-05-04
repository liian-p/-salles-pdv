import sqlite3
from database import obter_caminho_banco

class Produto:
    @staticmethod
    def adicionar(nome, preco):
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_todos():
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute("SELECT * FROM produtos ORDER BY nome")
        p = c.fetchall()
        conn.close()
        return p

    @staticmethod
    def excluir(id_produto):
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
        conn.commit()
        conn.close()


class Venda:
    @staticmethod
    def registrar(total_bruto, metodo, carrinho=None):
        taxas = Venda.obter_taxas()
        desconto = total_bruto * (taxas.get(metodo, 0) / 100)
        liquido = total_bruto - desconto

        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute(
            "INSERT INTO vendas (total_bruto, metodo, liquido, desconto, data) VALUES (?, ?, ?, ?, datetime('now', 'localtime'))",
            (total_bruto, metodo, liquido, desconto)
        )
        v_id = c.lastrowid

        if carrinho:
            for item in carrinho:
                c.execute(
                    "INSERT INTO itens_venda (venda_id, nome_produto, quantidade, preco_unitario, total_item) VALUES (?, ?, ?, ?, ?)",
                    (v_id, item[0], item[2], item[1], item[3])
                )
        conn.commit()
        conn.close()

    @staticmethod
    def listar_todas():
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute("SELECT * FROM vendas")
        v = c.fetchall()
        conn.close()
        return v

    @staticmethod
    def listar_itens_vendidos(data_corte):
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute(
            "SELECT i.nome_produto, i.quantidade, i.total_item, v.metodo, v.data "
            "FROM itens_venda i JOIN vendas v ON i.venda_id = v.id WHERE v.data >= ?",
            (data_corte,)
        )
        res = c.fetchall()
        conn.close()
        return res

    @staticmethod
    def obter_taxas():
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        try:
            c.execute("SELECT chave, valor FROM configuracoes")
            d = c.fetchall()
        except:
            d = []
        conn.close()
        return {k: v for k, v in d} if d else {"Pix": 0, "Débito": 1.99, "Crédito": 2.99, "Dinheiro": 0}

    @staticmethod
    def atualizar_taxas(taxas_dict):
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        for chave, valor in taxas_dict.items():
            c.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, valor))
        conn.commit()
        conn.close()


class Custo:
    @staticmethod
    def adicionar(desc, valor):
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute(
            "INSERT INTO custos (descricao, valor, data) VALUES (?, ?, datetime('now', 'localtime'))",
            (desc, valor)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def listar_todos():
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute("SELECT * FROM custos ORDER BY id DESC")
        res = c.fetchall()
        conn.close()
        return res

    @staticmethod
    def excluir(id_custo):
        conn = sqlite3.connect(obter_caminho_banco())
        c = conn.cursor()
        c.execute("DELETE FROM custos WHERE id = ?", (id_custo,))
        conn.commit()
        conn.close()
