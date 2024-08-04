// Example function to show subject content (e.g., in subjects/physics.js)
function showSubjectContent(container) {
    container.innerHTML = `
        <h2>Physics Lessons</h2>
        <div class="lesson-menu">
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson1')">Chapter 1: a</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson2')">Chapter 2: b</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson3')">Chapter 3: c</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson4')">Chapter 4: d</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson5')">Chapter 5: e</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson6')">Chapter 6: f</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson7')">Chapter 7: g</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson8')">Chapter 8: h</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson9')">Chapter 9: i</button>
            <button class="btn btn-primary btn-block" onclick="loadLesson('lesson10')">Chapter 10: j</button>
        </div>

        <div id="lessonContent" class="lesson-content">
            <p>Select a lesson to view its content.</p>
        </div>
    `;
}

// Function to load individual lessons
function loadLesson(lesson) {
    let content = '';
    switch (lesson) {
        case 'lesson1':
            content = `
                <h2>Lesson 1: Force</h2>
                <p>This is the content for Lesson 1.</p>
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/2.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/3.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/4.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/5.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/6.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/7.png" alt="image" class="lesson-img">`;
            break;
        case 'lesson2':
            content = `
                <h2>Lesson 2: Work, Energy and Power</h2>
                <p>This is the content for Lesson 2.</p>
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png" alt="image" class="lesson-img">
                <img src="https://www.vedantu.com/content-images/5b5578aae4b00a014d4897c3/1.png" alt="image" class="lesson-img">`;
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
