# TRATAMENTO DOS DADOS DO CNES, SIGTAP E TETO
## Autor: Otávio Augusto dos Santos
## Data: 2024-01-13

## Versão: 0.0.1
## Descrição: Bot de analise de dados na planilha de proposto (PLANO)
## Entrada: Planilha de proposto (PLANO)
## Saída: Relatório de inconsistências
## Observações:
## 1. O arquivo de entrada deve estar na pasta PLANILHA 
## 2. O arquivo de saída será gerado na pasta RESULTADOS
## 3. O arquivo de saída será salvo 2 Arquivos: TXT e XLSX]

# Importação das bibliotecas
import pandas as pd         # importando a biblioteca pandas
import numpy as np          # importando a biblioteca numpy
import time                 # importando a biblioteca time
import glob                 # importando a biblioteca glob
import os                   # importando a biblioteca os
import xlsxwriter           # importando a biblioteca xlsxwriter
import pyexcel as pe        # importando a biblioteca pyexcel
import locale               # importando a biblioteca locale
import math                 # importando a biblioteca math
import warnings
warnings.filterwarnings("ignore") 

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') # Definindo o locale para pt_BR
tempo_inicial = time.time() # tempo inicial para calcular o tempo de execução do código

from glob import glob # Utilizado para listar arquivos de um diretório
from datetime import datetime # Utilizado para trabalhar com datas

#Comando para exibir todas colunas do arquivo
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


df_cnes_leitos = pd.read_csv('BASE\.BASE_CNES_LEITOS.csv', sep=';', encoding='latin-1', dtype=str) # Importação dados do CNES
df_cnes_habilitacao = pd.read_csv('BASE\.BASE_CNES_HABILITACAO.csv', sep=';', encoding='latin-1', dtype=str) # Importação CNES Habilitação
df_cnes_servicos = pd.read_csv('BASE\.BASE_CNES_SERVICOS.csv', sep=';', encoding='latin-1', dtype=str) # Importação CNES Serviços
print(f"[OK] IMPORTAÇÃO DO CNES  ====================================================>: {time.strftime('%H:%M:%S')}")

df_sigtap = pd.read_csv('BASE\.BASE_SIGTAP_GERAL.csv', sep=';', encoding='latin-1', dtype=str)
df_sigtap['CO_PROCEDIMENTO']= df_sigtap['CO_PROCEDIMENTO'].astype(int) # Converte a coluna 'COD_PROCEDIMENTO' para string
print(f"[OK] IMPORTAÇÃO DO SIGTAP  ==================================================>: {time.strftime('%H:%M:%S')}")

# Importação da PLANILHA
## Analisando e tratamento da PLANILHA aba 1
df_planilha = glob('PLANILHA\*.xlsm')[0] # Planilha para ser validada
df_planilha_aba1 = pd.read_excel(df_planilha, sheet_name='PLANEJADO') # Lê o arquivo excel
df_planilha_aba1.rename(columns={'PLANO ESTADUAL DE REDUÇÃO DE FILAS DE ESPERA EM CIRURGIAS ELETIVAS - CNES':'CNES','Unnamed: 1':'ESTABELECIMENTO','Unnamed: 2':'CO_PROCEDIMENTO','Unnamed: 3':'DESC_PROCEDIMENTO',
                                 'Unnamed: 4':'INST_REGISTRO','Unnamed: 5':'SEL_REGISTRO','Unnamed: 6':'VALOR_PROC','Unnamed: 7':'VALOR_CONTRATADO','Unnamed: 8':'QUANT_EXEC','Unnamed: 9':'VALOR_TOTAL_CONTR',
                                 'Unnamed: 10':'PERC_CONTRATADO','Unnamed: 11':'GESTÃO','Unnamed: 12':'COD_NAT_JURIDICA','Unnamed: 13':'NAT_JURIDICA','Unnamed: 14':'COD_GESTOR','Unnamed: 15':'COD_GESTOR_ERRO',
                                 'Unnamed: 16':'GESTOR','Unnamed: 17':'DESC_GESTOR'},inplace=True) 
