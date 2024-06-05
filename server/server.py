import numpy as np
import pyrealsense2 as rs
from aiohttp import web
import socketio
import cv2
import base64
import ip as IP


# creates a new Async Socket IO Server
sio = socketio.AsyncServer()

# Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App instance
sio.attach(app)

async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on("hello")
async def another_event(data):
    print("User connected")
    await capture_video()

async def capture_video():
    # Configure the Intel RealSense camera
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)

    # Start the camera stream
    pipeline.start(config)

    while True:
        # Wait for the next frame from the camera
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # Convert the frame to an OpenCV image
        frame = np.asanyarray(color_frame.get_data())

        # Convert the frame to base64 string
        _, buffer = cv2.imencode('.jpg', frame)
        frame_str = base64.b64encode(buffer)

        # Send the frame to the client
        await sio.emit('frame', frame_str)
        await sio.sleep(0.01)

    # Stop the camera stream
    pipeline.stop()

app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, host=IP.getIP())
