#!/usr/bin/env python

#________INDEX____________.
#                         |
#  6 functions            |
#   (6=3+2+1)             |
#                         |
# -3 auxiliary            |
# -2 plots)               |
# -1 main)                |
#                         |
# (if __name__==__main__) |
#_________________________|

import os
import sys
import pickle
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from joblib import dump,load
from keras.initializers import LecunNormal
from keras import Sequential, backend
from keras.losses import categorical_crossentropy
from keras.layers import Dense
from keras.optimizers import SGD
from keras.models import load_model
from keras.metrics import AUC
from math import ceil
from random import randrange, sample, choice
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import  OneHotEncoder
from sympy.solvers import solve
from sympy import Symbol
from time import sleep


#----------------------------------------------------
# Three auxiliary generic function
#
# (1)       "tags_dict" : mapping from numbers
#                         to composers names
#
# (2)   "pickle_bridge" : recieves and returns 
#                         the same data. Optionally
#                         it saves it before return
#
# (3) "backend_wrapper" : executes functions and 
#                         before returning it 
#                         manually asks for memory
#                         release; in case this 
#                         script is iterated
#---------------------------------------------------

# (1)
def tags_dict():
  """
  ENCODER
  names (e.g. Bach) <--> numbers (0-7)
  """
  with open('datasets/tags.dat','r') as f:
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
def pickle_bridge(A,B):
  """
  If you want to save the output, 
  The following can be set to False
  """
  if True: 
    return A,B
  info = A['info']
  with open(f"info.pickle", "wb") as f:
    pickle.dump(A, f)  
  return A,B

# (3)
def backend_wrapper(process):
  """
  Memory leak protection:
  backend_wrapper(main(foo))
  should help in the releasing 
  of plots and tensorflow
  """
  debug = True
  if debug: process()
  else:
    backend.clear_session()
    try:
      process()
      print('SUCCESS!')
    except Exception as ins:
      print('ERROR: unexpected. \n',ins.args)
      backend.clear_session()
  return

#----------------------------------------------------
# Two plotting functions
#
# (4)  "simple_plotter" : recieves predictions and,
#                         if it was a neural network,
#                         plots ROC curves, output 
#                         weights, and training curves
#
# (5)   "multi_rocker"  : plots the one-vs-all ROC's 
#                        
#---------------------------------------------------

# (4)
def simple_plotter(h: dict, case: str):

  # If 'forest': dont show info
  if case=='forest': return
  fs = 12

  # A plotting auxiliary function
  def individual_weights(ytrue_, ypred_, axy, flag):
    if len(ytrue_)==len(ypred_): L = len(ypred_)
    else: len_error(ytrue_,ypred_)
    temp = pd.concat(
       [
        pd.DataFrame(
          {
            f'prediction {flag}':
                [ypred_[i] for i in range(L) if ytrue_[i]==1],
            'type': 
                f'positive {flag}' ,
                          }
                           ),
         pd.DataFrame(
           {
            f'prediction {flag}':
              [ypred_[i] for i in range(L) if ytrue_[i]==0],
           'type':
              f'negative {flag}',
                           }
                            ),
                              ]
                               )
    for x in [f'positive {flag}',f'negative {flag}']:
      sns.distplot(temp[temp['type']==x][f'prediction {flag}'],
                 bins=[y/10 for y in range(11)],
                 ax=axy, kde=False,
                 norm_hist=True,
                 label=x,)
    axy.set_xlim(0,1)
    axy.set_xlabel('Output Weights',fontsize=fs)
    axy.set_title('output weights por categoria',fontsize=fs)
    axy.axvline(x=0.5,c='r',lw=1,ls='-')  

  # Create the Figure and preprocess data
  f,ax = plt.subplots(2,5,figsize=(21,12))  
  L = h['ytrue'].shape[0]
  ytrue, ypred = h['ytrue'], h['ypred']
  del h['ytrue']
  del h['ypred']
  h = pd.DataFrame(h)  
  h['ref 100%']=1
  h['ref null hypothesis']=0.5
  fit_data = {'train auc': np.mean(h['auc'][-3:]),
              'validation auc': np.mean(h['val_auc'][-3:]),
               'train loss': np.mean(h['loss'][-3:]),
                 'validation loss':np.mean(h['val_loss'][-3:]),}

  # PLOT 0: Training & Validation Curves VS Epochs 
  sns.lineplot(data=h, ax=ax[0,0])
  ax[0,0].set_title(f'Loss & Accuracy vs Epochs',fontsize=fs)
  ax[0,0].set_xlabel('epochs',fontsize=fs)
  ax[0,0].set_ylim(0,2.5)
  
  # PLOT 1: Validation set's ROC
  multi_rocker(ax[0,1],ytrue,ypred)
  ax[0,1].set_ylim(0,1.05)
  ax[0,1].set_xlim(0,1)
  ax[0,1].set_title(f'ROC curves',fontsize=fs)
  ax[0,1].legend()


  # PLOTS 2 TO 10: Output Weights "per Class" (i.e. per composer)
  axind = {0:(0,2), 1:(0,3), 2:(0,4),
       3:(1,0),4:(1,1),
       5:(1,2),6:(1,3),7:(1,4),}
  for J in range(len(ytrue[0])):
    a = [x[J] for x in ytrue]
    b = [x[J] for x in ypred]
    individual_weights(
               a,
               b,
               ax[axind[J] ],
               J,
                  )
    ax[axind[J]].legend()

  # Tight Layout and save!
  plt.tight_layout()
  f.savefig('results/last-neural-network.png')

  return

