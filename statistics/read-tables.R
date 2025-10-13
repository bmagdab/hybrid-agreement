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

# dont do this!
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

# a plot but not really what i wanted
data %>% 
  filter((source_cat != 'profession') | (target_gender == 'f')) %>% 
  group_by(source_cat) %>% 
  count(type_of_agreement) %>% 
  mutate(percent = n / sum(n)) -> for_plot

ggplot(for_plot) + 
  geom_col(aes(x = source_cat, 
               y = percent, 
               fill = type_of_agreement))

# this plot is weird, so im taking it out for the moment
ggplot(data %>% 
         filter(source_cat != "profession") %>% 
         group_by(type_of_agreement) %>% 
         mutate(prop = sum(semantic_agr)/n())) + 
  geom_col(aes(x = type_of_agreement,
               y = prop,
               fill = source_cat))

# i talk about this in the discussion so for future reference:
data %>% filter(source_cat == "profession") %>% group_by(source_lexeme) %>% summarise(n = n(), prop = sum(semantic_agr)/n()) %>% filter(prop == 0) %>% summary(n)

# i need to see what happens if i remove the distance outliers

data %>%
  filter(
    distance >= quantile(distance, 0.25) - 1.5 * IQR(distance),
    distance <= quantile(distance, 0.75) + 1.5 * IQR(distance)
  ) -> dist_filt

summary(dist_filt)

forward.diff <- matrix(c(2/3, -1/3, -1/3, 1/3, 1/3, -2/3), ncol=2)
dist_filt$type_of_agreement <- as.factor(dist_filt$type_of_agreement)
contrasts(dist_filt$type_of_agreement) <- forward.diff
glm(semantic_agr ~ type_of_agreement,
    family = binomial(link = "logit"), data = dist_filt) -> dist_model

summary(dist_model)
# GOOD BUT I DONT HAVE TIME FOR THIS

# wait i also want a plot of semantic agreement with predicates depending on the distance
data %>% 
  filter(
    distance >= quantile(distance, 0.25) - 1.5 * IQR(distance),
    distance <= quantile(distance, 0.75) + 1.5 * IQR(distance)
    ) %>% 
  filter(type_of_agreement == "predicative") %>% 
  group_by(distance) %>% 
  summarise(mean(semantic_agr))
