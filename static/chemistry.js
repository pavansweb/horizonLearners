function showSubjectContent(container) {
    container.innerHTML = `
        <h2>Physics Lessons</h1>
        <div class="lesson-menu">
            <button onclick="loadLesson('lesson1')">Chapter 1: a</button>
            <button onclick="loadLesson('lesson2')">Chapter 2: b</button>
            <button onclick="loadLesson('lesson3')">Chapter 3: c</button>
            <button onclick="loadLesson('lesson4')">Chapter 4: d</button>
            <button onclick="loadLesson('lesson5')">Chapter 5: e</button>
        </div>
        <div id="lessonContent" class="lesson-content">
            <p>Select a lesson to view its content.</p>
        </div>
    `;
}

function loadLesson(lesson) {
    let content = '';
    switch (lesson) {
        case 'lesson1':
            content = `
                <h2>Lesson 1: Force</h2>
                <p> </p>
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png"> `

            break;
        case 'lesson2':
            content = `
                <h2>Lesson 2: Work, Energy and Power</h2>
                <p> </p>
                <img src=" ">
            `;
            break;

        // Add cases for other lessons

        default:
            content = `<p>Lesson content not available yet.</p>`;
    }

    // Hide the lesson menu after a lesson is clicked
    document.querySelector('.lesson-menu').style.display = 'none';

    // Display the lesson content
    document.getElementById('lessonContent').innerHTML = content;
}
