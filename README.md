# magpie
![Magpie AI Logo Project](./frontend/icon.png)


<!DOCTYPE html>
<html>
<body>
	<h1>MAGPIE AI</h1>
	<p>This Chrome Extension uses AI21 API to record speech during a meeting or video, store it in a Redis database and then ask any questions.</p>
	<h2>Features</h2>
	<ul>
		<li>Record speech during meetings or videos</li>
		<li>Store recordings in a Redis database</li>
		<li>Ask any questions related to the recording</li>
	</ul>
	<h2>Installation</h2>
	<ol>
		<li>Clone this repository or download it as a ZIP file</li>
		<li>Extract the ZIP file (if downloaded as ZIP)</li>
		<li>Open Google Chrome and navigate to chrome://extensions/</li>
		<li>Enable Developer Mode by clicking the toggle switch on the top right corner of the page</li>
		<li>Click on "Load unpacked" and select the extracted folder of this extension</li>
		<li>The extension should now be installed and ready to use!</li>
	</ol>
	<h2>Usage</h2>
	<ol>
		<li>Click on the extension icon in the top right corner of the browser</li>
		<li>Select "Start Recording"</li>
		<li>The extension will start recording your speech</li>
		<li>Click on "Stop Recording" when you're done</li>
		<li>The recording will be saved in the Redis database</li>
		<li>You can now ask any questions related to the recording by clicking on "Ask a Question" and typing in your question</li>
	</ol>
	<h2>Credits</h2>
	<p>This Chrome Extension uses the following technologies:</p>
	<ul>
		<li>AI21 API</li>
		<li>Redis database, Flask Server</li>
		<li>HTML, CSS, JavaScript</li>
		<li>Google Chrome Extension </li>
	</ul>
</body>
</html>
