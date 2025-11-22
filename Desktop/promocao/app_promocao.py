import streamlit as st
from datetime import datetime, date
from dateutil.relativedelta import relativedelta 
from typing import Optional 
import pandas as pd # Necessário para Streamlit exibir tabelas bem

# --- 1. Constantes e Dados Base ---
ABREVIATURAS_MAP = {
    "SD": "Soldado", "CB": "Cabo", "3SGT": "3º Sargento", "2SGT": "2º Sargento", 
    "1SGT": "1º Sargento", "ST": "Subtenente",
}
INTERSTICIOS_MILITARES = {
    "Soldado": [120, 60], "Cabo": [60, 30], "3º Sargento": [60, 30], 
    "2º Sargento": [60, 30], "1º Sargento": [36, 18],
}
DATAS_PROMOCAO_FIXAS = [(4, 22), (8, 21), (12, 26)]
ORDEM_GRADUACOES = ["Soldado", "Cabo", "3º Sargento", "2º Sargento", "1º Sargento", "Subtenente"]


# --- 2. Funções de Lógica (Mantidas) ---

def calcular_proxima_promocao(data_base: date, meses_intersticio: int) -> date:
    """Calcula a próxima data de promoção APÓS o interstício ser completado."""
    data_minima_elegivel = data_base + relativedelta(months=+meses_intersticio)
    ano_candidato = data_minima_elegivel.year

    for mes, dia in DATAS_PROMOCAO_FIXAS:
        try:
            data_promocao_candidata = date(ano_candidato, mes, dia)
        except ValueError:
            continue
        
        if data_promocao_candidata >= data_minima_elegivel:
            return data_promocao_candidata

    ano_candidato += 1
    mes_abril, dia_abril = DATAS_PROMOCAO_FIXAS[0] 
    
    try:
        proxima_abril = date(ano_candidato, mes_abril, dia_abril)
    except ValueError:
        proxima_abril = date(ano_candidato, mes_abril, 20) 
        
    return proxima_abril

def calcular_idade(data_nascimento: date, data_referencia: date) -> int:
    """Calcula a idade em anos na data de referência."""
    return relativedelta(data_referencia, data_nascimento).years


# --- 3. Funções de CÁLCULO (Adaptadas para Streamlit) ---

def calcular_proxima_imediata_streamlit(graduacao_atual: str, data_ultima_promocao: date, data_nascimento: Optional[date], houve_reducao: bool):
    """Opção 1: Calcula apenas a próxima promoção (versão Streamlit)."""
    
    # 1. Determinar o interstício
    indice_intersticio = 1 if houve_reducao else 0
    intersticio_em_meses = INTERSTICIOS_MILITARES.get(graduacao_atual, [0,0])[indice_intersticio]
    tipo_intersticio = "Reduzido" if houve_reducao else "Completo"
    
    # 2. Mapeamento da próxima graduação
    try:
        indice_atual = ORDEM_GRADUACOES.index(graduacao_atual)
        proxima_graduacao = ORDEM_GRADUACOES[indice_atual + 1]
    except (ValueError, IndexError):
        proxima_graduacao = "FIM DE CARREIRA (Praças)" 

    # 3. Cálculo
    data_minima_elegivel = data_ultima_promocao + relativedelta(months=+intersticio_em_meses)
    data_proxima_promocao = calcular_proxima_promocao(data_ultima_promocao, intersticio_em_meses)
    
    idade_na_promocao = calcular_idade(data_nascimento, data_proxima_promocao) if data_nascimento else None

    # 4. Exibir o resultado
    st.subheader(f"Resultado da Promoção de {graduacao_atual} a {proxima_graduacao}")
    
    dados = {
        "Detalhe": ["Data Base", "Tipo de Interstício", "Meses", "Data Mínima Elegível", "Próxima Data de Promoção"],
        "Valor": [
            data_ultima_promocao.strftime('%d/%m/%Y'),
            tipo_intersticio,
            f"{intersticio_em_meses} meses",
            data_minima_elegivel.strftime('%d/%m/%Y'),
            data_proxima_promocao.strftime('%d/%m/%Y')
        ]
    }
    
    df = pd.DataFrame(dados)
    st.table(df)

    if idade_na_promocao is not None:
        st.success(f"🎂 Idade na Promoção: **{idade_na_promocao} anos**")
        

def projetar_promocoes_streamlit(graduacao_inicial: str, data_base_promocao: date, indice_intersticio: int, data_nascimento: Optional[date]):
    """Opção 2 e 3: Projeta a carreira completa (versão Streamlit)."""
    
    tipo_intersticio = "MELHOR CENÁRIO (Com Redução)" if indice_intersticio == 1 else "PIOR CENÁRIO (Sem Redução)"
    st.subheader(f"📈 Projeção de Carreira - {tipo_intersticio}")
    st.write(f"Data Base: {data_base_promocao.strftime('%d/%m/%Y')}")
    
    plano_de_carreira = []
    
    try:
        indice_atual = ORDEM_GRADUACOES.index(graduacao_inicial)
    except ValueError:
        st.error(f"Erro interno: Graduação inicial '{graduacao_inicial}' não encontrada.")
        return

    data_base_para_calculo = data_base_promocao
    
    for i in range(indice_atual, len(ORDEM_GRADUACOES) - 1):
        graduacao_atual = ORDEM_GRADUACOES[i]
        proxima_graduacao = ORDEM_GRADUACOES[i + 1]
        
        intersticio = INTERSTICIOS_MILITARES.get(graduacao_atual, [0, 0])[indice_intersticio]
        data_promocao = calcular_proxima_promocao(data_base_para_calculo, intersticio)
        idade_na_promocao = calcular_idade(data_nascimento, data_promocao) if data_nascimento else None
        
        plano_de_carreira.append({
            "Promoção": f"De {graduacao_atual} para {proxima_graduacao}",
            "Data": data_promocao.strftime('%d/%m/%Y'),
            "Idade": idade_na_promocao if idade_na_promocao is not None else "-",
            "Meses Interstício": intersticio
        })
        
        data_base_para_calculo = data_promocao 

    # Exibir o resultado em tabela
    df = pd.DataFrame(plano_de_carreira)
    st.dataframe(df, hide_index=True)
    
    st.success(f"**Previsão de Promoção a Subtenente:** {data_base_para_calculo.strftime('%d/%m/%Y')}")
    
    if data_nascimento:
        idade_final = calcular_idade(data_nascimento, data_base_para_calculo)
        st.info(f"**Idade na Promoção Final:** {idade_final} anos")


