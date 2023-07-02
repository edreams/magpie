document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('save-link').addEventListener('click', saveLink);
  document.getElementById('summarize-link').addEventListener('click', summarizeAndSaveLink);
  document.getElementById('get-summaries').addEventListener('click', getSummaries);
  document.getElementById('send-text').addEventListener('click', sendSelectedText);
});

function saveLink(e) {
  e.preventDefault();

  var status = document.getElementById('status');

  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    var activeTab = tabs[0];
    var user_id = "123";  // Fixed user ID

    var req = new XMLHttpRequest();
    var baseUrl = "https://soychile.org/save-link";
    var body = JSON.stringify({
      'url': activeTab.url,
      'user_id': user_id
    });

    req.open("POST", baseUrl, true);
    req.setRequestHeader("Content-Type", "application/json");
    req.send(body);

    req.onreadystatechange = function() {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        status.textContent = "Link saved successfully!";
      }
      else if (this.readyState === XMLHttpRequest.DONE && this.status === 400) {
        status.textContent = "400 Error";
      }
      else if (this.readyState === XMLHttpRequest.DONE && this.status === 500) {
        status.textContent = "500 Error";
      }
      else {
        status.textContent = "Error saving link. Please, try again.";
      }
    }
  });
}

function summarizeAndSaveLink(e) {
  e.preventDefault();

  var status = document.getElementById('status');

  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    var activeTab = tabs[0];
    var user_id = "123";  // Fixed user ID

    var req = new XMLHttpRequest();
    var baseUrl = "https://soychile.org/summarize-and-save";
    var body = JSON.stringify({
      'url': activeTab.url,
      'user_id': user_id
    });

    req.open("POST", baseUrl, true);
    req.setRequestHeader("Content-Type", "application/json");
    req.send(body);

    req.onreadystatechange = function() {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        status.textContent = "Link summarized and saved successfully!";
      }
    }
  });
}

function getSummaries(e) {
  e.preventDefault();

  var status = document.getElementById('status');
  var summariesContainer = document.getElementById('summaries');

  var user_id = "123";  // Fixed user ID

  var req = new XMLHttpRequest();
  var baseUrl = "https://soychile.org/get-summaries";
  var body = JSON.stringify({
    'user_id': user_id
  });

  req.open("POST", baseUrl, true);
  req.setRequestHeader("Content-Type", "application/json");
  req.send(body);

  req.onreadystatechange = function() {
    if (this.readyState === XMLHttpRequest.DONE) {
      if (this.status === 200) {
        var response = JSON.parse(this.responseText);

        summariesContainer.textContent = "";

        if (response.summaries.length === 0) {
          var noSummariesElement = document.createElement('p');
          noSummariesElement.textContent = "No summaries available.";
          summariesContainer.appendChild(noSummariesElement);
        } else {
          response.summaries.forEach(function(summary) {
            var summaryElement = document.createElement('p');
            summaryElement.textContent = summary.link + ": " + summary.summary;
            summariesContainer.appendChild(summaryElement);
          });
        }
      } else {
        status.textContent = "Error retrieving summaries. Please try again.";
      }
    }
  }
}


function sendSelectedText() {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    chrome.tabs.sendMessage(tabs[0].id, { action: 'getSelectedText' }, function(response) {
      if (response && response.selectedText) {
        sendSelectedTextToBackend(response.selectedText);
      }
    });
  });
}


function sendSelectedTextToBackend(selectedText) {
  const data = {
    text: selectedText
  };

  fetch('https://soychile.org/play-selected', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(function(response) {
      if (response.ok) {
        return response.blob(); // Ahora esperamos un objeto Blob desde el backend
      } else {
        throw new Error('Error sending text to the backend');
      }
    })
    .then(function(audioBlob) {
      // Reproducir el audio en la extensión de Chrome
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    })
    .catch(function(error) {
      console.error('Error in the request to the backend:', error);
    });
}
