document.addEventListener('DOMContentLoaded', function () {
  chrome.storage.local.get(['extensionId', 'userId'], function(result) {
    var extensionId = result.extensionId;
    var userId = result.userId;

    if (!extensionId) {
      extensionId = generateUniqueIdentifier();
      chrome.storage.local.set({'extensionId': extensionId}, function() {
        createUser(extensionId);
      });
    } else {
      if (userId) {
        user_id = userId;
      }
      // Resto del código cuando el usuario ya está creado
      var saveLinkElement = document.getElementById('save-link');
      var standardSummaryElement = document.getElementById('standard-summary');
      var simpleSummaryElement = document.getElementById('simple-summary');
      var getSummariesElement = document.getElementById('get-summaries');
      var sendTextElement = document.getElementById('send-text');
      
      if(saveLinkElement){
        saveLinkElement.addEventListener('click', saveLink);
      }

      if(standardSummaryElement){
        standardSummaryElement.addEventListener('click', summarizeAndSaveLink);
      }
      
      if(simpleSummaryElement){
        simpleSummaryElement.addEventListener('click', simpleSummary);
      }

      if(getSummariesElement){
        getSummariesElement.addEventListener('click', myLibrary);
      }
      
      if(sendTextElement){
        sendTextElement.addEventListener('click', sendSelectedText);
      }

    }
  });
});



// document.addEventListener('DOMContentLoaded', function () {
//   chrome.storage.local.get(['extensionId', 'userId'], function(result) {
//     var extensionId = result.extensionId;
//     var userId = result.userId;

//     if (!extensionId) {
//       extensionId = generateUniqueIdentifier();
//       chrome.storage.local.set({'extensionId': extensionId}, function() {
//         createUser(extensionId);
//       });
//     } else {
//       if (userId) {
//         user_id = userId;
//       }
//       // Resto del código cuando el usuario ya está creado
//       document.getElementById('save-link').addEventListener('click', saveLink);
//       document.getElementById('standard-summary').addEventListener('click', summarizeAndSaveLink);
//       document.getElementById('simple-summary').addEventListener('click', simpleSummary);
//       document.getElementById('get-summaries').addEventListener('click', myLibrary);
//       //document.getElementById('send-text').addEventListener('click', sendSelectedText);
//       document.getElementById('send-text').addEventListener('click', sendSelectedText);

//     }
//   });
// });

function generateUniqueIdentifier() {
  var randomNumber = Math.floor(Math.random() * 9999999999999999);
  console.log("GenerateUniqueIdentifier", randomNumber);
  return randomNumber.toString();
}

function createUser(extensionId) {
  var req = new XMLHttpRequest();
  var baseUrl = "https://soychile.org/create-user";

  var body = JSON.stringify({
    'user_id': extensionId
  });

  req.open("POST", baseUrl, true);
  req.setRequestHeader("Content-Type", "application/json");
  req.send(body);

  req.onreadystatechange = function () {
    if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
      chrome.storage.local.set({'userId': this.responseText}, function() {
        console.log("User ID saved successfully!");
      });
    } else {
      console.log("Error creating user.");
    }
  }
}

function saveLink(e) {
  e.preventDefault();

  var status = document.getElementById('status');

  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var activeTab = tabs[0];
    var user_id = "";  // Variable para almacenar el ID del usuario

    chrome.storage.local.get('userId', function(result) {
      var userId = result.userId;
      if (userId) {
        user_id = userId;
      }

      var req = new XMLHttpRequest();
      var baseUrl = "https://soychile.org/save-link";
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
  });
}

function summarizeAndSaveLink(e) {
  e.preventDefault();
  
  var status = document.getElementById('status');
  var summary = document.getElementById('summary');
  
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var activeTab = tabs[0];
    var user_id = "";  
  
    chrome.storage.local.get('userId', function(result) {
      var userId = result.userId;
      if (userId) {
        user_id = userId;
      }
  
      chrome.scripting.executeScript({
        target: { tabId: activeTab.id }, 
        func: function() { 
          return document.body.innerText; 
        }
      }, function(result) {
        var content = result[0].result; 
        
        var req = new XMLHttpRequest();
        var baseUrl = "https://soychile.org/summarize-and-save";
        var body = JSON.stringify({
          'url': activeTab.url,
          'user_id': user_id,
          'content': content 
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
  
              summary.textContent = "";
              status.textContent = "Loading...";
              if (response.length === 0) {
                var noSummariesElement = document.createElement('p');
                noSummariesElement.textContent = "No summaries available.";
                status.textContent = "No summaries available.";
              } else {
                summary_div = document.getElementById('summary');
                body_tag = document.getElementsByTagName('body')[0];
  
                body_tag.style.padding = "20px 100px 20px 100px";
                summary_div.style.width = "150%";
                summary.innerHTML = response;
                status.innerHTML = "<b>Your summary:</b>";
              }
            } else {
              status.textContent = "Error retrieving summaries. Please try again.";
            }
          }
        }
      });
    });
  });
}

