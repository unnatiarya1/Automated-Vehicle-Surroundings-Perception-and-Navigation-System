import asyncio
import socketio
import cv2
import base64
import numpy as np
import lane2 as sl


sio = socketio.AsyncClient()
# sio = socketio.AsyncClient(ssl_verify=False)
Signaling_Server_Url = 'http://192.168.11.109:8080'

output_video_path = '/Users/unnat/projects/integrated_lanes/client/data/d1_test24.mp4'
output_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'),30, (640, 480))

@sio.event
async def connect():
    print("Connected")
    await sio.emit("hello")

@sio.event
async def disconnect():
    print("Disconnect")

@sio.on("frame")
async def cam(frame_base64):
    # print(len(frame_base64))
    frame_bytes = base64.b64decode(frame_base64)

    # Convert the bytes to a NumPy array
    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)

    # Decode the array into an OpenCV frame
    frame = cv2.imdecode(frame_array, flags=cv2.IMREAD_COLOR)

    video = sl.mainn(frame)

    output_writer.write(video)


    cv2.waitKey(1)
	
    return frame
    
async def main():
    await sio.connect(Signaling_Server_Url)
    await sio.wait()

asyncio.run(main())  

# Release the VideoWriter and close the OpenCV windows
output_writer.release()
cv2.destroyAllWindows()
