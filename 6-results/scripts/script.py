#________INDEX____________.
#                         |
#  3 functions            |
#   (6=3+2+1)             |
#                         |
# -4 auxiliary            |
# -1 main)                |
#                         |
# (if __name__==__main__) |
#_________________________|

import sys
import re

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

from scipy.stats import dirichlet, beta, bernoulli
from sklearn.metrics import precision_score, recall_score, f1_score
from functools import partial

#-------------------------------------------------------
# First part: Four (4) auxiliary generic functions
#
# (1)         "tags_dict" : mapping from numbers
#                           to composers' names
#
# (2)        "four_plots" : compare four classifiers
#                           for a specific composer
#                           in a specific axes
#                           (humans, random, random forests &
#                            neural network). It's
#                           a dispatcher for 'plotter' 
#
# (3)           "plotter" : the actual plotter func   
#
# (4) "measure_dispatcher": choose the comparison measure
#
#---------------------------------------------------------

# (1)
def tags_dict():
  with open('tags.dat','r') as f:
    tags_list = f.readlines()
  tags = {}
  key_pattern = re.compile('item:[ ]+([a-z]+)',re.I)
  item_pattern = re.compile('key:[ ]+([0-9]+)',re.I)
  for x in tags_list:
    tags[re.search(
             key_pattern, x
                    ).group(1)] = re.search(
                                    item_pattern, x
                                              ).group(1)
  inverted_tags = {}
  for k,i in tags.items(): inverted_tags[i] = k

  return tags, inverted_tags

# (2)
def four_plots(name: str, axis, data: dict):
  plotter('humans',name, axis, data['humans'])
  plotter('network',name, axis, data['network'])
  plotter('random',name, axis, data['random'])
  plotter('forest',name, axis, data['forest'])

  # insert here visual specs!
  #---------------------------------------------
  #ax.legend()
  #ax.set_title(f'{name}')
  props = dict(boxstyle='round', facecolor='lavender', alpha=0.3)
  ax.text(0.5, 0.95, name, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)
  ax.set_xlim(0,100)
  ax.set_ylim(0,200)
  ax.set_yticklabels([])
  ax.set_yticks([0,100,200])
  ax.set_xticks([0,25,50,75,100])
  #---------------------------------------------

  return

# (3)
def plotter(being: str, name: str, axis, data: dict):
  # Color-blind friendly palette
  colors = {'forest':'#d7191c',
           'network':'#fdae61',
           'random':'#abd9e9',
            'humans':'#2c7bb6',}

  # Beta Distribution generation from the measured predictive-quality
  ypred = beta.rvs(
            1+data[f'total {name}'][0] * data[name][0],
            1+data[f'total {name}'][0] * (1 - data[name][0]),
            size=4000,
                      )

  # plot with Seaborn that binnarizes automatically
  sns.distplot(100*ypred, bins=None, hist=True, kde=False,
                 label = f'{being}', ax=axis, color=colors[being])

  return 

# (4)
def measure_dispatcher(measure: str,ytrue: np.ndarray,
                     ypred:np.ndarray, optrand = 0):
  """
  possible measures:
   
  'recall' == TP / (TP + FN) 
  
  'precision' == TP / (TP + FP)
   
  'f1' == 2 * TP / (2*TP + FP + FN)
  
  'accuracy' = (TP + TN) / (TN + FN + TP + FP)
  """
  
  # Random ytrue,ypred & Tags
  if optrand:
    ytrue_rand, ypred_rand  = np.split(
                               np.argmax(
                                  dirichlet.rvs(
                                     alpha = [1,1]*4,
                                     size = 2*optrand
                                               ),
                                                1,
                                                  ).reshape( #split 2
                                                          2,-1,
                                                           ), 
                                                             2,0, 
                                                                )
    ytrue_rand = ytrue_rand.reshape(-1,)
    ypred_rand = ypred_rand.reshape(-1,)
  tags = {int(x):y for x,y in tags_dict()[1].items()}

  # Recall
  def recall(ytrue, ypred):
    nonlocal tags
    precision = recall_score(ytrue, ypred, average=None) 
    data = {}
    for x in tags.keys():
      data[tags[x]] = [precision[x]]
      #data[f'total {tags[x]}'] = [np.unique(
      #                             ypred,
      #                             return_counts=True,
      #                               )[1][x]]
      data[f'total {tags[x]}'] = [500]
    return data 

  # Precision
  def precision(ytrue, ypred):
    nonlocal tags
    precision = precision_score(ytrue, ypred, average=None) 
    data = {}
    for x in tags.keys():
      data[tags[x]] = [precision[x]]
      data[f'total {tags[x]}'] = [np.unique(
                                   ypred,
                                   return_counts=True,
                                     )[1][x]]
    return data 

  # F1
  def f1(ytrue, ypred):
    nonlocal tags
    precision = f1_score(ytrue, ypred, average=None) 
    data = {}
    for x in tags.keys():
      data[tags[x]] = [precision[x]]
      data[f'total {tags[x]}'] = [np.unique(
                                   ypred,
                                   return_counts=True,
                                     )[1][x]]
    return data 


  # Accuracy
  def accuracy(ytrue, ypred):
    nonlocal tags
    data = {}
    for x in tags.keys():
       temp = []
       for i,y in enumerate(ytrue):
         if ypred[i]==y and y==x: temp.append(1)
         elif ypred[i]==x: temp.append(0)
         elif y==x: temp.append(0)
         elif y!=x and ypred[i]!=x: temp.append(1)
       (data[tags[x]],
        data[f'total {tags[x]}']) =  ([sum(temp)/len(temp)],
                                               [len(temp)])  
    return data 
  
  func = {'accuracy': accuracy, 'f1':f1,
          'precision': precision, 'recall':recall,}

  if optrand:
    return func[measure](ytrue_rand, ypred_rand)
  else:      
    return func[measure](ytrue, ypred)


