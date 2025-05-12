import os

import API_paths
import json
from requests import request

import utils
from configs import (INTEGRATION_MANIFEST_PATH, ENGINE_MANIFEST_PATH,
                     DEVICE_AGENT_MANIFEST_PATH, CREDENTIALS_PATH, SERVER_URL)
from utils import authenticate

import cv2
import av
import io
from PIL import Image


class VMSRegistrator:

  def __init__(self):

    self._is_approved = False

    if os.path.exists(CREDENTIALS_PATH):
      self._is_approved = self.is_approved()
    else:
      url = SERVER_URL + API_paths.REGISTRATION_PATH
      with open(INTEGRATION_MANIFEST_PATH) as f:
        integration_manifest = json.load(f)
      with open(ENGINE_MANIFEST_PATH) as f:
        engine_manifest = json.load(f)
      with open(DEVICE_AGENT_MANIFEST_PATH) as f:
        device_agent_manifest = json.load(f)

      params = {
        "integrationManifest": integration_manifest,
        "engineManifest": engine_manifest,
        "deviceAgentManifest": device_agent_manifest,
        "isRestOnly": True,
        "pinCode": "9809"
                }
      result = request(url=url, method="POST", json=params, verify=False).json()
      credentials = {'password': result['password'], 'username': result['username']}
      with open(CREDENTIALS_PATH, 'w') as f:
        json.dump(credentials, f)

  def is_approved(self):

    if not self._is_approved:
      with open(CREDENTIALS_PATH) as f:
        credentials = json.load(f)
      token = authenticate()
      url = SERVER_URL + API_paths.USER_PATH + '/' + credentials['username']
      headers = {"Authorization": "Bearer " + token}
      result = request(url=url, method="GET", headers=headers, verify=False).json()
      return result['parameters']['integrationRequestData']['isApproved']

    else:
      return True

  @staticmethod
  def get_object_tracks(start_time, end_time):
    token = utils.authenticate()

    object_tracks = []

    url = SERVER_URL + API_paths.OBJECT_TRACKS_PATH
    params = {'startTimeMs': start_time, 'endTimeMs': end_time}
    headers = {"Authorization": "Bearer " + token}
    result = request(url=url, method="GET", headers=headers, params=params, verify=False).json()
    print(request(url=url, method="GET", headers=headers, params=params, verify=False).url)

    for object_track in result:
      # time_ms = object_track['firstAppearanceTimeMs']
      time_ms = object_track['bestShot']['timestampMs']
      track_id = object_track['id']
      device_id = object_track['deviceId']

      object_tracks.append({
        'time_ms': time_ms,
        'track_id': track_id,
        'device_id': device_id
      })

    return object_tracks

  @staticmethod
  def get_best_shot(device_id, track_id):


    token = utils.authenticate()

    url = SERVER_URL + API_paths.BEST_SHOT_PATH.format(id=track_id)
    params = {'deviceId': device_id}
    headers = {"Authorization": "Bearer " + token}
    result = request(url=url, method="GET", headers=headers, params=params, verify=False).content

    return result

  @staticmethod
  def get_frame(device_id, timestamp, rect=(0, 0, 1, 1)):
    token = utils.authenticate()
    print(timestamp)

    url = SERVER_URL + API_paths.HTTP_STREAM_PATH.format(id=device_id)
    params = {'positionMs': timestamp, 'endPositionMs': timestamp, 'accurateSeek': 'true', 'stream': 'primary'}
    headers = {"Authorization": "Bearer " + token}
    result = request(url=url, method="GET", headers=headers, params=params, verify=False)
    print(result)

    if type(rect) == str:
      rect = rect.strip('()')
      rect = rect.split(',')
      print('a string')

    if result.content is not None and result.content != b'':
      container = av.open(io.BytesIO(result.content))
      for frame in container.decode(video=0):
        img = frame.to_ndarray(format='bgr24')
        image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        x1 = float(rect[0]) * image.width
        x2 = float(rect[2]) * image.width
        y1 = float(rect[1]) * image.height
        y2 = float(rect[3]) * image.height

        print(rect)
        print(x1, x2, y1, y2)

        image = image.crop((x1, y1, x2, y2))
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        return buf.getvalue()
    else:
      return None
