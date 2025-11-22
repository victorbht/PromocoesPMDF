from datetime import datetime, date
from dateutil.relativedelta import relativedelta 
from typing import Optional 

# --- 1. Constantes e Dados Base ---

# Mapeamento de abreviaturas para nomes completos
ABREVIATURAS_MAP = {
    "SD": "Soldado",
    "CB": "Cabo",
    "3SGT": "3º Sargento",
    "2SGT": "2º Sargento",
    "1SGT": "1º Sargento",
    "ST": "Subtenente",
}

# Dicionário de Interstícios (Chave: Graduação ATUAL | Valor: [Completo, Reduzido] em meses)
INTERSTICIOS_MILITARES = {
    "Soldado": [120, 60],      # Para promover a Cabo
    "Cabo": [60, 30],         # Para promover a 3º Sargento
    "3º Sargento": [60, 30],  # Para promover a 2º Sargento
    "2º Sargento": [60, 30],  # Para promover a 1º Sargento
    "1º Sargento": [36, 18],  # Para promover a Subtenente
}

# Datas Fixas de Promoção (Formato: (Mês, Dia))
DATAS_PROMOCAO_FIXAS = [
    (4, 22), (8, 21), (12, 26) 
]

# Ordem de progressão de carreira
ORDEM_GRADUACOES = ["Soldado", "Cabo", "3º Sargento", "2º Sargento", "1º Sargento", "Subtenente"]

# --- 2. Funções de Suporte ---

def obter_data_valida(mensagem, pode_ser_vazio=False):
    """Loop para obter e validar a data no formato DD/MM/AAAA, com opção de vazio."""
    while True:
        data_str = input(mensagem).strip()
        
        if pode_ser_vazio and not data_str:
            return None

        try:
            data_objeto = datetime.strptime(data_str, "%d/%m/%Y").date()
            return data_objeto
        except ValueError:
            print(f"\n❌ ERRO: Por favor, digite a data no formato DD/MM/AAAA e certifique-se de que a data é válida.\n")

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


def obter_inputs_comuns():
    """
    Função para obter Graduação (com suporte a abreviaturas), Data Base e Data de Nascimento.
    Retorna a graduação no FORMATO COMPLETO.
    """
    graduacoes_validas = list(INTERSTICIOS_MILITARES.keys())
    abreviaturas_validas = list(ABREVIATURAS_MAP.keys())
    
    # Lista de todas as opções aceitas para exibição
    opcoes_input = graduacoes_validas + abreviaturas_validas
    opcoes_input.sort()

    while True:
        # Pede a entrada, exibe as opções e converte para maiúsculas/título para padronização
        graduacao_input = input(f"\nQual a graduação atual? ({', '.join(opcoes_input)}): ").strip().upper()
        
        graduacao_final = None

        # 1. Verifica se é uma abreviatura
        if graduacao_input in ABREVIATURAS_MAP:
            graduacao_final = ABREVIATURAS_MAP[graduacao_input]
        # 2. Verifica se é o nome completo (Padroniza para título, ex: 'Cabo')
        elif graduacao_input.title() in graduacoes_validas:
            graduacao_final = graduacao_input.title()
        # 3. Verifica o Subtenente (caso especial)
        elif graduacao_input == "ST" or graduacao_input.title() == "Subtenente":
             graduacao_final = "Subtenente"
        
        
        if graduacao_final:
            break
        print(f"❌ Graduação inválida. Use o nome completo ou uma abreviatura ({', '.join(abreviaturas_validas)}).")

    if graduacao_final == "Subtenente":
        return "Subtenente", None, None

    # Obter a data da última promoção
    data_ultima_promocao = obter_data_valida(f"Por favor, insira a data da última promoção (DD/MM/AAAA) para {graduacao_final}: ")
    
    # Obter a data de nascimento (opcional)
    data_nascimento = obter_data_valida("\n[OPCIONAL] Insira a data de nascimento (DD/MM/AAAA) ou deixe em branco: ", pode_ser_vazio=True)
    
    return graduacao_final, data_ultima_promocao, data_nascimento

