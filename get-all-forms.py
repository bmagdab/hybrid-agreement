import pandas as pd
import morfeusz2
morf = morfeusz2.Morfeusz()

# reading lists of nouns
with open('profession-nouns.txt', mode='r', encoding='utf-8') as professions_file:
    professions = professions_file.read()
    professions = professions.split('\n')
with open('socially-gendered-nouns.txt', mode='r', encoding='utf-8') as gendered_file:
    gendered = gendered_file.read()
    gendered = gendered.split('\n')

out_dict = {'form': [], 'lexeme': [], 'category': []}

for word in professions:
    for entry in morf.generate(word):
        if 'depr' not in entry[2] and 'brev' not in entry[2]:
            out_dict['form'].append(entry[0])
            out_dict['lexeme'].append(word)
            out_dict['category'].append('profession')

for word in gendered:
    for entry in morf.generate(word):
        if 'depr' not in entry[2] and 'brev' not in entry[2]:
            out_dict['form'].append(entry[0])
            out_dict['lexeme'].append(word)
            out_dict['category'].append('gendered')

df = pd.DataFrame(out_dict)
df.to_csv('noun_forms.csv')
