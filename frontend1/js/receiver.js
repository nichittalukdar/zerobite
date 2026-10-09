const RECEIVER_FOOD_KEY = "shareBiteFoods";

document.addEventListener("DOMContentLoaded", () => {
    const user = requireRole("receiver");
    if (!user) return;

    document.getElementById("receiver-name").textContent = user.name;
    setupReceiverMobile();
    setupReceiverLogout();
    setupReceiverFilters();
    renderReceiver(user);
    window.addEventListener("storage", () => renderReceiver(user));
});

function receiverFoods() {
    try { return JSON.parse(localStorage.getItem(RECEIVER_FOOD_KEY)) || []; }
    catch { return []; }
}
function saveReceiverFoods(list) { localStorage.setItem(RECEIVER_FOOD_KEY, JSON.stringify(list)); }

function renderReceiver(user) {
    const all = receiverFoods();
    const available = all.filter(item => (item.status || item.state || "Available").toLowerCase() === "available")
        .filter(item => String(item.donorId) !== String(user.id) && item.donorEmail !== user.email);
    const claimed = all.filter(item => item.claimedById === user.id || item.claimedByEmail === user.email);

    setText("available-count", available.length);
    setText("claimed-count", claimed.length);
    setText("community-quantity", available.reduce((sum, item) => sum + Number(item.quantity ?? item.qty ?? item.amount ?? 0), 0));

    renderAvailable(user);
    renderClaims(claimed);
}

function getFilteredAvailable(user) {
    const search = document.getElementById("food-search")?.value.trim().toLowerCase() || "";
    const filter = document.getElementById("food-filter")?.value || "all";
    return receiverFoods().filter(item => (item.status || item.state || "Available").toLowerCase() === "available")
        .filter(item => String(item.donorId) !== String(user.id) && item.donorEmail !== user.email)
        .filter(item => filter === "all" || item.foodType === filter)
        .filter(item => {
            const haystack = `${item.foodName || item.food || ""} ${item.location || item.address || ""} ${item.description || ""}`.toLowerCase();
            return !search || haystack.includes(search);
        });
}

function renderAvailable(user) {
    const list = document.getElementById("food-list");
    const empty = document.getElementById("empty-food");
    const noResults = document.getElementById("no-results");
    if (!list) return;

    const allAvailable = receiverFoods().filter(item => (item.status || item.state || "Available").toLowerCase() === "available")
        .filter(item => String(item.donorId) !== String(user.id) && item.donorEmail !== user.email);
    const filtered = getFilteredAvailable(user);

    if (!allAvailable.length) {
        list.innerHTML = ""; empty.style.display = "block"; noResults.style.display = "none"; return;
    }
    empty.style.display = "none";
    noResults.style.display = filtered.length ? "none" : "block";

    list.innerHTML = filtered.map(item => `
        <article class="receiver-food-card">
            <div class="receiver-food-card-top"><span class="food-type-badge">${escapeHTML(item.foodType || "Food")}</span><span class="food-available-badge">Available</span></div>
            <div class="receiver-food-card-body">
                <h3>${escapeHTML(item.foodName || item.food || "Food listing")}</h3>
                <p class="receiver-food-description">${escapeHTML(item.description || item.message || "No additional description.")}</p>
                <div class="receiver-food-details">
                    <div class="receiver-food-detail"><span class="detail-label">Quantity</span><strong>${escapeHTML(item.quantity ?? item.qty ?? item.amount ?? 0)} ${escapeHTML(item.unit || "items")}</strong></div>
                    <div class="receiver-food-detail"><span class="detail-label">Pickup</span><strong>${formatDate(item.pickupDate || item.date)}</strong></div>
                    <div class="receiver-food-detail"><span class="detail-label">Location</span><strong>${escapeHTML(item.location || item.address || "Not set")}</strong></div>
                    <div class="receiver-food-detail"><span class="detail-label">Donor</span><strong>${escapeHTML(item.donorName || "Community donor")}</strong></div>
                </div>
            </div>
            <div class="receiver-food-card-footer"><button class="btn btn-primary claim-food-btn" type="button" data-food-id="${escapeHTML(item.id)}">Claim food</button></div>
        </article>`).join("");

    list.querySelectorAll(".claim-food-btn").forEach(button => {
        button.addEventListener("click", () => claimFood(button.dataset.foodId, user));
    });
}

function claimFood(id, user) {
    const list = receiverFoods();
    const item = list.find(food => String(food.id) === String(id));
    if (!item) return showToast("That listing is no longer available.", true);

    const status = (item.status || item.state || "Available").toLowerCase();
    if (status !== "available") return showToast("That listing has already been claimed.", true);

    item.status = "Claimed";
    item.state = "Claimed";
    item.claimedById = user.id;
    item.claimedByName = user.name;
    item.claimedByEmail = user.email;
    item.claimedAt = new Date().toISOString();

    saveReceiverFoods(list);
    renderReceiver(user);
    showToast("Food claimed successfully.");
}

function renderClaims(claimed) {
    const list = document.getElementById("claimed-list");
    const empty = document.getElementById("empty-claims");
    if (!list || !empty) return;
    if (!claimed.length) { list.innerHTML = ""; empty.style.display = "block"; return; }
    empty.style.display = "none";
    list.innerHTML = claimed.map(item => `
        <article class="donation-card claimed-food-card">
            <div><span class="donation-status">Claimed</span><h3>${escapeHTML(item.foodName || item.food || "Food listing")}</h3>
            <div class="donation-card-details"><span>${escapeHTML(item.quantity ?? item.qty ?? item.amount ?? 0)} ${escapeHTML(item.unit || "items")}</span><span>${escapeHTML(item.location || item.address || "Location not set")}</span><span>${formatDate(item.pickupDate || item.date)}</span></div>
            ${item.description ? `<p class="donation-description">${escapeHTML(item.description)}</p>` : ""}</div><div></div>
        </article>`).join("");
}

function setupReceiverFilters() {
    const search = document.getElementById("food-search");
    const filter = document.getElementById("food-filter");
    const clear = document.getElementById("clear-filters");
    const user = getCurrentUser();
    search?.addEventListener("input", () => renderAvailable(user));
    filter?.addEventListener("change", () => renderAvailable(user));
    clear?.addEventListener("click", () => {
        search.value = "";
        filter.value = "all";
        renderAvailable(user);
    });
}
function setupReceiverMobile() {
    const toggle = document.getElementById("mobile-menu-toggle");
    const nav = document.getElementById("mobile-nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", () => {
        const open = nav.classList.toggle("open");
        toggle.setAttribute("aria-expanded", String(open));
        document.body.classList.toggle("menu-open", open);
    });
}
function setupReceiverLogout() {
    document.getElementById("logout-btn")?.addEventListener("click", logoutUser);
    document.getElementById("mobile-logout-btn")?.addEventListener("click", logoutUser);
}
function setText(id, value) { const el = document.getElementById(id); if (el) el.textContent = value; }
function formatDate(value) {
    if (!value) return "No date";
    const d = new Date(`${value}T00:00:00`);
    return Number.isNaN(d.getTime()) ? value : d.toLocaleDateString(undefined,{day:"numeric",month:"short",year:"numeric"});
}
function escapeHTML(value) { return String(value ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c])); }
function showToast(message,error=false){const toast=document.getElementById("toast"),text=document.getElementById("toast-message");if(!toast||!text)return;text.textContent=message;toast.classList.toggle("error",error);toast.classList.add("show");clearTimeout(window.__receiverToast);window.__receiverToast=setTimeout(()=>toast.classList.remove("show"),2800);}
