function speak(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
}
function playAudio(audioPath) {
    // sound = import(audioPath);
    console.log(audioPath);
    const audio = new Audio(audioPath);
    // audio.src = audioPath;
    audio.play();
}
 
// const links = ["https://example.com/link1", "https://example.com/link2", "https://example.com/link3"];
// const summaries = ["Summary 1", "Summary 2", "Summary 3"];

// document.addEventListener("DOMContentLoaded", function (event) {
//     // Get the container element
//     const container = document.querySelector('.container');

//     // Generate sections based on the number of links and summaries
//     for (let i = 0; i < links.length; i++) {
//         const sectionButton = document.createElement('a');
//         sectionButton.classList.add('section-button');
//         sectionButton.href = links[i];
//         sectionButton.target = '_blank';
//         sectionButton.textContent = 'Section ' + (i + 1);
//         container.appendChild(sectionButton);

//         const voiceButton = document.createElement('button');
//         voiceButton.classList.add('voice-button');
//         voiceButton.setAttribute('onclick', `speak('Article ${i + 1}')`);
//         voiceButton.textContent = '🔊';
//         container.appendChild(voiceButton);

//         const summary = document.createElement('p');
//         summary.textContent = summaries[i];
//         container.appendChild(summary);
//     }

    // const footer = document.createElement('p');
    // footer.classList.add('footer');
    // footer.textContent = 'Sincerely,\n\nYour MagpieAI Newsletter Team';
    // container.appendChild(footer);
// });

getSummaries();