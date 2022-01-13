#  d o c s t r i n g s
"""
$ python pair_target_frames.py target_frames/recording006_blue100 80 > results.html
"""

#  d e p e n d e n c i e s
import base64, json, os, pathlib, requests, sys
import xml.etree.ElementTree as ET

#  h e l p e r   f u n c t i o n s
def convertBase64(message):
  message_bytes = message.encode('utf-8')
  base64_bytes = base64.b64encode(message_bytes)
  return base64_bytes.decode('ascii')

def getHashConfig(database, identifier):
  config_str = f"""
[Session]
Engine0 = ImageSource
Engine1 = ImageHash
Engine2 = Response

[ImageSource]
Type = image

[ImageHash]
Type = ImageHash
Database = {database}
Identifier = {identifier}
MatchThreshold = 0

[Response]
Type = Response
Input = ImageHash.Result
"""
  return convertBase64(config_str)

def getClassConfig(classifier):
  config_str = f"""
[Session]
Engine0 = ImageSource
Engine1 = ColorCluster
Engine2 = ImageClass
Engine3 = Response

[ImageSource]
Type = image

[ColorCluster]
Type = ColorCluster
SampleInterval = 1ms
ColorDictionary = basiccolors.dat
ColorThreshold = 5

[ImageClass]
Type = ImageClassification
Classifier = {classifier}
ClassificationThreshold = 0
MaxClassResults = 1

[Response]
Type = Response
Input = ColorCluster.Result,ImageClass.Result
"""
  return convertBase64(config_str)
  
def getSimilarityScore(config, source_image):
  x = requests.post(f"{API}process&config={config}&sync=true",
    files = [
      ('Source', open(source_image, 'rb'))
    ]
  )
  # print(x.text)

  root = ET.fromstring(x.text)
  return float(root.find(".//ImageHashResult/identity/confidence").text)
  
def getErrorClass(config, source_image):
  x = requests.post(f"{API}process&config={config}&sync=true",
    files = [
      ('Source', open(source_image, 'rb'))
    ]
  )
  # print(x.text)

  root = ET.fromstring(x.text)  
  clusters = root.findall(".//ColorClusterResult/cluster")
  first_cluster_proportion = float(clusters[0].find("proportion").text)
  
  if first_cluster_proportion > 70.0:
    return "monochrome", first_cluster_proportion

  identifier = root.find(".//ImageClassificationResult/classification/identifier").text
  confidence = root.find(".//ImageClassificationResult/classification/confidence").text
  return identifier, float(confidence)

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  m a i n   e x e c u t i o n
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 0. Define variables:
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
API = "http://localhost:14000/action="

SOURCE_DIR = os.path.normpath(
  os.path.join(
    "C:\\MicroFocus\\MediaServer_12.10.0_WINDOWS_X86_64\\output", 
    sys.argv[1]
  )
)

SIMILARITY_THRESHOLD = float(sys.argv[2])
FILESTEM = pathlib.Path(SOURCE_DIR).stem
DB_NAME = FILESTEM.split("_")[0] + "_rejoined"

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 1. Collect list of golden record frame identifiers:
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
x = requests.get(f"{API}ListImageHashes&database={DB_NAME}")
# print(x.text)
root = ET.fromstring(x.text)

identifier_list = []
for entry in root.findall(".//entry"):
  identifier_list.append(entry.find("identifier").text)

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 2. Attempt to pair probe frames with golden record frames:
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print("Looking for pairs...")
pairs = []

for filename in os.listdir(SOURCE_DIR):
  if not filename.endswith(".png"): continue
  print(filename)

  source_image = os.path.join(SOURCE_DIR, filename)

  for i in range(len(pairs), len(identifier_list)):
    # Iterating over unpaired golden record identities.
    
    similarity_score = getSimilarityScore(
      getHashConfig(DB_NAME, identifier_list[i]),
      source_image
    )

    if similarity_score >= SIMILARITY_THRESHOLD:
      pairs.append({
        "probe": filename,
        "gold": identifier_list[i],
        "similarity": similarity_score
      })
      break

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 3. Attempt to classify unpaired frames from error database
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print("Looking for error types...")
errors = []

for filename in os.listdir(SOURCE_DIR):
  if not filename.endswith(".png"): continue
  print(filename)

  is_paired = False
  for pair in pairs:
    if pair["probe"] == filename:
      is_paired = True

  if not is_paired:
    error_class, class_score = getErrorClass(
      getClassConfig("Imagenet"),
      os.path.join(SOURCE_DIR, filename)
    )

    errors.append({
      "probe": filename,
      "class": error_class,
      "similarity": class_score
    })

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 4. Save results
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
results = {
  "gold": identifier_list,
  "paired": pairs,
  "unpaired": errors
}

with open(f'{FILESTEM}.json', 'w') as f:
  f.write(json.dumps(results, indent=2))
