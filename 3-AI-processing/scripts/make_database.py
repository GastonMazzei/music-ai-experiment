from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from random import sample
import pandas as pd
import numpy as np
import pickle
import sys

def shape_printer(data):
  for x in data.keys(): 
    print(f'FOR KEY {x} SHAPES ARE {data[x][0].shape} {data[x][1].shape}')
  return

def new_var(vector, center=True):
  """
  from tbeggining,tend 
  to 
  A) center_t and t_width
  or
  A) tbeggining and t_width
  """
  if center:
    def center_and_width(y):
      return np.asarray([(y[1]+y[0])/2,y[1]-y[0]] + y[2:].tolist())
    return np.apply_along_axis(center_and_width, 2, vector)
  else:
    def start_and_width(y):
      return np.asarray([y[0],y[1]-y[0]] + y[2:].tolist())
  return np.apply_along_axis(start_and_width, 2, vector)
  
def selector(v,L,vol=True, center=0):
  if L!=v.shape[1]: contract=True
  else: contract=False
  if not vol:
    print('removing volume!')
    out = v.reshape(v.shape[0],-1,4)[:,:,:-1]
    if contract:
      print(f'shapes total and wanted are for volume-cropper ')
      print(out.shape[1],L//3-1)
      localindexes = sorted(sample(range(out.shape[1]),L//3-1))
  else:
    out = v.reshape(v.shape[0],-1,4)
    if contract:
      localindexes = sorted(sample(range(out.shape[1]),L//4-1))
  if contract:
    print('shape before contraction...', out.shape)
    out = np.take(out, localindexes, 1)    
    print('shape after contraction...', out.shape)
  if center==0: 
    print('times being left as is')
  elif center==1: 
    print('centering times!')
    out = new_var(out,True) 
  else:
    print('time start and width')  
    out = new_var(out,False)
  def shuffle_along_axis(a, axis):
    idx = np.random.rand(*a.shape).argsort(axis=axis)
    return np.take_along_axis(a,idx,axis=axis)
  # Path A: Fast? not working
  #if False:
  #  out = shuffle_along_axis(out, 1)
  # Path B: Slow? working
  #else:
  #  out = [np.random.permutation(x) for x in out]
  return np.asarray(out).reshape(v.shape[0],-1)

def main(contraction_factor, vol, centering):
  data ={}
  original_data = {}
  names = ['total-train','val','test']
  for x in names:
    temp = pd.read_csv('datasets/'+
                   f'{x}.csv',
                   low_memory=False,
                        ).fillna(
                            0).sample(
                               frac=1
                                  ).iloc[:,1:].to_numpy()  
    L = temp[:,:-1].shape[1]
    print(f'L is {L}! (expected {336*2/4}??)')
    #contraction_factor = 0.5
    #vol = 1 #1 means YES, VOLUME PLZ!
    #centering = 1#2
    print(f'contracting to {int(L*contraction_factor)/21}-'\
                f'{int(L*contraction_factor)/28} samples/sec')
    data[x] = (
            selector(temp[:,:-1],int(L*contraction_factor),
             vol,
              centering,), 
             temp[:,-1],
              )
    original_data[x] = (
            temp[:,:-1], 
             temp[:,-1],
              )

    del(temp)
  return data, original_data

# MaxMin! ==0
def minmaxme(data):
  s = MinMaxScaler().fit(np.concatenate([x[0] for x in data.values()]))
  for k,i in data.items():
    data[k] = (s.transform(i[0]),i[1])
  return data

# Standard! ==1
def standarizeme(data):
  s = StandardScaler().fit(np.concatenate([x[0] for x in data.values()]))
  for k,i in data.items():
    data[k] = (s.transform(i[0]),i[1])
  return data

# PCA!
def pcame(data, original_data,Nc):
  #Nc = int(L*contraction_factor)//5
  #Nc = 20
  print('using ',Nc,'PCA components!')
  pca = PCA(n_components=Nc).fit(
                np.concatenate([x[0] for x in original_data.values()]))
  for k,i in data.items():
    data[k] = (np.concatenate(
                              [
                               pca.transform(original_data[k][0]),
                                           i[0],
                                                  ]
                                          ,1),i[1])
  print('PCA features were added to the dataset! new shape is..')
  return data

def saveme(data):
  with open(f'datasets/database.pkl','wb') as f:
    pickle.dump(data,f)
  return print('SAVED!')

if __name__=='__main__':
  #main(contraction_factor, vol, centering)
  # vol=1 mantains volume
  # centering = 0  leaves time as is
  #           = 1  centers and width
  #           = 2  start and width
  print(sys.argv[:])
  (contraction_factor,
  [vol, centering,
   scaler, pca],
       *_
                 ) = (float(sys.argv[1]),
                       [int(x) for x in sys.argv[2:]])
  d1, d2 = main(contraction_factor, vol, centering)  
  shape_printer(d1)
  if not pca and scaler:
    if scaler==1:
      print('applied standard scaler!')
      d1 = standarizeme(d1)
    elif scaler==0:
      print('applied minmax scaler!')
      d1 = minmaxme(d1)
    elif scaler==2:
      print('no scaling applied!') 
  elif pca:
    if scaler==1:
      print('applied standard scaler!')
      d1 = standarizeme(d1)
    elif scaler==0:
      print('applied minmax scaler!')
      d1 = minmaxme(d1)
    elif scaler==2:
      print('no scaling applied!') 
    print('applied PCA and kept',pca,' components!')
    d1 = pcame(d1,d2,pca)
    if scaler==1:
      print('applied standard scaler!')
      d1 = standarizeme(d1)
    elif scaler==0:
      print('applied minmax scaler!')
      d1 = minmaxme(d1)
    elif scaler==2:
      print('no scaling applied!') 
  shape_printer(d1)
  saveme(d1)

  





