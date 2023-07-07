
![Magpie AI Logo Project](./frontend/icon.png)
<!DOCTYPE html>
<html>
<body>
	<h1>MAGPIE AI</h1>
	<p>Introducing our groundbreaking Chrome Extension plugin <a href="https://http://130.211.217.70/">Magpie AI</a> designed to revolutionize the way busy professionals stay informed amidst their hectic schedules. In today's information-driven world, newsletters and articles flood our inboxes, overwhelming us with valuable insights buried in lengthy content. Our plugin offers a game-changing solution, effortlessly summarizing and distilling this wealth of information into concise, digestible nuggets of knowledge read to you like an audiobook.</p>
	<p>This project was made for the <a href="https://lablab.ai/event/plug-into-ai-with-ai21">Plug into AI with AI21</a> in July 2023 organized by <a href="https://lablab.ai">lablab.ai</a>.</p>
	<h2>Features</h2>
	<ul>
		<li> Bookmark: Store the website URL in database</li> 
		<li> Standard Summary: Summarize this article using AI21 Task-specific API </li> 
		<li> Simple Summary: Attempt to create a simpler summary without jargons using AI21 Jurassic 2-Ultra Model </li> 
		<li> Play selected Text: User select words on the article, then this button will speakout those words</li> 
		<li> My library: Open a library website with articles and their summaries saved by Magpie AI, with an option to speakout those summaries when users click "speaker" buttons</li> 
	</ul>
	<h2>Installation</h2>
	<ol>
		<li>Download this <a href="http://130.211.217.70/plugin.tar.gz">Zip file</a> (if Chrome does not allow, please copy the address and paste it to the browser, or use our page <a href="http://130.211.217.70/">Magpie AI</a>)</li>
		<li>Extract the ZIP file</li>
		<li>Open Google Chrome and navigate to chrome://extensions/</li>
		<li>Enable Developer Mode by clicking the toggle switch on the top right corner of the page</li>
		<li>Click on "Load unpacked" and select the extracted folder of this extension</li>
		<li>The extension should now be installed and ready to use!</li>
	</ol>
	<h2>Usage</h2>
	<ol>
		<li> Click on the extension icon in the top right corner of the browser</li>
		<li> Interact with the Plug-in using one of five features </li>
	</ol>
	<h2>Credits</h2>
	<p>This Chrome Extension uses the following technologies:</p>
	<ul>
		<li>AI21 API</li>
		<li>ElevenLabs API</li>
		<li>PostgreSQL database</li>
	        <li>Flask Server</li>
		<li>Python, HTML, CSS, JavaScript</li>
		<li>Google Chrome Extension </li>
	</ul>
</body>
</html>
