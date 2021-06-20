import threading
from flask import Response, Flask
import cv2

app = Flask(__name__)

global video_frame

global thread_lock
thread_lock = threading.Lock()

# camera parameters
width = 224
height = 224
fps = 21
capture_width = 3280
capture_height = 2464

GSTREAMER_PIPELINE = ('nvarguscamerasrc ! video/x-raw(memory:NVMM), '
    f'width={capture_width}, height={capture_height}, '
    f'format=(string)NV12, framerate=(fraction){fps}/1 ! nvvidconv ! '
    f'video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! '
    'appsink wait-on-eos=false max-buffers=1 drop=True')

# the thread to get video frames
def get_video_frame():

    # declare global variable
    global video_frame, thread_lock

    # use the cv2 VideoCapture
    video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)

    while video_capture.isOpened():
        return_key, frame = video_capture.read()
        if not return_key:
            break
        
        # save the frame into the global variable
        with thread_lock:
            video_frame = frame.copy()

        key = cv2.waitKey(30) & 0xff
        if key == 27:
            break
    
    video_capture.release()


# flask application behaviors
def stream_encoded_frame():
    global thread_lock
    
    while True:
        with thread_lock:
            global video_frame

            if video_frame is None:
                continue

            return_key, encoded_frame = cv2.imencode(".jpg", video_frame)

            if not return_key:
                continue

        yield (b'--frame\r\n'
            b'Content-Type:image/jpeg\r\n\r\n'
            + bytearray(video_frame) +
            b'\r\n')

@app.route('/')
def stream_video():
    return Response(stream_encoded_frame(), mimetype='multipart/x-mixed-replace;boundary=frame')

# main thread
if __name__ == '__main__':
    # start the thread for getting video frames
    get_video_thread = threading.Thread(target=get_video_frame)
    get_video_thread.daemon = True
    get_video_thread.start()


    # start the flask application
    app.run('0.0.0.0', port='8000')
