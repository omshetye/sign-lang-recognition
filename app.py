from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
import mediapipe as mp
import joblib
import cv2
import pyttsx3
import threading

app = Flask(__name__)
camera_enabled = False

# Load the model
model_path = 'model/model_2.p'
model_dict = joblib.load(model_path)
model = model_dict['model']

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

@app.route('/camera', methods=['POST'])
def toggle_camera():
    global camera_enabled
    camera_enabled = not camera_enabled
    return jsonify({'camera_enabled': camera_enabled})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    frame_data = data.get('frame', '')
    
    if frame_data:
        # Decode base64 image data
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        # Convert to numpy array
        frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
        # Decode image
        if frame_np is not None:
            frame = cv2.imdecode(frame_np, flags=cv2.IMREAD_COLOR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            
            data_aux = []
            x_ = []
            y_ = []

            if results.multi_hand_landmarks:
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
                        print(predicted_character)
                        return jsonify(prediction=predicted_character)
                    else:
                        return jsonify(prediction="No valid hand landmarks detected")
                else:
                    return jsonify(prediction="No valid hand landmarks detected")
            else:
                return jsonify(prediction="")
        else:
            return jsonify(prediction="Frame data not received")

@app.route('/stream_video', methods=['POST'])
def stream_video():
    data = request.json
    frame_data = data.get('frame', '')
    
    if frame_data:
        # Decode base64 image data
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        # Convert to numpy array
        frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
        # Decode image
        frame = cv2.imdecode(frame_np, flags=cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        data_aux = []
        x_ = []
        y_ = []

        if results.multi_hand_landmarks:
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
    else:
        return jsonify(prediction="Frame data not received")
    
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
