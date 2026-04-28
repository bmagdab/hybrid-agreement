from tqdm import tqdm
import pandas as pd
import regex as re
from utils import *     # read_conllu, compare_morph_descr, write_json and some variables
from get_info import count_distance
from decoding_distance import decode
import morfeusz2
morf = morfeusz2.Morfeusz()

# all of this is basically copied from check_agreement.py, but I changed a few things; they are marked *NEW*

# list of symbols marking the verb flexemes that agree with the subject in gender
verb_like = ['praet', 'pact', 'ppas']
starting_number = 0
json_path = 'occurrences\\'
# files = [f'NKJP_300M_{x:03d}' for x in range(starting_number, 191)]
# files = ['NKJP_1M']
files = ['NKJP_300M_072']


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
    else:
        print('BAD')    # *NEW* I'm only looking at occurrences with profession nouns

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
        'type_of_text': occurrence['type_of_text'],
        'source_cat': occurrence['category'],
        'source_form': occurrence['form'],
        'source_lexeme': occurrence['lexeme'],
        'source_morph_descr': occurrence['morph_descr'],
        'source_gram_gender': re.search(r':[mnf]\d?\b', occurrence['morph_descr']).group()[1:],
        'source_other_gender': other_gender
    }
    return info


def get_target_info(target, info, occurrence):
    """
    finds information about the given target of agreement
    :param target: dictionary of information about the target of agreement
    :param info: dictionary of information about the source of agreement
    :param occurrence: dictionary with information about occurrence of the word of interest
    """
    gender = re.search(r':[mnf]\d?\b', target['morph_descr'])
    if not gender:
        return None
    else:
        gender = gender.group()[1:]

    if 'relation' not in target.keys():
        agr_type = 'relpron'
    elif 'adj:' in target['morph_descr']:
        agr_type = 'attributive'
    else:
        agr_type = 'predicative'

    if 'target_first' not in target.keys():
        targ_first, dist = decode(target, occurrence)
        target['distance'] = dist
        target['target_first'] = targ_first

    info['target_form'] = target['form']
    info['target_morph_descr'] = target['morph_descr']
    info['target_gender'] = gender
    info['type_of_agreement'] = agr_type
    info['distance'] = target['distance']
    info['target_first'] = target['target_first']

    # all the information found for an occurrence of agreement is added to the dictionary that will be turned into
    # a DataFrame
    for key in info.keys():
        out_dict[key].append(info[key])

    out_dict['apposition'].append(apposition)
    out_dict['appos_morph_descr'].append(appos_morph_descr)


def write_csv(file_name, out_dict):
    # create a folder called "agreement-occurrences" if needed
    out_directory = 'agreement-occurrences'
    if not os.path.isdir(out_directory):
        os.mkdir(out_directory)

    out_path = out_directory + '\\' + file_name + '.csv'
    df = pd.DataFrame(out_dict)
    df.to_csv(out_path, index=False)


def get_info(word, sentence, nouns_table):
    """
    for a given word in a sentence finds the information later required to check gender agreement with other words
    :param word: a dictionary with information corresponding to the word of interest
    :param sentence: a dictionary with information about the sentence, where the word was found
    :param nouns_table: a pandas DataFrame with all forms of words that are searched in the corpus
    :return: a dictionary with the required information about the word
    """
    # finds the lexical form of the noun
    if word['form'] in nouns_table.form.values:
        # in the table with listed nouns
        lexeme = nouns_table[nouns_table.form == word['form']].lexeme.values[0]
    else:   # if it's not in the table it should be a depreciative form
        lexeme = ''
        for analysis in morf.analyse(word['form']):
            if re.search(r'depr|subst', analysis[2][2]) and analysis[2][3] != ['nazwisko']:
                # Morfeusz gives a number of analyses, we are looking for the analyses of nouns (not e.g. a verb with
                # the same form) and we want to exclude surnames
                lexeme = re.match(r'\w+', analysis[2][1]).group()
        if not lexeme:
            lexeme = word['form']
            # return False
            # this is what I did previously, but it doesn't work when I use the function for better-profession-nouns.py

    # finds the category of the noun from the table of listed nouns or from the morphological description
    if word['form'] in nouns_table.form.values:
        category = nouns_table[nouns_table.form == word['form']].category.values[0]
    elif 'depr' in word['morph_descr']:
        category = 'depreciative'
    else:
        category = ''
        # print(f"Can't find category of the word {word['form']} from sentence {sentence['id']} in file {sentence['file']}.")

    # iterates through the words in the sentence to find:
    # the dependency head of the word,
    # the words dependencies,
    # its relative pronouns
    head = []
    dependents = []
    relprons = []

    for other_word in sentence['words']:
        if other_word['id'] == word['head']:
            # head = [other_word['form'], other_word['morph_descr'], word['label']]
            head = {
                'form': other_word['form'],
                'relation': word['label'],
                'morph_descr': other_word['morph_descr'],
                'distance': count_distance(word, other_word, sentence),
                'id': other_word['id']
            }

        # for the relative pronouns looks for the :relcl relation subtype
        elif other_word['head'] == word['id'] and ':relcl' in other_word['label']:
            # the relative pronoun is attached to the main predicate of the relative clause, so we iterate again
            for another_word in sentence['words']:
                # the relative pronoun is marked with PronType=Rel in the FEATS column in conllu
                if another_word['head'] == other_word['id'] and 'PronType=Rel' in another_word['feats']:
                    relprons.append({'form': another_word['form'],
                                     'morph_descr': another_word['morph_descr'],
                                     'distance': count_distance(word, another_word, sentence),
                                     'id': another_word['id']})

        elif other_word['head'] == word['id']:
            dependents.append({'form': other_word['form'],
                               'relation': other_word['label'],
                               'morph_descr': other_word['morph_descr'],
                               'distance': count_distance(word, other_word, sentence),
                               'id': other_word['id']})
    if not head:
        head = {}    # there may be no head above the noun

    saved_word = {'form': word['form'],
                  'lexeme': lexeme,
                  'file_name': sentence['file'],
                  'sent_id': sentence['id'],
                  'sent': sentence['sentence'],
                  'type_of_text': sentence['type'],
                  'morph_descr': word['morph_descr'],
                  'category': category,
                  'head': head,
                  'dependents': dependents,
                  'rel_prons': relprons}
    return saved_word