df_planilha_aba1.drop(0, inplace=True) # Remove a primeira linha do arquivo
df_planilha_aba1.drop(1, inplace=True) # Remove a segunda linha do arquivo

quant_fila = df_planilha_aba1['QUANT_EXEC'].sum() # Soma o valor total da coluna 'QUANT_FILA'
quant_fila = '{0:,}'.format(quant_fila).replace(',','.') #Aqui coloca os pontos
quant_prodedimentos = df_planilha_aba1['CO_PROCEDIMENTO'].count() # Conta a quantidade de procedimentos
print(f"[OK] IMPORTAÇÃO DO PLANO  ===================================================>: {time.strftime('%H:%M:%S')}")

# Procedimento requer habilitação
df_sigtap_h = df_sigtap[['CO_PROCEDIMENTO','EXIGE_HABILITACAO','CO_HABILITACAO']] # Cria um novo dataframe com as colunas 'COD_PROCEDIMENTO','EXIGE HABILITACAO','CO_HABILITACAO'
df_sigtap_h.drop_duplicates(subset='CO_PROCEDIMENTO', keep='first', inplace=True) # Remove os valores duplicados da coluna 'COD_PROCEDIMENTO'
df_planilha_aba1['PROC_HABILITACAO'] = df_planilha_aba1['CO_PROCEDIMENTO'].map(df_sigtap_h.set_index('CO_PROCEDIMENTO')['EXIGE_HABILITACAO']) # Adiciona uma nova coluna com a informação de habilitação do procedimento
## Procedimento requer serviço/class
df_sigtap_s = df_sigtap[['CO_PROCEDIMENTO','EXIGE_SERVIÇO','CO_SERVICO','CO_CLASSIFICACAO']] # Cria um novo dataframe com as colunas 'COD_PROCEDIMENTO','EXIGE SERVICO','CO_SERVICO'
df_sigtap_s.drop_duplicates(subset='CO_PROCEDIMENTO', keep='first', inplace=True) # Remove os valores duplicados da coluna 'COD_PROCEDIMENTO'
df_planilha_aba1['PROC_SERVICO'] = df_planilha_aba1['CO_PROCEDIMENTO'].map(df_sigtap_s.set_index('CO_PROCEDIMENTO')['EXIGE_SERVIÇO']) # Adiciona uma nova coluna com a informação de serviço do procedimento
print(f"[OK] IMPORTAÇÃO DE HABILITAÇÃO E SERVIÇO  ===================================>: {time.strftime('%H:%M:%S')}")

# Verificar se o CNES esta ATIVO:
df_cnes_habilitacao['CO_CNES'] = df_cnes_habilitacao['CO_CNES'].astype(str) # Converte a coluna 'CNES' para string
df_cnes_habilitacao2 = df_cnes_habilitacao.loc[df_cnes_habilitacao['CO_MOTIVO_DESAB'] > '0'] # Seleciona apenas os CNES habilitados
df_planilha_aba1['CNES_ATIVO'] = np.where(df_planilha_aba1['CNES'].isin(df_cnes_habilitacao2['CO_CNES']), 'NÃO', '-') # Adiciona a coluna 'CNES_ATIVO' ao dataframe
print(f"[OK] VERIFICAR CNES ATIVOS  =================================================>: {time.strftime('%H:%M:%S')}")


# Verificar se o procedimento informado é valido 
df_planilha_aba1['PROC_VALIDO'] = np.where(df_planilha_aba1['CO_PROCEDIMENTO'].isin(df_sigtap['CO_PROCEDIMENTO']), '-','NÃO')
print(f"[OK] VERIFICAR PROCEDIMENTO VALIDOS  ========================================>: {time.strftime('%H:%M:%S')}")

