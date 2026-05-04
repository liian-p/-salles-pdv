import streamlit as st
import os
import io
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")

from database import inicializar_banco
from models import Produto, Venda, Custo

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Salles PDV",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado com as cores da marca ─────────────────────────────────
st.markdown("""
<style>
    /* Cor primária nos botões type="primary" */
    .stButton > button[kind="primary"] {
        background-color: #ad231a !important;
        border-color: #ad231a !important;
        color: #f8dfce !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #c97933 !important;
        border-color: #c97933 !important;
    }
    /* Cabeçalho da sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    /* Métricas com destaque */
    [data-testid="metric-container"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 10px;
    }
    /* Remove padding excessivo */
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Inicialização ────────────────────────────────────────────────────────────
inicializar_banco()

if "logado" not in st.session_state:
    st.session_state.logado = False
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "recibo_bytes" not in st.session_state:
    st.session_state.recibo_bytes = None
if "confirmar_limpeza" not in st.session_state:
    st.session_state.confirmar_limpeza = False


# ═══════════════════════════════════════════════════════════════════════════════
#  TELA DE LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def tela_login():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        if os.path.exists("logo.png"):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image("logo.png", use_container_width=True)
        st.markdown("<h2 style='text-align:center;color:#f8dfce'>Acesso ao Sistema</h2>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário", placeholder="admin")
        senha   = st.text_input("Senha", type="password", placeholder="••••••")
        if st.button("Entrar", use_container_width=True, type="primary"):
            if usuario == "AnaB" and senha == "12345":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: CAIXA (PDV)
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_caixa():
    st.header("💳 Caixa")

    produtos = Produto.listar_todos()
    col_esq, col_dir = st.columns([1, 1.4], gap="large")

    # ── Painel esquerdo: adicionar produto ──────────────────────────────────
    with col_esq:
        with st.container(border=True):
            st.subheader("🛍️ Adicionar Produto")
            if produtos:
                opcoes = {f"{p[1]}  —  R$ {p[2]:.2f}": p for p in produtos}
                sel = st.selectbox("Produto", list(opcoes.keys()), label_visibility="collapsed")
                qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)
                if st.button("➕ Adicionar ao Carrinho", use_container_width=True, type="primary"):
                    prod = opcoes[sel]
                    st.session_state.carrinho.append({
                        "nome": prod[1], "preco": prod[2],
                        "qtd": int(qtd), "total": prod[2] * qtd
                    })
                    st.success(f"**{prod[1]}** adicionado!")
                    st.rerun()
            else:
                st.info("Nenhum produto cadastrado. Adicione em **📦 Produtos**.")

    # ── Painel direito: carrinho ────────────────────────────────────────────
    with col_dir:
        with st.container(border=True):
            st.subheader("🛒 Carrinho")

            if st.session_state.carrinho:
                for i, item in enumerate(st.session_state.carrinho):
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.write(f"**{item['nome']}** × {item['qtd']}   →   R$ {item['total']:.2f}")
                    with c2:
                        if st.button("✕", key=f"rm_{i}", help="Remover item"):
                            st.session_state.carrinho.pop(i)
                            st.rerun()

                st.divider()
                total = sum(i["total"] for i in st.session_state.carrinho)
                st.metric("**Total**", f"R$ {total:.2f}")

                metodo = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Débito", "Crédito"])

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("✅ Finalizar Venda", use_container_width=True, type="primary"):
                        lista = [(i["nome"], i["preco"], i["qtd"], i["total"]) for i in st.session_state.carrinho]
                        Venda.registrar(total, metodo, lista)
                        st.session_state.recibo_bytes = _gerar_recibo(metodo, total, st.session_state.carrinho)
                        st.session_state.carrinho = []
                        st.success("✅ Venda finalizada com sucesso!")
                        st.rerun()
                with b2:
                    if st.button("🗑️ Limpar Carrinho", use_container_width=True):
                        st.session_state.carrinho = []
                        st.rerun()
            else:
                st.info("O carrinho está vazio.")

    # ── Download do último recibo ────────────────────────────────────────────
    if st.session_state.recibo_bytes:
        st.divider()
        nome_arquivo = f"Recibo_{datetime.now().strftime('%d%m%Y_%H%M%S')}.png"
        st.download_button(
            label="📥 Baixar Último Recibo (PNG)",
            data=st.session_state.recibo_bytes,
            file_name=nome_arquivo,
            mime="image/png",
            use_container_width=False,
        )


def _gerar_recibo(metodo, total, carrinho):
    """Gera o recibo em memória e retorna os bytes PNG."""
    agrupados = {}
    for item in carrinho:
        n = item["nome"]
        if n in agrupados:
            agrupados[n]["qtd"]   += item["qtd"]
            agrupados[n]["total"] += item["total"]
        else:
            agrupados[n] = {"qtd": item["qtd"], "total": item["total"]}

    data_atual = datetime.now()
    largura    = 450
    altura     = 520 + len(agrupados) * 40
    img  = Image.new("RGB", (largura, altura), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font   = ImageFont.truetype("consola.ttf", 18)
        font_b = ImageFont.truetype("consolab.ttf", 18)
    except Exception:
        font   = ImageFont.load_default()
        font_b = ImageFont.load_default()

    y = 30
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png").convert("RGBA")
        logo.thumbnail((200, 200))
        img.paste(logo, ((largura - logo.width) // 2, y), logo)
        y += logo.height + 20

    sep2 = "=" * 48
    sep1 = "-" * 48

    def centro(texto, f):
        return (largura - draw.textlength(texto, f)) // 2

    for txt in [sep2, "CUPOM DE VENDA", sep2]:
        draw.text((centro(txt, font), y), txt, fill=(0, 0, 0), font=font)
        y += 30
    y += 10
    draw.text((25, y), f"Data: {data_atual.strftime('%d/%m/%Y %H:%M:%S')}", fill=(0, 0, 0), font=font)
    y += 30
    draw.text((25, y), sep1, fill=(0, 0, 0), font=font)
    y += 40

    for nome, d in agrupados.items():
        txt_item  = f"{nome} x{d['qtd']}"
        txt_preco = f"R$ {d['total']:.2f}"
        draw.text((25, y), txt_item, fill=(0, 0, 0), font=font)
        draw.text((largura - draw.textlength(txt_preco, font) - 25, y), txt_preco, fill=(0, 0, 0), font=font)
        y += 35

    y += 10
    draw.text((25, y), sep1, fill=(0, 0, 0), font=font)
    y += 40
    txt_t = f"R$ {total:.2f}"
    draw.text((25, y), "TOTAL:", fill=(0, 0, 0), font=font_b)
    draw.text((largura - draw.textlength(txt_t, font_b) - 25, y), txt_t, fill=(0, 0, 0), font=font_b)
    y += 35
    draw.text((25, y), "PAGAMENTO:", fill=(0, 0, 0), font=font)
    draw.text((largura - draw.textlength(metodo, font) - 25, y), metodo, fill=(0, 0, 0), font=font)
    y += 50
    for txt in [sep2, "OBRIGADO PELA PREFERÊNCIA!", sep2]:
        draw.text((centro(txt, font), y), txt, fill=(0, 0, 0), font=font)
        y += 35

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: PRODUTOS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_produtos():
    st.header("📦 Produtos")
    col_esq, col_dir = st.columns([1, 1.4], gap="large")

    with col_esq:
        with st.container(border=True):
            st.subheader("Cadastrar Produto")
            nome  = st.text_input("Nome do Produto", placeholder="Ex: Brigadeiro, Bolo de Pote...")
            preco = st.number_input("Preço de Venda (R$)", min_value=0.01, value=5.00, format="%.2f")
            if st.button("✅ Salvar Produto", use_container_width=True, type="primary"):
                if nome.strip():
                    Produto.adicionar(nome.strip(), preco)
                    st.success(f"**{nome}** salvo com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha o nome do produto.")

    with col_dir:
        with st.container(border=True):
            st.subheader("Produtos Cadastrados")
            produtos = Produto.listar_todos()
            if produtos:
                # Cabeçalho
                h1, h2, h3 = st.columns([4, 2, 1])
                h1.markdown("**Nome**"); h2.markdown("**Preço**"); h3.markdown("**Excluir**")
                st.divider()
                for p in produtos:
                    c1, c2, c3 = st.columns([4, 2, 1])
                    c1.write(p[1])
                    c2.write(f"R$ {p[2]:.2f}")
                    with c3:
                        if st.button("🗑️", key=f"dp_{p[0]}", help=f"Excluir {p[1]}"):
                            Produto.excluir(p[0])
                            st.rerun()
            else:
                st.info("Nenhum produto cadastrado ainda.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: CUSTOS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_custos():
    st.header("💸 Custos Operacionais")
    col_esq, col_dir = st.columns([1, 1.4], gap="large")

    with col_esq:
        with st.container(border=True):
            st.subheader("Registrar Gasto")
            desc  = st.text_input("Descrição", placeholder="Ex: Insumos, Aluguel, Gás...")
            valor = st.number_input("Valor (R$)", min_value=0.01, value=50.00, format="%.2f")
            if st.button("✅ Salvar Gasto", use_container_width=True, type="primary"):
                if desc.strip():
                    Custo.adicionar(desc.strip(), valor)
                    st.success("Gasto registrado!")
                    st.rerun()
                else:
                    st.warning("Preencha a descrição.")

    with col_dir:
        with st.container(border=True):
            st.subheader("Histórico de Custos")
            custos = Custo.listar_todos()
            if custos:
                h1, h2, h3, h4 = st.columns([4, 2, 3, 1])
                h1.markdown("**Descrição**"); h2.markdown("**Valor**"); h3.markdown("**Data**"); h4.markdown("**Del.**")
                st.divider()
                for c in custos:
                    c1, c2, c3, c4 = st.columns([4, 2, 3, 1])
                    c1.write(c[1])
                    c2.write(f"R$ {c[2]:.2f}")
                    c3.write(str(c[3])[:10] if c[3] else "—")
                    with c4:
                        if st.button("🗑️", key=f"dc_{c[0]}"):
                            Custo.excluir(c[0])
                            st.rerun()
            else:
                st.info("Nenhum gasto registrado ainda.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: CONFIGURAÇÃO DE TAXAS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_config():
    st.header("⚙️ Configuração de Taxas")
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.container(border=True):
            st.subheader("Taxas por Forma de Pagamento (%)")
            taxas = Venda.obter_taxas()
            with st.form("form_taxas"):
                pix     = st.number_input("Taxa Pix (%)",     value=float(taxas.get("Pix", 0)),    format="%.2f", min_value=0.0)
                debito  = st.number_input("Taxa Débito (%)",  value=float(taxas.get("Débito", 1.99)), format="%.2f", min_value=0.0)
                credito = st.number_input("Taxa Crédito (%)", value=float(taxas.get("Crédito", 2.99)), format="%.2f", min_value=0.0)
                st.caption("💡 Dinheiro sempre com taxa 0%.")
                if st.form_submit_button("Atualizar Taxas", use_container_width=True, type="primary"):
                    Venda.atualizar_taxas({"Pix": pix, "Débito": debito, "Crédito": credito, "Dinheiro": 0})
                    st.success("Taxas atualizadas com sucesso!")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PÁGINA: RELATÓRIO / RESUMO
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_resumo():
    st.header("📊 Relatório")

    filtro = st.segmented_control("Período", ["Diário", "Semanal", "Mensal"], default="Diário")
    if not filtro:
        filtro = "Diário"

    hoje  = datetime.now().date()
    dias  = {"Diário": 0, "Semanal": 7, "Mensal": 30}
    corte = hoje - timedelta(days=dias[filtro])

    bruto = taxas_tot = custos_tot = 0
    metodos = {"Dinheiro": 0, "Pix": 0, "Débito": 0, "Crédito": 0}

    for v in Venda.listar_todas():
        try:
            dv = datetime.strptime(v[5], "%Y-%m-%d %H:%M:%S").date()
            if dv >= corte:
                bruto     += v[1]
                taxas_tot += v[4] or 0
                metodos[v[2]] = metodos.get(v[2], 0) + v[1]
        except Exception:
            pass

    for c in Custo.listar_todos():
        try:
            dc = datetime.strptime(c[3], "%Y-%m-%d %H:%M:%S").date()
            if dc >= corte:
                custos_tot += c[2]
        except Exception:
            pass

    lucro = bruto - taxas_tot - custos_tot

    # ── Cards de indicadores ─────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Vendas Brutas",   f"R$ {bruto:.2f}")
    k2.metric("🏧 Taxas Máquina",   f"R$ {taxas_tot:.2f}",  delta=f"-{taxas_tot:.2f}",  delta_color="inverse")
    k3.metric("💸 Custos Operac.",   f"R$ {custos_tot:.2f}", delta=f"-{custos_tot:.2f}", delta_color="inverse")
    k4.metric("✅ Lucro Real",       f"R$ {lucro:.2f}",      delta=f"+{lucro:.2f}" if lucro >= 0 else f"{lucro:.2f}")

    st.divider()

    # ── Métodos de pagamento ─────────────────────────────────────────────────
    st.subheader("Métodos de Pagamento")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💵 Dinheiro", f"R$ {metodos.get('Dinheiro', 0):.2f}")
    m2.metric("💠 Pix",      f"R$ {metodos.get('Pix', 0):.2f}")
    m3.metric("💳 Débito",   f"R$ {metodos.get('Débito', 0):.2f}")
    m4.metric("💳 Crédito",  f"R$ {metodos.get('Crédito', 0):.2f}")

    st.divider()

    # ── Gráficos ─────────────────────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Vendas por Método")
        vals = {k: v for k, v in metodos.items() if v > 0}
        if vals:
            fig, ax = plt.subplots(figsize=(5, 4))
            fig.patch.set_facecolor("#0e1117")
            ax.set_facecolor("#0e1117")
            ax.pie(vals.values(), labels=vals.keys(), autopct="%1.1f%%",
                   colors=["#ad231a", "#c97933", "#3498db", "#2ecc71"],
                   textprops={"color": "white"})
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Nenhuma venda no período.")

    with col_g2:
        st.subheader("Resumo Financeiro")
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor("#0e1117")
        ax2.set_facecolor("#0e1117")
        barras = ax2.bar(["Bruto", "Taxas", "Custos", "Lucro"],
                         [bruto, taxas_tot, custos_tot, lucro],
                         color=["#3498db", "#e74c3c", "#e67e22", "#2ecc71"])
        ax2.tick_params(colors="white"); ax2.yaxis.label.set_color("white")
        for spine in ax2.spines.values(): spine.set_edgecolor("#333")
        for bar in barras:
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f"R${bar.get_height():.0f}", ha="center", color="white", fontsize=9)
        st.pyplot(fig2)
        plt.close(fig2)

    st.divider()

    # ── Tabela de detalhamento ───────────────────────────────────────────────
    st.subheader("Detalhamento de Vendas")
    corte_str = corte.strftime("%Y-%m-%d 00:00:00")
    itens = Venda.listar_itens_vendidos(corte_str)

    if itens:
        df = pd.DataFrame(itens, columns=["Produto", "Qtd", "Total (R$)", "Método", "Data/Hora"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Export Excel ─────────────────────────────────────────────────────
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Vendas", index=False)
            df_custos = pd.DataFrame(Custo.listar_todos(), columns=["ID", "Descrição", "Valor (R$)", "Data"])
            df_custos.to_excel(writer, sheet_name="Custos", index=False)

        st.download_button(
            label="📥 Baixar Relatório Excel",
            data=buf.getvalue(),
            file_name=f"Relatorio_Salles_{filtro}_{hoje}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.info("Nenhuma venda registrada no período selecionado.")

    # ── Área de limpeza ──────────────────────────────────────────────────────
    st.divider()
    with st.expander("🗑️ Limpar Dados", expanded=False):
        st.warning("⚠️ **Atenção:** Esta ação apaga os dados permanentemente e não pode ser desfeita!")

        op1, op2 = st.columns(2)
        with op1:
            limpar_vendas = st.checkbox("Limpar todas as Vendas")
        with op2:
            limpar_custos = st.checkbox("Limpar todos os Custos")

        if st.button("🗑️ Limpar Dados Selecionados", type="primary"):
            if not limpar_vendas and not limpar_custos:
                st.error("Selecione ao menos uma opção acima.")
            else:
                st.session_state.confirmar_limpeza = True
                st.session_state.limpar_vendas = limpar_vendas
                st.session_state.limpar_custos = limpar_custos

        if st.session_state.confirmar_limpeza:
            st.error("**Tem certeza?** Essa ação não pode ser desfeita!")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Sim, limpar agora", use_container_width=True, type="primary"):
                    import sqlite3
                    from database import obter_caminho_banco
                    conn = sqlite3.connect(obter_caminho_banco())
                    cur  = conn.cursor()
                    if st.session_state.get("limpar_vendas"):
                        cur.execute("DELETE FROM vendas")
                        cur.execute("DELETE FROM itens_venda")
                    if st.session_state.get("limpar_custos"):
                        cur.execute("DELETE FROM custos")
                    conn.commit()
                    conn.close()
                    st.session_state.confirmar_limpeza = False
                    st.success("✅ Dados apagados com sucesso!")
                    st.rerun()
            with c2:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.confirmar_limpeza = False
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  ROTEADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logado:
    tela_login()
else:
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=160)
        else:
            st.title("SALLES")
        st.markdown("---")
        pagina = st.radio(
            "Navegação",
            ["💳 Caixa", "📦 Produtos", "💸 Custos", "⚙️ Taxas", "📊 Relatório"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado  = False
            st.session_state.carrinho = []
            st.rerun()

    PAGINAS = {
        "💳 Caixa":      pagina_caixa,
        "📦 Produtos":   pagina_produtos,
        "💸 Custos":     pagina_custos,
        "⚙️ Taxas":      pagina_config,
        "📊 Relatório":  pagina_resumo,
    }
    PAGINAS[pagina]()
