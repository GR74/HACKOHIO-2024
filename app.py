from flask import Flask, Response, render_template
import cv2
from ultralytics import YOLO

app = Flask(__name__)

model = YOLO('yolov8n-seg.pt')  # Ensure you have the model file in the same directory
list2 = [46, 47, 49]

cap = cv2.VideoCapture(0)  # Change to 1 or 2 if necessary
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)

is_running = False

def generate_frames():
    global is_running
    while is_running:
        success, frame = cap.read()
        if not success:
            break
        
        results = model.predict(frame, classes=list2, verbose=False)
        annotated_frame = results[0].plot()
        
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start')
def start():
    global is_running
    if not is_running:
        is_running = True
    return {"status": "Detection started"}

@app.route('/stop')
def stop():
    global is_running
    is_running = False
    return {"status": "Detection stopped"}

@app.route('/test.html')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