# Verificar habilitação x CNES
df_planilha_aba1['LINHA'] = df_planilha_aba1.reset_index().index+1 # numerar as linhas 
df_planilha_aba1_h = df_planilha_aba1[['CNES','CO_PROCEDIMENTO']] # Cria um novo dataframe com as colunas 'CNES','COD_PROCEDIMENTO',
df_cnes_habilitacao = df_cnes_habilitacao.rename(columns={'CO_CNES':'CNES'})
df_planilha_aba1_h.drop_duplicates(subset='CO_PROCEDIMENTO', keep='first', inplace=True) # Remove os valores duplicados da coluna 'COD_PROCEDIMENTO'
df_planilha_aba1_h['PROC_HABILITACAO'] = df_planilha_aba1_h['CO_PROCEDIMENTO'].map(df_sigtap_h.set_index('CO_PROCEDIMENTO')['EXIGE_HABILITACAO']) # Adiciona uma nova coluna com a informação de habilitação do procedimento
df_planilha_aba1_h = df_planilha_aba1_h.merge(df_sigtap_h[['CO_PROCEDIMENTO','CO_HABILITACAO']], on='CO_PROCEDIMENTO', how='left') # Adiciona a coluna 'PROC_VALIDO' ao dataframe
df_planilha_aba1_h = df_planilha_aba1_h.merge(df_cnes_habilitacao[['CNES','CO_CODIGO_GRUPO']], on='CNES', how='left') # Adiciona a coluna 'PROC_VALIDO' ao dataframe
df_planilha_aba1_h.drop(df_planilha_aba1_h.loc[df_planilha_aba1_h['PROC_HABILITACAO'] == '-'].index, inplace=True) # Remove os procedimentos que não exigem habilitação
df_planilha_aba1_h['CNES_HABILITADO'] = np.where(df_planilha_aba1_h['CO_CODIGO_GRUPO'].isin(df_planilha_aba1_h['CO_HABILITACAO']), 'SIM','EXIGE_HAB') # Adiciona a coluna 'CNES_HABILITADO' ao dataframe
df_planilha_aba1_h.drop_duplicates(subset='CO_PROCEDIMENTO', keep='first', inplace=True) # Remove os valores duplicados da coluna 'CNES'
df_planilha_aba1 = df_planilha_aba1.merge(df_planilha_aba1_h[['CNES','CO_PROCEDIMENTO','CNES_HABILITADO']], on=['CNES','CO_PROCEDIMENTO'], how='left') # Adiciona a coluna 'CNES_HABILITADO' ao dataframe
df_planilha_aba1.drop_duplicates(subset='LINHA', keep='first', inplace=True) # Remove os valores duplicados da coluna 'CNES'
print(f"[OK] VERIFICADO HABILITAÇÃO  ================================================>: {time.strftime('%H:%M:%S')}")

