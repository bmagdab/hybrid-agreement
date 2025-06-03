import regex as re
import morfeusz2
morf = morfeusz2.Morfeusz()


def get_info(word, sentence, nouns_table):
    # finds the lexical form of the noun
    if word['form'] in nouns_table.form.values:
        lexeme = nouns_table[nouns_table.form == word['form']].lexeme.values[0]
        # in the table with listed nouns
    else:
        lexeme = re.match(r'\w+', morf.analyse(word['form'])[0][2][1]).group()
        # or using the morphological analyser Morfeusz if it's a depreciative form

    # finds the category from the table of listed nouns or from the morphological description
    if word['form'] in nouns_table.form.values:
        category = nouns_table[nouns_table.form == word['form']].category.values[0]
    elif 'depr' in word['morph_descr']:
        category = 'depreciative'
    else:
        category = ''
        print(f"Can't find category of the word {word['form']} from sentence {sentence['id']} in file {sentence['file']}.")

    # iterates through the words in the sentence to find:
    # the dependency head of the word,
    # its dependencies and the relative pronouns,
    # its relative pronouns
    head = []
    dependents = []
    relprons = []

    for other_word in sentence['words']:
        if other_word['id'] == word['head']:
            head = [other_word['form'], other_word['morph_descr']]

        # looks for the :relcl relation subtype
        elif other_word['head'] == word['id'] and ':relcl' in other_word['label']:
            # the relative pronoun is attached to the main predicate of the relative clause, so we iterate again
            for another_word in sentence['words']:
                # the relative pronoun is marked with PronType=Rel in the FEATS column in conllu
                if another_word['head'] == other_word['id'] and 'PronType=Rel' in another_word['feats']:
                    relprons.append({'form': another_word['form'],
                                     'morph_descr': another_word['morph_descr']})

        elif other_word['head'] == word['id']:
            dependents.append({'form': other_word['form'],
                               'relation': other_word['label'],
                               'morph_descr': other_word['morph_descr']})
    if not head:
        head = ['', '']     # there may be no head above the noun

    saved_word = {'form': word['form'],
                  'lexeme': lexeme,
                  'file_name': sentence['file'],
                  'sent_id': sentence['id'],
                  'morph_descr': word['morph_descr'],
                  'category': category,
                  'head': head,
                  'dependents': dependents,
                  'rel_prons': relprons}
    return saved_word
