# Arquivo: otimizador_core.py (VERSÃO COMPLETA E CORRIGIDA)

import json
import random
from pathlib import Path
from datetime import datetime

# --- Parâmetros e Configurações ---
LARGURA_CHAPA_PADRAO = 1200
META_EXCELENCIA = 99.0
HISTORICO_FILE = Path("historico_otimizacao.json")

# --- Funções de Histórico e Utilitários ---

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
    """Gera um ID único e canônico para um conjunto de peças."""
    return "|".join(f"{largura}x{qtd}" for largura, qtd in sorted(pecas_dict.items()))

def formatar_cortes_agrupados(cortes):
    """Agrupa cortes iguais e retorna uma string formatada."""
    contagem = {}
    for valor in cortes:
        contagem[valor] = contagem.get(valor, 0) + 1
    agrupados = []
    for valor, qtd in sorted(contagem.items(), key=lambda item: item[0], reverse=True):
        agrupados.append(f"{valor}mm #{qtd}")
    return "  //  ".join(agrupados)
# DENTRO DE otimizador_core.py

# DENTRO DE otimizador_core.py

def gerar_visualizacao_chapa(chapa_info, largura_chapa, largura_total_barra=50):
    """
    Gera uma representação visual limpa e robusta do uso da chapa.
    Esta versão garante que o comprimento total da barra seja sempre exato.
    """
    
    # 1. Calcula a proporção de uso com base na largura total da chapa.
    proporcao_usada = chapa_info['largura_usada'] / largura_chapa
    
    # 2. Calcula o número de caracteres para a parte usada.
    #    Usar round() garante que a distribuição seja a mais precisa possível.
    usado_chars = int(round(proporcao_usada * largura_total_barra))
    
    # 3. A sobra é simplesmente o restante dos caracteres para completar a barra.
    #    Isso garante que a soma de usado + sobra sempre será igual a largura_total_barra.
    sobra_chars = largura_total_barra - usado_chars
    
    # 4. Constrói a barra.
    #    O '█' (U+2588) representa a parte usada (bloco cheio).
    #    O '░' (U+2591) representa a sobra (bloco pontilhado).
    barra = ('█' * usado_chars) + ('░' * sobra_chars)
    
    return "|" + barra + "|"

# --- Funções de Algoritmos de Otimização ---

def otimizar_com_lista_best_fit(pecas, largura_chapa):
    """Otimiza o corte usando o algoritmo Best-Fit."""
    chapas = []
    for peca in pecas:
        melhor_chapa_index = -1
        menor_espaco_vazio = largura_chapa + 1
        for i, chapa in enumerate(chapas):
            espaco_livre = largura_chapa - chapa['largura_usada']
            if peca <= espaco_livre and espaco_livre < menor_espaco_vazio:
                melhor_chapa_index = i
                menor_espaco_vazio = espaco_livre
        if melhor_chapa_index == -1:
            chapas.append({'largura_usada': peca, 'cortes': [peca]})
        else:
            chapas[melhor_chapa_index]['largura_usada'] += peca
            chapas[melhor_chapa_index]['cortes'].append(peca)

    if not chapas:
        return {'total_chapas': 0, 'aproveitamento': 0, 'detalhes_chapas': []}

    total_chapas = len(chapas)
    largura_total_usada = sum(chapa['largura_usada'] for chapa in chapas)
    aproveitamento = (largura_total_usada / (total_chapas * largura_chapa)) * 100
    detalhes = [{'cortes': c['cortes'], 'largura_usada': c['largura_usada'], 'sobra': largura_chapa - c['largura_usada']} for c in chapas]
    return {'total_chapas': total_chapas, 'aproveitamento': aproveitamento, 'detalhes_chapas': detalhes}

def otimizar_com_lista_ffd(pecas_ordenadas, largura_chapa):
    """Otimiza o corte usando o algoritmo First-Fit (FFD)."""
    chapas = []
    for peca in pecas_ordenadas:
        chapa_encontrada = False
        for chapa in chapas:
            if (largura_chapa - chapa['largura_usada']) >= peca:
                chapa['largura_usada'] += peca
                chapa['cortes'].append(peca)
                chapa_encontrada = True
                break
        if not chapa_encontrada:
            chapas.append({'largura_usada': peca, 'cortes': [peca]})

    if not chapas:
        return {'total_chapas': 0, 'aproveitamento': 0, 'detalhes_chapas': []}

    total_chapas = len(chapas)
    largura_total_usada = sum(chapa['largura_usada'] for chapa in chapas)
    aproveitamento = (largura_total_usada / (total_chapas * largura_chapa)) * 100
    detalhes = [{'cortes': c['cortes'], 'largura_usada': c['largura_usada'], 'sobra': largura_chapa - c['largura_usada']} for c in chapas]
    return {'total_chapas': total_chapas, 'aproveitamento': aproveitamento, 'detalhes_chapas': detalhes}

