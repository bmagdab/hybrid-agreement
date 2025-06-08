from tqdm import tqdm
import pandas as pd
from utils import *
from get_info import get_info
from datetime import datetime


def main():
    noun_forms = pd.read_csv('noun_forms.csv')
    form_list = noun_forms.form.values

    for file in filelist:
        print(f'{datetime.now()} -- processing {file}.conllu')
        conllu = read_conllu(file)
        found_words = []

        for sentence in tqdm(conllu):
            for word in sentence['words']:
                if ((word['form'] in form_list and
                     compare_morph_descr(word, noun_forms)) or
                        'depr' in word['morph_descr']):
                    found = get_info(word, sentence, noun_forms)
                    if found:
                        found_words.append(found)
        print(f'{file}.conllu done, writing {file}.json\n')
        write_json(found_words, file)


main()
