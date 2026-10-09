document.addEventListener("DOMContentLoaded", () => {
    const user = requireRole("admin");
    if (!user) return;

    document.getElementById("admin-avatar").textContent = (user.name || "A").charAt(0).toUpperCase();
    document.getElementById("admin-date").textContent = new Date().toLocaleDateString(undefined,{day:"numeric",month:"short",year:"numeric"});

    setupAdminNavigation();
    setupAdminMenu();
    setupAdminLogout();
    setupDonationFilters();
    renderAdmin();

    window.addEventListener("storage", renderAdmin);
});

function readList(key) {
    try { return JSON.parse(localStorage.getItem(key)) || []; }
    catch { return []; }
}
function renderAdmin() {
    const users = readList("zeroBiteUsers");
    const foods = readList("shareBiteFoods");
    const available = foods.filter(item => (item.status || item.state || "Available").toLowerCase() === "available");
    const claimed = foods.filter(item => (item.status || item.state || "").toLowerCase() === "claimed");

    setText("total-users", users.length);
    setText("total-donations", foods.length);
    setText("claimed-food", claimed.length);
    setText("available-food", available.length);
    setText("admin-donor-count", users.filter(u => u.role === "donor").length);
    setText("admin-receiver-count", users.filter(u => u.role === "receiver").length);
    setText("admin-total-account-count", users.length);

    renderDonationTable(foods);
    renderUsers(users);
    renderActivity(users, foods);
}

function renderDonationTable(foods) {
    const body = document.getElementById("donation-table-body");
    const empty = document.getElementById("donation-empty");
    const search = document.getElementById("donation-search")?.value.trim().toLowerCase() || "";
    const filter = document.getElementById("donation-filter")?.value || "all";

    const filtered = foods.filter(item => {
        const status = (item.status || item.state || "Available").toLowerCase();
        const haystack = `${item.foodName || item.food || ""} ${item.donorName || ""} ${item.location || item.address || ""}`.toLowerCase();
        return (filter === "all" || status === filter) && (!search || haystack.includes(search));
    });

    body.innerHTML = filtered.map(item => {
        const status = (item.status || item.state || "Available").toLowerCase();
        return `<tr>
            <td><strong>${escapeHTML(item.foodName || item.food || "Food")}</strong></td>
            <td>${escapeHTML(item.donorName || item.donorEmail || "Unknown")}</td>
            <td>${escapeHTML(item.quantity ?? item.qty ?? item.amount ?? 0)} ${escapeHTML(item.unit || "items")}</td>
            <td>${escapeHTML(item.location || item.address || "Not set")}</td>
            <td><span class="admin-status-badge ${status === "claimed" ? "claimed" : "available"}">${escapeHTML(status)}</span></td>
            <td>${formatDate(item.pickupDate || item.date)}</td>
        </tr>`;
    }).join("");

    empty.style.display = filtered.length ? "none" : "block";
}

function renderUsers(users) {
    const list = document.getElementById("admin-user-list");
    list.innerHTML = users.length ? users.map(user => `
        <article class="admin-user-card">
            <div class="admin-user-card-main"><span class="admin-user-avatar">${escapeHTML((user.name || "U").charAt(0).toUpperCase())}</span><div class="admin-user-info"><strong>${escapeHTML(user.name || "Unnamed")}</strong><span>${escapeHTML(user.email || "")}</span></div></div>
            <span class="admin-user-role">${escapeHTML(user.role || "user")}</span>
        </article>`).join("") : `<div class="admin-table-empty">No users yet.</div>`;
}

function renderActivity(users, foods) {
    const list = document.getElementById("admin-activity-list");
    const activities = [];
    users.forEach(user => activities.push({type:"USER", title:"New account", text:`${user.name || "A user"} joined as a ${user.role || "user"}.`, time:user.createdAt}));
    foods.forEach(food => {
        activities.push({type:"FOOD", title:"Food listed", text:`${food.foodName || food.food || "Food"} was shared by ${food.donorName || "a donor"}.`, time:food.createdAt});
        if ((food.status || food.state || "").toLowerCase() === "claimed") {
            activities.push({type:"CLAIM", title:"Food claimed", text:`${food.foodName || food.food || "Food"} was claimed by ${food.claimedByName || "a receiver"}.`, time:food.claimedAt});
        }
    });
    activities.sort((a,b)=>new Date(b.time||0)-new Date(a.time||0));
    list.innerHTML = activities.slice(0,8).map((item,index)=>`
        <article class="admin-activity-item"><span class="admin-activity-icon">${String(index+1).padStart(2,"0")}</span><div class="admin-activity-content"><strong>${escapeHTML(item.title)}</strong><p>${escapeHTML(item.text)}</p></div><span class="admin-activity-time">${formatDateTime(item.time)}</span></article>`).join("") || `<div class="admin-table-empty">No activity yet.</div>`;
}

function setupAdminNavigation() {
    document.querySelectorAll("[data-scroll-target]").forEach(button => {
        button.addEventListener("click", () => document.querySelector(button.dataset.scrollTarget)?.scrollIntoView({behavior:"smooth"}));
    });
    document.querySelectorAll(".admin-nav-link").forEach(link => {
        link.addEventListener("click", () => {
            document.querySelectorAll(".admin-nav-link").forEach(item => item.classList.remove("active"));
            link.classList.add("active");
            closeAdminMenu();
        });
    });
}
function setupAdminMenu() {
    const button = document.getElementById("admin-menu-btn");
    const sidebar = document.getElementById("admin-sidebar");
    const overlay = document.getElementById("admin-overlay");
    button?.addEventListener("click", () => { sidebar.classList.add("open"); overlay.classList.add("active"); });
    overlay?.addEventListener("click", closeAdminMenu);
}
function closeAdminMenu() {
    document.getElementById("admin-sidebar")?.classList.remove("open");
    document.getElementById("admin-overlay")?.classList.remove("active");
}
function setupAdminLogout() { document.getElementById("admin-logout")?.addEventListener("click", logoutUser); }
function setupDonationFilters() {
    document.getElementById("donation-search")?.addEventListener("input", renderAdmin);
    document.getElementById("donation-filter")?.addEventListener("change", renderAdmin);
}
function setText(id,value){const el=document.getElementById(id);if(el)el.textContent=value}
function formatDate(value){if(!value)return"No date";const d=new Date(`${value}T00:00:00`);return Number.isNaN(d.getTime())?value:d.toLocaleDateString(undefined,{day:"numeric",month:"short",year:"numeric"})}
function formatDateTime(value){if(!value)return"";const d=new Date(value);return Number.isNaN(d.getTime())?"":d.toLocaleDateString(undefined,{day:"numeric",month:"short"})}
function escapeHTML(value){return String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
