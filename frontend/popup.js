document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('save-link').addEventListener('click', saveLink);
  document.getElementById('standard-summary').addEventListener('click', summarizeAndSaveLink);
  document.getElementById('simple-summary').addEventListener('click', simpleSummary);
  document.getElementById('get-summaries').addEventListener('click', myLibrary);
  document.getElementById('send-text').addEventListener('click', sendSelectedText);
});

function saveLink(e) {
  e.preventDefault();

  var status = document.getElementById('status');

  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var activeTab = tabs[0];
    var user_id = "123";  // Fixed user ID

    var req = new XMLHttpRequest();
    var baseUrl = "http://localhost:5000/save-link";
    var body = JSON.stringify({
      'url': activeTab.url,
      'user_id': user_id
    });

    req.open("POST", baseUrl, true);
    req.setRequestHeader("Content-Type", "application/json");
    req.send(body);

    req.onreadystatechange = function () {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        status.textContent = "Link saved successfully!";
      }
      else if (this.readyState === XMLHttpRequest.DONE && this.status === 400) {
        status.textContent = "400 Error";
      }
      else if (this.readyState === XMLHttpRequest.DONE && this.status === 500) {
        status.textContent = "500 Error";
      }
      else if (this.readyState === XMLHttpRequest.DONE && this.status === 409) {
        status.textContent = "Link already saved!";
      }
      else {
        status.textContent = "Error saving link. Please try again.";
      }
    }
  });
}

function summarizeAndSaveLink(e) {
  e.preventDefault();

  var status = document.getElementById('status');
  var summary = document.getElementById('summary');

  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var activeTab = tabs[0];
    var user_id = "123";  // Fixed user ID

    var req = new XMLHttpRequest();
    var baseUrl = "http://localhost:5000/summarize-and-save";
    var body = JSON.stringify({
      'url': activeTab.url,
      'user_id': user_id
    });

    req.open("POST", baseUrl, true);
    req.setRequestHeader("Content-Type", "application/json");
    req.send(body);

    // req.onreadystatechange = function() {
    //   if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
    //     status.textContent = "Link summarized and saved successfully!";
    //   }
    // }
    status.textContent = "Loading...";
    summary.textContent = "";
    req.onreadystatechange = function () {
      if (this.readyState === XMLHttpRequest.DONE) {
        if (this.status === 200) {
          var response = JSON.parse(this.responseText);

          summary.textContent = "";
          status.textContent = "Loading...";
          if (response.length === 0) {
            var noSummariesElement = document.createElement('p');
            noSummariesElement.textContent = "No summaries available.";
            status.textContent = "No summaries available.";
            //summaryContainer.appendChild(noSummariesElement);
          } else {
            summary_div = document.getElementById('summary');
            body_tag = document.getElementsByTagName('body')[0];

            body_tag.style.padding = "20px 100px 20px 100px";
            summary_div.style.width = "150%";
            summary.textContent = response.trim();
            // console.log(response);
            status.innerHTML = "<b>Your summary:</b>";
          }
        } else {
          status.textContent = "Error retrieving summaries. Please try again.";
        }
      }
    }
  });
}

function simpleSummary(e) {
  e.preventDefault();

  var status = document.getElementById('status');
  var summary = document.getElementById('summary');

  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var activeTab = tabs[0];
    var user_id = "123";  // Fixed user ID

    var req = new XMLHttpRequest();
    var baseUrl = "http://localhost:5000/simple-summary";
    var body = JSON.stringify({
      'url': activeTab.url,
      'user_id': user_id
    });

    req.open("POST", baseUrl, true);
    req.setRequestHeader("Content-Type", "application/json");
    req.send(body);

    status.textContent = "Loading...";
    summary.textContent = "";

    req.onreadystatechange = function () {
      if (this.readyState === XMLHttpRequest.DONE) {
        if (this.status === 200) {
          var response = JSON.parse(this.responseText);
          console.log(response.length);
          console.log(response);
          summary.textContent = "";
          if (response.length === 0) {
            var noSummariesElement = document.createElement('p');
            noSummariesElement.textContent = "No summaries available.";
            status.textContent = "No summaries available.";
            //summaryContainer.appendChild(noSummariesElement);
          } else {

            summary_div = document.getElementById('summary');
            body_tag = document.getElementsByTagName('body')[0];

            body_tag.style.padding = "20px 100px 20px 100px";
            summary_div.style.width = "150%";
            summary.textContent = response.trim();

            console.log(response);
            status.innerHTML = "<b>Simplified summary:</b>";
          }
        } else {
          status.textContent = "Error retrieving summaries. Please try again.";
        }
      }
    }
  });
}

