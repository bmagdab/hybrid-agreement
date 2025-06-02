import regex as re
import pandas as pd

# This script creates a list of profession nouns I need for my corpus study. The list is based on two papers:

# Szpyra-Kozłowska, J. (2019). Premiera, premierka czy pani premier? Nowe nazwy żeńskie i ograniczenia w ich tworzeniu w
# świetle badania ankietowego. Język Polski, 22–40. https://doi.org/10.31286/JP.99.2.2

# Szpyra-Kozłowska, J., & Laidler, K. (2022). Czy nazwy żeńskie typu architektka, chirurżka i adiunktka są trudne do
# wymówienia? Badanie empiryczne. Język Polski, 37–54. https://doi.org/10.31286/JP.00137

with open('survey-2019-results.txt', mode='r', encoding='utf-8') as source:
    text = source.read()
    # text in the file is copied from the pdf, so I have to clean the unnecessary newlines and headers

text = re.sub(r'(\d+ \| )?Artykuły I ROZPRAWY \| Język Polski \| XCIX 2( \| \d+)?', '', text) # removing the headers
text = re.sub(r'\n', '', text) # removing the newlines
splt = re.split(r'\d+\. ', text) # the results are presented in a numbered list, so I split by the numbers

dict_results = {'word': [], 'no answer': []}
for s in splt[1:]:
    for_regex = re.sub(r'\s*$', '', s) # removing whitespaces at the end of the line
    dict_results['word'].append(re.match(r'\w+', for_regex).group())
    dict_results['no answer'].append(re.search(r'\d+$', for_regex).group())

# if I want to sort them by the number of times participants answered that there's no possible answer:
# df = pd.DataFrame(dict_results)
# print(df.sort_values(by='no answer', ascending=False))

out_list = dict_results['word']
experiment_words = ['ftyzjatra', 'ekspert', 'elekt', 'pediatra', 'chirurg', 'petent', 'architekt', 'foniatra',
                    'dramaturg', 'prefekt', 'prezydent', 'adiunkt', 'metalurg', 'lump', 'psychiatra', 'subiekt',
                    'herszt', 'geriatra', 'demiurg', 'geometra']
# those words are from the 2022 paper, I put them here manually because there was a list in the pdf that didn't
# require parsing but did require changing forms and I couldn't have done that automatically

out_list = list(set(out_list + experiment_words))
print(len(out_list))

with open('profession-nouns.txt', mode='w', encoding='utf-8') as output:
    output.writelines(line + '\n' for line in out_list)
