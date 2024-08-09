const content = document.getElementById("content");
const menu = document.getElementById("menu");
const backButton = document.getElementById("backButton");
const spinner = document.getElementById("spinner");
const scrollToTopButton = document.getElementById("scrollToTopButton");
const toggle = document.getElementById("darkModeToggle");
const sunIcon = document.querySelector(".sun-icon");
const moonIcon = document.querySelector(".moon-icon");
const profilePictureInput = document.getElementById("profilePictureInput");
const profilePicture = document.getElementById("profilePicture");

window.addEventListener('load', function() {
    setTimeout(function() {
        document.getElementById('overlay').classList.add('hidden');
    }, 1000); // 1 seconds
});




// Function to set dark mode icons
const setIcons = (isDarkMode) => {
    if (isDarkMode) {
        sunIcon.style.display = "none";
        moonIcon.style.display = "inline";
    } else {
        sunIcon.style.display = "inline";
        moonIcon.style.display = "none";
    }
};

// Dark mode toggle
toggle.addEventListener("change", () => {
    const isDarkMode = toggle.checked;
    document.body.classList.toggle("dark-mode", isDarkMode);
    setIcons(isDarkMode);
    localStorage.setItem("dark-mode", isDarkMode ? "enabled" : "disabled");
});

if (localStorage.getItem("dark-mode") === "enabled") {
    toggle.checked = true;
    document.body.classList.add("dark-mode");
    setIcons(true);
} else {
    setIcons(false);
}

// Function to load a subject
function loadSubject(subject) {
    menu.style.display = "none";
    backButton.style.display = "block";
    spinner.style.display = "block";

    loadSubjectContent(subject);
}

// Function to dynamically load the subject script
function loadSubjectContent(subject) {
    content.innerHTML = "";

    const script = document.createElement("script");
    script.src = `static/subjects/${subject}.js`;
    script.onload = () => {
        spinner.style.display = "none";

        if (typeof showSubjectContent === "function") {
            showSubjectContent(content);
        } else {
            content.innerHTML = `<p>Error loading subject content.</p>`;
        }
    };
    script.onerror = () => {
        spinner.style.display = "none";
        content.innerHTML = `<p>Error loading subject content.</p>`;
    };
    document.body.appendChild(script);
}

// Function to show the main menu
function showMenu() {
    content.innerHTML = `<p>Select a subject to get started.</p>`;
    menu.style.display = "flex";
    backButton.style.display = "none";
    spinner.style.display = "none";

    const subjectScripts = document.querySelectorAll(
        'script[src^="static/subjects/"]',
    );
    subjectScripts.forEach((script) => script.remove());
}

// Function to scroll to the top
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}



// Toggle sidebar visibility
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar.style.left === '0px') {
        sidebar.style.left = '-250px';
    } else {
        sidebar.style.left = '0';
    }
}


// Logout function
function logout() {
    fetch("/logout", { method: "POST" })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                window.location.href = "/login";
            } else {
                alert("Logout failed");
            }
        })
        .catch((error) => {
            alert("Logout failed");
        });
}

// Fetch user info and set profile picture
// Fetch user info and set profile picture
fetch("/user")
    .then((response) => response.json())
    .then((data) => {
        const userInfoElement = document.getElementById("user-info");
        const toggleSidebarButton = document.getElementById("toggleSidebarButton");
        const loginNavItem = document.getElementById("loginNavItem");

        if (data.email) {
            // User is logged in
            toggleSidebarButton.style.backgroundImage = `url(${data.profile_picture || '/static/icons/user-profile.png'})`;
            loginNavItem.style.display = "none";
            toggleSidebarButton.style.display = "block";
            userInfoElement.innerHTML = `
                <div class="profile-pic">
                    <label class="-label" for="file">
                        <span class="glyphicon glyphicon-camera"></span>
                        <span>Change Image</span>
                        <input id="file" type="file" onchange="uploadProfilePicture(event)" />
                    </label>
                </div>
                <div class="profile-name">
                    <span id="userName">Name: ${data.name || 'N/A'}</span>
                    <button id="editNameBtn" class="edit-icon">✎</button>
                    <input type="text" id="editNameInput" class="edit-input" style="display: none;" placeholder="Enter new name" />
                    <button id="saveNameBtn" class="save-name-btn" style="display: none;">Save</button>
                </div>
                <p>Email: ${data.email}</p>
                <p>Joined: ${data.joined}</p>
                <button class="btn btn-primary" onclick="logout()">Logout</button>
                <button class="btn btn-primary"><a style='color:white' href='/change-password'>Change Password</a></button>
            `;
            loadProfilePicture();
            setupNameEditing();  // Call setupNameEditing after user info is loaded
        } else {
            // User is not logged in
            toggleSidebarButton.style.display = "none";
            loginNavItem.style.display = "block";
        }
    })
    .catch((error) => {
        console.error("Error fetching user info:", error);
    });


// Setup event listeners for name editing
function setupNameEditing() {
    const editNameBtn = document.getElementById("editNameBtn");
    const editNameInput = document.getElementById("editNameInput");
    const saveNameBtn = document.getElementById("saveNameBtn");
    const userName = document.getElementById("userName");

    editNameBtn.addEventListener("click", () => {
        // Show input and save button, hide user name and edit button
        userName.classList.add("hidden");
        editNameInput.style.display = "inline";
        saveNameBtn.style.display = "inline";
        editNameInput.value = userName.textContent.replace("Name: ", "").trim();
        editNameBtn.style.display = "none";
    });

    saveNameBtn.addEventListener("click", () => {
        const newName = editNameInput.value.trim();
        if (newName) {
            fetch("/update-name", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ name: newName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    userName.textContent = `Name: ${newName}`;
                    userName.classList.remove("hidden");
                    editNameInput.style.display = "none";
                    saveNameBtn.style.display = "none";
                    editNameBtn.style.display = "inline";
                } else {
                    alert("Failed to update name: " + data.message);
                }
            })
            .catch(error => {
                alert("Error updating name: " + error.message);
            });
        } else {
            alert("Name cannot be empty");
        }
    });
}




// Handle profile picture upload
function uploadProfilePicture(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append("file", file);

        fetch("/upload-profile-picture", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.message === "Profile picture uploaded successfully") {
                    document.querySelector(".-label").style.backgroundImage =
                        `url(${data.profile_picture_url})`;
                    loadProfilePicture();
                    localStorage.setItem(
                        "profilePicture",
                        data.profile_picture_url,
                    );
                    
                } else {
                    alert("Profile picture upload failed: " + data.message);
                }
            })
            .catch(() => {
                alert("Error during profile picture upload");
            });
    }
}

// Fetch the profile picture URL from the server and set it
function loadProfilePicture() {
    fetch("/user")
        .then((response) => response.json())
        .then((data) => {
            if (data.profile_picture) {
                document.getElementById("toggleSidebarButton").style.backgroundImage =
                        `url(${data.profile_picture})`;;

                document.querySelector(".-label").style.backgroundImage =
                    `url(${data.profile_picture})`;
            }
        })
        .catch(() => {
            console.error("Error fetching profile picture");
        });
}

// Load the profile picture when the DOM is ready
document.addEventListener("DOMContentLoaded", loadProfilePicture);
