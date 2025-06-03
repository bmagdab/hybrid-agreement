from tqdm import tqdm
import pandas as pd
from utils import *
from get_info import get_info


def main():
    noun_forms = pd.read_csv('noun_forms.csv')
    form_list = noun_forms.form.values

    for file in tqdm(filelist):
        file = read_conllu(file)
        found_words = []

        for sentence in file:
            for word in sentence['words']:
                if ((word['form'] in form_list and
                     compare_morph_descr(word, noun_forms)) or
                        'depr' in word['morph_descr']):
                    found = get_info(word, sentence, noun_forms)
                    found_words.append(found)

        # write_json(found_words)


main()
