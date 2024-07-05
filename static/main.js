function updateCameraButton(enabled) {
    const button = document.getElementById('camera-button');
    button.innerHTML = enabled ? '<i class="fas fa-camera-slash"></i> Disable Camera' : '<i class="fas fa-camera"></i>  Enable Camera';
    const videoFeed = document.getElementById('video-feed');
    if (enabled) {
        videoFeed.src = "/video_feed";
    } else {
        videoFeed.src = "static/icons/plaaceholder.jpeg";
    }
}


function toggleCamera() {
    axios.post('/camera')
        .then(response => {
            console.log(response.data); // Log response for debugging
            updateCameraButton(response.data.camera_enabled);
            if(response.data.camera_enabled) {
                setInterval(getPrediction, 2500);
            }
        })
        .catch(error => console.error('Error toggling camera:', error));
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

function getPrediction() {
    axios.get('/predict')
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
    
    // Check if there's something to remove
    if (textContent.length > 0) {
        predSentenceElement.value = textContent.slice(0, -1); // Remove the last character
    }
}

function clearWord() {
    var predSentenceElement = document.getElementById('pred-sentence');
    predSentenceElement.value= "";
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
            updateCameraButton(response.data.camera_enabled);
        })
        .catch(error => console.error('Error fetching initial camera state:', error));
});

document.addEventListener('DOMContentLoaded', function() {
    const checkbox = document.getElementById('dark-mode-checkbox');
  
    // Check if dark mode preference is saved in local storage
    if (localStorage.getItem('dark-mode') === 'enabled') {
      document.body.classList.add('dark-mode');
      checkbox.checked = true;
    }
  
    checkbox.addEventListener('change', function() {
      if (checkbox.checked) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('dark-mode', 'enabled'); // Save preference to local storage
      } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('dark-mode', 'disabled'); // Save preference to local storage
      }
    });
  });
  