def exibir_intersticios_streamlit():
    """Opção 4: Exibe todos os interstícios definidos em formato Streamlit."""
    st.subheader("Tabela de Interstícios (Meses)")

    data = []
    for i in range(len(ORDEM_GRADUACOES) - 1):
        graduacao_atual = ORDEM_GRADUACOES[i]
        proxima_graduacao = ORDEM_GRADUACOES[i + 1]
        
        if graduacao_atual in INTERSTICIOS_MILITARES:
            intersticios = INTERSTICIOS_MILITARES[graduacao_atual]
            
            data.append({
                "Promoção": f"De {graduacao_atual} para {proxima_graduacao}",
                "Completo": intersticios[0],
                "Reduzido": intersticios[1]
            })
        
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True)


# --- 4. Função Principal Streamlit (Aplica a GUI) ---

def app_principal():
    st.set_page_config(page_title="Projetor de Carreira Militar", layout="wide")
    st.title("🛡️ Calculadora de Promoção Militar")
    st.markdown("---")
    
    # ----------------------------------------------------
    # COLUNAS DE INPUT
    # ----------------------------------------------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dados de Início")
        
        # Graduação (Com opções completas e abreviadas)
        opcoes_graduacao = ORDEM_GRADUACOES.copy()
        
        # Mapeamos a entrada abreviada para a entrada completa internamente
        graduacao_input = st.selectbox("1. Qual sua graduação atual?", opcoes_graduacao)
        
        if graduacao_input == "Subtenente":
            st.warning("✅ Já alcançou o posto final da carreira de Praças.")
            return

        # Data da Última Promoção
        data_ultima_promocao = st.date_input("2. Data da Última Promoção:", value=date.today())

        # Data de Nascimento (Opcional)
        com_data_nascimento = st.checkbox("Incluir cálculo de idade?")
        data_nascimento = None
        if com_data_nascimento:
            # Garante que a data de nascimento seja razoável (ex: mais de 18 anos atrás)
            data_nascimento = st.date_input("3. Data de Nascimento:", value=date(1995, 1, 1))
            

    with col2:
        st.subheader("Opções de Cálculo")
        
        # Redução de Interstício para Cálculo Imediato
        reducao_imediata = st.radio("4. Houve redução para a próxima promoção imediata?", ('Não', 'Sim'), horizontal=True)
        houve_reducao = (reducao_imediata == 'Sim')

        # Funcionalidade do Menu
        funcionalidade = st.radio(
            "5. Selecione a Projeção Desejada:",
            ['Próxima Promoção Imediata', 'Plano de Carreira (Melhor Cenário)', 'Plano de Carreira (Pior Cenário)', 'Exibir Tabela de Interstícios']
        )
        
        st.markdown("---")
        if st.button("CALCULAR PROJEÇÃO", type="primary"):
            st.session_state.run_calculation = True
        
    st.markdown("---")
    
    # ----------------------------------------------------
    # EXIBIÇÃO DE RESULTADOS
    # ----------------------------------------------------
    if 'run_calculation' in st.session_state and st.session_state.run_calculation:
        
        # ⚠️ Nota: A abreviatura foi removida do selectbox, simplificando o input.
        # A lógica de abreviaturas está agora apenas no mapeamento de nomes (INTERSTICIOS_MILITARES).
        
        if funcionalidade == 'Próxima Promoção Imediata':
            calcular_proxima_imediata_streamlit(graduacao_input, data_ultima_promocao, data_nascimento, houve_reducao)
        
        elif funcionalidade == 'Plano de Carreira (Melhor Cenário)':
            # Índice 1 = Reduzido (Melhor)
            projetar_promocoes_streamlit(graduacao_input, data_ultima_promocao, 1, data_nascimento)
            
        elif funcionalidade == 'Plano de Carreira (Pior Cenário)':
            # Índice 0 = Completo (Pior)
            projetar_promocoes_streamlit(graduacao_input, data_ultima_promocao, 0, data_nascimento)
            
        elif funcionalidade == 'Exibir Tabela de Interstícios':
            exibir_intersticios_streamlit()

# Comando para rodar a aplicação Streamlit
if __name__ == '__main__':
    # Inicializa o estado para rodar o cálculo (usado para exibir o resultado apenas após o clique do botão)
    if 'run_calculation' not in st.session_state:
        st.session_state.run_calculation = False
        
    app_principal()