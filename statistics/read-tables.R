library(dplyr)
library(ggplot2)

path = "C:/Users/magda/moje/hybrid-agreement-corpus/agreement-occurrences"
numbers <- sprintf("%03d", 0:190)
filenames <- paste0("NKJP_300M_", numbers, ".csv")
filepaths <- file.path(path, filenames)

data <- lapply(filepaths, read.csv) %>% bind_rows()

data %>% 
  group_by(source_cat, type_of_agreement) %>% 
  summarise(prop = sum(source_other_gender == target_gender)/n())

data %>% 
  group_by(type_of_agreement) %>% 
  summarise(dist = mean(abs(distance)))

data %>% filter(source_cat == 'gendered') -> gend
gend %>% 
  group_by(type_of_agreement) %>% 
  summarise(
    condition = sum(source_other_gender == target_gender),
    total = n(),
    prop = condition/total
    )

data %>% filter(source_cat == 'depreciative') -> depr
depr %>% 
  group_by(type_of_agreement) %>% 
  summarise(
    condition = sum(source_other_gender == target_gender),
    total = n(),
    prop = condition/total
    )
