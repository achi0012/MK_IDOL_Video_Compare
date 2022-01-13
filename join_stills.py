# docstrings
"""
$ ipython join_stills.py fps /path/to/my/video.ext suffix
"""

#  d e p e n d e n c i e s
import os, sys, pathlib

#  c o n f i g u r a t i o n
source_video = sys.argv[2]
fps = float(sys.argv[1])
try: suffix = sys.argv[3]
except IndexError: suffix = "rejoined"

output_suffix = f'_{suffix}.mp4'
source_filepath = pathlib.Path(source_video)
stills_dir = os.path.normpath(source_filepath.stem)

#  e x t r a c t   s t i l l s
command = f'ffmpeg -framerate {str(fps)} -i "{stills_dir}\\frame%03d.png" "{str(source_filepath).replace(source_filepath.suffix, output_suffix)}"'

# print(command)
os.system(command)
