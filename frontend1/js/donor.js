const FOOD_STORAGE_KEY = "shareBiteFoods";

document.addEventListener("DOMContentLoaded", () => {
    const user = requireRole("donor");
    if (!user) return;

    const name = document.getElementById("donor-name");
    if (name) name.textContent = user.name;

    const form = document.getElementById("donation-form");
    const pickupDate = document.getElementById("pickup-date");
    if (pickupDate) pickupDate.min = new Date().toISOString().split("T")[0];

    renderDonorData(user);
    setupMobileNav();
    setupLogout();

    if (form) form.addEventListener("submit", event => handleDonationSubmit(event, user));

    window.addEventListener("storage", () => renderDonorData(user));
});

function foods() {
    try { return JSON.parse(localStorage.getItem(FOOD_STORAGE_KEY)) || []; }
    catch { return []; }
}
function saveFoods(list) { localStorage.setItem(FOOD_STORAGE_KEY, JSON.stringify(list)); }

function handleDonationSubmit(event, user) {
    event.preventDefault();
    clearFormErrors();

    const values = {
        foodName: document.getElementById("food-name").value.trim(),
        foodType: document.getElementById("food-type").value,
        quantity: Number(document.getElementById("food-quantity").value),
        unit: document.getElementById("quantity-unit").value,
        location: document.getElementById("food-location").value.trim(),
        pickupDate: document.getElementById("pickup-date").value,
        description: document.getElementById("food-description").value.trim(),
        message: document.getElementById("donation-message").value.trim()
    };

    let valid = true;
    const required = [
        ["food-name", values.foodName],
        ["food-type", values.foodType],
        ["food-quantity", values.quantity > 0],
        ["quantity-unit", values.unit],
        ["food-location", values.location],
        ["pickup-date", values.pickupDate]
    ];
    required.forEach(([id, ok]) => {
        if (!ok) { setFormError(id, "Required"); valid = false; }
    });
    if (!valid) return;

    const item = {
        id: Date.now().toString(),
        foodName: values.foodName,
        food: values.foodName,
        foodType: values.foodType,
        quantity: values.quantity,
        qty: values.quantity,
        amount: values.quantity,
        unit: values.unit,
        location: values.location,
        address: values.location,
        pickupLocation: values.location,
        pickupDate: values.pickupDate,
        date: values.pickupDate,
        description: values.description,
        message: values.message,
        donorName: user.name,
        donorEmail: user.email,
        donorId: user.id,
        status: "Available",
        state: "Available",
        createdAt: new Date().toISOString()
    };

    const list = foods();
    list.unshift(item);
    saveFoods(list);

    event.target.reset();
    document.getElementById("pickup-date").min = new Date().toISOString().split("T")[0];
    renderDonorData(user);
    showToast("Donation published successfully.");
}

function renderDonorData(user) {
    const own = foods().filter(item => String(item.donorId) === String(user.id) || item.donorEmail === user.email);
    const total = own.length;
    const meals = own.reduce((sum, item) => {
        const q = Number(item.quantity ?? item.qty ?? item.amount ?? 0);
        return sum + (String(item.unit).toLowerCase() === "kg" ? q * 4 : q);
    }, 0);
    const quantity = own.reduce((sum, item) => sum + Number(item.quantity ?? item.qty ?? item.amount ?? 0), 0);

    setText("total-donations", total);
    setText("total-meals", Math.round(meals));
    setText("waste-reduced", quantity);

    const list = document.getElementById("donation-list");
    const empty = document.getElementById("empty-donations");
    if (!list || !empty) return;

    if (!own.length) {
        list.innerHTML = "";
        empty.style.display = "block";
        return;
    }

    empty.style.display = "none";
    list.innerHTML = own.map(item => {
        const status = item.status || item.state || "Available";
        return `<article class="donation-card">
            <div>
                <span class="donation-status">${escapeHTML(status)}</span>
                <h3>${escapeHTML(item.foodName || item.food || "Food listing")}</h3>
                <div class="donation-card-details">
                    <span>${escapeHTML(item.quantity ?? item.qty ?? item.amount ?? "0")} ${escapeHTML(item.unit || "items")}</span>
                    <span>${escapeHTML(item.location || item.address || "Location not set")}</span>
                    <span>${formatDate(item.pickupDate || item.date)}</span>
                </div>
                ${item.description ? `<p class="donation-description">${escapeHTML(item.description)}</p>` : ""}
            </div>
            <div></div>
        </article>`;
    }).join("");
}

function setupMobileNav() {
    const toggle = document.getElementById("mobile-menu-toggle");
    const nav = document.getElementById("mobile-nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", () => {
        const open = nav.classList.toggle("open");
        toggle.setAttribute("aria-expanded", String(open));
        document.body.classList.toggle("menu-open", open);
    });
}
function setupLogout() {
    document.getElementById("logout-btn")?.addEventListener("click", logoutUser);
    document.getElementById("mobile-logout-btn")?.addEventListener("click", logoutUser);
}
function setText(id, value) { const el = document.getElementById(id); if (el) el.textContent = value; }
function setFormError(id, message) {
    const input = document.getElementById(id);
    if (!input) return;
    input.classList.add("input-error");
    input.closest(".form-group")?.querySelector(".form-error")?.replaceChildren(document.createTextNode(message));
}
function clearFormErrors() {
    document.querySelectorAll(".input-error").forEach(el => el.classList.remove("input-error"));
    document.querySelectorAll(".form-error").forEach(el => el.textContent = "");
}
function formatDate(value) {
    if (!value) return "No date";
    const date = new Date(`${value}T00:00:00`);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString(undefined, {day:"numeric",month:"short",year:"numeric"});
}
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;" }[char]));
}
function showToast(message, error = false) {
    const toast = document.getElementById("toast");
    const text = document.getElementById("toast-message");
    if (!toast || !text) return;
    text.textContent = message;
    toast.classList.toggle("error", error);
    toast.classList.add("show");
    clearTimeout(window.__zeroBiteToast);
    window.__zeroBiteToast = setTimeout(() => toast.classList.remove("show"), 2800);
}
