from pandas.api.types import is_string_dtype, is_numeric_dtype, is_bool_dtype, is_categorical_dtype

import re, pickle, gzip, hashlib
import numpy as np
import pandas as pd
from pathlib import Path

try:
  import matplotlib.pyplot as plt
  import seaborn as sns
except Exception as e:
  print(e)
  print("Not importing matplotlib and seaborn")

def sha256digest(content, truncate_len=10):
  return hashlib.sha224(content.encode('utf-8')).hexdigest()[:truncate_len]

def isNone_or_NaN(x):
  return (x is None) or (isinstance(x, float) and np.isnan(x))

def tf_dataset_peek(ds, loc, as_numpy=False):
  if as_numpy:
    ds = ds.as_numpy_iterator()
    
  for k, x in enumerate(ds):
    if k < loc: continue
    break

  return x

def load_from_pickle(filename, compressed=False):
  try:
    if not compressed:
      with open(str(filename), 'rb') as f:
        obj = pickle.load(f)
    else:
      with gzip.open(str(filename), 'rb') as f:
        obj = pickle.load(f)

  except Exception as ex:
    print(ex)
    return None

  return obj

def save_to_pickle(obj, filename, compressed=False):
  try:
    if not compressed:
      with open(str(filename), 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    else:
      with gzip.open(str(filename), 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

  except Exception as ex:
    print(ex)

def join_df(left, right, left_on, right_on=None, suffix='_y', how='left'):
    if right_on is None: right_on = left_on
    return left.merge(right, how=how, left_on=left_on, right_on=right_on, 
                      suffixes=("", suffix))

def plot_training_loss(history):
  ''' Plot training loss vs. epochs '''

  loss = history['loss']
  epochs = range(len(loss)) 

  plt.figure(figsize=(8, 8))
  plt.plot(epochs, loss, 'bo', label='Training loss')
  plt.title('Training loss')
  plt.xlabel('epochs')
  plt.legend(loc='best')
  plt.grid()

def plot_loss_accuracy(history):
  acc = history['acc']
  val_acc = history['val_acc']
  loss = history['loss']
  val_loss = history['val_loss']

  epochs = range(len(acc))

  # Plotting Accuracy vs Epoch curve
  plt.figure(figsize=(8, 8))

  plt.plot(epochs, acc, 'bo', label='Training acc')
  plt.plot(epochs, val_acc, 'b', label='Validation acc')
  plt.title('Training and validation accuracy')
  #plt.legend(loc='upper left')
  plt.legend(loc='best')
  plt.grid()


  # Plotting Loss vs Epoch curve
  plt.figure(figsize=(8, 8))

  plt.plot(epochs, loss, 'bo', label='Training loss')
  plt.plot(epochs, val_loss, 'b', label='Validation loss')
  plt.title('Training and validation loss')
  #plt.legend()
  plt.legend(loc='best')
  plt.grid()

def plot_loss_and_metrics(history, metric_name, plot_last_n=None):
  if plot_last_n is None:
    metric = history[metric_name]
    val_metric = history['val_' + metric_name]

    loss = history['loss']
    val_loss = history['val_loss']
  else:
    metric = history[metric_name][-plot_last_n:]
    val_metric = history['val_' + metric_name][-plot_last_n:]

    loss = history['loss'][-plot_last_n:]
    val_loss = history['val_loss'][-plot_last_n:]

  epochs = range(len(metric))

  # Plotting Accuracy vs Epoch curve
  plt.figure(figsize=(8, 8))

  plt.plot(epochs, metric, 'bo', label=f'Training {metric_name}')
  plt.plot(epochs, val_metric, 'b', label=f'Validation {metric_name}')
  plt.title(f'Training and validation {metric_name}')
  #plt.legend(loc='upper left')
  plt.legend(loc='best')
  plt.grid()


  # Plotting Loss vs Epoch curve
  plt.figure(figsize=(8, 8))

  plt.plot(epochs, loss, 'bo', label='Training loss')
  plt.plot(epochs, val_loss, 'b', label='Validation loss')
  plt.title('Training and validation loss')
  #plt.legend()
  plt.legend(loc='best')
  plt.grid()

def combine_history(history0, history1):
  return {metric0: val0 + val1 for (metric0, val0), (metric1, val1) in zip(history0.items(), history1.items())}

class PercentileScore:
  def __init__(self, values: np.ndarray=None, max_score=100, filename: Path=None):
    '''
    Given values (a distribution), compute the percentile of a arbitrary given value
    max_score is the maximum score that can be given to a value, default is 100. Increasing this
    corresponds to finer grain percentille scoring
    '''
    if filename is None:
      self.bins = np.percentile(values, np.linspace(0, 100, max_score+1))
      self.bins[0] = 0.
      self.bins[-1] = 1.
    else:
      # load from .npy
      self.load(filename)


  def __call__(self, p):
    if isinstance(p, np.ndarray):
      return np.digitize(p, self.bins) - 1

    return np.where(self.bins >= p)[0][0] - 1

  def save(self, filename: Path = None):
    if filename is None: filename = Path('percentile_score_bins.npy')
    if isinstance(filename, str): filename = Path(filename)

    print(f'Saving percentile score bins to {filename}')
    np.save(filename, self.bins)

  def load(self, filename: Path = None):
    if filename is None: filename = Path('percentile_score_bins.npy')
    if isinstance(filename, str): filename = Path(filename)

    print(f'Loading percentile score bins from {filename}')
    self.bins = np.load(filename)
