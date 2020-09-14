import re

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

from itertools import chain
from functools import partial
from scipy.interpolate import interp1d
from sklearn.metrics import accuracy_score

def init_answ():
  return pd.read_csv('form-answers.csv')

def init_vids():
  return pd.read_csv('form-questions.csv',header=None)

def flattener(xv, yv):
  L = len(yv[0])
  xv = np.asarray(list(xv) * L)
  yv = np.asarray(yv).flatten()
  return [x for x in zip(*[xv,yv])]

def tags_dict():
  with open('../tags.dat','r') as f:
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
  return tags

def output_by_case(df: pd.DataFrame,flag: str):
  tags = tags_dict()
  L = (df.shape[1]-1)//2
  output_cols = [f'{flag} {i}' for i in range(1,L+1)]
  output = df[output_cols].applymap(lambda x: tags[x])
  return df['time'].to_numpy(),output.to_numpy()

def running_mean(xv, yv, treshold):
  output = []
  for i,x in enumerate(xv):
    if x<=treshold:
      output += [yv[i]]
    else: pass #break 
  if not output: output = [9999]
  return np.mean(output)

def plot_per_composer(data: pd.DataFrame, ax, wanted: list):
  tags = tags_dict()
  cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
  j = 0
  for key,item in data.items():
    if key not in [wanted]: 
      j+=1
      continue
    inner_frame = pd.DataFrame()
    time, answers = zip(*item)
    answers = [int(x) for x in answers]
    ytrue = [int(tags[key]) for x in range(len(time))]
    accuracy = [100*accuracy_score(
                             [x], [answers[i]]
                                   ) for i,x in enumerate(ytrue)]
    ax.scatter(
               time,
               accuracy,
               label=f'{key}: Measurements',
               color=cycle[j],
               s=40,
                        )
    sample_mean = [np.mean(accuracy) for x in time]    
    sns.lineplot(
            time,
            sample_mean,
            #label=f'{key} mean',
            color=cycle[j],
            ax=ax,
                          )
    auxiliary_mean = [running_mean(time,accuracy,x) for x in time]
    reduced_time = []
    progressive_mean = []
    for i,x in enumerate(time):
      if auxiliary_mean[i]!=9999:
        reduced_time.append(x)
        progressive_mean.append(auxiliary_mean[i])
    sns.lineplot(
           reduced_time,
           progressive_mean,
           label=f'{key}: Mean Converging Progressively',
           ax=ax,
           color=cycle[j],
                           )  
    A, B = zip(*sorted(zip(time, progressive_mean)))
    ax.fill_between(A,B,sample_mean, color=cycle[j])
    j += 1
  return

def graphical_statistics(t: np.array, ytrue: np.array,
                         ypred: np.array, **kwargs):
  ax = kwargs['axis']
  questions = ','.join([str(x+1) for x in kwargs['questions']])
  if len(ytrue)==len(ypred): L = len(ytrue)
  else: 
    print('ERROR: MISMATCHED LEN!')
    raise IndexError
  accuracy = np.asarray([100 * 
          accuracy_score(
                 [ytrue[i][j] for j in kwargs['questions']],
                 [ypred[i][j] for j in kwargs['questions']],  
                                               ) for i in range(L)])
  sns.scatterplot(
                  t,
                  accuracy,
                  ax=ax,
                  label=f'accuracy over {questions}',
                      )
  mean = [running_mean(t,accuracy,x) for x in t]
  sns.lineplot(
               t,
               mean,
               label=f'mean value over {questions}',
               ax=ax, 
                     )
  return


def start_plot():
  f, ax = plt.subplots()
  return f,ax

def end_plot(ax, flag: str, author='composers'): 
  if flag=='Figure 3':
    ax.set_title('Accuracy(%) of respondents'\
          ' calculated over different questions')
    ax.set_xlabel('Experiment time (%)')
    ax.set_ylabel('Accuracy of Humans')
    ax.set_ylim(-5,105)
    ax.patch.set_facecolor('ivory')
    plt.show()
  elif flag=='Figure 4':
    ax.set_title(f'Classification Accuracy Measurements (%) along Time for {author}'\
                   '\nand the progressive convergence of the mean')
    ax.set_xlabel('Experiment time (%)')
    ax.set_ylabel('Accuracy measured in Humans')
    ax.set_ylim(-5,105)
    ax.patch.set_facecolor('ivory')
    plt.legend(ncol=1, fancybox=True, shadow=True, fontsize=8)
  return
def time_process(flag: str, s: str):
  # Time Format in Answers:
  #17/08/2020 19:48:00
  # Time format in Vids
  #8/27 18:10:0  
  if flag=='answ':
    parts, trash, extra = s.split('/')
    parts = [parts] + extra.split(' ')[-1].split(':')
  elif flag=='vids':
    trash, parts = s.split('/')
    parts = list(
         chain.from_iterable(
                [x.split(':') for x in parts.split(' ')]
                                                         )
                                                           )
  else: 
    import sys
    print('ERROR: wrong time_process flag - exiting')
    sys.exit(1)
  for i,x in enumerate([86400,3600,60,1]):
    parts[i] = int(parts[i])*x
  return sum(parts)

  
