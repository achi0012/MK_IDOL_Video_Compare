# docstrings
"""
$ python train_image_hash.py target_frames/recording006
"""
import os, pathlib, requests, sys

api = "http://localhost:14000/action="
ms_dir = "C:\\MicroFocus\\MediaServer_12.10.0_WINDOWS_X86_64"

source_dir = os.path.normpath(os.path.join(
  ms_dir, "output", sys.argv[1]
))

source_filepath = pathlib.Path(source_dir)
db_name = source_filepath.stem
print(db_name)

x = requests.get(f"{api}RemoveImageHashDatabase&database={db_name}")
print(x.text)

x = requests.get(f"{api}CreateImageHashDatabase&database={db_name}")
print(x.text)

for filename in os.listdir(source_dir):
  if not filename.endswith(".png"): continue

  source_image = os.path.join(source_dir, filename)
  identifier = filename.replace('.png', '')

  x = requests.post(f"{api}TrainImageHash&database={db_name}&identifier={identifier}&imagelabel={identifier}",
    files = [
      ('ImageData', open(source_image, 'rb'))
    ]
  )
  print(x.text)

  print('http://localhost:14000/a=gui#/train/imageHash(tool:select)')
