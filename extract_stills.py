# docstrings
"""
$ python extract_stills.py fps /path/to/my/video.ext
"""

#  d e p e n d e n c i e s
import os, sys, shutil, pathlib

#  c o n f i g u r a t i o n
source_video = sys.argv[2]
fps = float(sys.argv[1])

source_filename = pathlib.Path(source_video).stem
stills_dir = os.path.normpath(source_filename)

try:
  shutil.rmtree(stills_dir)
except FileNotFoundError:
  pass

os.makedirs(stills_dir)

#  e x t r a c t   s t i l l s
command = f'ffmpeg -i {source_video} -r {str(fps)} "{stills_dir}\\frame%03d.png"'

# print(command)
os.system(command)
