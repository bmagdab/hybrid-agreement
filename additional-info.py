import pandas as pd
from utils import read_conllu

path = 'agreement-occurrences/'

df = pd.read_csv(path + 'NKJP_1M.csv')

print('reading conllu')
conllu = read_conllu('NKJP_1M')
print('conllu read, converting into df')
conl_tab = pd.DataFrame.from_records(conllu)

sentence_source = []

for i in range(len(df)):
    sentence_source.append(conl_tab[conl_tab.id == df.iloc[i]['sentence_id']].type.item())

df['type_of_text'] = sentence_source

df.to_csv(path + 'NKJP_1M.csv', index=False)
