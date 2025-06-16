import pandas as pd

# # read txt files
# with open('profession-nouns.txt', mode='r', encoding='utf-8') as profession:
#     profession_list = profession.read().splitlines()
#
# with open('socially-gendered-nouns.txt', mode='r', encoding='utf-8') as gendered:
#     gendered_list = gendered.read().splitlines()
#
# # write a csv
# df = pd.DataFrame({'Noun in Polish': profession_list+gendered_list,
#                    'Translation or definition in English': ['' for _ in range(len(profession_list+gendered_list))],
#                    'Category': ['profession' for _ in range(len(profession_list))] +
#                                ['gendered' for _ in range(len(gendered_list))]})
# df.to_csv('noun_no-translations.csv', index=False)

# manually translate the words in the csv

# read the csv with translations
df = pd.read_csv('noun_translations.csv')
df = df.sort_values('Noun in Polish')

# print the latex code to make the table
begin = r"""\begin{longtblr}[
caption = {Socially gendered and profession nouns in Polish and their translations or definitions in English},
label = {tab:noun-translations},
]{
hlines, vlines,
rowhead = 1,
row{1} = {gray9},
column{1} = {.2\hsize},
column{2} = {.45\hsize},
column{3} = {.15\hsize},
}"""
header = df.columns[0] + ' & ' + df.columns[1] + ' & ' + df.columns[2] + r'\\'
end = r'\end{longtblr}'
tex_lines = [begin, header]

for row in range(len(df)):
    tex_lines.append(df.iloc[row].iloc[0] + ' & ' + df.iloc[row].iloc[1] + ' & ' + df.iloc[row].iloc[2] + r'\\')

tex_lines.append(end)

# write the latex code to a .tex file
with open('writing/Chapters/noun-translations.tex', mode='w', encoding='utf-8') as out:
    out.writelines(line + '\n' for line in tex_lines)