noun_forms = pd.read_csv('noun_forms.csv')
for file in tqdm(files):
    occurrences = file_into_dict(file)  # list of words found in the corpus with the words that agree gender with them
    conllu = read_conllu(file)
    out_dict = {'file_id': [],
                'sentence_id': [],
                'sentence': [],
                'type_of_text': [],
                'source_cat': [],               # gendered, profession or depreciative
                'source_form': [],
                'source_lexeme': [],
                'source_morph_descr': [],
                'source_gram_gender': [],
                'source_other_gender': [],
                'target_form': [],
                'target_morph_descr': [],
                'target_gender': [],
                'type_of_agreement': [],        # attributive, predicative or relative pronoun
                'distance': [],
                'target_first': [],
                'apposition': [],               # form of the apposition, if there is one
                'appos_morph_descr': []
                }

    for entry in occurrences:
        if entry['category'] != 'profession':   # *NEW* I'm only looking at profession nouns now
            continue
        if not get_source_info(entry):
            continue

        apposition = False

        source_info = get_source_info(entry)
        # *NEW* searching for the sentence again if the head is an apposition, then I want different information for the
        # head, dependents and relprons
        if entry['head'] != {} and entry['head']['relation'] == 'appos':
            # print('looking for ' + str(entry['sent_id']))
            try:
                sentence = conllu[entry['sent_id']-1-100000*int(file[-3:])]
            except IndexError:
                # file NKJP_300M_072 doesn't open fully, I will try to continue without finishing it for now
                print(f'conllu {file} has {len(conllu)} sentences, but we are looking for one indexed {entry['sent_id']-1-100000*int(file[-3:])}')
                continue
            words = sentence['words']
            for word in words:
                if (word['form'] == entry['form']   # is word the source of agreement?
                        and word['morph_descr'] == entry['morph_descr']
                        and words[word['head']-1]['form'] == entry['head']['form']
                        and words[word['head']-1]['morph_descr'] == entry['head']['morph_descr']):
                    # if it is, I'm saving it and its head (the apposition) for easier reference
                    appos = words[word['head']-1]
                    source = word

                    # I'm saving the information about the apposition
                    appos_info = get_info(words[word['head']-1], sentence, noun_forms)
                    # in this information I am interested in the head and dependents of that apposition, which I will
                    # now treat as the head and dependents of my source of agreement
                    entry['head'] = appos_info['head']
                    entry['dependents'] = appos_info['dependents']
                    entry['rel_prons'] = appos_info['rel_prons']

                    if entry['head'] == {}:
                        to_redistance = entry['dependents'] + entry['rel_prons']
                    else:
                        entry['head']['id'] = appos['head']
                        to_redistance = [entry['head']] + entry['dependents'] + entry['rel_prons']

                    for target in to_redistance:
                        target['distance'] = count_distance(source, target, sentence)

                    apposition = appos['form']
                    appos_morph_descr = appos['morph_descr']
                    break

        if not apposition:
            for target in entry['dependents']:
                if target['relation'] == 'appos':
                    apposition = target['form']
                    appos_morph_descr = target['morph_descr']
                    break
        if not apposition:
            apposition = ''
            appos_morph_descr = ''

        # there is predicative agreement only if...
        if (entry['head'] != {} and                                                     # the word has a dependency head
                re.search(r'praet|pact|ppas', entry['head']['morph_descr']) and  # the head is a verb inflected for gender
                re.search(r':nom', entry['morph_descr']) and                     # the word is in nominative case
                entry['head']['relation'] in ['nsubj', 'appos']):                       # *NEW* the word is the subject OR an apposition
            get_target_info(entry['head'], source_info, entry)

        # iterates through the dependents, but saves them only if they are adjectives (attributive agreement)
        for dep in entry['dependents']:
            if 'adj:' in dep['morph_descr']:
                get_target_info(dep, source_info, entry)

        # iterates through the relative pronouns that refer to the word, saves all of them
        for relpron in entry['rel_prons']:
            get_target_info(relpron, source_info, entry)

        dict_check = len(out_dict['file_id'])
        for k in out_dict.keys():
            if len(out_dict[k]) != dict_check:
                raise Exception(f'column {k} has length {len(out_dict[k])} and not {dict_check}')

    write_csv('new-profession-nouns\\' + file, out_dict)