# (5)
def multi_rocker(
                 axy: type(plt.subplots()[1]), 
                 y_trues: np.ndarray,
                 y_preds: np.ndarray,
                 ):
  """
  One-Vs-All ROC-curve:
  """
  fpr = dict()
  tags = tags_dict()[1]
  tpr = dict()
  roc_auc = dict()
  n_classes = len(y_trues[0])
  wanted = list(range(n_classes))
  for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_trues[:, i], y_preds[:, i])
    roc_auc[i] = round(auc(fpr[i], tpr[i]),2)
  extra = 0
  for i in range(n_classes):
    axy.plot(fpr[i], tpr[i], label=f'case {tags[str(wanted[i])]}'\
                                             f' auc {roc_auc[i]}')
    axy.set_xlim([0.0, 1.0])
    axy.set_ylim([0.0, 1.1])
    axy.set_xlabel('False Positive Rate')
    axy.set_ylabel('True Positive Rate')
    axy.legend(loc="lower right")
    extra = i
  i = extra
  axy.plot(fpr[i],fpr[i],label='null hypothesis',lw=1.5,ls=':',c='r')

  return


#--------------------------
# MAIN: builds, fit and 
# evaluate AI-based models
#--------------------------

# (6)
def main(**kwargs):
  """
  1-Load the data
  2-Build the network OR forest
  3-Fit it
  4-Return evaluations

  KWARGS:

    for all:
      "case" = 'network' or 'forest'

    for network:
      "neurons" 
      "epochs"
      "batch"
      "lr" (learning rate) 
      "deep" (0-N hidden layers)
      "verbose" ()          
  """
  
  #Step 0) KEYS retrieval 
  #---------------------------------------------------
  batch = kwargs.get('batch',32)
  epochs = kwargs.get('epochs',100)
  neurons = kwargs.get('neurons',16)
  verbose = kwargs.get('verbose',1)
  LR = kwargs.get('lr',0.01)
  deep = kwargs.get('deep',0)
  case = kwargs.get('case','network')

  #Step 1) LOAD Data
  #---------------------------------------------------
  with open('datasets/database.pkl','rb') as f:
    data = pickle.load(f)    
  # Fix keys! "total-train"-->"train"
  data['train'] = data['total-train']
  del(data['total-train'])
                               
  #Step 2) BUILD the network OR forest
  #---------------------------------------------------
  if case=='network':    
    # One Hot Encoding: 
    #   ytrue = [0,3,..]--> [[1,0,..], [0,0,0,1,..], ..]
    #
    if True:
      for x in data.keys():
        data[x] = (data[x][0],
           OneHotEncoder().fit_transform(
                        data[x][1].reshape(-1,1)
                                     ).toarray(),)
    # INFO: there are 8 composers
    last_neur_shape = 8   
    # First layer!
    architecture = [Dense(neurons,activation='selu',
                  input_shape=(len(data['train'][0][0]),),
                         kernel_initializer = LecunNormal(),
                                                          ),]
    # Hidden layer!
    architecture += [Dense(neurons,
                        activation='selu',
                        kernel_initializer = LecunNormal(), 
                                                         ),
                                                          ]
    # N=deep extra layers are added!
    if deep: 
      architecture += [Dense(neurons,
                      activation='selu',
                      kernel_initializer = LecunNormal(), 
                              )] * deep
    # Last layer!
    architecture += [Dense(
                        last_neur_shape,
                       activation='softmax'), 
                                           ]
    # Build the model!
    model = Sequential(architecture)
    # Use as multiclassification metric 
    # the area under the roc curves!
    auc_metric = AUC(num_thresholds=200,
      curve="ROC",
      summation_method="interpolation",
      name=None,
      dtype=None,
      thresholds=None,
      multi_label=False,
      label_weights=None,)

    # Compile the model and fit it!
    model.compile(
                 optimizer=SGD(learning_rate=LR),
            loss='categorical_crossentropy',
            metrics=[auc_metric])
    # check in console that architecture was as required!
    print(model.summary())
    history = model.fit(data['train'][0], data['train'][1],
        batch_size = batch, epochs = epochs,
        verbose=verbose,
        validation_data=(data['val'][0], data['val'][1]))


    #3) Evaluate the network
    history = history.history
    history['ypred'] = model.predict(data['val'][0])
    history['ytrue'] = data['val'][1]

    # Save VALIDATION predictions and correct values
    local_dictionary = {
            'true': np.argmax(history['ytrue'],1),
            'predicted': np.argmax(history['ypred'],1),
                        }
    with open(f'results/val-network-predictions.csv', 'a') as f:
      pd.DataFrame(local_dictionary).to_csv(
                        f, mode='a', header=f.tell()==0, index=False)

    # Save TESTING predictions and correct values
    local_dictionary = {
             'predicted': np.argmax(model.predict(data['test'][0]),1),
              'true': np.argmax(data['test'][1],1),
                        }
    with open(f'results/test-network-predictions.csv', 'a') as f:
      pd.DataFrame(local_dictionary).to_csv(
                        f, mode='a', header=f.tell()==0, index=False)

    return history, 'network'

  elif case=='forest':
    
    # Build and fit!
    clf = RandomForestClassifier(n_estimators=200)
    clf.fit(
          data['train'][0],
          data['train'][1], )
    history = {}
    history['ypred'] = clf.predict(data['val'][0])
    history['ytrue'] = data['val'][1]

    # Save VALIDATION predictions and correct values
    local_dictionary = {
            'true': history['ytrue'],
            'predicted': history['ypred'],
                        }
    with open(f'results/val-forest-predictions.csv', 'a') as f:
      pd.DataFrame(local_dictionary).to_csv(
                        f, mode='a', header=f.tell()==0, index=False)

    # Save TESTING predictions and correct values
    local_dictionary = {
             'predicted': clf.predict(data['test'][0]),
              'true': data['test'][1],
                        }
    with open(f'results/test-forest-predictions.csv', 'a') as f:
      pd.DataFrame(local_dictionary).to_csv(
                        f, mode='a', header=f.tell()==0, index=False)


    return history, 'forest'
