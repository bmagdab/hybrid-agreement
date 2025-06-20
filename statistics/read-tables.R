library(dplyr)
library(ggplot2)
library(stringr)

# reading data
path = "C:/Users/magda/moje/hybrid-agreement-corpus/agreement-occurrences"
numbers <- sprintf("%03d", 0:190)
filenames <- paste0("NKJP_300M_", numbers, ".csv")
filepaths <- file.path(path, filenames)

data <- lapply(filepaths, read.csv) %>% bind_rows()

# summaries
data %>% 
  group_by(source_cat, type_of_agreement) %>% 
  summarise(prop = sum(source_other_gender == target_gender)/n())

data %>% 
  group_by(type_of_agreement) %>% 
  summarise(dist = mean(abs(distance)))

# filtering profession nouns
data %>% 
  filter(source_cat == 'profession') %>% 
  filter(target_gender == 'f') -> prof

prof %>% 
  mutate(source_case = str_extract(source_morph_descr, 'nom|gen|acc|dat|loc|inst|voc'),
         target_case = str_extract(target_morph_descr, 'nom|gen|acc|dat|loc|inst|voc')) -> prof

prof %>% 
  filter((source_case != target_case) & !(is.na(target_case))) -> what

# filtering gendered nouns
data %>% filter(source_cat == 'gendered') -> gend
gend %>% 
  group_by(type_of_agreement) %>% 
  summarise(
    condition = sum(source_other_gender == target_gender),
    total = n(),
    prop = condition/total
    )

# filtering depreciative forms
data %>% filter(source_cat == 'depreciative') -> depr
depr %>% 
  group_by(type_of_agreement) %>% 
  summarise(
    condition = sum(source_other_gender == target_gender),
    total = n(),
    prop = condition/total
    )