#------------------------------------------------------------------
#                          M  A   I  N 
#------------------------------------------------------------------
def main(measure):

  # Define the measure!
  #
  # (with TP: True Positive
  #       TN: True Negative
  #       ...etc)
  # 
  # 'recall' == TP / (TP + FN) 
  #
  # 'precision' == TP / (TP + FP)
  # 
  #  'f1' == 2 * TP / (2*TP + FP + FN)
  #
  #  'accuracy' = (TP + TN) / (TN + FN + TP + FP)
  #____________________________________________
  expand = partial(measure_dispatcher, measure)
  #--------------------------------------------  

  # 1) HUMAN answers are loaded
  #humans = pd.read_csv('human-predictions.csv').iloc[:,1:]
  a=pd.read_csv(
         'human-predictions.csv'
                   ).applymap(
                      lambda x: int(
                         tags_dict()[0][x]
                                    )
                                     ).to_numpy()
  humans = pd.DataFrame(expand(a[:,0],a[:,1]))

  # 2) Random
  samples = 6000
  random = expand(range(samples), range(samples), samples)  

  # 3)
  if True:
    #----R-A-N-D-O-M--F-O-R-E-S-T---c-l-a-s-s-i-f-i-e-r----.
    # choose:                                              |
    #         'val' == validation set (more points)        |
    #                                                      |
    #         'test' == testing set (more comparable, only |
    #                                over the audio-samples|
    #                                 humans answered on)  |
    name = 'val'
    #------------------------------------------------------/
    forest = pd.read_csv(name+'-forest-predictions.csv')
    forest = expand(forest.iloc[:,0].to_numpy(),
                      forest.iloc[:,1].to_numpy())
  # 4)
  if True:
    #----------N-E-U-R-A-L--N-E-T-W-O-R-K------------------.
    # choose:                                              |
    #         'val' == validation set (more points)        |
    #                                                      |
    #         'test' == testing set (more comparable, only |
    #                                over the audio-samples|
    #                                 humans answered on)  |
    name = 'val'
    #------------------------------------------------------/
    network = pd.read_csv(name+'-network-predictions.csv')
    network = expand(network.iloc[:,0].to_numpy(),
                     network.iloc[:,1].to_numpy())


  return {'random':random, 'humans':humans,
               'network':network, 'forest':forest}










if __name__=='__main__':
  
  # Define a figure with 2x4=8 subplots
  nrow = 4; ncol = 2;
  alpha = 8
  fig, axs = plt.subplots(nrows=nrow, ncols=ncol, 
                           figsize=(alpha*2,alpha),dpi=200)

  # Extract composers names from the quiz data
  names = ['Scarlatti', 'Sor', 'Bach',
         'Vivaldi','Stravinsky',
         'Haendel', 'Liszt', 'Haydn', ]

  # Generate a dictionary with results
  try: 
    metric = sys.argv[1]
  except IndexError:
    metric = 'f1'
  data = main(metric)

  # Plot one composers' classification result in each subplot
  for i,ax in enumerate(axs.reshape(-1)): 
    try:
      four_plots(names[i], ax, data)
    except IndexError: pass


  #------------------------------------------
  # Visual specs, Save & View!
  #------------------------------------------
  fig.text(0.5, 0.89, '(Probability Density Function of the True Positive Rate'\
                      ' conditioned to a positive observation)' ,ha='center',fontsize=11)
  fig.text(0.5,0.92, '$PDF(Recall)$', fontsize=14.5,ha='center')
  fig.text(0.5, 0.04, 'Probability of a positive being True Positive', ha='center')
  fig.text(0.1, 0.5, 'Probability Density', va='center', rotation='vertical')
  fig.set_facecolor('ivory')
  for i,ax in enumerate(axs.reshape(-1)):
    if i==7: ax.legend()
  #------------------------------------------
  plt.savefig('../RESULTS/RESULTS.png', facecolor='ivory')

