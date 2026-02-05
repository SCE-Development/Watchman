import uvicorn
import cv2
import logging
import datetime
import asyncio
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

logging.basicConfig(
  format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
  datefmt="%Y-%m-%dT%H:%M:%S",
  level=logging.INFO
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app):
  yield
  webcam.release()

app = FastAPI(lifespan=lifespan)

def get_frame_bytes():
  if not webcam or not webcam.isOpened():
    return

  did_read_frame, frame = webcam.read()

  if not did_read_frame:
    logging.error("failed to read frame from webcam")

  cv2.putText(
    img=frame, 
    text="beninator security systems", 
    fontFace=cv2.FONT_HERSHEY_COMPLEX, 
    fontScale=1, 
    thickness=1, 
    color=(255, 255, 255),
    org=(10, 20)
  )

  encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
  did_encode_frame, jpeg = cv2.imencode(".jpg", frame, encode_param)

  if not did_encode_frame:
    logging.error("failed to encode frame")    

  return jpeg.tobytes()

async def frame_generator():
  while True:
    frame = get_frame_bytes()
    if frame:
      yield (
        b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
      )

    await asyncio.sleep(0.15)

@app.get("/feed")
async def feed(): 
  if not webcam or not webcam.isOpened():
    return Response("NO FEED - FAILED TO OPEN WEBCAM")

  return StreamingResponse(
    frame_generator(),
    media_type='multipart/x-mixed-replace; boundary=frame'
  )

if __name__ == "bensecuritysystems":
  webcam = cv2.VideoCapture(0)

if __name__ == "__main__":
  uvicorn.run("bensecuritysystems:app", host="0.0.0.0", port=9999)