def calcular_melhor_otimizacao(pecas_dict, largura_chapa, excelencia, algoritmo='best_fit'):
    """Testa estratégias para encontrar a melhor otimização, usando o algoritmo escolhido."""
    if not pecas_dict:
        return {'total_chapas': 0, 'aproveitamento': 0, 'detalhes_chapas': []}

    pecas = []
    for largura, quantidade in pecas_dict.items():
        pecas.extend([largura] * quantidade)
    
    if algoritmo == 'ffd':
        pecas_ordenadas = sorted(pecas, reverse=True)
        return otimizar_com_lista_ffd(pecas_ordenadas, largura_chapa)
    else: # algoritmo == 'best_fit'
        estrategias = [sorted(pecas, reverse=True), sorted(pecas)]
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
                break
        return melhor_resultado

# --- Funções de Geração de Relatório e Execução ---

# DENTRO DE otimizador_core.py

# DENTRO DE otimizador_core.py (Substituir a função existente)

def exibir_resultados_como_texto(resultado, largura_chapa):
    """Gera o relatório de otimização com formatação e visualização aprimoradas."""
    if resultado['total_chapas'] == 0:
        return "Nenhuma peça para otimizar."

    relatorio = []
    
    relatorio.append("======================================")
    relatorio.append("==        PLANO DE CORTE FINAL        ==")
    relatorio.append("======================================")
    relatorio.append(f"  Aproveitamento Geral..: {resultado['aproveitamento']:.2f}%%")
    relatorio.append(f"  Total de Chapas.......: {resultado['total_chapas']}")
    relatorio.append("--------------------------------------\n")

    for i, chapa in enumerate(resultado['detalhes_chapas']):
        chapa_num = i + 1
        aproveitamento_chapa = (chapa['largura_usada'] / largura_chapa) * 100
        cortes_str = formatar_cortes_agrupados(chapa['cortes'])
        
        # --- NOVA LINHA DE VISUALIZAÇÃO ---
        visualizacao_str = gerar_visualizacao_chapa(chapa, largura_chapa)
        
        linha_info = (
            f"Chapa {chapa_num:<2}: [{cortes_str}]  ->  "
            f"Uso: {chapa['largura_usada']}mm | "
            f"Sobra: {chapa['sobra']}mm (Aprov: {aproveitamento_chapa:.2f}%%)"
        )
        relatorio.append(linha_info)
        relatorio.append(f"          {visualizacao_str}\n") # Adiciona a visualização abaixo da info
    
    return "\n".join(relatorio)

# DENTRO DE otimizador_core.py

def executar_otimizacao(pecas_para_corte, largura_chapa, excelencia, algoritmo='best_fit'):
    """Função principal que orquestra a otimização e RETORNA o relatório."""
    historico = carregar_historico()
    id_pecas = gerar_id_unico(pecas_para_corte) + f"|alg:{algoritmo}"
    solucao_armazenada = historico.get(id_pecas)
    
    if solucao_armazenada and solucao_armazenada['aproveitamento'] >= excelencia:
        relatorio_final = f"--- Solução (Algoritmo: {algoritmo.upper()}) encontrada no histórico! ---\n"
        relatorio_final += exibir_resultados_como_texto(solucao_armazenada, largura_chapa)
        return relatorio_final

    resultado = calcular_melhor_otimizacao(pecas_para_corte, largura_chapa, excelencia, algoritmo)

    solucao_anterior = historico.get(id_pecas)
    if not solucao_anterior or resultado['aproveitamento'] > solucao_anterior.get('aproveitamento', 0):
        historico[id_pecas] = {
            'total_chapas': resultado['total_chapas'],
            'aproveitamento': resultado['aproveitamento'],
            'detalhes_chapas': resultado['detalhes_chapas'],
            'timestamp': datetime.now().isoformat()
        }
        salvar_historico(historico)

    relatorio_final = exibir_resultados_como_texto(resultado, largura_chapa)

    # --- NOVO FORMATO DO ALERTA ---
    if resultado['aproveitamento'] < excelencia:
        alerta = (
            f"\n\n--------------------------------------\n"
            f"ATENÇÃO: A meta de {excelencia}%% não foi atingida.\n"
            f"Melhor aproveitamento encontrado: {resultado['aproveitamento']:.2f}%%"
        )
        relatorio_final += alerta
        
    return relatorio_final