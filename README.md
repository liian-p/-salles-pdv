# 🍰 Salles PDV — Versão Web (Streamlit)

## Arquivos do projeto

```
salles_pdv/
├── app.py            ← aplicativo principal (substitui o main.py)
├── database.py       ← banco de dados SQLite
├── models.py         ← modelos de dados
├── logo.png          ← logo da marca
├── requirements.txt  ← bibliotecas necessárias
└── data/
    └── sistema.db    ← criado automaticamente ao rodar
```

---

## ▶️ Como rodar no seu PC (VS Code)

1. **Abra o terminal** no VS Code (`Ctrl + J`)

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Rode o app:**
   ```bash
   streamlit run app.py
   ```

4. O navegador abrirá automaticamente com o sistema.  
   Login: **admin** / Senha: **admin**

---

## 🌐 Como publicar na internet (grátis)

### Passo 1 — Subir para o GitHub
- Crie uma conta em [github.com](https://github.com)
- No VS Code, vá em Source Control → "Publish to GitHub"
- Escolha repositório **privado** (seus dados ficam seguros)

### Passo 2 — Publicar no Streamlit Cloud
- Acesse [share.streamlit.io](https://share.streamlit.io)
- Faça login com sua conta do GitHub
- Clique em **"New app"**
- Selecione seu repositório
- Em **Main file path**, coloque: `app.py`
- Clique em **Deploy!**

O site ficará no ar em alguns minutos, com um link para acessar de qualquer dispositivo. 🎉

---

## ✅ O que foi preservado

- Login com usuário/senha
- Caixa com carrinho de compras
- Geração de recibo (download em PNG)
- Cadastro e exclusão de produtos
- Registro e exclusão de custos
- Configuração de taxas (Pix, Débito, Crédito)
- Relatório com gráficos e download em Excel
- Banco de dados SQLite (todos os dados salvos)
