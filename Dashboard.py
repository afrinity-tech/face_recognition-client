#!/usr/bin/env python3
import base64
import signal
import time
import cv2
import threading  # Import threading to run main() in a new thread
from fastapi.responses import StreamingResponse
import numpy as np
from fastapi import Response
from main import main  # Assuming main() is defined in another file
from nicegui import Client, app, core, run, ui

# In case you don't have a webcam, this will provide a black placeholder image.
black_1px = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjYGBg+A8AAQQBAHAgZQsAAAAASUVORK5CYII='
placeholder = Response(content=base64.b64decode(black_1px.encode('ascii')), media_type='image/png')

# Load the Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# State variables to control face detection and pause
face_detection_enabled = False
feed_paused = False
last_frame = None  # Stores the last frame to display when paused
main_thread = None  # To store the thread running the main() function

def convert(frame: np.ndarray) -> bytes:
    """Converts a frame from OpenCV to a JPEG image."""
    _, imencode_image = cv2.imencode('.jpg', frame)
    return imencode_image.tobytes()

def detect_faces(frame: np.ndarray) -> np.ndarray:
    """Detect faces in a frame and draw rectangles around them."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)  # Detect faces

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # Draw rectangle around face
    return frame

def setup() -> None:
    global face_detection_enabled, feed_paused, last_frame, main_thread

    # OpenCV is used to access the webcam.
    video_capture = cv2.VideoCapture(0)

    @app.get('/video/frame')
    async def grab_video_frame() -> Response:
        global last_frame

        if not video_capture.isOpened():
            return placeholder
        
        # If the feed is paused, return the last frame
        if feed_paused:
            if last_frame is not None:
                jpeg = await run.cpu_bound(convert, last_frame)
                return Response(content=jpeg, media_type='image/jpeg')
            else:
                return placeholder

        # Otherwise, read a new frame from the video stream
        _, frame = await run.io_bound(video_capture.read)
        if frame is None:
            return placeholder

        # If face detection is enabled, process the frame to detect faces
        if face_detection_enabled:
            frame_with_faces = await run.cpu_bound(detect_faces, frame)
        else:
            frame_with_faces = frame

        # Store the last frame before conversion
        last_frame = frame_with_faces

        # Convert the frame (with or without faces) to JPEG
        jpeg = await run.cpu_bound(convert, frame_with_faces)
        return Response(content=jpeg, media_type='image/jpeg')
    
    @app.get('/video/stream')
    async def video_stream():
        if not video_capture.isOpened():
            return placeholder

        def generate():
            while True:
                _, frame = video_capture.read()
                if frame is None:
                    break
                jpeg = convert(frame)
                # Yield each frame as part of the MJPEG stream
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')

        return StreamingResponse(generate(), media_type='multipart/x-mixed-replace; boundary=frame')

    # Button functions
    def toggle_face_detection() -> None:
        """Toggle face detection on or off and run main() in a separate thread."""
        global face_detection_enabled, main_thread
        face_detection_enabled = not face_detection_enabled

        if face_detection_enabled:
            # If face detection is enabled, run main() in a new thread
            if main_thread is None or not main_thread.is_alive():
                main_thread = threading.Thread(target=main)
                main_thread.start()
        print(f"Face detection {'enabled' if face_detection_enabled else 'disabled'}")

    def pause_feed() -> None:
        """Pause the video feed (freeze on the last frame)."""
        global feed_paused
        feed_paused = True
        print("Video feed paused")

    def resume_feed() -> None:
        """Resume the video feed."""
        global feed_paused
        feed_paused = False
        print("Video feed resumed")

    # UI layout for sidebar and main content
    with ui.row().classes('w-full h-screen'):
        with ui.column().classes('w-1/5 bg-gray-800 text-white h-full p-4'):
            ui.label("Dashboard Options").classes('text-2xl font-bold mb-4')
            ui.button('Pause', on_click=pause_feed).classes('w-full mb-2')
            ui.button('Resume', on_click=resume_feed).classes('w-full mb-2')
            ui.button('Detect face', on_click=toggle_face_detection).classes('w-full mb-2')
        with ui.column().classes('w-3/4 bg-cyan-200 p-4 h-full'):
            video_image = ui.interactive_image().classes('w-full h-full')
            ui.timer(interval=0.1, callback=lambda: video_image.set_source(f'/video/frame?{time.time()}'))

    async def disconnect() -> None:
        """Disconnect all clients from current running server."""
        for client_id in Client.instances:
            await core.sio.disconnect(client_id)

    def handle_sigint(signum, frame) -> None:
        ui.timer(0.1, disconnect, once=True)
        ui.timer(1, lambda: signal.default_int_handler(signum, frame), once=True)

    async def cleanup() -> None:
        await disconnect()
        video_capture.release()

    app.on_shutdown(cleanup)
    signal.signal(signal.SIGINT, handle_sigint)

app.on_startup(setup)
ui.run()
