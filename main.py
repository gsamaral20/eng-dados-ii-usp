import pandas as pd


caminho_arquivo = 'data/livros.csv'
df = pd.read_csv(caminho_arquivo)
#print(df.head())

#print(df.shape)

#df.info()

#print(df.columns)

traducao_colunas = {
    'Book': 'livro', 
    'Author(s)': 'autor', 
    'Original language': 'idioma_original', 
    'First published': 'ano_publicacao',
    'Approximate sales in millions': 'vendas', 
    'Genre': 'genero'
}

df.rename(columns=traducao_colunas, inplace=True)

#print(df.head())

#print(df.isnull().sum())

autores_unicos = pd.DataFrame(df['autor'].unique(), columns=['autor'])
autores_unicos['autor_id'] = autores_unicos.index + 1
#print(autores_unicos.head())

df = df.merge(autores_unicos, on='autor', how='left')
#print(df.head())

autores = pd.DataFrame(df['autor'].unique(), columns=['nome'])

with open('autores.sql', 'w', encoding='utf-8') as file:
    for _, row in autores.iterrows():
        nome = row['nome'].replace("'", "''")
        file.write(f"INSERT INTO autores (nome) VALUES ('{nome}');\n")

df['genero'] = df['genero'].fillna('Unknown')

generos = pd.DataFrame(df['genero'].unique(), columns=['genero'])



from deep_translator import GoogleTranslator

# Supondo que você tenha um DataFrame chamado generos com a coluna 'genero'
generos['genero_pt'] = generos['genero'].apply(
    lambda x: GoogleTranslator(source='auto', target='pt').translate(x)
)

#print(generos.head())

generos['genero_pt'] = generos['genero_pt'].replace('Novella', 'Novela')

generos['genero_pt'] = generos['genero_pt'].str.lower()

#print(generos.shape)

with open('generos.sql', 'w', encoding='utf-8') as arquivo:
    for nome in generos['genero_pt']:
        nome_validado = nome.replace("'", "''")
        arquivo.write(f"INSERT INTO generos (nome) VALUES ('{nome_validado}');\n")

generos_unicos = pd.DataFrame(df['genero'].unique(), columns=['genero'])
generos_unicos['genero_id'] = generos_unicos.index + 1

df = df.merge(generos_unicos, on='genero', how='left')

#print(df.head())

with open('livros.sql', 'w', encoding='utf-8') as f:
    for _, row in df.iterrows():
        nome_livro = row['livro'].replace("'", "''")  # Escapa aspas simples
        idioma = row['idioma_original'].replace("'", "''")
        ano = int(row['ano_publicacao'])
        vendas = float(row['vendas'])
        autor_id = int(row['autor_id'])
        genero_id = int(row['genero_id'])

        sql = (
            f"INSERT INTO livros (nome, idioma, ano_publicacao, vendas, autor_id, genero_id) "
            f"VALUES ('{nome_livro}', '{idioma}', {ano}, {vendas:.2f}, {autor_id}, {genero_id});\n"
        )
        f.write(sql)

api = 'https://raw.githubusercontent.com/guilhermeonrails/datas-csv/refs/heads/main/comentarios.json'
df_comentarios = pd.read_json(api)
#df_comentarios.head()

#df_comentarios.shape
df_comentarios = df_comentarios.merge(
    df[['livro']].reset_index().rename(columns={'index': 'id_livro'}),
    on='livro',
    how='left'
)
#df_comentarios.head()

df_comentarios.isnull().sum()

print(f"{df_comentarios['id_livro'].max()} {df_comentarios['id_livro'].min()}")
df_comentarios[df_comentarios['id_livro'] == 0]

df_comentarios['id_livro'] += 1
print(f"{df_comentarios['id_livro'].max()} {df_comentarios['id_livro'].min()}")

# Substitui valores nulos por NULL e escapa aspas
def format_value(value):
    if pd.isna(value):
        return 'NULL'
    elif isinstance(value, str):
        value = value.replace("'", "''")  # Escapa aspas simples para SQL
        return f"'{value}'"
    else:
        return str(value)

# Nome do arquivo
output_file = "comentarios.sql"

# Abrir o arquivo e escrever os INSERTs
with open(output_file, 'w', encoding='utf-8') as f:
    for _, row in df_comentarios.iterrows():
        values = (
            format_value(row['id_livro']),
            format_value(row['nome']),
            format_value(row['sobrenome']),
            format_value(row['comentario'])
        )
        sql = f"INSERT INTO comentarios (livro_id, nome, sobrenome, comentario) VALUES ({', '.join(values)});\n"
        f.write(sql)

print(f"Arquivo '{output_file}' gerado com sucesso.")