function simpleSummary(e) {
  e.preventDefault();
  
  var status = document.getElementById('status');
  var summary = document.getElementById('summary');
  
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    var activeTab = tabs[0];
    var user_id = "";  
  
    chrome.storage.local.get('userId', function(result) {
      var userId = result.userId;
      if (userId) {
        user_id = userId;
      }
  
      chrome.scripting.executeScript({
        target: { tabId: activeTab.id }, 
        func: function() { 
          return document.body.innerText; 
        }
      }, function(result) {
        var content = result[0].result; 
        
        var req = new XMLHttpRequest();
        var baseUrl = "https://soychile.org/simple-summary";
        var body = JSON.stringify({
          'url': activeTab.url,
          'user_id': user_id,
          'content': content 
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
  
              summary.textContent = "";
              if (response.length === 0) {
                var noSummariesElement = document.createElement('p');
                noSummariesElement.textContent = "No summaries available.";
                status.textContent = "No summaries available.";
              } else {
                summary_div = document.getElementById('summary');
                body_tag = document.getElementsByTagName('body')[0];
  
                body_tag.style.padding = "20px 100px 20px 100px";
                summary_div.style.width = "150%";
                summary.innerHTML = response;
                status.innerHTML = "<b>Your summary:</b>";
              }
            } else {
              status.textContent = "Error retrieving summaries. Please try again.";
            }
          }
        }
      });
    });
  });
}

function myLibrary() {
  created_tab = chrome.tabs.create({ url: './templates/index3.html' });
  console.log(`Created tab: ${created_tab}`);
}

// Mantén una referencia global al audio en reproducción
let playingAudio = null;

function getSummaries() {
  var status = document.getElementById('status');
  var user_id = "";  // Variable para almacenar el ID del usuario

  chrome.storage.local.get('userId', function(result) {
    var userId = result.userId;
    if (userId) {
      user_id = userId;
    }

    var req = new XMLHttpRequest();
    var baseUrl = "https://soychile.org/get-summaries";
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
                fetch('https://soychile.org/play-summary', {
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
                      return response.blob();
                    } else {
                      throw new Error('Error sending text to the backend');
                    }
                  })
                  .then(function (audioBlob) {
                    if (playingAudio) { // Si hay un audio en reproducción, lo detiene.
                      playingAudio.pause();
                      playingAudio.currentTime = 0;
                    }
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    audio.play();
                    playingAudio = audio; // Guarda la referencia al audio en reproducción
                  })
                  .catch(function (error) {
                    console.error('Error in the request to the backend:', error);
                  });
              });
              voiceButton.textContent = '🔊';

              // Añade un botón de pausa después de 'voiceButton'
              const pauseButton = document.createElement('button');
              pauseButton.classList.add('pause-button');
              pauseButton.textContent = '⏸️'; // El emoji de pausa
              pauseButton.addEventListener('click', function () {
                if (playingAudio && !playingAudio.paused) {
                  playingAudio.pause();
                }
              });

              // Añade un botón de detención después de 'pauseButton'
              const stopButton = document.createElement('button');
              stopButton.classList.add('stop-button');
              stopButton.textContent = '⏹️'; // El emoji de detención
              stopButton.addEventListener('click', function () {
                if (playingAudio) {
                  playingAudio.pause();
                  playingAudio.currentTime = 0; // Vuelve al inicio del audio
                }
              });

              summariesContainer.appendChild(sectionButton);
              summariesContainer.appendChild(voiceButton);
              summariesContainer.appendChild(pauseButton);
              summariesContainer.appendChild(stopButton);
              
              console.log(headline);

              const summary = document.createElement('p');
              summary.textContent = response.summaries[i].summary;
              summariesContainer.appendChild(summary);
            }
            const footer = document.createElement('p');
            footer.classList.add('footer');
            summariesContainer.appendChild(footer);
          }
        } else {
          status.textContent = "Error retrieving summaries. Please try again.";
        }
      }
    }
  });
}

function sendSelectedText() {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    chrome.scripting.executeScript({
      target: {tabId: tabs[0].id},
      files: ['content.js']
    });
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
