import sqlite3
from time import sleep

import faiss
import open_clip
import torch
import os
from PIL import Image
import requests
import time
from io import BytesIO
import numpy as np

from config import DBPATH, MODEL_STATE_PATH, MEDIATOR_URL, OBJECT_TRACKS_PATH, BEST_SHOT_PATH, DELTA_TIME, INDEX_PATH

conn = sqlite3.connect(DBPATH)

cursor = conn.cursor()

cursor.execute(
  "CREATE TABLE IF NOT EXISTS embeddings (id INTEGER PRIMARY KEY, timems TEXT, deviceid TEXT, trackid TEXT)")
conn.commit()

device = "cuda" if torch.cuda.is_available() else "mps" if torch.mps.is_available() else "cpu"
print(device)
model, _, preprocess = open_clip.create_model_and_transforms("ViT-L/14-quickgelu", pretrained="openai",
                                                             device=device)
model.to(device).eval()

if not os.path.isfile(MODEL_STATE_PATH):
  torch.save(model.state_dict(), MODEL_STATE_PATH)
else:
  model.load_state_dict(torch.load(MODEL_STATE_PATH))

while True:

  print('started')
  current_time = time.time()
  start_time = int((time.time() - DELTA_TIME) * 1000)
  end_time = int(time.time() * 1000)

  params = {'start_time': start_time, 'end_time': end_time}
  test = requests.get(MEDIATOR_URL + OBJECT_TRACKS_PATH, params=params)
  object_tracks = requests.get(MEDIATOR_URL + OBJECT_TRACKS_PATH, params=params).json()

  print('got objects')

  index = None
  done = 0
  for track in object_tracks:
    response = requests.get(
      MEDIATOR_URL + BEST_SHOT_PATH.format(track_id=track['track_id'], device_id=track['device_id']))
    image = Image.open(BytesIO(response.content))
    image_tensor = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
      embedding = model.encode_image(image_tensor).cpu().numpy()

    if index is None:
      if os.path.isfile(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
      else:
        embedding_dim = embedding.shape[1]
        index = faiss.IndexFlatL2(embedding_dim)

    # print(embedding/np.linalg.norm(embedding, axis=1, keepdims=True))

    index.add(embedding/np.linalg.norm(embedding, axis=1, keepdims=True))
    cursor.execute(
      "INSERT INTO embeddings (timems, deviceid, trackid) VALUES (?,?,?)",
      (track['time_ms'], track['device_id'], track['track_id']))
    conn.commit()

    faiss.write_index(index, INDEX_PATH)
    done += 1
    print(done/len(object_tracks))

  elapsed_time = time.time() - current_time
  sleep(DELTA_TIME - elapsed_time)
