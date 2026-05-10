import pandas as pd


with open('depreciatives-experiment.xlsx', mode='rb') as excel:
    items = pd.read_excel(excel, sheet_name='items')
    controls = pd.read_excel(excel, sheet_name='controls')
    distractors = pd.read_excel(excel, sheet_name='distractors')

# adding a column assigning the items into groups
gr_numbers = [1, 2, 3, 4, 5, 6]
col_groups = []
for _ in range(6):
    col_groups += 4*gr_numbers
    gr_numbers = [gr_numbers.pop(5)] + gr_numbers
items.insert(len(items.columns), 'group', col_groups)

# adding the group column for the controls
gr_numbers = [7, 8, 8, 7]
controls.insert(len(controls.columns), 'group', 6*gr_numbers)

# adding the group column for the distractors
distractors.insert(len(distractors.columns), 'group', 24*[9])

# merging all the stimuli - ADD THE DISTRACTORS ONCE FINISHED
stimuli = pd.concat([items, controls, distractors])

# converting the dataframe to the json format
json_stimuli = stimuli.to_json(orient='records', force_ascii=False, lines=True)

# removing the quotes around column names
for col in stimuli.columns:
    json_stimuli = json_stimuli.replace(f"\"{col}\"", f"{col}")

# adding comas after each entry
json_stimuli = json_stimuli.replace('}', '},')

# wrapping the stimuli into a js variable
json_stimuli = 'var all_stimuli = [\n' + json_stimuli[:-2] + ']'

# writing the file
with open('stimuli.js', mode='w', encoding='utf-8') as out_stimuli:
    out_stimuli.write(json_stimuli)
