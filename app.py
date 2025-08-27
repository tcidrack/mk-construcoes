import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MK Construções - Orçamento", layout="wide")

# ================= LOGO E TÍTULO =================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo/logo-mk.webp", width=150)
with col2:
    st.title("MK CONSTRUÇÕES")
    st.subheader("📊 Planilha de Orçamento")
st.markdown("---")

# ================= SERVIÇOS =================
servicos_padrao = {
    "DEMOLIÇÃO": "m²",
    "LIMPEZA": "m²",
    "IMPERMEABILIZAÇÃO (MANTA)": "m²",
    "REBOCO": "m²",
    "CONTRA-PISO": "m²",
    "REVESTIMENTO": "m²",
    "REJUNTE": "m²",
    "PONTO DE ENERGIA": "un",
    "FORRO": "m²",
    "RESTAURAÇÃO": "m²",
    "EMASSAMENTO": "m²",
    "PINTURA": "m²"
}

# ================= Unidades Disponíveis =================
unidades_disponiveis = ["mm", "cm", "m", "m²", "m³", "un", "kg", "l", "pacote"]

st.markdown("### ⚙️ Selecione os serviços que deseja incluir")
servicos_selecionados = st.multiselect("Serviços", options=list(servicos_padrao.keys()))

if servicos_selecionados:
    dados = []
    st.markdown("### 📋 Insira quantidade, unidade e valor unitário")
    
    for servico in servicos_selecionados:
        cols = st.columns([3, 2, 2, 2])
        
        # Seleção de unidade
        unidade = cols[1].selectbox(
            label=f"Unidade de {servico}",
            options=unidades_disponiveis,
            index=unidades_disponiveis.index(servicos_padrao[servico]) if servicos_padrao[servico] in unidades_disponiveis else 0,
            key=f"unidade_{servico}"
        )

        # Quantidade: inteiro, editável
        qtd = cols[2].number_input(
            label=f"Quantidade de {servico}",
            min_value=0,
            value=0,
            step=1,
            format="%d",
            key=f"qtd_{servico}"
        )

        # Valor Unitário: digitável, com 2 casas decimais
        key_valor = f"valor_{servico}"
        valor_input = cols[3].text_input(
            label=f"Valor Unitário de {servico} (R$)",
            value=st.session_state.get(key_valor, "0,00"),
            key=key_valor
        )

        # Converte o valor para float para cálculos
        try:
            valor_float = round(float(valor_input.replace(",", ".")), 2)
        except ValueError:
            valor_float = 0.0

        total = qtd * valor_float
        dados.append([servico, unidade, qtd, valor_float, total])

    df = pd.DataFrame(
        dados,
        columns=["Serviço", "Unidade", "Quantidade", "Valor Unitário (R$)", "Valor Total (R$)"]
    )

    # Formatação brasileira para exibição no Streamlit
    df["Valor Unitário (R$)"] = df["Valor Unitário (R$)"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    df["Valor Total (R$)"] = df["Valor Total (R$)"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    # Adicionar linha de TOTAL GERAL
    total_geral = sum([qtd * valor_float for _, _, qtd, valor_float, _ in dados])
    total_geral_formatado = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    df.loc[len(df)] = ["VALOR TOTAL", "", "", "", total_geral_formatado]

    # Ajuste de largura das colunas no Streamlit
    def estilizar_tabela(df):
        styles = [
            {"selector": "th", "props": [("min-width", "150px"), ("text-align", "center")]},
            {"selector": "td", "props": [("min-width", "150px"), ("text-align", "center")]}
        ]
        return df.style.set_table_styles(styles)

    st.dataframe(estilizar_tabela(df), use_container_width=True)

    # ================= Exportar Excel com colunas largas e centralizar apenas Quantidade =================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Orçamento")
        workbook = writer.book
        worksheet = writer.sheets["Orçamento"]

        # Formato centralizado apenas para Quantidade
        centralizado = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

        for i, col in enumerate(df.columns):
            # Largura baseada no maior conteúdo entre dados e cabeçalho
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
            if col == "Quantidade":
                worksheet.set_column(i, i, max_len, centralizado)
            else:
                worksheet.set_column(i, i, max_len)

    output.seek(0)
    st.download_button(
        label="📥 Baixar Planilha Excel",
        data=output.getvalue(),
        file_name="orcamento_mk_construcoes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Selecione serviços para montar o orçamento.")
