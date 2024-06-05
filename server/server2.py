from aiohttp import web
import socketio
import ip as IP
import base64
import cv2

# creates a new Async Socket IO Server
sio = socketio.AsyncServer()

# Creates a new Aiohttp Web Application
app = web.Application()
# Binds our Socket.IO server to our Web App
sio.attach(app)

async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on("hello")
async def another_event(data):
    print("user connected ")
    await capture_video()

async def capture_video():
    # Open the video capture
    cap = cv2.VideoCapture(0)

    while True:
        # Read the current frame
        ret, frame = cap.read()
     
        # # Convert the frame to base64 string
        _, buffer = cv2.imencode('.jpg', frame)
        frame_str = base64.b64encode(buffer)
        
        # print(len(frame_str))
        #cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
         break

        # # Send the frame to the client
        await sio.emit('frame', frame_str)
        await sio.sleep(0.01)

    cap.release()

app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app , host=IP.getIP())