# --- 3. Funções de Menu (Opções 1, 2, 3 e 4) ---

def calcular_proxima_imediata():
    """Opção 1: Calcula apenas a próxima promoção com escolha de interstício."""
    print("\n--- 1. CÁLCULO DA PRÓXIMA PROMOÇÃO IMEDIATA ---")
    
    graduacao_atual, data_ultima_promocao, data_nascimento = obter_inputs_comuns()
    
    if graduacao_atual == "Subtenente":
        print("\n✅ Já alcançou o posto final da carreira de Praças.")
        return

    while True:
        resposta_reducao = input(f"Houve redução de interstício para esta promoção? (Sim/Não): ").lower().strip()
        if resposta_reducao in ["sim", "não", "nao"]:
            break
        print("❌ Opção inválida. Digite 'Sim' ou 'Não'.")

    indice_intersticio = 0
    if resposta_reducao == "sim":
        indice_intersticio = 1

    intersticio_em_meses = INTERSTICIOS_MILITARES.get(graduacao_atual, [0,0])[indice_intersticio]
    tipo_intersticio = "Reduzido" if indice_intersticio == 1 else "Completo"
    
    try:
        indice_atual = ORDEM_GRADUACOES.index(graduacao_atual)
        proxima_graduacao = ORDEM_GRADUACOES[indice_atual + 1]
    except (ValueError, IndexError):
        proxima_graduacao = "FIM DE CARREIRA (Praças)" 

    if data_ultima_promocao is None:
        print("❌ Erro: Data da última promoção é obrigatória.")
        return
        
    data_minima_elegivel = data_ultima_promocao + relativedelta(months=+intersticio_em_meses)
    data_proxima_promocao = calcular_proxima_promocao(data_ultima_promocao, intersticio_em_meses)
    
    idade_na_promocao = calcular_idade(data_nascimento, data_proxima_promocao) if data_nascimento else None

    print("\n" + "="*70)
    print(f"RESUMO DO CÁLCULO PARA PROMOÇÃO DE {graduacao_atual.upper()} A {proxima_graduacao.upper()}")
    print("="*70)
    print(f"Data da última promoção (Base): {data_ultima_promocao.strftime('%d/%m/%Y')}")
    print(f"Interstício (Tipo: {tipo_intersticio}): {intersticio_em_meses} meses")
    print(f"Data Mínima de Elegibilidade: {data_minima_elegivel.strftime('%d/%m/%Y')}")
    print("-" * 70)
    print(f"🗓️ Próxima Data de Promoção: {data_proxima_promocao.strftime('%d/%m/%Y')}")
    
    if idade_na_promocao is not None:
        print(f"🎂 Idade na Promoção: {idade_na_promocao} anos")
        
    print("="*70)


def projetar_promocoes(graduacao_inicial: str, data_base_promocao: date, indice_intersticio: int, data_nascimento: Optional[date]):
    """
    Opção 2 e 3: Projeta a carreira completa até Subtenente.
    """
    tipo_intersticio = "Reduzido (Melhor Cenário)" if indice_intersticio == 1 else "Completo (Pior Cenário)"
    
    print("\n" + "="*70)
    print(f"📈 PROJEÇÃO DE CARREIRA: {tipo_intersticio.upper()}")
    print(f"Data Base: {data_base_promocao.strftime('%d/%m/%Y')}")
    print("="*70)
    
    header = f"{'PROMOÇÃO':<27} | {'DATA':<12}"
    if data_nascimento:
        header += f" | {'IDADE':<5}"
    print(header)
    print("-" * (43 if not data_nascimento else 50))
    
    try:
        indice_atual = ORDEM_GRADUACOES.index(graduacao_inicial)
    except ValueError:
        print(f"❌ Erro interno: Graduação inicial '{graduacao_inicial}' não encontrada.")
        return

    data_base_para_calculo = data_base_promocao
    
    for i in range(indice_atual, len(ORDEM_GRADUACOES) - 1):
        graduacao_atual = ORDEM_GRADUACOES[i]
        proxima_graduacao = ORDEM_GRADUACOES[i + 1]
        
        intersticio = INTERSTICIOS_MILITARES.get(graduacao_atual, [0, 0])[indice_intersticio]
        data_promocao = calcular_proxima_promocao(data_base_para_calculo, intersticio)
        
        idade_na_promocao = calcular_idade(data_nascimento, data_promocao) if data_nascimento else None
        
        promocao_str = f"De {graduacao_atual} para {proxima_graduacao}"
        print(f"{promocao_str:<27} | {data_promocao.strftime('%d/%m/%Y'):<12}", end="")
        
        if idade_na_promocao is not None:
             print(f" | {idade_na_promocao:<5} anos")
        else:
            print()
            
        data_base_para_calculo = data_promocao 

    print("="*70)
    print(f"** Previsão de Promoção a Subtenente: {data_base_para_calculo.strftime('%d/%m/%Y')} **")
    
    if data_nascimento:
        idade_final = calcular_idade(data_nascimento, data_base_para_calculo)
        print(f"** Idade na Promoção Final: {idade_final} anos **")
        
    print("="*70)


