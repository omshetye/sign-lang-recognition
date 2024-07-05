from flask import Flask, render_template, request, Response, jsonify
import pickle
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading

app = Flask(__name__)
camera_enabled = False
cap = None

# Load the model
model_path = 'model/model_2.p'
model_dict = pickle.load(open(model_path, 'rb'))
model = model_dict['model']

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

def gen_frames():
    global cap, camera_enabled
    while True:
        if camera_enabled and cap and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')

@app.route('/camera', methods=['POST'])
def toggle_camera():
    global camera_enabled, cap
    camera_enabled = not camera_enabled
    if camera_enabled:
        cap = cv2.VideoCapture(0)
    else:
        if cap:
            cap.release()
            cap = None
    return jsonify({'camera_enabled': camera_enabled})

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/predict', methods=['GET'])
def predict():
    global cap
    if cap is None or not cap.isOpened():
        return jsonify(prediction="")

    ret, frame = cap.read()
    if not ret:
        return jsonify(prediction="Failed to capture frame")
    data_aux = []
    x_ = []
    y_ = []

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        print(f"Number of landmarks detected: {len(results.multi_hand_landmarks)}")
        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)

        if len(x_) > 0 and len(y_) > 0:
            min_x = min(x_)
            min_y = min(y_)
            
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min_x)
                data_aux.append(y - min_y)

            if len(data_aux) > 0:
                prediction = model.predict([np.asarray(data_aux)])
                predicted_character = prediction[0]
                return jsonify(prediction=predicted_character)
            else:
                return jsonify(prediction="No valid hand landmarks detected")
        else:
            return jsonify(prediction="No valid hand landmarks detected")
    else:
        return jsonify(prediction="")


def speak_text(text):
    # Reinitialize the pyttsx3 engine within the thread
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Adjust speaking rate (default is 200)
    # Change voice (optional)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()


@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
  
    if text:
        # Run the text-to-speech in a separate thread
        tts_thread = threading.Thread(target=speak_text, args=(text,))
        tts_thread.start()
        return jsonify({'status': 'success', 'message': 'Text has been spoken'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No text provided'}), 400


if __name__ == '__main__':
    app.run(debug=True)
