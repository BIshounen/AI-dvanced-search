from flask import Flask, render_template, request
import torch
import sqlite3
import open_clip
import faiss
import numpy as np
from PIL import Image
import requests
from io import BytesIO

from config import EMBEDDINGS_PATH, MODEL_STATE_PATH, INDEX_PATH, MEDIATOR_URL, BEST_SHOT_URL, FRAME_URL

app = Flask(__name__)


def normalize_vector(vec):
  return vec / np.linalg.norm(vec, axis=1, keepdims=True)


def search_by_text_or_image(query, is_image, top_k=5):
  conn = sqlite3.connect(EMBEDDINGS_PATH)
  cursor = conn.cursor()

  device = "cuda" if torch.cuda.is_available() else "mps" if torch.mps.is_available() else "cpu"
  print(device)
  model, _, preprocess = open_clip.create_model_and_transforms("ViT-L/14-quickgelu", pretrained="openai",
                                                               device=device)
  model.to(device).eval()
  model.load_state_dict(torch.load(MODEL_STATE_PATH))

  with torch.no_grad():
    if not is_image:
      features = model.encode_text(open_clip.tokenize([query]).to(device)).cpu().numpy()
    else:
      response = requests.get(query)
      input_image = preprocess(Image.open(BytesIO(response.content)).convert('RGB')).unsqueeze(0).to(device)
      features = model.encode_image(input_image).to(device).cpu().numpy()

  index = faiss.read_index(INDEX_PATH)
  distances, indices = index.search(features, top_k)  # Search FAISS

  # Fetch timestamps from DB
  cursor.execute("SELECT timems, deviceid, trackid FROM embeddings WHERE id IN ({})".format(
    ",".join(str(i + 1) for i in indices[0])
  ))
  results = cursor.fetchall()
  cards = []
  print("\n🔍 Search Results for:", query)
  for idx, (time_ms, device_id, track_id) in enumerate(results):
    print(f"{idx + 1}. Timestamp: {time_ms} (score: {distances[0][idx]:.4f})")
    img_url = MEDIATOR_URL + BEST_SHOT_URL.format(track_id=track_id, device_id=device_id)
    search_url = '/search?query=' + img_url + '&is_image=true'
    cards.append({'time_ms': time_ms,
                  'device_id': device_id,
                  'track_id': track_id,
                  'img_url': img_url,
                  'search_url': search_url})

  return cards


@app.route('/')
def index_page():
  return render_template('index.html')


@app.route('/search')
def search():
  query = request.args.get('query')
  is_image = request.args.get('is_image')
  cards = search_by_text_or_image(query, is_image)
  return render_template('search.html', cards=cards)


@app.route('/canvas')
def canvas():
  return render_template('canvas.html', get_frame_url=MEDIATOR_URL+FRAME_URL)

app.run(port=5050)