def calcular_plano_carreira(melhor_cenario: bool):
    """Gerencia a chamada para a função de projeção (Opção 2 e 3)."""
    
    graduacao_atual, data_ultima_promocao, data_nascimento = obter_inputs_comuns()
    
    if graduacao_atual == "Subtenente":
        print("\n✅ Já alcançou o posto final da carreira de Praças.")
        return
    
    if data_ultima_promocao is None:
        print("❌ Erro: Data da última promoção é obrigatória.")
        return
        
    indice = 1 if melhor_cenario else 0 
    
    projetar_promocoes(graduacao_atual, data_ultima_promocao, indice, data_nascimento)


def exibir_intersticios():
    """Opção 4: Exibe todos os interstícios definidos, com o formato "De X para Y"."""
    print("\n" + "="*70)
    print("TABELA DE INTERSTÍCIOS (MESES)")
    print("="*70)
    print(f"{'PROMOÇÃO':<30} | {'COMPLETO':<10} | {'REDUZIDO':<10}")
    print("-" * 55)
    
    for i in range(len(ORDEM_GRADUACOES) - 1):
        graduacao_atual = ORDEM_GRADUACOES[i]
        proxima_graduacao = ORDEM_GRADUACOES[i + 1]
        
        if graduacao_atual in INTERSTICIOS_MILITARES:
            intersticios = INTERSTICIOS_MILITARES[graduacao_atual]
            promocao_str = f"De {graduacao_atual} para {proxima_graduacao}"
            
            print(f"{promocao_str:<30} | {intersticios[0]:<10} | {intersticios[1]:<10}")
        
    print("="*70)

# --- 4. Menu Principal ---

def menu_principal():
    """Gerencia o menu, o loop e a execução das opções."""
    
    while True:
        print("\n" + "#"*40)
        print(" SISTEMA DE PROJEÇÃO DE CARREIRA MILITAR ")
        print("#"*40)
        print("1) Calcular data da próxima promoção")
        print("2) Calcular plano de carreira (Melhor Cenário - Reduções)")
        print("3) Calcular plano de carreira (Pior Cenário - Sem Reduções)")
        print("4) Exibir interstícios")
        print("0) Sair")
        print("-" * 40)
        
        escolha = input("Selecione uma opção (0-4): ").strip()
        
        if escolha == '1':
            calcular_proxima_imediata()
        elif escolha == '2':
            calcular_plano_carreira(melhor_cenario=True)
        elif escolha == '3':
            calcular_plano_carreira(melhor_cenario=False)
        elif escolha == '4':
            exibir_intersticios()
        elif escolha == '0':
            print("\nObrigado por utilizar o sistema. Até logo! 👋\n")
            break
        else:
            print("\n❌ Opção inválida. Por favor, digite um número de 0 a 4.")
            
        if escolha != '0':
            input("\nPressione ENTER para voltar ao menu...")
        

if __name__ == "__main__":
    menu_principal()