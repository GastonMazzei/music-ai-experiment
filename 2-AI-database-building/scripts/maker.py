import os
import sys

import pandas as pd
import numpy as np

from numpy.random import randint
from random import choice, sample, uniform
from functools import partial


def extract_seven(y, optflag=False, optflag2=False):
  # Intro: check format, build data 
  if y[-3:]=='csv': 
    F = y
    data = pd.read_csv(F)
    times_used = [-8]
    times_used_new = [(-100,-80)]
    if optflag2: LIMITCOUNT=30
    else: LIMITCOUNT=4
  else: 
    print('ERROR: A NON .CSV WAS PASSED')
    print('no mechanism to deal with this')
    print('EXITING')
    sys.exit(1)

  # A collection of functions

  # F0
  def support(optflag2):
    if not optflag2: return uniform(2,6)
    else: return uniform(0.3,0.6)

  # F1
  def checker(tsample, used_times):
    if (
      min(
       [abs(x_ - tsample) for x_ in used_times]
           )
            ) < support(optflag2): return True
    return False

  # F2
  def produce_time():
    Tmax = max(data.start)-7
    t0 = np.random.random()*Tmax
    tf = t0 + 7
    return (t0,tf)

  # F3
  def checker_new_latest(tsample,tsamplemax, used_times):
    indexes = []
    margin = 3.5
    lower_margin = margin
    upper_margin = lower_margin
    for x in used_times:
      if ((x[0]<tsample) and
          (x[1]>(tsample+
                 upper_margin)
                   )): return True
      if (((
           x[0] +
           lower_margin
               )<tsamplemax) and
          (x[1]>tsamplemax)): return True
      if ((x[0]>tsample) and
          (x[1]<tsamplemax)): return True
      if ((x[0]<tsample) and
          (x[1]>tsamplemax)): return True
    return False

  # F4
  def checker_new(tsample,tsamplemax, used_times):
    if (
      min(
       [abs(x_[0] - tsample) for x_ in used_times]
           )
            ) < support(optflag2): return True
    if (
      min(
       [abs(x_[1] - tsamplemax) for x_ in used_times]
           )
            ) < support(optflag2): return True
    return False

  # F5
  def produce_time_new():
    nonlocal optflag
    Tmax = max(data.start)-7
    t0 = np.random.random()*Tmax
    tf = t0 + 7 + uniform(-float(sys.argv[2]), float(sys.argv[2]))
    return (t0,tf)

  # F6
  def seven_main(optarg = -1):
    nonlocal LIMITCOUNT
    nonlocal times_used
    nonlocal times_used_new
    classic = False
    if not (optarg+1):
      if classic:
        (t0,tf) = produce_time()
        counter = 0
        while checker(t0, times_used):
          (t0,tf) = produce_time()
          counter += 1
          if counter== LIMITCOUNT: raise IndexError
        times_used.append(t0)
      else:
        (t0,tf) = produce_time_new()
        counter = 0
        while checker_new_latest(t0,tf, times_used_new):
          (t0,tf) = produce_time_new()
          counter += 1
          if counter== 4: raise IndexError
        times_used_new.append((t0,tf))
    else:
      t0 = optarg
      tf = t0 + 7
    print('chosen times are ',t0,tf,'...time window is ',tf-t0,' !!!')
    return  extract(classic,data[(
                   (data.start.between(t0,tf)) |
                   (
                    (data.start.between(-1,t0,inclusive=False)) &
                    (data.end.between(t0,3600,inclusive=False)) 
                                                                 )  
                                                )].to_numpy(), t0, tf)
  # Body
  if optflag:
    results = [seven_main(x) for x in optflag]
  else:
    if False:
      if not optflag2: 
        TIMES = int(1.3*((max(data.start)-7)//7))
      else: 
        TIMES = int(5*((max(data.start)-7)//7))
      print(f'defined {TIMES} time-iterations')
      results = [seven_main() for x in range(TIMES)]
    else:
      try:
        results = []
        while True: 
          results += [seven_main()]
      except IndexError: pass        

  return results


def extract(classicindex, vector: np.ndarray, min_time: float, max_time: float): 
  def something(min_time: float , v: np.ndarray):
    if v[1]>min_time + 7: v[1] = min_time + 7
    if v[0]<min_time: v[0] = min_time
    return np.asarray([v[0]-min_time, v[1]-min_time, 
                      v[2], v[3], v[4]])
  def something_new(min_time: float , max_time: float, v: np.ndarray):
    if v[1]>max_time: v[1] = max_time
    if v[0]<min_time: v[0] = min_time
    return np.asarray( 
                      [
                       (v[0]-min_time)/(max_time-min_time),
                       (v[1]-min_time)/(max_time-min_time), 
                      v[2]/128, v[3]/128, v[4]
                        ]
                         )
  if classicindex:
    apply_me = partial(something, min_time)
  else:
    apply_me = partial(something_new, min_time, max_time)    
  return np.apply_along_axis(apply_me, 1, vector).flatten()


def add_new(a_list,mx,flag,optional_directory=False):
  TEMP = pd.DataFrame(a_list)
  if not optional_directory:
    with open(f'DATA-{flag}.csv', 'a') as f:
      TEMP.to_csv(f, mode='a', header=f.tell()==0)
  else:
    with open(f'{optional_directory}/DATA-{flag}.csv', 'a') as f:
      TEMP.to_csv(f, mode='a', header=f.tell()==0)

  return


def build_new(c_list, flag, secondflag, optional_directory=False,**kwargs):
  MAXCOLS = int(kwargs.get('maxcols',sys.argv[1]))
  results = []
  for c in c_list:
    c = c.reshape(-1,5)[:,:-1]
    shape = c.shape[0]*c.shape[1]
    if shape>=MAXCOLS:
      print(f'\n\n\n\nINFO: "{secondflag} could use more than '\
           f'{MAXCOLS} features!"\n\n\n---------------\n\n\n\n')
      localindexes = sorted(sample(range(c.shape[0]),MAXCOLS//4))
      results.append(np.take(c, localindexes,0).flatten()) 
    else:
      q = np.zeros(MAXCOLS)
      q[:shape] = c.flatten()[:]
      results.append(q)
  add_new(results, MAXCOLS, flag, optional_directory)
  return 

def process(foo, flag, stravinsky=False):
  try:
    if stravinsky:
      build_new(
        extract_seven(foo,False,True),
        flag, foo
                        )  
    else:
      build_new(
        extract_seven(foo),
        flag, foo
                        )  
  except Exception as ins:
    print(ins.args)
    print('\n\n\nCase was: ',foo,'\n\n\n')
    print('---------A-N--E-R-R-O-R------------\n\n\n\n')

def foldermaker(s):
  try: os.mkdir(s)
  except: pass
 
  return

def initialize(optflag=False):
  try: 
    os.mkdir('TRAIN')
    os.mkdir('VALID')
    currentfiles = [j for j in os.listdir() if j[-3:]=='csv']
    if os.getcwd().split('/')[-1]=='Stravinsky':
      VALID = sample(currentfiles,6)
    else:
      VALID = sample(currentfiles,21)
    dicc = {'TRAIN': [x for x in currentfiles if x not in VALID],
              'VALID': VALID}
  

  except Exception as ins:
    print(ins.args)
    print('if directories exist we should:')
    mssg = """
    1) check if there are already 10 valids
    2) if so, check if thre is a DATA-VALID.csv
    3) if so, check if it's "large enough"
    4) check if there are remaining training samples
    5) if so, add them to DATA-TRAIN.csv
    6) if there is not such a file, create it and 
       include the samples already in TRAIN directory
    """
    print(mssg)
    print('\n\nCURRENTLY JUST emptying back TRAIN-VALID'\
      ' into the "general soup" and killing DATA-X.csv')
    commands = ['mv TRAIN/* .', 'mv VALID/* .',
                'rm -r TRAIN', 'rm -r VALID', 
                'rm DATA-TRAIN.csv', 'rm DATA-VALID.csv']
    for i_ in commands:
      try: 
        os.system(i_)
      except: 
        print("WARNING: if file doesn't exist plz ignore")

    if optflag: return sys.exit(1)
    return initialize(True)

  return dicc


def cond_build(lim,J):
  try:     
    if os.path.getsize(f'DATA-{J}.csv')>lim: return True
  except: pass
  return False


def main(d,cond):
  inf = 10000
  ORIG = os.getcwd()
  os.chdir(d)
  separate = initialize()
  for k, val in separate.items():
    LIMIT = inf
    for X in val:
      print('about to process ',X,' for ',k)
      try:
        if d=='Stravinsky':
          process(X,k, True)
        else:
          process(X,k)
        print('ended successfully!')
      except Exception as ins:
        print(f'WARNING: problem encountered for {d} {k} {val}')
        print(ins.args)
        print('Continuing iterations...')
      LIMIT -= 1
      os.system(f'mv {X} {k}')
      if LIMIT==0 or cond(k): 
        print('LIMIT REACHED')
        break 
  os.chdir(ORIG)
   
  return





if __name__=='__main__':
  print('time window is ',sys.argv[2])
  print('and maxcols are ',sys.argv[1])
  from time import sleep
  sleep(2)
  from functools import partial
  # The smaller database will define:
  #
  # Max_Dataset_Size( sampling_rate, time_window) 
  #
  for macro_name in ['Stravinsky']:
    main('Stravinsky',partial(cond_build, 20E6) )
  for macro_name in [j_ for j_ in os.listdir() if (os.path.isdir(j_)
                                         and j_ not in ['__pycache__',
                                                          'Stravinsky',
                                                     'scripts'])]:
    main(macro_name, partial(
               cond_build,6 *
               os.path.getsize(
                  'Stravinsky/DATA-TRAIN.csv')
                              )
                               )  
  print('\n\nSCRIPT HAS ENDED!!!\n')
