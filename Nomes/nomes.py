import requests
import sqlite3
import csv

url = "https://data.directory.openbankingbrasil.org.br/participants"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    # Conectando ao Banco de Dados
    conn = sqlite3.connect("nomes.db")
    c = conn.cursor()

    # Drop da tabela existente (se houver)
    c.execute("DROP TABLE IF EXISTS participants")

    # Criando a tabela de participantes
    c.execute("""CREATE TABLE participants (
                    id INTEGER PRIMARY KEY,
                    OrganisationId TEXT,
                    OrganisationName TEXT,
                    logo_url TEXT,
                    authorization_server_url TEXT
                )""")

    # Inserindo os dados dos participantes na tabela
    for participant in data:
        # Verificando se o participante tem o atributo "CustomerFriendlyLogoUri"
        logo_url = participant.get("CustomerFriendlyLogoUri")
        if logo_url and logo_url.endswith(".svg"):
            logo_url = logo_url.replace(".svg", ".png")

        # Verificando se o participante tem o atributo "apis"
        apis = participant.get("apis")
        authorization_server_url = ""
        if apis:
            authorization_server_url = apis[0].get("endpoint", "")

        # Inserindo os dados do participante na tabela
        c.execute("INSERT INTO participants (OrganisationId, OrganisationName, logo_url, authorization_server_url) VALUES (?, ?, ?, ?)",
                  (participant["OrganisationId"], participant["OrganisationName"], logo_url, authorization_server_url))

    # Commit das alterações e fechamento da conexão com o banco de dados
    conn.commit()
    conn.close()
    # Acessando o banco de dados e escrevendo os dados em um arquivo CSV
    conn = sqlite3.connect("nomes.db")
    c = conn.cursor()

    # Selecionando todos os participantes do banco de dados
    c.execute("SELECT * FROM participants")
    rows = c.fetchall()

    # Criando o arquivo CSV e escrevendo os dados nele
    with open("nomes.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Escrevendo o cabeçalho do arquivo CSV
        writer.writerow(["OrganisationId", "OrganisationName",
                        "logo_url", "authorization_server_url"])

        # Escrevendo os dados de cada participante no arquivo CSV
        for row in rows:
            writer.writerow(row)

    # Fechando a conexão com o banco de dados
    conn.close()
    
else:
    print("Erro ao obter dados da API:", response.status_code)
