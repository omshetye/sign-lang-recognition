const video = document.getElementById('videoElement');
let stream = null;

function startCamera() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(usrStream) {
                stream = usrStream;
                video.srcObject = stream;
                video.play();
                captureFrame();
            })
            .catch(function(err) {
                console.error('Error accessing the camera:', err);
            });
    } else {
        console.error('getUserMedia is not supported by this browser');
    }
}

function sendTextToTts() {
    const text = document.getElementById('pred-sentence').value
    const speakButton = document.getElementById('speak-button');
    speakButton.disabled = true;
    axios.post('/speak', { text: text })
        .then(response => {
            // Log the response if needed
            console.log(response.data.message);
        })
        .catch(error => {
            // Handle errors if needed
            console.error('Error sending text for TTS:', error);
        });

    // Re-enable the button after 2 seconds
    setTimeout(() => {
        speakButton.disabled = false;
        ttsStatus.innerText = '';
    }, 2000);
}

function toggleCamera() {
    if (!stream) {
        startCamera();
        document.getElementById('camera-button').innerHTML = '<i class="fas fa-camera-slash"></i> Disable Camera';
    } else {
        stopCamera();
        document.getElementById('camera-button').innerHTML = '<i class="fas fa-camera"></i> Enable Camera';
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        stream = null;
    }
}

function captureFrame() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageDataURL = canvas.toDataURL('image/jpeg');
    sendFrame(imageDataURL);

    setTimeout(captureFrame, 2000); // Adjust frame capture interval as needed
}

function sendFrame(imageDataURL) {
    axios.post('/predict', { frame: imageDataURL })
        .then(response => {
            const prediction = response.data.prediction;
            if (prediction === 'space') {
                document.getElementById('prediction').innerText = 'Current prediction: ' + prediction;
                addSpace();
            } else if (prediction === 'back') {
                document.getElementById('prediction').innerText = 'Current prediction: ' + prediction;
                removeLastCharacter();
            } else {
                document.getElementById('prediction').innerText = 'Current prediction: ' + prediction;
                document.getElementById('pred-sentence').value += prediction;
            }
        })
        .catch(error => {
            console.error('Error getting prediction:', error);
            document.getElementById('prediction').innerText = 'Error fetching prediction';
        });
}

function removeLastCharacter() {
    var predSentenceElement = document.getElementById('pred-sentence');
    var textContent = predSentenceElement.value;
    
    if (textContent.length > 0) {
        predSentenceElement.value = textContent.slice(0, -1);
    }
}

function clearWord() {
    document.getElementById('pred-sentence').value = '';
}

const spaceChar = "  ";

function addSpace() {
    var predSentenceElement = document.getElementById('pred-sentence');
    if (predSentenceElement.value.length > 0) {
        predSentenceElement.value += `${spaceChar}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    axios.get('/camera')
        .then(response => {
            if (response.data.camera_enabled) {
                startCamera();
                document.getElementById('camera-button').innerHTML = '<i class="fas fa-camera-slash"></i> Disable Camera';
            } else {
                stopCamera();
                document.getElementById('camera-button').innerHTML = '<i class="fas fa-camera"></i> Enable Camera';
            }
        })
        .catch(error => console.error('Error fetching initial camera state:', error));
});

document.addEventListener('DOMContentLoaded', function() {
    const checkbox = document.getElementById('dark-mode-checkbox');
  
    if (localStorage.getItem('dark-mode') === 'enabled') {
      document.body.classList.add('dark-mode');
      checkbox.checked = true;
    }
  
    checkbox.addEventListener('change', function() {
      if (checkbox.checked) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('dark-mode', 'enabled');
      } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('dark-mode', 'disabled');
      }
    });
});
