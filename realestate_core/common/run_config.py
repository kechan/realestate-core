from __future__ import print_function

from pathlib import Path

bOnColab = Path('/content').exists()
bOnKaggle = Path('/kaggle/').exists()
bOnGCPVM = Path('/home/jupyter').exists()
bOnPaperspace = Path('/notebooks').exists()
bOnLocal = Path('/Users/kelvinchan').exists() or Path('/Users/kechan').exists()


if bOnColab:
  home = Path('/content/drive/MyDrive')
elif bOnKaggle:
  home = Path('/kaggle/working')
elif bOnGCPVM:
  home = Path('/home/jupyter')
else:
  home = Path.home()/'kelvin@jumptools.com - Google Drive/My Drive'