# Verificar serviços/class x CNES
df_planilha_aba1_s = df_planilha_aba1[['CNES','CO_PROCEDIMENTO']] # Cria um novo dataframe com as colunas 'CNES','COD_PROCEDIMENTO',
df_planilha_aba1_s.drop_duplicates(subset='CO_PROCEDIMENTO', keep='first', inplace=True) # Remove os valores duplicados da coluna 'COD_PROCEDIMENTO'
df_planilha_aba1_s['EXIGE_SERVIÇO'] = df_planilha_aba1_s['CO_PROCEDIMENTO'].map(df_sigtap_s.set_index('CO_PROCEDIMENTO')['EXIGE_SERVIÇO']) # Adiciona uma nova coluna com a informação de habilitação do procedimento
df_planilha_aba1_s = df_planilha_aba1_s.merge(df_sigtap_s[['CO_PROCEDIMENTO','CO_SERVICO']], on='CO_PROCEDIMENTO', how='left') # Adiciona a coluna 'PROC_VALIDO' ao dataframe
df_cnes_servicos = df_cnes_servicos.rename(columns={"CO_CNES": "CNES"}) # Renomeia a coluna 'CO_CNES' para 'CNES'
df_planilha_aba1_s = df_planilha_aba1_s.merge(df_cnes_servicos[['CNES','CO_SERVICO']], on='CNES', how='left') # Adiciona a coluna 'PROC_VALIDO' ao dataframe
df_planilha_aba1_s.drop(df_planilha_aba1_s.loc[df_planilha_aba1_s['EXIGE_SERVIÇO'] == '-'].index, inplace=True) # Remove os procedimentos que não exigem habilitação
df_planilha_aba1_s['CNES_SERVICO'] = np.where(df_planilha_aba1_s['CO_SERVICO_x'].isin(df_planilha_aba1_s['CO_SERVICO_y']), '-','EXIGE_SERV') # Adiciona a coluna 'CNES_HABILITADO' ao dataframe
df_planilha_aba1_s.drop_duplicates(subset='CO_PROCEDIMENTO', keep='first', inplace=True) # Remove os valores duplicados da coluna 'CNES'
df_planilha_aba1 = df_planilha_aba1.merge(df_planilha_aba1_s[['CNES','CO_PROCEDIMENTO','CNES_SERVICO']], on=['CNES','CO_PROCEDIMENTO'], how='left') # Adiciona a coluna 'CNES_HABILITADO' ao dataframe
df_planilha_aba1.drop_duplicates(subset='LINHA', keep='first', inplace=True) # Remove os valores duplicados da coluna 'CNES'
print(f"[OK] VERIFICADO SERVIÇO  ====================================================>: {time.strftime('%H:%M:%S')}")

df_planilha_aba1.fillna('-',inplace=True) # LIMPEZA DO NaN para -
df_planilha_aba1 = df_planilha_aba1.loc[df_planilha_aba1['CO_PROCEDIMENTO'] != '-', :]

# Verificar tipo de Gestão
df_planilha_aba1_g = df_planilha_aba1[['CNES','GESTÃO','LINHA']] # Cria um novo dataframe com as colunas 'CNES','COD_PROCEDIMENTO', 
df_cnes_gestao = df_cnes_leitos[['CO_CNES','TP_GESTAO']] # Cria um novo dataframe com as colunas 'CNES','COD_PROCEDIMENTO',]
df_cnes_gestao = df_cnes_gestao.rename(columns={"CO_CNES": "CNES"}) # Renomeia a coluna 'CO_CNES' para 'CNES'
df_planilha_aba1_g = df_planilha_aba1_g.merge(df_cnes_gestao[['CNES','TP_GESTAO']], on='CNES', how='left') # Adiciona a coluna 'PROC_VALIDO' ao dataframe
df_planilha_aba1_g['TP_GESTAO'] = df_planilha_aba1_g['TP_GESTAO'].replace({'M': 'MUNICIPAL', 'E': 'ESTADUAL', 'D': 'DUPLA'})
df_planilha_aba1_g.drop_duplicates(subset='LINHA', keep='first', inplace=True) # Remove os valores duplicados da coluna 'COD_PROCEDIMENTO'

df_planilha_aba1_g['GESTAO_VALIDA'] =   np.where((df_planilha_aba1_g['GESTÃO'] == 'MUNICIPAL') & (df_planilha_aba1_g['TP_GESTAO'] == 'MUNICIPAL'), '-', 
                                        np.where((df_planilha_aba1_g['GESTÃO'] == 'ESTADUAL') & (df_planilha_aba1_g['TP_GESTAO'] == 'ESTADUAL'), '-', 
                                        np.where((df_planilha_aba1_g['GESTÃO'] == 'MUNICIPAL') & (df_planilha_aba1_g['TP_GESTAO'] == 'DUPLA'), '-', 
                                        np.where((df_planilha_aba1_g['GESTÃO'] == 'ESTADUAL') & (df_planilha_aba1_g['TP_GESTAO'] == 'DUPLA'), '-', 
                                        np.where((df_planilha_aba1_g['GESTÃO'] == 'MUNICIPAL') & (df_planilha_aba1_g['TP_GESTAO'] == 'ESTADUAL'), 'NÃO', 
                                        np.where((df_planilha_aba1_g['GESTÃO'] == 'ESTADUAL') & (df_planilha_aba1_g['TP_GESTAO'] == 'MUNICIPAL'), 'NÃO', '-')))))) # verificar gestão

