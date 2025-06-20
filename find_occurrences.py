from tqdm import tqdm
import pandas as pd
from utils import *     # read_conllu, compare_morph_descr, write_json and some variables
from get_info import get_info
from datetime import datetime


def main():
    # reading from a file nouns that will be searched in the corpus, the file gives different forms of each noun,
    # their morphological descriptions and category of noun ('profession' noun or a socially gendered noun)
    noun_forms = pd.read_csv('noun_forms.csv')
    form_list = noun_forms.form.values

    for file in filelist:
        print(f'{datetime.now()} -- processing {file}.conllu')
        # the conllu file is read into a list of dictionaries
        conllu = read_conllu(file)
        found_words = []

        for sentence in tqdm(conllu):
            for word in sentence['words']:  # an occurrence of a word is saved...
                if ((word['form'] in form_list and  # if it's in the list of search nouns and the morphological
                     compare_morph_descr(word, noun_forms)) or  # description matches, so it really is the same word
                        'depr' in word['morph_descr']):     # or if it's a depreciative form of a noun
                    found = get_info(word, sentence, noun_forms)
                    if found:
                        found_words.append(found)   # words are saved as dictionaries into a list
        print(f'{file}.conllu done, writing {file}.json\n')
        write_json(found_words, file)   # the list of dictionaries (words) is saved as a .json file


main()
