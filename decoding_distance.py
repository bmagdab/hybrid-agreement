from check_agreement import file_into_dict
import regex as re
from utils import write_json

starting_number = 0
json_path = 'occurrences\\'
files = [f'NKJP_300M_{x:03d}' for x in range(starting_number, 191)]
# files = ['NKJP_1M']


def decode(target, occurrence):
    """
    takes distance coded as a difference and returns ordering and actual distance
    :param target: dictionary with information about target of agreeement
    :param occurrence: dictionary with information about occurrence of the word of interest
    :return: two integers: target_first, distance; target_first is boolean and distance is an absolute value
    """
    if 'target_first' in target.keys():
        return target['target_first'], target['distance']
    distance = abs(target['distance'])
    target_first = None

    # it doesn't matter if it's a punctuation mark, an abbreviation or a parsing mistake, it will be filtered out anyway
    if (('relation' in target.keys() and target['relation'] == 'punct') or
            not re.search(r'\w', target['form']) or
            target['morph_descr'] in ['interp', 'emo'] or
            (occurrence['sent_id'] == 9522021 and occurrence['file_name'] == 'NKJP_300M_095') or    # is unnecessary and breaks my code
            re.search(r'brev', target['morph_descr'])):
        target_first = 0
        return target_first, distance

    if target['distance'] > 0:
        target_first = 0
    elif target['distance'] < 0:
        target_first = 1
    else:
        list_of_words = re.findall(r'\w+', occurrence['sent'])
        list_of_words = [word.lower() for word in list_of_words]
        for i, word in enumerate(list_of_words):
            if word == occurrence['form'].lower():
                if i > 0 and list_of_words[i-1] == target['form'].lower():
                    target_first = 1
                    break
                elif i < len(list_of_words) - 1 and list_of_words[i+1] == target['form'].lower():
                    target_first = 0
                    break
        if not isinstance(target_first, int):
            raise Exception(f"""Ordering of target and source of agreement not found!
            file: {occurrence['file_name']}
            sentence id: {occurrence['sent_id']}
            source: {occurrence['form']}
            target: {target['form']}""")
    return target_first, distance


# for file in files:
#     occurrences = file_into_dict(file)
#     for occ in occurrences:
#         if occ['head'] != {}:
#             targ_first, dist = decode(occ['head'], occ)
#             occ['head']['distance'] = dist
#             occ['head']['target_first'] = targ_first
#         for dep in occ['dependents']:
#             targ_first, dist = decode(dep, occ)
#             dep['distance'] = dist
#             dep['target_first'] = targ_first
#         for relpron in occ['rel_prons']:
#             targ_first, dist = decode(relpron, occ)
#             relpron['distance'] = dist
#             relpron['target_first'] = targ_first
#     write_json(occurrences, file)
