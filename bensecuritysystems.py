import uvicorn
import cv2
import logging
import datetime
from fastapi import FastAPI, Response

app = FastAPI()
webcam = cv2.VideoCapture(0)

logging.basicConfig(level=logging.INFO)

async def frame_generator():
  pass

@app.get("/feed")
async def feed():  
  if not webcam.isOpened():
    return Response()

  ret, frame = webcam.read()

  if not ret:
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

  ret, jpeg = cv2.imencode(".jpg", frame)

  if not ret:
    logging.error("failed to encode frame")

  frame_bytes = jpeg.tobytes()

  return Response(content=frame_bytes, media_type="image/jpg")

if __name__ == "__main__":
  webcam = cv2.VideoCapture(0)
  uvicorn.run("bensecuritysystems:app", host="0.0.0.0", port=9999)

