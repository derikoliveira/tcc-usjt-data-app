# Importando Dados

1. Instalar a última versão do [Python 3](https://www.python.org/downloads/)
    - Na instalação marque a opção "Adicionar Python ao PATH"
2. Abrir o projeto no terminal, no mesmo caminho desse README
3. Instalar as dependências do Python: ```$ pip install -r requirements.txt```
4. Fazer o [download](https://sites.google.com/a/chromium.org/chromedriver/downloads) do driver do chrome 
para o selenium utilizar
5. Adicione o driver ao seu PATH
6. Pegar sua [key](https://www.alphavantage.co/support/#api-key) na Alpha Vantage
7. Rodar a importação: ```$ python import_data.py```

### Argumentos

Exemplo: ```$ python import_data.py --full```

| Argumento  | Valor Padrão | Descrição |
|------------|--------------|-----------|
| -f / --full |     False    | Importa todos os dados disponíveis (leva mais tempo) |



### Opcional

Adicionar arquivo **local_settings.py** com os dados, assim como em **local_settings_example.py**

Dessa maneira não vai ser necessário colocar as informações no input a cada importação

