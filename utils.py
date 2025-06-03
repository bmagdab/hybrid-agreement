# for file managing functions mainly
import re

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
                     'words': []}

        for line in lines:
            # getting the ID of the sentence in the file
            sent_id = re.findall(r'# id = (\d+)', line)
            if sent_id:
                sent_dict['id'] = sent_id[0]

            # saving each word as a dictionary of all the information I need
            if re.match(r'\d', line):
                word = line.split('\t')
                sent_dict['words'].append({'id': int(word[0]),
                                           'form': word[1],
                                           'POS': word[3],
                                           'morph_descr': word[4],
                                           'feats': word[5],
                                           'head': int(word[6]),
                                           'label': word[7]})
        corpus.append(sent_dict)
    return corpus


def write_json():
    # create a folder called "occurences" if needed
    pass
