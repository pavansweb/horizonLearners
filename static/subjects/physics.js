// Example function to show subject content (e.g., in subjects/physics.js)
function showSubjectContent(container) {
    container.innerHTML = `
        <h2>Choose Board</h2>
        <div class="lesson-menu">
            <button class="btn btn-primary btn-block" onclick="loadboard('Cbse')">CBSE</button>
            <button class="btn btn-primary btn-block" onclick="loadBoard('icse')">ICSE</button>
            
        </div>
        <div id="lessonContent" class="lesson-content">
            <p>Select a lesson to view its content.</p>
        </div>
    `;
}

// Function to load individual lessons
function loadBoard(board) {
    let content = '';
    switch (board) {
        case 'Cbse':
            content = `
               <div class="lesson-menu">
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson1')">Chapter 1: Force</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson2')">Chapter 2: Work, Energy and Power</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson3')">Chapter 3: Machines</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson4')">Chapter 4: Refraction of Light at Plane Surfaces</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson5')">Chapter 5: Refraction through a Lens</button>
        </div>`;
            break;
        case 'icse':
            content = `
                <div class="lesson-menu">
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson1')">Chapter 1: Force</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson2')">Chapter 2: Work, Energy and Power</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson3')">Chapter 3: Machines</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson4')">Chapter 4: Refraction of Light at Plane Surfaces</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson5')">Chapter 5: Refraction through a Lens</button>
        </div>`;
            break;

        // Add cases for other lessons

        default:
            content = `<p>Lesson content not available yet.</p>`;
    }

    // Hide the lesson menu after a lesson is clicked
    document.querySelector('.lesson-menu').style.display = 'none';

    // Display the lesson content with a back button
    document.getElementById('lessonContent').innerHTML = `
        <button class="btn btn-secondary mb-3" onclick="showLessonMenu()">Back to Lessons</button>
        ${content}
    `;
}