#----------------------------------e-n-d--o-f--f-u-n-c-t-i-o-n-s-------














if __name__=='__main__':

  def neuron_definer(n: int, deep: int, features: int):
    """
    Calculate the neural network neurons 
    from the "data/degrees of freedom"
    required input
    """
    x = Symbol('x')
    with open('datasets/database.pkl','rb') as f:
      data = pickle.load(f)  
    L = len(data['total-train'][1])
    del(data)  
    return float(max(solve(L/(x*(features+10)+(1+deep)*(x**2))-1-n, x)))

  if True:

    if sys.argv[11]=='network':

      params = []
      for x in sys.argv[1:5]:
        params += [int(x)]
      [NEU, EPO, BA, dp, LR] = [*params,float(sys.argv[5])]
      features = (
                 
                 int(sys.argv[12]) * float(sys.argv[8]) *
                (1-1/4 * (1-int(sys.argv[10]))) +
                int(sys.argv[6])            )
      NEU = neuron_definer(NEU, dp, features)
      NEU = int(NEU)+1
      backend_wrapper(
                lambda: simple_plotter(*pickle_bridge(
                        *main(
                               neurons=NEU, epochs=EPO, 
                               batch=BA,  verbose=1, 
                               deep=dp, lr=LR,
                               case = sys.argv[11],
                                                       ))))

    elif sys.argv[11]=='forest':

      params = []
      backend_wrapper(
                lambda: simple_plotter(*pickle_bridge(
                        *main(
                               case = sys.argv[11],
                                                       ))))