def time_update(df: pd.DataFrame, flag: str):
  L = len(df.columns)
  df.columns = list(range(L))
  temporal_f = partial(time_process, flag)
  df[0] = pd.to_numeric(df[0].apply(temporal_f))
  return df

def info_joiner():
  # Loading and processing to seconds-time from day one
  data = {}
  for k,i in {'answ':init_answ, 
            'vids':init_vids}.items(): 
    d = i()
    d = d.dropna()  
    data[k] = time_update(d,k)    
    del(d)
   
  # THIS IS ONE OF THE FEW CUSTOM-MADE PARTS OF THE PROJECT!
  #   (i.e. where the number 7=6+1 is 
  #      being used instead of len(questions))
  # Cols to [time,question_i,..,q..,answer_i,..,answer_N]
  last = 7
  for k,i in data.items():
	    data[k].columns = [newnames(k,j) for j in range(last)]
  # Full names to last names
  for i in range(1,last):
    data['answ'].iloc[:,i] = data['answ'].iloc[:,i].apply(lambda x: x.split(' ')[-1])
  # Links to composer
  for i in range(1,last):
    data['vids'].iloc[:,i] = data['vids'].iloc[:,i].apply(
                                              links_to_composer)
  # return!
  return data['answ'].merge(data['vids'], how='outer', on='time'
                                 ).fillna(0).sort_values('time')


def newnames(macro_key: str, key: int):
  newnames_dict = {
     'vids':{
    0:'time', 1:'question 1',
    2:'question 2', 3:'question 3',
    4:'question 4', 5:'question 5',
    6:'question 6',},
     'answ':{
    0:'time', 1:'answer 1',
    2:'answer 2', 3:'answer 3',
    4:'answer 4', 5:'answer 5',
    6:'answer 6',},
                     }
  return newnames_dict[macro_key][key]

def links_to_composer(l: str):
  # Videos' links... If you make a playlist of your own then you should replace it!
  Bach = [
  "https://www.youtube.com/watch?v=Zi7xqNE9hKE&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=37H4BM_pp1A&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=OlYwbVuXktw&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=Pyn7NQlk354&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=a9rjf33hzpE&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=kWjiw61dC-Y&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=ZY0knIYxGLE&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=I1sjNpUVe5M&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=gl8RYKki77I&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=09Vbq5qtUAo&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=uyhwRC1Y2tI&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=SdlB2zYeHh4&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=UrTXJG8IvZg&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=VkoUYPODOG0&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=vZ2JN6FCkYQ&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  "https://www.youtube.com/watch?v=OYdg7LPEJT0&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
  ]

  Haendel =[
"https://www.youtube.com/watch?v=pngWvUl4sc4&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=WO7NW4nHMkI&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=vqinoOm9eQ0&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=aBU01cro8EE&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=983y7LiQphI&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=ifG1Z1ZUZtU&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=tvzzvve589k&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=FnOmTVScDbo&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=yCAwpdrOFE4&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=8NS6heiyCB8&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=W0QhwapBLgs&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=MBaW8JbwVac&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=sxPoY5C83Ko&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=OMsCoTkflEs&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=_3C_6dOHKr8&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=JQxYu_BWEIk&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
]

  Haydn =[
"https://www.youtube.com/watch?v=vX9DKaondGg&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=8mabrff8wqU&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=QD1KOICxFEk&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=g9eUkSXIbNg&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=fNk1SaARaao&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=FZ8SlKbQ3Ig&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=pYcmKdCbu5E&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=RO-41fWxVJ4&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=7o_jMhwq1tw&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=CqaiZVzpF_M&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=flWkToby9sA&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=t3lQCk_Joyg&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=xnpBlIbUHxI&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=AHKqDlIVw_o&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=H804sD3F57M&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=Tzry3Kt8oWc&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
]

  Liszt =[
"https://www.youtube.com/watch?v=UVPbLvtMhYs&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=lBHdnk0UXLw&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=lEg_w0SGiKA&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=QSLFkWH5y_Y&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=XXxVESZ1nf4&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=VaPAPzcKIKY&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=Ub-OmxR4xh0&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=A0SLxIKFJsE&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=xWMgru2DJ44&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=r-O-VgIwtns&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=b7rr2dg94MQ&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=esB4xwLs0QU&list=PLP7aDKJlAREGG70Fs5q0cuHmAzyFeq2JL&t=0s",
"https://www.youtube.com/watch?v=2efPiNEwAMg&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=z0rMs0C8BQU&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=iw8s7n4thc8&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=Wc77iymBd_0&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
]

  Scarlatti =[
"https://www.youtube.com/watch?v=8OMKQp4WT5s&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=5Htx9NaAYgs&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=hs3o-KqLa74&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=x7YlcnSmcDo&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=0ZJmJF0MP94&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=y15ThHHbU6M&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=aCan2XTMB6U&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=VhQIPmrWF4U&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=-FPbhEA0RAs&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=mrE1Zo_QiHk&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=OV2yobZrLiE&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=fCx4fo0CSsk&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=hkLywDqs13g&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=ZWA5SMzmZgw&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=BHhY4g4Rzr8&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=4IfrndUGwEc&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
]

  Sor =[
"https://www.youtube.com/watch?v=cz9jPglrHbQ&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=iycLjdwNxn0&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=wFY1d0sz8iw&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=ud_87UFQo1I&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=Arjkgs7vkSM&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=q29GjY3ULCs&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=yrUo7Ase8rY&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=fX2ebVAb4-8&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=lUXQRY6TBE8&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=gaATfVdy0cY&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=bb1_NGpvoLE&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=zRrlq9iiTVc&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=UvEGwPHuMh0&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=hMFhQdy_aYw&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=5tYQEkwIUQo&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=cPZPVolymCo&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
]

  Stravinsky =[
"https://www.youtube.com/watch?v=Zo4WEQOkYzw&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=mR4271hPBHg&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=estlzxbrEgo&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=CFARfuTfSAs&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=s5M2btAIYTE&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=pqbvpo5jc4Y&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=h9nCLbwa7_o&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=LL4LRjO9rHQ&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=REK0XYCK0gE&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=So25AAzgpIo&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=9cy1jhLmeZE&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=3zofhFzI_z8&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=Hn-qBcZntJQ&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=2Dwszd9Y7v4&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=vYptmqnKsGo&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=eB46OihJVSA&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
]

  Vivaldi =[
"https://www.youtube.com/watch?v=GmoK5c_2u2A&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=rbV80Qxp-6Y&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=bHo3twFPOpo&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=kPRWNrcxDPM&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=14Xyq7soBF4&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=0sZ3R_Nmz9Q&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=J03vqxTPpRk&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=56dVN3Lcga4&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=oJgzflKi3vw&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=J9G2BJowQTA&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=GCIZLDcNcvs&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=xDSYmgyPWGc&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=HjPFmFQi8FQ&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=OsawMbkAnhM&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=vV4-McgTpX4&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
"https://www.youtube.com/watch?v=6xLvKUq57AI&list=PLOvycn63s7W_I3JwxlKUogQ6-NCLX3e6I&t=0s",
]
  selector = {
    'Bach':Bach,
    'Haendel':Haendel,
    'Haydn':Haydn,
    'Liszt':Liszt,
    'Scarlatti':Scarlatti,
    'Sor':Sor,
    'Stravinsky':Stravinsky,
    'Vivaldi':Vivaldi, 
                      }
  result = []
  for k,x in selector.items():
    if l in x: result.append(k)
  if len(result)!=1: raise('LINK PROVIDED WAS INCORRECT!')
  else: return result[0]

