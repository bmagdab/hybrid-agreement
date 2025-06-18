import regex as re
import morfeusz2
morf = morfeusz2.Morfeusz()


def count_distance(source, target, sentence):
    """
    counts the distance between the source of agreement and target of agreement; distance is measured in words and word
    is understood as a string of (non-punctuation) characters
    :param source: dictionary corresponding to the word that is the source of agreement
    :param target: dictionary corresponding to the word that is the target of agreement
    :param sentence: dictionary corresponding to the sentence, where the two words were found
    :return: distance between words, can be negative, which means the target of agreement was first
    """
    start = min(source['id'], target['id'])
    end = max(source['id'], target['id'])

    middle_words = []
    for word in sentence['words']:
        if word['id'] in range(start+1, end):   # start+1 because I only want to count intervening words
            middle_words.append(word)

    count = 0
    for word in middle_words:
        if word['POS'] != 'PUNCT':
            count += 1

    if start == target['id']:
        # make the number negative if the target was first
        count = count * -1

    return count


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
            return False    # if nothing is found, the function was run by mistake and we stop it

    # finds the category of the noun from the table of listed nouns or from the morphological description
    if word['form'] in nouns_table.form.values:
        category = nouns_table[nouns_table.form == word['form']].category.values[0]
    elif 'depr' in word['morph_descr']:
        category = 'depreciative'
    else:
        category = ''
        print(f"Can't find category of the word {word['form']} from sentence {sentence['id']} in file {sentence['file']}.")

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
                'distance': count_distance(word, other_word, sentence)
            }

        # for the relative pronouns looks for the :relcl relation subtype
        elif other_word['head'] == word['id'] and ':relcl' in other_word['label']:
            # the relative pronoun is attached to the main predicate of the relative clause, so we iterate again
            for another_word in sentence['words']:
                # the relative pronoun is marked with PronType=Rel in the FEATS column in conllu
                if another_word['head'] == other_word['id'] and 'PronType=Rel' in another_word['feats']:
                    relprons.append({'form': another_word['form'],
                                     'morph_descr': another_word['morph_descr'],
                                     'distance': count_distance(word, another_word, sentence)})

        elif other_word['head'] == word['id']:
            dependents.append({'form': other_word['form'],
                               'relation': other_word['label'],
                               'morph_descr': other_word['morph_descr'],
                               'distance': count_distance(word, other_word, sentence)})
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
