document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('save-link').addEventListener('click', saveLink);
  document.getElementById('summarize-link').addEventListener('click', summarizeAndSaveLink);
  document.getElementById('get-summaries').addEventListener('click', getSummaries);
});

function saveLink(e) {
  e.preventDefault();

  var status = document.getElementById('status');

  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
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

    req.onreadystatechange = function() {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        status.textContent = "Link saved successfully!";
      }
    }
  });
}

function summarizeAndSaveLink(e) {
  e.preventDefault();

  var status = document.getElementById('status');

  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
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
  var baseUrl = "http://localhost:5000/get-summaries";
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

        response.summaries.forEach(function(summary) {
          var summaryElement = document.createElement('p');
          summaryElement.textContent = summary.link + ": " + summary.summary;
          summariesContainer.appendChild(summaryElement);
        });
      } else {
        status.textContent = "Error retrieving summaries. Please, try again.";
      }
    }
  }
}