def main_processor():  
  info = info_joiner()
  info.index = list(range(len(info.index)))
  max_ind = max(info.index)
  min_ind = min(info.index)
  indexes = info[info['answer 1'].apply(lambda x: x!=0)].index.tolist()
  wanted = sorted(
              list(
                 set(
                   list(
                 chain.from_iterable([[x-1,x,x+1] for x in indexes])
                                           )
                                            )
                                             )
                                               )
  wanted = [x for x in wanted if ((x< max_ind) and (x> min_ind))]
  return info.loc[wanted]

def table_printer(df):
  cases = ['time']
  for x in range(1,7):
    cases += [f'question {x}',f'answer {x}']

  import plotly.graph_objects as go
  fig = go.Figure(data=[go.Table(
    header=dict(values= cases ,
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values = [df[x] for x in cases ],
               fill_color='lavender',
               align='center'))
  ])

  fig.show()
  return 

def time_me_back(n: int):
  month, year = 'Aug', '2020'
  times = {}
  others = ['day','hour','minute','second']
  divisors = [86400, 3600, 60, 1]
  for i,x in enumerate(others):
    a, n = n // divisors[i], n % divisors[i]
    times[x] = a 
  return f'{year}-{month}-{times["day"]} '\
         f'{times["hour"]}:{times["minute"]}:{times["second"]}'


def sorter_for_visualization(df):
  df.index = list(range(len(df.index)))
  names = ['time']
  for i in range(1,(len(df.columns)-1)//2+1):
    names += [f'question {i}',f'answer {i}']    
  return df[names]


def erase_emtpies(d):
  pass

def add_question(d):
  def f(s,ind,p):
    if p!=0: return p
    else:
      try:
        out = s.loc[ind-1]
      except KeyError:
        out = p
    return out
  print('previous data: ',d.head())
  for x in [x for x in d.columns if 'question' in x]:
    print(f'processing case {x}')
    while ((d[x]==0).any()):
      d.loc[d[x]==0,x] = d[d[x]==0][x].to_frame().apply(lambda y: y.apply(partial(f,d[x],y.name)),axis=1)
  print('final output: ', d.head())

  return d

def erase_empties(d):
  return d[d['answer 1']!=0]












