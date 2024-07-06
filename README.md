# HastaTalk - Sign Language Gesture Recognition
HastaTalk is a tool for efficient sign language communication using hand gestures. This web-app uses Mediapipe for hand landmark detection and a Random Forest ML model to recognize ASL hand signs.

## Table of Contents
1. Features
2. Demo
3. Requirements
4. Installation
5. Usage
6. Acknowledgements

## Features
- Real-time hand sign recognition
- Ability to construct sentences from recognized signs
- Speech-to-text conversion of recognized gestures
- Toggle dark mode for better visibility

## Demo

https://github.com/omshetye/sign-lang-recognition/assets/103515277/f029c5bf-e861-4cfb-93a5-17f238bf119a


## Requirements
- Pyhon 3.9
- Flask
- Medipipe
- OpenCV
- Numpy
- Joblib

## Installation
You can run the app on your system locally by following the below set of instructions:
1. Clone the repository
     git clone https://github.com/omshetye/sign-lang-recognition.git
     cd sign-lang-recognition
   
3. Create a virtual environment and activate it:
     python -m venv venv
     source venv\Scripts\activate

4. Install the dependencies:
      pip install -r requirements.txt

## Usage
1. Running the application locally:
      python app.py

2. Open your browser and navigate to http://127.0.0.1:8000

## Acknowledgments
- Mediapipe for hand landmark detection.
- OpenCV for image processing.
- Flask for the web framework.
