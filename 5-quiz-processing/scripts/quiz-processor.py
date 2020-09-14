import os

import numpy as np
import pandas as pd

from extras import *

def init_answ():
  return pd.read_csv('form-answers.csv')

def init_vids():
  return pd.read_csv('form-questions.csv',header=None)

if __name__=='__main__':
  if True:
    # (1) Load the data and process
    os.chdir('../raw-data')
    df = sorter_for_visualization(
                        main_processor()
                                     )
    
    df = add_question(df)
    df = erase_empties(df)
    df = df.replace(0, '')

    # (2) In this file results are stored in format:
    #__q_1_|_a_1_|_q_2_|_a_2_|_....|
    # Bach |Haydn|Liszt| Sor | ....|
    #------------------------------|
    # etc....
    #
    df.to_csv('../processed/data-in-table.csv',index=False)


    # (3) In this file results are stored in format:
    # _true_|_pred_|
    #  Bach | Bach |
    #Vivaldi| Sor  |
    # ..    | ..   |
    #
    #----------------------------------------
    # THIS is used in ../results to compare
    # against AI-based classification methods
    #----------------------------------------
    x = df.iloc[:,1:].to_numpy()
    composers = ['bach','vivaldi','liszt','haendel','haydn',
               'stravinsky','scarlatti','sor',]
    counts = {}
    ytrue = x.reshape(-1,2)[:,0]
    ypred = []
    new_df = pd.DataFrame({'true': x.reshape(-1,2)[:,0],
                            'pred':x.reshape(-1,2)[:,1]})
    new_df.to_csv('../processed/human-predictions.csv', index=False)
    new_df.to_csv('../../6-results/data/human-predictions.csv',index=False)



