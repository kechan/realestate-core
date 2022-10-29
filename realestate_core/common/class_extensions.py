import pandas as pd
from functools import partialmethod
pd.DataFrame.q_py = partialmethod(pd.DataFrame.query, engine='python')
pd.DataFrame.defrag_index = partialmethod(pd.DataFrame.reset_index, drop=True)

from pathlib import Path
Path.ls = lambda x: list(x.iterdir())
Path.lf = lambda pth, pat='*': list(pth.glob(pat))
Path.rlf = lambda pth, pat='*': list(pth.rglob(pat))

try:
  from google.cloud.storage.bucket import Bucket
  def _download_from_gcs(self, src, dst_dir=None, debug=False):
    try:
      blob = self.blob(src)
      if dst_dir is None:
        # download to local and use the same filename
        target_path = str(Path(src).name)
      else:
        target_path = str(Path(dst_dir)/Path(src).name)

      blob.download_to_filename(target_path)
    except Exception as ex:
      if debug:
        raise   
      else:
        print('Something has gone wrong. Please debug.')

  Bucket.download = _download_from_gcs
except:
  print('google.cloud.storage.bucket.Bucket not found, please pip install google-cloud-storage')

