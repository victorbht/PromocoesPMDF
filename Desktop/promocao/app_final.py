import streamlit as st
from datetime import datetime, date
from dateutil.relativedelta import relativedelta 
import pandas as pd 

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Carreira Militar", 
    page_icon="👮‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILO CSS ---
COR_DESTAQUE = "#0E4C92" # Azul Royal (Genérico e Profissional)
COR_FUNDO_CARD = "#F8F9FA"

st.markdown(f"""
<style>
    /* Cards (Metrics) */
    [data-testid="stMetric"] {{
        background-color: {COR_FUNDO_CARD};
        border: 1px solid #E0E0E0;
        border-left: 5px solid {COR_DESTAQUE};
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    /* Botões */
    div.stButton > button:first-child {{
        background-color: {COR_DESTAQUE};
        color: white;
        font-weight: bold;
    }}
    
    /* Centralizar elementos da sidebar */
    [data-testid="stSidebar"] {{
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. DADOS ---
ORDEM_GRADUACOES = ["Soldado", "Cabo", "3º Sargento", "2º Sargento", "1º Sargento", "Subtenente"]
INTERSTICIOS_MILITARES = {
    "Soldado": [120, 60], "Cabo": [60, 30], "3º Sargento": [60, 30], 
    "2º Sargento": [60, 30], "1º Sargento": [36, 18],
}
DATAS_PROMOCAO_FIXAS = [(4, 22), (8, 21), (12, 26)]

# --- 4. LÓGICA ---
def calcular_proxima_promocao(data_base: date, meses_intersticio: int) -> date:
    data_minima = data_base + relativedelta(months=+meses_intersticio)
    ano_cand = data_minima.year
    for mes, dia in DATAS_PROMOCAO_FIXAS:
        try:
            cand = date(ano_cand, mes, dia)
        except: continue
        if cand >= data_minima: return cand
    mes_abril, dia_abril = DATAS_PROMOCAO_FIXAS[0]
    try: return date(ano_cand + 1, mes_abril, dia_abril)
    except: return date(ano_cand + 1, mes_abril, 20)

def calc_idade(nasc: date, ref: date) -> int:
    return relativedelta(ref, nasc).years

# --- 5. INTERFACE ---

def render_proxima_promocao(grad_atual, data_ult, data_nasc, com_reducao):
    idx = 1 if com_reducao else 0
    try:
        i_atual = ORDEM_GRADUACOES.index(grad_atual)
        prox = ORDEM_GRADUACOES[i_atual + 1]
    except:
        st.error("Erro de sequência."); return

    meses = INTERSTICIOS_MILITARES.get(grad_atual, [0,0])[idx]
    data_promo = calcular_proxima_promocao(data_ult, meses)
    
    st.markdown(f"### 🎯 Próximo Degrau: **{prox}**")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DATA ESTIMADA", data_promo.strftime("%d/%m/%Y"))
    c2.metric("INTERSTÍCIO", f"{meses} meses", delta="Reduzido" if com_reducao else "Completo", delta_color="off")
    
    hoje = date.today()
    dias_total = (data_promo - data_ult).days
    dias_corridos = (hoje - data_ult).days
    progresso = max(0.0, min(1.0, dias_corridos / dias_total)) if dias_total > 0 else 1.0
    
    c3.metric("CUMPRIDO", f"{int(progresso*100)}%")
    
    if data_nasc:
        idade = calc_idade(data_nasc, data_promo)
        c4.metric("IDADE ESTIMADA", f"{idade} anos")
    else:
        c4.metric("IDADE", "--")
    
    st.write("Progresso do Tempo:")
    st.progress(progresso)
    
    if progresso >= 1.0:
        st.success("✅ Requisito de tempo cumprido.")

def render_plano_carreira(grad_ini, data_base, cenario_idx, data_nasc):
    try:
        idx_start = ORDEM_GRADUACOES.index(grad_ini)
    except: return

    tipo = "CENÁRIO OTIMISTA (Com Reduções)" if cenario_idx == 1 else "CENÁRIO CONSERVADOR (Sem Reduções)"
    st.markdown(f"### 📈 {tipo}")
    
    data_cursor = data_base
    dados_tabela = []

    col_timeline, col_tabela = st.columns([2, 3])

    with col_timeline:
        st.write("**LINHA DO TEMPO**")
        for i in range(idx_start, len(ORDEM_GRADUACOES) - 1):
            atual = ORDEM_GRADUACOES[i]
            prox = ORDEM_GRADUACOES[i+1]
            meses = INTERSTICIOS_MILITARES.get(atual, [0,0])[cenario_idx]
            data_promo = calcular_proxima_promocao(data_cursor, meses)
            idade_str = f"{calc_idade(data_nasc, data_promo)} anos" if data_nasc else "-"
            
            with st.expander(f"{atual} ➝ {prox}", expanded=(i == idx_start)):
                st.markdown(f"**Data:** {data_promo.strftime('%d/%m/%Y')} | **Duração:** {meses} meses")
            
            dados_tabela.append({"Graduação": atual, "Para": prox, "Data Promoção": data_promo, "Meses": meses, "Idade": idade_str})
            data_cursor = data_promo

    with col_tabela:
        st.write("**RESUMO**")
        if dados_tabela:
            m1, m2 = st.columns(2)
            m1.metric("DATA FINAL", data_cursor.strftime("%d/%m/%Y"))
            m2.metric("IDADE FINAL", f"{calc_idade(data_nasc, data_cursor)} anos" if data_nasc else "--")
            
            df = pd.DataFrame(dados_tabela)
            df_show = df.copy()
            df_show["Data Promoção"] = df_show["Data Promoção"].apply(lambda x: x.strftime("%d/%m/%Y"))
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DOWNLOAD PLANEJAMENTO", data=csv, file_name="plano_carreira_simulado.csv", mime="text/csv", use_container_width=True, type="primary")

# --- 6. MAIN APP ---

def main():
    with st.sidebar:
        # LOGO EM EMOJI (Zero risco, carrega sempre)
        st.markdown("<div style='text-align: center; font-size: 80px;'>👮‍♂️</div>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center;'>Simulador de Carreira</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        grad_input = st.selectbox("GRADUAÇÃO ATUAL", ORDEM_GRADUACOES, index=1)
        data_ult = st.date_input("DATA DA ÚLTIMA PROMOÇÃO", value=date.today(), format="DD/MM/YYYY")
        
        st.markdown("#### DADOS PESSOAIS")
        usar_nasc = st.toggle("Incluir Idade", value=True)
        data_nasc = st.date_input("DATA DE NASCIMENTO", value=date(1995,1,1), format="DD/MM/YYYY") if usar_nasc else None
        
        st.markdown("---")
        
        # AVISO LEGAL
        st.warning(
            "⚠️ **AVISO LEGAL**\n\n"
            "Esta ferramenta é uma iniciativa independente e **NÃO** possui vínculo oficial com a Polícia Militar do Distrito Federal.\n\n"
            "Os cálculos são estimativas baseadas na Lei 12.086/2009."
        )

    st.title("Planejamento de Carreira Militar")
    st.markdown("**Baseado na Legislação do Distrito Federal**")

    tab1, tab2, tab3 = st.tabs(["PRÓXIMA PROMOÇÃO", "PLANO DE CARREIRA", "LEGISLAÇÃO"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        modo_reducao = st.radio("CONDIÇÃO:", ["Com Redução (50%)", "Interstício Completo"], horizontal=True)
        if grad_input == "Subtenente":
            st.success("Topo da carreira alcançado.")
        else:
            render_proxima_promocao(grad_input, data_ult, data_nasc, "Com Redução" in modo_reducao)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        cenario_global = st.selectbox("CENÁRIO:", ["Otimista (Sempre reduzido)", "Pessimista (Sempre cheio)"])
        if grad_input == "Subtenente":
            st.warning("Sem projeções.")
        else:
            render_plano_carreira(grad_input, data_ult, 1 if "Otimista" in cenario_global else 0, data_nasc)

    with tab3:
        st.markdown("### Quadro de Praças (Referência)")
        dados = []
        for g in ORDEM_GRADUACOES[:-1]:
            ints = INTERSTICIOS_MILITARES.get(g, [0,0])
            dados.append({"De": g, "Completo": f"{ints[0]} m", "Reduzido": f"{ints[1]} m"})
        
        st.dataframe(pd.DataFrame(dados), hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()