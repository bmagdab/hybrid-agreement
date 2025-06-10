import json
import pandas as pd
import regex as re
import os


starting_number = 0
json_path = 'occurrences\\'
files = [f'NKJP_300M_{x:03d}' for x in range(starting_number, 191)]
# files = ['NKJP_1M']

# a dictionary of social genders associated with each lexeme in the list of socially gendered nouns
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
    """
    reads the file into a list of dictionaries, where each dictionary corresponds to an occurrence of a word found in
    the corpus with its head and dependencies
    :param file_name: name of the file to be read, without the .json extension
    :return: list of words as dictionaries
    """
    with open(json_path + file_name + '.json', mode='r', encoding='utf-8') as source:
        occurrence_list = json.load(source)
    return occurrence_list


def get_source_info(occurrence):
    """
    for a given occurrence of the word finds the information about the word (and not any of its dependencies!), which is
    the source of agreement, and information about where the word was found
    :param occurrence: a dictionary of information about the found word
    :return: a dictionary of information about the word, but restructured :)
    """
    if occurrence['category'] == 'profession':
        # if the noun refers to a profession, it's commonly used for men so the alternative gender is feminine
        other_gender = 'f'
    elif occurrence['category'] == 'depreciative':
        # if the noun is in the depreciative form, it's marked as not m1 because of its shape,
        # but "semantically" it's m1
        other_gender = 'm1'
    else:
        # for the socially gendered nouns it depends on the specific lexeme, so the information is looked up in the
        # dedicated dictionary
        other_gender = gendered_dict[occurrence['lexeme']]

    # if the noun is in plural and the hybrid agreement is between feminine and neuter, the occurrence is excluded
    # because the agreeing word has the same form for plural feminine and plural neuter
    if (re.search(r':pl\b', occurrence['morph_descr']) and
            re.search(r':n\b', occurrence['morph_descr']) and
            other_gender == 'f'):
        return False

    if not re.search(r'subst|depr', occurrence['morph_descr']):
        return False

    info = {
        'file_id': occurrence['file_name'],
        'sentence_id': occurrence['sent_id'],
        'sentence': occurrence['sent'],
        'source_cat': occurrence['category'],
        'source_form': occurrence['form'],
        'source_lexeme': occurrence['lexeme'],
        'source_morph_descr': occurrence['morph_descr'],
        'source_gram_gender': re.search(r':[mnf]\d?\b', occurrence['morph_descr']).group()[1:],
        'source_other_gender': other_gender
    }
    return info


def get_target_info(target, info):
    """
    finds information about the given target of agreement
    :param target: dictionary of information about the target of agreement
    :param info: dictionary of information about the source of agreement
    """
    if isinstance(target, list):
        gender = re.search(r':[mnf]\d?\b', target[1]).group()[1:]
        info['target_form'] = target[0]
        info['target_morph_descr'] = target[1]
        info['target_gender'] = gender
        info['type_of_agreement'] = 'predicative'
    else:
        if not re.search(r':[mnf]\d?\b', target['morph_descr']):
            return None
        info['target_form'] = target['form']
        info['target_morph_descr'] = target['morph_descr']
        info['target_gender'] = re.search(r':[mnf]\d?\b', target['morph_descr']).group()[1:]
        info['type_of_agreement'] = 'relpron' if len(target) == 2 else 'attributive'

    # all the information found for an occurrence of agreement is added to the dictionary that will be turned into
    # a DataFrame
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


# iterated through the .json files and saves the occurrences of agreement
for file in files:
    occurrences = file_into_dict(file)  # list of words found in the corpus with the words that agree gender with them
    out_dict = {'file_id': [],
                'sentence_id': [],
                'sentence': [],
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

        # there is predicative agreement only if...
        if (entry['head'] != ['', '', ''] and                               # the word has a dependency head
                re.search(r'praet|pact|ppas', entry['head'][1]) and  # the head is a verb inflected for gender
                re.search(r':nom', entry['morph_descr']) and         # the word is in nominative case
                entry['head'][2] == 'nsubj'):                               # the word is the subject
            get_target_info(entry['head'], source_info)

        # iterates through the dependents, but saves them only if they are adjectives (attributive agreement)
        for dep in entry['dependents']:
            if 'adj:' in dep['morph_descr']:
                get_target_info(dep, source_info)

        # iterates through the relative pronouns that refer to the word, saves all of them
        for relpron in entry['rel_prons']:
            get_target_info(relpron, source_info)

    write_csv(file, out_dict)
