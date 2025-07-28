import json
import random
from pathlib import Path
from datetime import datetime

# --- Parâmetros e Configurações ---
# Em uma aplicação real, viriam da GUI.
LARGURA_CHAPA_PADRAO = 1200
META_EXCELENCIA = 99.0
HISTORICO_FILE = Path("historico_otimizacao.json") #Path para acessar um arquivo terceiro nesse caso para acessar

def carregar_historico():
    """Carrega o histórico de otimizações de um arquivo JSON."""
    if HISTORICO_FILE.exists():
        with open(HISTORICO_FILE, 'r') as f:
            return json.load(f)
    return {}

def salvar_historico(historico):
    """Salva o histórico de otimizações em um arquivo JSON."""
    with open(HISTORICO_FILE, 'w') as f:
        json.dump(historico, f, indent=4)

def gerar_id_unico(pecas_dict):
    """
    Gera um ID único e canônico para um conjunto de peças.
    Ex: {100: 2, 250: 1} -> "100x2|250x1"
    """
    # Ordena pela largura da peça para garantir consistência
    return "|".join(f"{largura}x{qtd}" for largura, qtd in sorted(pecas_dict.items()))

def formatar_cortes_agrupados(cortes):
    """Agrupa cortes iguais e retorna uma string formatada."""
    contagem = {}
    for valor in cortes:
        contagem[valor] = contagem.get(valor, 0) + 1
    
    # Ordena pela largura da peça, do maior para o menor
    agrupados = []
    for valor, qtd in sorted(contagem.items(), key=lambda item: item[0], reverse=True):
        agrupados.append(f"{valor}mm #{qtd}")
    return "  //  ".join(agrupados)

def otimizar_com_lista_best_fit(pecas, largura_chapa):
    """
    Otimiza o corte usando o algoritmo Best-Fit.
    Tenta encaixar a peça na chapa onde o espaço restante será mínimo.
    """
    chapas = []  # Lista de dicionários, cada um representando uma chapa
    for peca in pecas:
        melhor_chapa_index = -1
        menor_espaco_vazio = largura_chapa + 1 # Um valor maior que qualquer sobra possível

        for i, chapa in enumerate(chapas):
            espaco_livre = largura_chapa - chapa['largura_usada']
            if peca <= espaco_livre and espaco_livre < menor_espaco_vazio:
                melhor_chapa_index = i
                menor_espaco_vazio = espaco_livre
        
        if melhor_chapa_index == -1:
            # Nenhuma chapa existente pode acomodar a peça, cria uma nova
            chapas.append({'largura_usada': peca, 'cortes': [peca]})
        else:
            # Adiciona a peça à melhor chapa encontrada
            chapas[melhor_chapa_index]['largura_usada'] += peca
            chapas[melhor_chapa_index]['cortes'].append(peca)

    if not chapas:
        return {'total_chapas': 0, 'aproveitamento': 0, 'detalhes_chapas': []}

    total_chapas = len(chapas)
    largura_total_usada = sum(chapa['largura_usada'] for chapa in chapas)
    aproveitamento = (largura_total_usada / (total_chapas * largura_chapa)) * 100

    detalhes = [
        {
            'cortes': chapa['cortes'],
            'largura_usada': chapa['largura_usada'],
            'sobra': largura_chapa - chapa['largura_usada']
        } for chapa in chapas
    ]
    
    return {
        'total_chapas': total_chapas,
        'aproveitamento': aproveitamento,
        'detalhes_chapas': detalhes
    }

