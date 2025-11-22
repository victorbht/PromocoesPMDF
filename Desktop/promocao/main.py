from datetime import datetime, date
from dateutil.relativedelta import relativedelta 

# --- 1. Constantes e Dados Base ---

# Dicionário de Interstícios (Chave: Graduação ATUAL | Valor: [Completo, Reduzido em 50%] em meses)
INTERSTICIOS_MILITARES = {
    "Soldado": [120, 60],      # Para promover a Cabo
    "Cabo": [60, 30],         # Para promover a 3º Sargento
    "3º Sargento": [60, 30],  # Para promover a 2º Sargento
    "2º Sargento": [60, 30],  # Para promover a 1º Sargento
    "1º Sargento": [36, 18],  # Para promover a Subtenente
}

# Datas Fixas de Promoção (Formato: (Mês, Dia))
DATAS_PROMOCAO_FIXAS = [
    (4, 22),  # 22 de Abril
    (8, 21),  # 21 de Agosto
    (12, 26) # 26 de Dezembro
]

# Ordem de progressão de carreira (para identificar a próxima graduação automaticamente)
ORDEM_GRADUACOES = ["Soldado", "Cabo", "3º Sargento", "2º Sargento", "1º Sargento", "Subtenente"]

# --- 2. Funções de Cálculo e Validação ---

def obter_data_valida(mensagem):
    """Loop para obter e validar a data no formato DD/MM/AAAA."""
    while True:
        data_str = input(mensagem)
        try:
            # Tenta converter a string para um objeto datetime
            data_objeto = datetime.strptime(data_str, "%d/%m/%Y").date()
            return data_objeto
        except ValueError:
            # Captura erros de formato inválido ou de valor inválido
            print(f"\n❌ ERRO: Por favor, digite a data no formato DD/MM/AAAA e certifique-se de que a data é válida.\n")

def calcular_proxima_promocao(data_base: date, meses_intersticio: int) -> date:
    """
    Calcula a próxima data de promoção (22/04, 21/08 ou 26/12) APÓS o interstício ser completado.
    """
    # 1. Calcular a data MÍNIMA de elegibilidade
    data_minima_elegivel = data_base + relativedelta(months=+meses_intersticio)

    # 2. Inicializa o ano de busca a partir do ano de elegibilidade
    ano_candidato = data_minima_elegivel.year

    # 3. Itera sobre as datas fixas no ano de elegibilidade
    for mes, dia in DATAS_PROMOCAO_FIXAS:
        try:
            data_promocao_candidata = date(ano_candidato, mes, dia)
        except ValueError:
            continue
        
        # 4. Se a data fixa de promoção for posterior ou igual à data mínima, é a próxima.
        if data_promocao_candidata >= data_minima_elegivel:
            return data_promocao_candidata

    # 5. Se todas as datas do ano_candidato já passaram, a próxima promoção é em Abril do ano seguinte.
    ano_candidato += 1
    # Pega a primeira data (22/04) do próximo ano
    mes_abril, dia_abril = DATAS_PROMOCAO_FIXAS[0] 
    
    try:
        proxima_abril = date(ano_candidato, mes_abril, dia_abril)
    except ValueError:
        proxima_abril = date(ano_candidato, mes_abril, 20) 
        
    return proxima_abril

# --- 3. Lógica Principal (Cálculo Imediato) ---

def iniciar_calculo_promocao():
    """Função principal para obter inputs e calcular a próxima promoção imediata."""
    
    # 1. Obter a graduação atual do usuário
    graduacoes_validas = list(INTERSTICIOS_MILITARES.keys())
    while True:
        graduacao_desejada = input(f"Qual a graduação atual? ({', '.join(graduacoes_validas)}): ").strip().title()
        
        # # Adicionar tratamento de erro (try-except) caso a graduação não esteja no dicionário
        if graduacao_desejada in graduacoes_validas:
            break
        print(f"❌ Graduação inválida. Digite uma das seguintes: {', '.join(graduacoes_validas)}.")

    # 2. Obter a data da última promoção com tratamento de erro
    data_ultima_promocao = obter_data_valida(f"Por favor, insira a data da última promoção (DD/MM/AAAA) para {graduacao_desejada}: ")

    # 3. Obter a opção de redução de interstício
    while True:
        resposta_reducao = input(f"Houve redução de interstício? (Sim/Não): ").lower().strip()
        if resposta_reducao in ["sim", "não", "nao"]:
            break
        print("❌ Opção inválida. Digite 'Sim' ou 'Não'.")

    # 4. Determinar o interstício e a próxima graduação
    indice_intersticio = 0 # Padrão: Interstício Completo (0)
    if resposta_reducao == "sim":
        indice_intersticio = 1 # Interstício Reduzido (1)

    intersticio_em_meses = INTERSTICIOS_MILITARES[graduacao_desejada][indice_intersticio]
    tipo_intersticio = "Reduzido" if indice_intersticio == 1 else "Completo"
    
    # Mapeamento da próxima graduação usando a lista ORDEM_GRADUACOES
    try:
        indice_atual = ORDEM_GRADUACOES.index(graduacao_desejada)
        proxima_graduacao = ORDEM_GRADUACOES[indice_atual + 1]
    except (ValueError, IndexError):
        # Para Subtenente ou graduações não mapeadas
        proxima_graduacao = "FIM DE CARREIRA (Praças)" 

    # 5. Calcular a data de promoção
    data_minima_elegivel = data_ultima_promocao + relativedelta(months=+intersticio_em_meses)
    data_proxima_promocao = calcular_proxima_promocao(data_ultima_promocao, intersticio_em_meses)

    # 6. Exibir o resultado
    print("\n" + "="*70)
    print(f"RESUMO DO CÁLCULO PARA PROMOÇÃO DE {graduacao_desejada.upper()} A {proxima_graduacao.upper()}")
    print("="*70)
    print(f"Data da última promoção (Base): {data_ultima_promocao.strftime('%d/%m/%Y')}")
    print(f"Interstício (Tipo: {tipo_intersticio}): {intersticio_em_meses} meses")
    print(f"Data Mínima de Elegibilidade: {data_minima_elegivel.strftime('%d/%m/%Y')}")
    print("-" * 70)
    print(f"🗓️ Próxima Data de Promoção: {data_proxima_promocao.strftime('%d/%m/%Y')}")
    print("="*70)

# Para rodar o sistema, você descomenta a linha abaixo
# iniciar_calculo_promocao()