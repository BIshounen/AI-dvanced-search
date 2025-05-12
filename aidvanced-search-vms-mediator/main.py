from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import time


from vms_registrator import VMSRegistrator

vms_registrator = VMSRegistrator()

vms_registrator.get_frame("e3e9a385-7fe0-3ba5-5482-a86cde7faf48", 1745659512152)

app = FastAPI()

origins = [
  "http://localhost",
  "http://localhost:5050",
  "http://127.0.0.1:5050",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_approved():
  return {'approved': vms_registrator.is_approved()}


@app.get("/object-tracks")
def get_object_tracks(start_time: int = None, end_time: int = None):
  print(start_time, end_time)
  return vms_registrator.get_object_tracks(start_time, end_time)


@app.get("/devices/{device_id}/best-shots/{track_id}",
         responses = {
           200: {
             "content": {"image/png": {}}
           }
         },
         response_class=Response
         )
def get_best_shot(device_id: str, track_id: str):
  print(device_id, track_id)
  return Response(content=vms_registrator.get_best_shot(device_id, track_id), media_type="image/png")

@app.get("/devices/{device_id}/frame",
         responses = {
           200: {
             "content": {"image/png": {}}
           }
         },
         response_class=Response
         )
def get_frame(device_id: str, rect=None, timestamp: int=time.time()*1000):
  print(rect)
  if rect is None:
    rect = (0, 0, 1, 1)
  return Response(content=vms_registrator.get_frame(device_id, timestamp, rect), media_type="image/png")