df_planilha_aba1 = df_planilha_aba1.merge(df_planilha_aba1_g[['LINHA','GESTAO_VALIDA']], on='LINHA', how='left') # Adiciona a coluna 'CNES_HABILITADO' ao dataframe
print(f"[OK] VERIFICADO GESTÃO VALIDA  ==============================================>: {time.strftime('%H:%M:%S')}")


# RELATORIO FINAL
caminho_nova_pasta = "RESULTADOS"

try:
    os.mkdir(caminho_nova_pasta) 
    print(f"[OK] CRIAÇÃO DE PASTA RESULTADOS  ===========================================>: {time.strftime('%H:%M:%S')}")
except OSError as erro:
    print(f"[OK] PASTA RESULTADOS EXISTENTE  ============================================>: {time.strftime('%H:%M:%S')}")
quant_cnes = df_planilha_aba1['CNES'].nunique() # Quantidade de CNES
quant_cnes_municipal = df_planilha_aba1['CNES'].loc[df_planilha_aba1['GESTÃO'] == 'MUNICIPAL'].nunique() # Quantidade de municípios
quant_cnes_estadual = df_planilha_aba1['CNES'].loc[df_planilha_aba1['GESTÃO'] == 'ESTADUAL'].nunique() # Quantidade de estadual
df_planilha_aba1 = df_planilha_aba1.drop('LINHA',axis=1)

# Supondo que você já tenha o DataFrame df_planilha e df_planilha_aba1

df_planilha = os.path.splitext(os.path.basename(df_planilha))[0]  # Pega o nome do arquivo sem a extensão
file_nome = df_planilha.split('/')[-1]  # Pega o nome do arquivo

# Cria um arquivo Excel usando a biblioteca XlsxWriter
with pd.ExcelWriter(f'RESULTADOS/{file_nome}_resultado.xlsx', engine='xlsxwriter') as writer:
    df_planilha_aba1.to_excel(writer, sheet_name='Aba 1', index=False)

# Não é necessário chamar writer.save() ou writer.close() quando usando o bloco 'with'
    
print(f"[OK] GERANDO ARQUIVO PARA XLSX  =============================================>: {time.strftime('%H:%M:%S')}")



tempo_final = time.time()
tempo_total = int(tempo_final - tempo_inicial)

minutos = tempo_total // 60
segundos = tempo_total % 60

data_hora_atual = datetime.now() # Pega a data e hora atual

# SALVANDO OS RESULTADOS    
arquivo = open(f'RESULTADOS/{file_nome}_resultado.txt', 'w')  #Criar arquivo txt resultado em modo de escrita

# Informações do arquivo
print(f"\n=============================================== INFORMAÇÕES DO ARQUIVO ================================================", file=arquivo)

print(f"\n======================================================[ ABA 1 ]========================================================", file=arquivo)

# Verificação de procedimentos inválidos
if df_planilha_aba1['PROC_VALIDO'].str.contains('NÃO').any():
    print(f" [ERRO] - ABA 1 - Existem procedimentos na Fila, que não são válidos; ==============> NOME DA COLUNA ['PROC_VALIDO'](V)", file=arquivo)
else:
    print(f" [OK] - ABA 1 - Não existem procedimentos inválidos; ===============================> NOME DA COLUNA ['PROC_VALIDO'](V)", file=arquivo)

# Verificação de CNES ativo
if df_planilha_aba1['CNES_ATIVO'].str.contains('NÃO').any():
    print(f" [ERRO] - ABA 1 - Existem CNES inativos; ============================================> NOME DA COLUNA ['CNES_ATIVO'](U)", file=arquivo)
