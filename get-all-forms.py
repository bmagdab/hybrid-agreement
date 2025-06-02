import morfeusz2
morf = morfeusz2.Morfeusz()

# reading lists of nouns
with open('profession-nouns.txt', mode='r', encoding='utf-8') as professions_file:
    professions = professions_file.read()
    professions = professions.split('\n')
with open('socially-gendered-nouns.txt', mode='r', encoding='utf-8') as gendered_file:
    gendered = gendered_file.read()
    gendered = gendered.split('\n')

for word in professions+gendered:
    print(word)
    of_interest = []
    for form in morf.generate(word):
        print(form)
    #     if 'depr' not in form[2] and 'brev' not in form[2]:
    #         of_interest.append(form)
    # print(word + ': ' + str(len(of_interest)))
