from tqdm import tqdm


def main():
    form_list = get_forms()

    for file in tqdm(filelist):
        file = read_conllu(file)
        found_words = []

        for sentence in file:
            for word in sentence:
                if word in form_list or word.description.contains('depr'):
                    found = get_info(word)
                    found_words.append(found)

        write_json(found_words)