// function to play audio from file location
function speak(audioPath) {
  const audio = new Audio(audioPath);
  audio.play();
}

function myLibrary() {
  created_tab = chrome.tabs.create({ url: './templates/index3.html' });
  console.log(`Created tab: ${created_tab}`);
  // created_tab.then(getSummaries, (err) => {console.log(err);});
}

function getSummaries() {
  // e.preventDefault();
  // document = tab.document;
  console.log("Hello!");
  console.log(document.getElementsByTagName("*"))
  var status = document.getElementById('status');

  console.log(status);
  // console.log(summariesContainer);

  var user_id = "123";  // Fixed user ID

  // Response part from backend
  var req = new XMLHttpRequest();
  var baseUrl = "http://localhost:5000/get-summaries";
  var body = JSON.stringify({
    'user_id': user_id
  });

  req.open("POST", baseUrl, true);
  req.setRequestHeader("Content-Type", "application/json");
  req.send(body);

  req.onreadystatechange = function () {
    if (this.readyState === XMLHttpRequest.DONE) {
      if (this.status === 200) {
        console.log(this.responseText);
        var response = JSON.parse(this.responseText);
        console.log(response);

        var summariesContainer = document.getElementById('summaries');
        summariesContainer.textContent = "";

        if (response.summaries.length === 0) {
          var noSummariesElement = document.createElement('p');
          noSummariesElement.textContent = "No summaries available.";
          summariesContainer.appendChild(noSummariesElement);
        } else {
          // response.summaries.forEach(function(summary) {
          //   var summaryElement = document.createElement('p');
          //   summaryElement.textContent = summary.link + ": " + summary.summary;
          //   summariesContainer.appendChild(summaryElement);
          // });
          for (let i = 0; i < response.summaries.length; i++) {
            var headline = response.summaries[i].headline;
            console.log(headline);
            const sectionButton = document.createElement('a');
            sectionButton.classList.add('section-button');
            sectionButton.href = response.summaries[i].link;
            sectionButton.target = '_blank';
            sectionButton.textContent = (i + 1) + ". " + headline;


            var audioFile = `../backend/audio/${response.summaries[i].headline}.mp3`;
            const voiceButton = document.createElement('button');
            voiceButton.classList.add('voice-button');
            voiceButton.name = headline;
            voiceButton.addEventListener('click', function () {
              console.log(voiceButton.name);
              fetch('http://localhost:5000/play-summary', {
                method: 'POST',
                body: JSON.stringify({
                  "headline": voiceButton.name,
                }),
                headers: {
                  'Content-Type': 'application/json'
                }
              })
                .then(function (response) {
                  if (response.ok) {
                    return response.blob(); // Now we expect a Blob object from the backend
                  } else {
                    throw new Error('Error sending text to the backend');
                  }
                })
                .then(function (audioBlob) {
                  //Play audio in chrome extension
                  const audioUrl = URL.createObjectURL(audioBlob);
                  const audio = new Audio(audioUrl);
                  audio.play();
                })
                .catch(function (error) {
                  console.error('Error in the request to the backend:', error);
                });
              // console.log(audioFile);
              // playAudio(audioFile);
            });
            voiceButton.textContent = '🔊';
            
            summariesContainer.appendChild(sectionButton);
            summariesContainer.appendChild(voiceButton);
            console.log(headline);

            const summary = document.createElement('p');
            summary.textContent = response.summaries[i].summary;
            summariesContainer.appendChild(summary);
          }
          const footer = document.createElement('p');
          footer.classList.add('footer');
          //footer.textContent = 'Sincerely,\n\nYour MagpieAI Newsletter Team';
          summariesContainer.appendChild(footer);
        }
      } else {
        status.textContent = "Error retrieving summaries. Please try again.";
      }
    }
  }
}


function sendSelectedText() {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.tabs.sendMessage(tabs[0].id, { action: 'getSelectedText' }, function (response) {
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

  fetch('http://localhost:5000/play-selected', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(function (response) {
      if (response.ok) {
        return response.blob(); // Now we expect a Blob object from the backend
      } else {
        throw new Error('Error sending text to the backend');
      }
    })
    .then(function (audioBlob) {
      //Play audio in chrome extension
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    })
    .catch(function (error) {
      console.error('Error in the request to the backend:', error);
    });
}
