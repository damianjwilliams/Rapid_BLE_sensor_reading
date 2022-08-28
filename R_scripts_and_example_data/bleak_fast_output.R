library (tidyverse)
library (scales)
library(rstatix)
library(splitstackshape)

f_subtract = function(x) {
  x - x[1]
}


#Folder_name <- "/Users/damianwilliams/Desktop/fast_advertising"
Folder_name <- "C:/Users/Damian/Desktop/fast_advertising"
setwd(Folder_name)

file_list <-
  list.files(
    path = Folder_name,
    recursive = F,
    full.names = T,
    include.dirs = FALSE,
    pattern = "\\.txt$"
  )

data_df <- file_list %>%
  set_names(nm = (basename(.) %>%
                    tools::file_path_sans_ext())) %>%
  map_df(read_tsv,
         col_names = F,
         .id = "File.name")

colnames(data_df) <-
  c("Recording_type",
    "Recording_number",
    "Computer_time_ms",
    "ESP32_time_ms")

# data_df %>%
#   dplyr::group_by(Recording_number, Recording_type) %>%
#   dplyr::summarise(n = dplyr::n(), .groups = "drop") %>%
#   dplyr::filter(n > 1L) 

data_df_wide <- data_df %>%
  pivot_wider(
    names_from = Recording_type,
    values_from = c("Computer_time_ms", "ESP32_time_ms"),
    names_sep = ".") %>%
  drop_na()

data_df_interval <- data_df_wide


#Subtract first time point
data_df_wide <- data_df_wide %>%
mutate(across(2:ncol(.), f_subtract))

#reorganize to long format
reorganised <- data_df_wide %>%
  pivot_longer(-Recording_number) %>%
  cSplit("name", ".")%>%
  pivot_wider(names_from = name_1)

#Plot read time against transmitted time
ggplot(reorganised, aes(x = Computer_time_ms, y = ESP32_time_ms, color = name_2)) +
  geom_point(alpha = 0.5) +
  geom_abline(intercept = 0, slope = 1) +
  theme_classic()+
  theme(legend.title=element_blank())+
  labs(y = "ESP32 broadcast time (ms)",
       x = "Python read time (ms)",
       subtitle="The first 1000 successfully read data packets are plotted ",
       title = "Time data transmitted vs. time data read",
        caption = "Data packets that are transmitted and read with very little latency fall close to the black line" )
  ggsave("trans vs rec plot.png",
         width = 8,
         height = 6,
         units = "in")

#Interval 
f_interval = function(x) {
  x - lag(x,default = x[1])
}


data_df_interval  <- data_df_interval %>%
  #mutate(across(c("Computer_time_ms","ESP32_time_ms"), f_subtract))%>%
  mutate(across(2:ncol(.), f_interval))%>%
  pivot_longer(-Recording_number)%>%
  filter(grepl("ESP32",name))%>%
  mutate(name = gsub("ESP32_time_ms.","",name))%>%
  mutate(name = gsub("_method","",name))

ggplot(data_df_interval, aes(x = name, y = value)) +
  geom_jitter(alpha = 0.5) +
  scale_y_continuous(breaks = pretty_breaks(), trans = 'log2') +
  theme_classic()+
  theme(axis.text.x = element_text(angle = 45))

#Remov outliers
outliers <- data_df_interval %>%
  identify_outliers(value)
data_df_interval <- anti_join(data_df_interval, outliers)

#Different methods to plot interval

data_df_interval%>%
  #filter(grepl("ESP",name))%>%
  ggplot(., aes(x = Recording_number, y = value)) +
  geom_point(aes(color=name)) +
  theme_classic()

data_df_interval%>%
  #filter(grepl("ESP",name))%>%
  ggplot(., aes(x = name, y = value)) +
  geom_jitter(aes(color=name),alpha=0.2) +
  theme_classic()

data_df_interval%>%
  #filter(grepl("ESP",name))%>%
  ggplot(., aes(x = value)) +
  geom_histogram(aes(fill=name)) +
  theme_classic()

data_df_interval%>%
  #filter(grepl("ESP",name))%>%
  ggplot(., aes(x = name, y = value,fill=name)) +
  geom_violin()+
  theme_classic()

#Interval bar chart

new_way <- data_df_interval %>%
  mutate(value = floor(value / 5) * 5)%>%
  filter(value >0)%>%
  mutate(value = as_factor(value))

data_df_interval%>%
  group_by(name)%>%
  summarise(n=mean(value))
  
ggplot(new_way, aes(value,fill=name)) +
  geom_bar(position = position_dodge2(preserve = "single"))+
  theme_classic()+
  theme(legend.title=element_blank())+
  labs(y = "Number of readings",
       x = "Interval between advertisement timestamps (ms)",
       subtitle="The first 1000 successfully read advertisements are plotted ",
       title = "Interval between readings (ms)",
       caption = "" )
ggsave("interval.png",
       width = 8,
       height = 6,
       units = "in")