def calcular_melhor_otimizacao(pecas_dict, largura_chapa, excelencia):
    """
    Testa múltiplas estratégias (ordenação, aleatoriedade) para encontrar a melhor otimização.
    """
    if not pecas_dict:
        return {'total_chapas': 0, 'aproveitamento': 0, 'detalhes_chapas': []}

    # Gera a lista completa de peças
    pecas = []
    for largura, quantidade in pecas_dict.items():
        pecas.extend([largura] * quantidade)
        
    # Estratégias de ordenação
    estrategias = [
        sorted(pecas, reverse=True),  # Decrescente (base para o FFD)
        sorted(pecas),                # Crescente
    ]
    # Adiciona várias tentativas aleatórias para buscar melhores resultados
    for _ in range(8):
        lista_aleatoria = pecas[:]
        random.shuffle(lista_aleatoria)
        estrategias.append(lista_aleatoria)

    melhor_resultado = None

    for lista in estrategias:
        resultado = otimizar_com_lista_best_fit(lista, largura_chapa)
        if not melhor_resultado or resultado['aproveitamento'] > melhor_resultado['aproveitamento']:
            melhor_resultado = resultado
        
        if melhor_resultado['aproveitamento'] >= excelencia:
            break # Meta atingida, não precisa procurar mais

    return melhor_resultado

def exibir_resultados(resultado, largura_chapa):
    """Exibe os resultados da otimização no console."""
    if resultado['total_chapas'] == 0:
        print("Nenhuma peça para otimizar.")
        return

    print("\n--- RELATÓRIO DE OTIMIZAÇÃO ---")
    print(f"Total de Chapas Utilizadas: {resultado['total_chapas']}")
    print(f"Aproveitamento Geral: {resultado['aproveitamento']:.2f}%\n")

    for i, chapa in enumerate(resultado['detalhes_chapas']):
        aproveitamento_chapa = (chapa['largura_usada'] / largura_chapa) * 100
        cortes_str = formatar_cortes_agrupados(chapa['cortes'])
        print(
            f"Chapa {i + 1}: [{cortes_str}] | "
            f"Total: {chapa['largura_usada']}mm | "
            f"Sobra: {chapa['sobra']}mm | "
            f"Aproveitamento: {aproveitamento_chapa:.2f}%"
        )
    print("-----------------------------\n")

def executar_otimizacao(pecas_para_corte, largura_chapa, excelencia):
    """Função principal que orquestra a otimização."""
    historico = carregar_historico()
    id_pecas = gerar_id_unico(pecas_para_corte)

    solucao_armazenada = historico.get(id_pecas)
    
    if solucao_armazenada and solucao_armazenada['aproveitamento'] >= excelencia:
        print("--- Solução de alta performance encontrada no histórico! ---")
        exibir_resultados(solucao_armazenada, largura_chapa)
        return

    print("Calculando nova otimização...")
    resultado = calcular_melhor_otimizacao(pecas_para_corte, largura_chapa, excelencia)

    # Só salva se atingir a excelência ou se for a primeira vez
    if not solucao_armazenada or resultado['aproveitamento'] >= excelencia:
        historico[id_pecas] = {
            'total_chapas': resultado['total_chapas'],
            'aproveitamento': resultado['aproveitamento'],
            'detalhes_chapas': resultado['detalhes_chapas'],
            'timestamp': datetime.now().isoformat()
        }
        salvar_historico(historico)
        print("Nova solução salva no histórico.")

    exibir_resultados(resultado, largura_chapa)

    if resultado['aproveitamento'] < excelencia:
        print(
            f"ATENÇÃO: Não foi possível atingir a meta de excelência de {excelencia}%.\n"
            f"Melhor aproveitamento encontrado: {resultado['aproveitamento']:.2f}%"
        )

# --- Ponto de Entrada da Aplicação (Exemplo para Sprint 1) ---
if __name__ == "__main__":
    # Exemplo de um pedido de corte
    # Em uma aplicação real, isso viria de um arquivo ou da GUI
    meu_pedido_de_corte = {
        500: 4,  # 4 peças de 500mm
        350: 5,  # 5 peças de 350mm
        215: 8,  # 8 peças de 215mm
        110: 10, # 10 peças de 110mm
    }

    print(f"Iniciando otimização para o pedido:")
    print(meu_pedido_de_corte)
    print(f"Largura da Chapa: {LARGURA_CHAPA_PADRAO}mm | Meta de Aproveitamento: {META_EXCELENCIA}%")
    print("-" * 30)
    
    executar_otimizacao(meu_pedido_de_corte, LARGURA_CHAPA_PADRAO, META_EXCELENCIA)