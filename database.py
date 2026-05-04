import sqlite3
import os

def obter_caminho_banco():
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(pasta, exist_ok=True)
    return os.path.join(pasta, 'sistema.db')

def inicializar_banco():
    caminho = obter_caminho_banco()
    conn = sqlite3.connect(caminho)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        preco REAL NOT NULL,
                        estoque INTEGER DEFAULT 0)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        total_bruto REAL NOT NULL,
                        metodo TEXT NOT NULL,
                        liquido REAL,
                        desconto REAL,
                        data TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_venda (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        venda_id INTEGER,
                        nome_produto TEXT,
                        quantidade INTEGER,
                        preco_unitario REAL,
                        total_item REAL,
                        FOREIGN KEY(venda_id) REFERENCES vendas(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS custos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        descricao TEXT,
                        valor REAL,
                        data TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS configuracoes (
                        chave TEXT PRIMARY KEY,
                        valor REAL)''')

    cursor.execute("SELECT COUNT(*) FROM configuracoes")
    if cursor.fetchone()[0] == 0:
        taxas_padrao = [('Pix', 0), ('Débito', 1.99), ('Crédito', 2.99), ('Dinheiro', 0)]
        cursor.executemany("INSERT INTO configuracoes (chave, valor) VALUES (?, ?)", taxas_padrao)

    conn.commit()
    conn.close()
