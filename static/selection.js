document.getElementById("select_photo").addEventListener("click", function() {
    document.querySelector(".editor").scrollIntoView({ 
        behavior: 'smooth' 
    });
});



let selectedFilenames = [];

function toggleSelection(element, filename) {
    element.classList.toggle('selected');
    if (selectedFilenames.includes(filename)) {
        console.log("Selected filenames:", selectedFilenames);
        // Deselecting: remove filename from the array
        const index = selectedFilenames.indexOf(filename);
        if (index !== -1) {
            selectedFilenames.splice(index, 1);
        }
    } else {
        // Selecting: add filename to the array
        selectedFilenames.push(filename);
    }
    console.log("***Selected filenames:", selectedFilenames);
}

function saveSelection() {
    // Send selected filenames to Python using AJAX
    fetch('/save_selected_photos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filenames: selectedFilenames })
    })
    .then(response => {
        if (response.ok) {
            console.log('Selected filenames sent successfully');
        } else {
            console.error('Failed to send selected filenames');
        }
    })
    .catch(error => {
        console.error('Error sending selected filenames:', error);
    });
}

function searchImages() {
    var query = document.getElementById('search-bar').value.trim().toLowerCase();

    if (query === '') {
        clearSearchResults(); // Clear search results box if query is empty
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/search?query=' + encodeURIComponent(query), true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    displaySearchResults(response.images, query);
                } else {
                    displaySearchResults([], query);
                }
            } else {
                displayErrorMessage();
            }
        }
    };
    xhr.send();
}

function displaySearchResults(images, query) {
    var resultDiv = document.getElementById('search-result-message');
    resultDiv.innerHTML = '';

    if (images.length > 0) {
        var resultMessage = 'Found ' + images.length + ' image(s):<br>';
        images.forEach(function(image) {
            resultMessage += '<div class="search-result-item">' + image + '</div>';
        });
        resultDiv.innerHTML = resultMessage;

        // Scale up the searched image
        var searchedImage = document.querySelector('.edit-box[title="' + query + '"]');
        if (searchedImage) {
            searchedImage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            searchedImage.style.transition = 'transform 0.3s ease-in-out';
            searchedImage.style.transform = 'scale(1.1)';
        }
    } else {
        resultDiv.innerHTML = 'No images found for the given query.';
    }
}

function clearSearchResults() {
    var resultDiv = document.getElementById('search-result-message');
    resultDiv.innerHTML = '';

    // Reset all scaled images to their normal size
    var scaledImages = document.querySelectorAll('.edit-box');
    scaledImages.forEach(function(image) {
        image.style.transition = 'none';
        image.style.transform = 'scale(1)';
    });
}

// Function to apply style for matched filenames
function applyMatchedStyle(matchedFilenames) {
    matchedFilenames.forEach(function(filename) {
        var matchedBox = document.querySelector('.edit-box[data-filename="' + filename + '"]');
        if (matchedBox) {
            matchedBox.classList.add('matched-filename');
        }
    });
}

// Function to display "Filename not found" message on the page
function displayNotFoundMessage() {
    var messageContainer = document.getElementById('search-message');
    messageContainer.textContent = 'Filename not found.';
}

// Function to display error message on the page
function displayErrorMessage() {
    var messageContainer = document.getElementById('search-message');
    messageContainer.textContent = 'Error occurred while searching.';
}


function addTransition() {
    fetch('/add_transition', {
        method: 'GET',
    })
    .then(response => {
        if (response.ok) {
            console.log('Add transition request sent successfully');
            return response.json();
        } else {
            throw new Error('Failed to send add transition request');
        }
    })
    .then(data => {
        if (!data.video_url) {
            throw new Error('No video_url in response');
        }
        let videoUrl = data.video_url;
        console.log('Video URL:', videoUrl);

        // Update the video element to display the newly created video
        setTimeout(() => {
            let videoTag = document.getElementById('video-preview');
            videoTag.src = videoUrl;
            videoTag.type = 'video/mp4';
            videoTag.load();
            videoTag.play(); // Start playing the video automatically
        }, 3000);
    })
    .catch(error => {
        console.error('Error sending add transition request:', error);
    });
}

// Event listener for the "fade" button
document.getElementById("fade").addEventListener("click", function() {
    addTransition();
});

document.getElementById("rotate").addEventListener("click", function() {
    addTransition_rotate();
});

// Function to trigger the add_transition function in Python
function addTransition_rotate() {
    fetch('/add_transition_rotate', {
        method: 'GET',
    })
    .then(response => {
        if (response.ok) {
            console.log('Add transition request sent successfully');
            return response.json();
        } else {
            throw new Error('Failed to send add transition request');
        }
    })
    .then(data => {
        if (!data.video_url) {
            throw new Error('No video_url in response');
        }
        let videoUrl = data.video_url;
        console.log('Video URL:', videoUrl);

        // Update the video element to display the newly created video
        setTimeout(() => {
            let videoTag = document.getElementById('video-preview');
            videoTag.src = videoUrl;
            videoTag.type = 'video/mp4';
            videoTag.load();
            videoTag.play(); // Start playing the video automatically
        }, 3000);
    })
    .catch(error => {
        console.error('Error sending add transition request:', error);
    });
}




