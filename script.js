// Get references to DOM elements
const content = document.getElementById('content');
const menu = document.getElementById('menu');
const backButton = document.getElementById('backButton');
const spinner = document.getElementById('spinner');
const scrollToTopButton = document.getElementById('scrollToTopButton');

// Function to load a subject
function loadSubject(subject) {
    // Hide menu, show back button, and show spinner
    menu.style.display = 'none';
    backButton.style.display = 'block';
    spinner.style.display = 'block';

    // Load subject content
    loadSubjectContent(subject);
}

// Function to dynamically load the subject script
function loadSubjectContent(subject) {
    // Remove any existing content
    content.innerHTML = '';

    // Dynamically load subject script
    const script = document.createElement('script');
    script.src = `subjects/${subject}.js`;
    script.onload = () => {
        // Hide spinner once content is loaded
        spinner.style.display = 'none';

        // Assuming showSubjectContent is defined in each subject's JS file
        if (typeof showSubjectContent === 'function') {
            showSubjectContent(content);
        } else {
            content.innerHTML = `<p>Error loading subject content.</p>`;
        }
    };
    script.onerror = () => {
        spinner.style.display = 'none'; // Hide spinner on error
        content.innerHTML = `<p>Error loading subject content.</p>`;
    };
    document.body.appendChild(script);
}

// Function to show the main menu
function showMenu() {
    // Clear content, show menu, and hide spinner
    content.innerHTML = `<p>Select a subject to get started.</p>`;
    menu.style.display = 'flex';
    backButton.style.display = 'none';
    spinner.style.display = 'none';

    // Remove subject-specific script
    const subjectScripts = document.querySelectorAll('script[src^="subjects/"]');
    subjectScripts.forEach(script => script.remove());
}

// Function to show the lesson menu
function showLessonMenu() {
    // Show the lesson menu and hide the lesson content
    document.querySelector('.lesson-menu').style.display = 'flex';
    document.getElementById('lessonContent').innerHTML = `<p>Select a lesson to view its content.</p>`;
}

// Function to scroll to the top
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Show the scroll to top button when the user scrolls down
window.addEventListener('scroll', () => {
    if (window.scrollY > 200) {
        scrollToTopButton.style.display = 'block';
    } else {
        scrollToTopButton.style.display = 'none';
    }
});
