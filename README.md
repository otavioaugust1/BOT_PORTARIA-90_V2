# BOT_PORTARIA-90_V2
 
# Aplicação de Análise e Tratamento de Dados
Este repositório contém scripts em Python para análise e tratamento de dados provenientes de fontes diversas. Os scripts fornecem funcionalidades para validar, limpar e processar dados em formatos específicos, gerando relatórios de inconsistências e resultados.

## Arquivos
### tratamento_base.py
Este script realiza o tratamento dos dados provenientes de diferentes fontes, incluindo arquivos CSV e planilhas Excel. Ele lida com a importação, limpeza e organização dos dados, preparando-os para análises posteriores.

### validador.py
O script validador.py realiza a validação dos dados processados pelo tratamento_base.py. Ele verifica a consistência dos dados, identificando inconsistências, como procedimentos inválidos, CNES inativos, habilitação de procedimentos, serviços, e gestões distintas entre CNES e CNES-WEB.

## Requisitos do Sistema
1. O script requer as seguintes bibliotecas Python, listadas no arquivo requirements.txt:

## Como Utilizar
1. Crie um ambiente virtual (venv) para isolar as dependências do projeto:

```
python -m venv portaria 
``` 
Ative o ambiente virtual:

```
portaria\Scripts\Activate
```
Instale as bibliotecas necessárias:
``` 
pip install -r requirements.txt
```
Atualize o pip para a versão mais recente:

```
python.exe -m pip install --upgrade pip
``` 
Execute os scripts conforme necessário.

Após o uso, desative o ambiente virtual:

```
deactivate
```
Se desejar, você pode remover o ambiente virtual:

``` 
rm -r portaria
```
Os resultados das análises e tratamentos serão armazenados nos diretórios RESULTADOS.

# Observações

* Certifique-se de colocar os arquivos de dados a serem processados nas pastas apropriadas conforme especificado nos scripts.
* Os resultados das análises e tratamentos serão armazenados nos diretórios RESULTADOS.
* Para garantir o funcionamento adequado dos scripts, verifique se os arquivos de dados estão formatados corretamente e seguem as expectativas de entrada dos scripts.
