from pandas.api.types import is_string_dtype, is_numeric_dtype, is_bool_dtype, is_categorical_dtype

import re, pickle, gzip, hashlib
import numpy as np
import pandas as pd

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

