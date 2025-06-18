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

        # for each sentence I want:
        sent_dict = {'id': 0,           # the ID of the sentence in the file
                     'file': file,      # name of the file
                     'sentence': '',    # text of the sentence
                     'type': '',        # type of text
                     'words': []}       # list of words in the sentence

        for line in lines:
            # getting the ID of the sentence in the file
            sent_id = re.findall(r'# id = (\d+)', line)
            if sent_id:
                sent_dict['id'] = int(sent_id[0])

            # getting the text of the sentence
            sent_text = re.findall(r'# sent = (.*)', line)
            if sent_text:
                sent_dict['sentence'] = sent_text[0]

            # getting the type of text
            sent_type = re.findall(r'# type = (.*)', line)
            if sent_type:
                sent_dict['type'] = sent_type[0]

            # saving each word as a dictionary of all the information I need
            if re.match(r'\d', line):
                word = line.split('\t')
                sent_dict['words'].append({'id': int(word[0]),
                                           'form': word[1] if 'depr' in word[4] else word[1].lower(),
                                           # ^ I only want lowercase words, because it later makes it easier to look
                                           # them up anywhere, but if it's a depreciative form, it might be a surname
                                           # and I can tell by the uppercase first letter -- I want to filter out
                                           # the surnames later
                                           'POS': word[3],
                                           'morph_descr': word[4],  # in the Morfeusz convention
                                           'feats': word[5],        # in the UD convention (there's additional info)
                                           'head': int(word[6]),
                                           'label': word[7]})
        corpus.append(sent_dict)
    return corpus


def compare_morph_descr(found_word, reference_table):
    # the morphological description found in the conllu file is split in the following way:
    # 'subst:sg:nom:m1' -> [['subst'], ['sg'], ['nom'], ['m1']]
    found_descr = [feature.split('.') for feature in found_word['morph_descr'].split(':')]

    # looking up all possible morphological descriptions matching the given word form
    matching_entries = reference_table[reference_table.form == found_word['form'].lower()].morph_descr.values

    same = False    # if there are no matching forms, it's not the word I was looking for and it returns False
    for entry in matching_entries:
        ref_descr_str = entry
        # each matching morphological description is split similarly as the one found in the conllu file, but here
        # there can be multiple options for one value of a feature, so it may look like this:
        # 'subst:sg:nom.voc:m1' -> [['subst'], ['sg'], ['nom', 'voc'], ['m1']]
        ref_descr = [feature.split('.') for feature in ref_descr_str.split(':')]
        # the descriptions in the conllu file cannot have multiple options per feature, but they are treated as though
        # they can because it's possible with the descriptions from the reference table and I want to be able to compare
        # them easily in the loop below

        # I assume the reference description matches the found one and if it doesn't, the loop will mark it as not same
        same = True
        for i, feature in enumerate(found_descr):
            # the loop goes through all features in [['subst'], ['sg'], ['nom'], ['m1']]
            for value in feature:
                # for each value in the feature it checks the reference description
                # for example if 'nom' is in ['nom', 'voc']
                if value not in ref_descr[i]:
                    same = False
                    break
                    # if the found value is not in the reference description, then this description doesn't work and
                    # I should check the next one
            if not same:
                break   # to check the next description I have to break out of the second loop
    return same


def write_json(occurences, file_name):
    # create a folder called "occurrences" if needed
    out_directory = 'occurrences'
    if not os.path.isdir(out_directory):
        os.mkdir(out_directory)

    out_path = out_directory + '\\' + file_name + '.json'

    with open(out_path, mode='w', encoding='utf-8') as out_file:
        json.dump(occurences, out_file, indent=2, ensure_ascii=False)
