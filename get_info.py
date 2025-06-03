def get_info(word, sentence, nouns_table):
    # get lexeme
    lexeme = nouns_table[nouns_table.form == word['form']].lexeme.values[0]

    # get category from noun_list or from morph description
    if word['form'] in nouns_table.form.values:
        category = nouns_table[nouns_table.form == word['form']].category.values[0]
    elif 'depr' in word['morph_descr']:
        category = 'depreciative'
    else:
        category = ''
        print(f"Can't find category of the word {word['form']} from sentence {sentence['id']} in file {sentence['file']}.")

    # iter by words in sentence to find:
    #   head
    #   dependents
    #   relprons
    head = []
    dependents = []
    relprons = []
    for other_word in sentence['words']:
        if other_word['id'] == word['head']:
            head = [other_word['form'], other_word['morph_descr']]
        elif other_word['head'] == word['id'] and ':relcl' in other_word['label']:
            for another_word in sentence['words']:
                if another_word['head'] == other_word['id'] and 'PronType=Rel' in another_word['feats']:
                    relprons.append({'form': another_word['form'],
                                     'morph_descr': another_word['morph_descr']})
        elif other_word['head'] == word['id']:
            dependents.append({'form': other_word['form'],
                               'relation': other_word['label'],
                               'morph_descr': other_word['morph_descr']})
    if not head:
        head = ['', '']

    saved_word = {'form': word['form'].lower(),
                  'lexeme': lexeme,
                  'file_name': sentence['file'],
                  'sent_id': sentence['id'],
                  'morph_descr': word['morph_descr'],
                  'category': category,
                  'head': head,
                  'dependents': dependents,
                  'rel_prons': relprons}
    return saved_word
