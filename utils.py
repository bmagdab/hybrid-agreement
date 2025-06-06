import regex as re
import os
import json

starting_number = 0
path = 'NKJP\\'
# filelist = [f'NKJP_300M_{x:03d}' for x in range(starting_number, 191)]
filelist = ['NKJP_1M']


def read_conllu(file):
    # reading the conllu file
    with open(path + file + '.conllu', mode='r', encoding='utf-8') as nkjp:
        nkjp_lines = nkjp.read()

    # the output will be a list of dictionaries, where each dictionary corresponds to a sentence
    corpus = []
    sentences = nkjp_lines.split('\n\n')

    for sent in sentences:
        lines = sent.split('\n')

        # for each sentence I want the ID of the sentence in the file, name of the file and list of words in th sentence
        sent_dict = {'id': 0,
                     'file': file,
                     'sentence': '',
                     'words': []}

        for line in lines:
            # getting the ID of the sentence in the file
            sent_id = re.findall(r'# id = (\d+)', line)
            if sent_id:
                sent_dict['id'] = int(sent_id[0])

            # getting the text of the sentence
            sent_text = re.findall(r'# sent = (.*)', line)
            if sent_text:
                sent_dict['sentence'] = sent_text[0]

            # saving each word as a dictionary of all the information I need
            if re.match(r'\d', line):
                word = line.split('\t')
                sent_dict['words'].append({'id': int(word[0]),
                                           'form': word[1] if 'depr' in word[4] else word[1].lower(),
                                           'POS': word[3],
                                           'morph_descr': word[4],
                                           'feats': word[5],
                                           'head': int(word[6]),
                                           'label': word[7]})
        corpus.append(sent_dict)
    return corpus


def compare_morph_descr(found_word, reference_table):
    matching_entries = reference_table[reference_table.form == found_word['form'].lower()].morph_descr.values
    same = False
    for entry in matching_entries:
        ref_descr_str = entry
        found_descr = [feature.split('.') for feature in found_word['morph_descr'].split(':')]
        ref_descr = [feature.split('.') for feature in ref_descr_str.split(':')]
        same = True
        for i, feature in enumerate(found_descr):
            for value in feature:
                if value not in ref_descr[i]:
                    same = False
                    break
            if not same:
                break
    return same


def write_json(occurences, file_name):
    # create a folder called "occurrences" if needed
    out_directory = 'occurrences'
    if not os.path.isdir(out_directory):
        os.mkdir(out_directory)

    out_path = out_directory + '\\' + file_name + '.json'

    with open(out_path, mode='w', encoding='utf-8') as out_file:
        json.dump(occurences, out_file, indent=2, ensure_ascii=False)
