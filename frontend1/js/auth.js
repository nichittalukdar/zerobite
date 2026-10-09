const USERS_KEY = "zeroBiteUsers";
const CURRENT_USER_KEY = "zeroBiteCurrentUser";

function readJSON(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) ?? fallback; }
    catch { return fallback; }
}
function writeJSON(key, value) { localStorage.setItem(key, JSON.stringify(value)); }

function getCurrentUser() { return readJSON(CURRENT_USER_KEY, null); }
function isLoggedIn() { return Boolean(getCurrentUser()); }

function loginPath() {
    return window.location.pathname.includes("/pages/") ? "login.html" : "pages/login.html";
}
function homePath() {
    return window.location.pathname.includes("/pages/") ? "../index.html" : "index.html";
}
function dashboardPath(role) {
    return window.location.pathname.includes("/pages/") ? `${role}.html` : `pages/${role}.html`;
}

function logoutUser() {
    localStorage.removeItem(CURRENT_USER_KEY);
    window.location.href = loginPath();
}

function requireRole(role) {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = loginPath();
        return null;
    }
    if (user.role !== role) {
        window.location.href = dashboardPath(user.role);
        return null;
    }
    return user;
}

function showAuthMessage(message) {
    const box = document.getElementById("auth-message");
    if (!box) return;
    box.textContent = message;
    box.classList.add("show");
}

function clearAuthMessage() {
    const box = document.getElementById("auth-message");
    if (!box) return;
    box.textContent = "";
    box.classList.remove("show");
}

function setupPasswordToggles() {
    document.querySelectorAll("[data-password-toggle]").forEach(button => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.dataset.passwordToggle);
            if (!input) return;
            const visible = input.type === "text";
            input.type = visible ? "password" : "text";
            button.textContent = visible ? "Show" : "Hide";
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupPasswordToggles();

    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", event => {
            event.preventDefault();
            clearAuthMessage();

            const name = document.getElementById("signup-name").value.trim();
            const email = document.getElementById("signup-email").value.trim().toLowerCase();
            const password = document.getElementById("signup-password").value;
            const confirm = document.getElementById("signup-confirm-password").value;
            const role = document.getElementById("signup-role").value;

            if (!name || !email || !password || !confirm || !role) return showAuthMessage("Please complete every field.");
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return showAuthMessage("Please enter a valid email address.");
            if (password.length < 6) return showAuthMessage("Password must be at least 6 characters.");
            if (password !== confirm) return showAuthMessage("Passwords do not match.");

            const users = readJSON(USERS_KEY, []);
            if (users.some(user => user.email === email)) return showAuthMessage("An account with this email already exists.");

            const user = {
                id: Date.now().toString(),
                name, email, password, role,
                createdAt: new Date().toISOString()
            };
            users.push(user);
            writeJSON(USERS_KEY, users);
            writeJSON(CURRENT_USER_KEY, { id: user.id, name: user.name, email: user.email, role: user.role });
            window.location.href = dashboardPath(role);
        });
    }

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", event => {
            event.preventDefault();
            clearAuthMessage();

            const email = document.getElementById("login-email").value.trim().toLowerCase();
            const password = document.getElementById("login-password").value;
            const users = readJSON(USERS_KEY, []);
            const user = users.find(item => item.email === email && item.password === password);

            if (!user) return showAuthMessage("Email or password is incorrect.");
            writeJSON(CURRENT_USER_KEY, { id: user.id, name: user.name, email: user.email, role: user.role });
            window.location.href = dashboardPath(user.role);
        });
    }

    document.querySelectorAll("[data-google-login]").forEach(button => {
        button.addEventListener("click", () => showAuthMessage("Google sign-in needs a backend provider. Use email sign-up for this prototype."));
    });

    document.querySelectorAll("[data-forgot-password]").forEach(button => {
        button.addEventListener("click", () => showAuthMessage("Password recovery needs a backend email service in the production version."));
    });
});

window.getCurrentUser = getCurrentUser;
window.isLoggedIn = isLoggedIn;
window.logoutUser = logoutUser;
window.requireRole = requireRole;

(function bootstrapAdminAccount(){
    const users = readJSON(USERS_KEY, []);
    if (!users.some(user => user.role === "admin")) {
        users.push({
            id: "admin-prototype",
            name: "ZeroBite Admin",
            email: "admin@zerobite.local",
            password: "admin123",
            role: "admin",
            createdAt: new Date().toISOString()
        });
        writeJSON(USERS_KEY, users);
    }
})();