else:
    print(f" [OK] - ABA 1 - Não existem CNES inativos; ==========================================> NOME DA COLUNA ['CNES_ATIVO'](U)", file=arquivo)

# Verificação de CNES habilitado
if df_planilha_aba1['CNES_HABILITADO'].str.contains('EXIGE_HAB').any():
    print(f" [ALERTA] - ABA 1 - Existem CNES não habilitados; ==============================> NOME DA COLUNA ['CNES_HABILITADO'](X)", file=arquivo)
else:
    print(f" [OK] - ABA 1 - Não existem CNES não habilitados; ==============================> NOME DA COLUNA ['CNES_HABILITADO'](X)", file=arquivo)

# Verificação de CNES serviço ativo
if df_planilha_aba1['CNES_SERVICO'].str.contains('EXIGE_SERV').any():
    print(f" [ALERTA] - ABA 1 - Existem CNES não serviço/class;==================================> NOME DA COLUNA [CNES_SERVICO](Y)", file=arquivo)
else:
    print(f" [OK] - ABA 1 - Não existem CNES não serviço/class;==================================> NOME DA COLUNA [CNES_SERVICO](Y)", file=arquivo)

# CNES GESTÃO ESTAD_X EXECUÇÃO
if df_planilha_aba1['GESTAO_VALIDA'].str.contains('NÃO').any():
    print(f" [ALERTA] - ABA 1 - Existem CNES informado com gestão diferente do CNES-WEB; =====> NOME DA COLUNA ['GESTAO_VALIDA'](Z)", file=arquivo)
else:
    print(f" [OK] - ABA 1 - CNES informado com gestão igual ao CNES-WEB; =====================> NOME DA COLUNA ['GESTAO_VALIDA'](Z)", file=arquivo)

print(f"\n\n=====================================================[ ARQUIVO ]=======================================================", file=arquivo)

print(f" [OK] - Arquivo enviado pelo gestor: '{file_nome}';", file=arquivo)
print(f" [OK] - Arquivo TXT: '{file_nome} - resultado.txt'  gerado com sucesso;", file=arquivo)
print(f" [OK] - Arquivo XLS: '{file_nome} - resultado.xlsx' gerado com sucesso;", file=arquivo)

# RESULTADO FINAL
print(f"\n \n=================================================== RESULTADO FINAL ===================================================  \n", file=arquivo)
#print(f" UF DO PLANO DE AÇÃO ===========================================> {uf}", file=arquivo)
print(f" QUANTIDADE DE SOLICITAÇÕES NA FILA ATÉ DIA 31/12/22 ===========> {quant_fila}", file=arquivo)
print(f" QTDE PROCEDIMENTO CIRURGICOS INFORMADO NA FILA   ==============> {quant_prodedimentos}", file=arquivo)
print(f" TOTAL DE ESTABELECIMENTOS CNES ================================> {quant_cnes}", file=arquivo)
print(f" TOTAL DE ESTABELECIMENTOS EM GESTÃO MUNICIPAL =================> {quant_cnes_municipal}", file=arquivo)
print(f" TOTAL DE ESTABELECIMENTOS EM GESTÃO ESTADUAL ==================> {quant_cnes_estadual}", file=arquivo)

#print(f" VALOR TOTAL ALOCADO NA PLANILHA ===============================> {valor_total}", file=arquivo)

print(f"\n \n====================================================== VERSÃO 1.0.8 ==================================================", file=arquivo)

# Tempo de execução
print(f" [TEMPO] - Total de execução: ===============================================================> {minutos} minutos e {segundos} segundos", file=arquivo)
print(f" [DATA HORA] - Data e hora de execução: ============================================================>", data_hora_atual.strftime("%d/%m/%Y %H:%M"), file=arquivo)

# Fechar arquivo txt
arquivo.close()
print(f"[OK] GERANDO ARQUIVO ANALISE  ===============================================>: {time.strftime('%H:%M:%S')}")
