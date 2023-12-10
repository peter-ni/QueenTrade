library(readr)
library(ggplot2)
library(tidyverse)
library(dplyr)


white_in_df = read_csv("Desktop/Projects/QueenTrade/QueenTrade/white_df.csv") %>% as.data.frame()
black_in_df = read_csv("Desktop/Projects/QueenTrade/QueenTrade/black_df.csv") %>% as.data.frame()


white_df = white_in_df %>% transmute(MyELO = WhiteElo,
                                     OppELO = BlackElo,
                                     pre_eval = pre_eval,
                                     post_eval = post_eval,
                                     queen_trade_made = queen_trade_made,
                                     first_queen_trade = first_queen_trade,
                                     eval_diff = post_eval - pre_eval,
                                     win = ifelse(result == '1-0', 1, 0),
                                     result = result)


black_df = black_in_df %>% transmute(MyELO = BlackElo,
                                     OppELO = WhiteElo,
                                     pre_eval = pre_eval,
                                     post_eval = post_eval,
                                     queen_trade_made = queen_trade_made,
                                     first_queen_trade = first_queen_trade,
                                     eval_diff = post_eval - pre_eval,
                                     win = ifelse(result == '0-1', 1, 0),
                                     result = result)




# Installing DAGitty

# install.packages('remotes')
# remotes::install_github("jtextor/dagitty/r")
library(dagitty)


win_dag = dagitty('dag{
    MyELO -> pre_eval
    ELODiff -> pre_eval
    MyELO -> queen_trade_made
    ELODiff -> queen_trade_made
    pre_eval -> queen_trade_made
    ELODiff -> win
    MyELO -> win
    ELODiff -> win
    pre_eval -> win
    queen_trade_made -> win
}')


coordinates(win_dag) = list(
  x = c(MyELO = 1, ELODiff = 2, queen_trade_made = 1, pre_eval = 2, win = 1.5),
  y = c(MyELO = 1, ELODiff = 1, queen_trade_made = 2, pre_eval = 2, win = 3)
)

plot(win_dag)
win_set = adjustmentSets(win_dag, exposure = 'queen_trade_made', outcome = 'win')
print(win_set)


imp_dag = dagitty('dag{
    MyELO -> pre_eval
    ELODiff -> pre_eval
    MyELO -> queen_trade_made
    ELODiff -> queen_trade_made
    pre_eval -> queen_trade_made
    MyELO -> improvement
    ELODiff -> improvement
    pre_eval -> improvement
    queen_trade_made -> improvement
}')

coordinates(imp_dag) = list(
  x = c(MyELO = 1, ELODiff = 2, queen_trade_made = 1, pre_eval = 2, improvement = 1.5),
  y = c(MyELO = 1, ELODiff = 1, queen_trade_made = 2, pre_eval = 2, improvement = 3)
)

plot(imp_dag)
imp_set = adjustmentSets(imp_dag, exposure = 'queen_trade_made', outcome = 'improvement')
# ==================



white_subset = white_df %>% 
  mutate(queen_trade_made = ifelse(queen_trade_made, 1, 0),
         ELO_diff = MyELO - OppELO,
         improvement = ifelse(post_eval - pre_eval > 0, 1, 0)) %>% 
  filter(abs(pre_eval) < 10000)


black_subset = black_df %>% 
  mutate(queen_trade_made = ifelse(queen_trade_made, 1, 0),
         ELO_diff = MyELO - OppELO,
         improvement = ifelse(post_eval - pre_eval > 0, 1, 0)) %>% 
  filter(abs(pre_eval) < 10000)

win_lm_white = glm(win ~ queen_trade_made + MyELO + ELO_diff + pre_eval, data = white_subset, family = 'binomial')
improvement_lm_white = glm(improvement ~ queen_trade_made + MyELO + pre_eval, data = white_subset, family = 'binomial')

win_lm_black = glm(win ~ queen_trade_made + MyELO + ELO_diff + pre_eval, data = black_subset, family = 'binomial')
improvement_lm_black = glm(improvement ~ queen_trade_made + MyELO + ELO_diff + pre_eval, data = black_subset, family = 'binomial')


win_white_preds = predict(win_lm_white, newdata = white_subset, type = 'response')
improvement_white_preds = predict(improvement_lm_white, newdata = white_subset, type = 'response')

win_black_preds = predict(win_lm_black, newdata = black_subset, type = 'response')
improvement_black_preds = predict(improvement_lm_black, newdata = black_subset, type = 'response')

library(pROC)
white_win_roc = roc(white_subset$win, win_white_preds)
white_improvement_roc = roc(white_subset$improvement, improvement_white_preds)

black_win_roc = roc(black_subset$win, win_black_preds)
black_improvement_roc = roc(black_subset$improvement, improvement_black_preds)







