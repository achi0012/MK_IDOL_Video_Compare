# docstrings
"""
$ python process.py ct_news/recording006_testcard150.mp4 keyframes.cfg
"""
import os, requests, sys

api = "http://localhost:14000/action="

source_video = os.path.normpath(os.path.join(os.getcwd(), sys.argv[1]))
config_file = os.path.normpath(os.path.join(os.getcwd(), sys.argv[2]))

x = requests.post(f"{api}process",
  files = [
    ('Config', open(config_file, 'rb')),
    ('Source', open(source_video, 'rb'))
  ]
)
print(x.text)

print('http://localhost:14000/a=queueinfo&queueaction=getstatus&queuename=process')
