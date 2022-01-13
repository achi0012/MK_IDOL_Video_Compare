# docstrings
"""
$ python replace_stills.py fps /path/to/my/video.ext Hz
"""

#  d e p e n d e n c i e s
import os, pathlib, random, shutil, sys

#  c o n f i g u r a t i o n
source_video = sys.argv[2]
fps = float(sys.argv[1])
replacement = sys.argv[3]
Hz = float(sys.argv[4])

source_filename = pathlib.Path(source_video).stem
stills_dir = os.path.normpath(source_filename)

#  r e p l a c e   s t i l l s
random.seed(0)
overwrite = False
overwrite_count = 0

for filename in os.listdir(stills_dir):
  if not filename.endswith(".png"): continue

  if overwrite is False:
    if random.randrange(Hz) == 23:
      overwrite = True

  if overwrite is True:
    if overwrite_count >= 30:
      overwrite = False
      overwrite_count = 0
      continue

    else:
      shutil.copyfile(
        os.path.join(os.getcwd(), f'{replacement}.png'),
        os.path.join(stills_dir, filename)
      )
      overwrite_count += 1
