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
print(df.head())

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

print(generos.head())

