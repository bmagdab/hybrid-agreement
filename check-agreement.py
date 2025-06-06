import json

import pandas as pd
import regex as re
import os


starting_number = 0
json_path = 'occurrences\\'
# files = [f'NKJP_300M_{x:03d}' for x in range(starting_number, 191)]
files = ['NKJP_1M']
gendered_dict = {
    'babochłop': 'f',
    'babol': 'f',
    'babon': 'f',
    'babsko': 'f',
    'babsztyl': 'f',
    'babus': 'f',
    'chłopaczysko': 'm1',
    'chłopobaba': 'm1',
    'ciota': 'm1',
    'dziewczątko': 'f',
    'dziewczę': 'f',
    'dziewuszysko': 'f',
    'kobieciątko': 'f',
    'kobiecisko': 'f',
    'kobieton': 'f',
    'pacholę': 'm1',
    'pannisko': 'f',
    'pasztet': 'f',
    'wamp': 'f'
}
# list of symbols marking the verb flexemes that agree with the subject in gender
verb_like = ['praet', 'pact', 'ppas']


def file_into_dict(file_name):
    with open(json_path + file_name + '.json', mode='r', encoding='utf-8') as source:
        occurrence_list = json.load(source)
    return occurrence_list


def get_source_info(occurrence):
    if occurrence['category'] == 'profession':
        other_gender = 'f'
    elif occurrence['category'] == 'depreciative':
        other_gender = 'm1'
    else:
        other_gender = gendered_dict[occurrence['lexeme']]

    if (re.search(r':n\b', entry['morph_descr']) and
            re.search(r':pl\b', entry['morph_descr'])) and other_gender == 'f':
        return False

    info = {
        'file_id': occurrence['file_name'],
        'sentence_id': occurrence['sent_id'],
        'source_cat': occurrence['category'],
        'source_form': occurrence['form'],
        'source_lexeme': occurrence['lexeme'],
        'source_morph_descr': occurrence['morph_descr'],
        'source_gram_gender': re.search(r':[mnf]\d?\b', occurrence['morph_descr']).group()[1:],
        'source_other_gender': other_gender
    }
    return info


def get_target_info(target, info):
    if isinstance(target, list):
        gender = re.search(r':[mnf]\d?\b', target[1]).group()[1:]
        info['target_form'] = target[0]
        info['target_morph_descr'] = target[1]
        info['target_gender'] = gender
        info['type_of_agreement'] = 'predicative'
    else:
        info['target_form'] = target['form']
        info['target_morph_descr'] = target['morph_descr']
        info['target_gender'] = re.search(r':[mnf]\d?\b', target['morph_descr']).group()[1:]
        info['type_of_agreement'] = 'relpron' if len(target) == 2 else 'attributive'

    for key in info.keys():
        out_dict[key].append(info[key])


def write_csv(file_name, out_dict):
    # create a folder called "agreement-occurrences" if needed
    out_directory = 'agreement-occurrences'
    if not os.path.isdir(out_directory):
        os.mkdir(out_directory)

    out_path = out_directory + '\\' + file_name + '.csv'
    df = pd.DataFrame(out_dict)
    df.to_csv(out_path, index=False)


for file in files:
    occurrences = file_into_dict(file)
    out_dict = {'file_id': [],
                'sentence_id': [],
                'source_cat': [],               # gendered, profession or depreciative
                'source_form': [],
                'source_lexeme': [],
                'source_morph_descr': [],
                'source_gram_gender': [],
                'source_other_gender': [],
                'target_form': [],
                'target_morph_descr': [],
                'target_gender': [],
                'type_of_agreement': []         # attributive, predicative or relative pronoun
                }
    for entry in occurrences:
        if not get_source_info(entry):
            continue
        source_info = get_source_info(entry)
        if (entry['head'] != ['', ''] and
                re.search(r'praet|pact|ppas', entry['head'][1]) and
                not re.search(r':voc', entry['morph_descr'])):
            get_target_info(entry['head'], source_info)
        for dep in entry['dependents']:
            if 'adj:' in dep['morph_descr']:
                get_target_info(dep, source_info)
        for relpron in entry['rel_prons']:
            get_target_info(relpron, source_info)

    write_csv(file, out_dict)
