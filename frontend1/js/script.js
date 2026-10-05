// =========================
// HOMEPAGE NAVIGATION
// =========================

function goToDonor() {
    window.location.href = "/frontend1/pages/donor.html";
}

function goToReceiver() {
    window.location.href = "/frontend1/pages/receiver.html";
}


// =========================
// LOGIN / SIGNUP
// =========================

function loginUser() {
    alert("Login system coming soon!");
}

function signupUser() {
    alert("Sign Up system coming soon!");
}


// =========================
// LOGOUT
// =========================

function logoutUser() {
    window.location.href = "../index.html";
}


// =========================
// DONOR DASHBOARD
// =========================

function openDonationForm() {

    const form =
        document.getElementById("donation-form");

    if (form) {

        form.scrollIntoView({
            behavior: "smooth"
        });

    }
}


// =========================
// FOOD DONATION FORM
// =========================

const foodForm =
    document.getElementById("food-form");


if (foodForm) {

    foodForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            // =========================
            // GET FORM VALUES
            // =========================

            const foodName =
                document
                    .getElementById("food-name")
                    .value
                    .trim();


            const quantity =
                Number(
                    document
                        .getElementById("quantity")
                        .value
                );


            const serves =
                Number(
                    document
                        .getElementById("serves")
                        .value
                );


            const location =
                document
                    .getElementById("location")
                    .value
                    .trim();


            const description =
                document
                    .getElementById("description")
                    .value
                    .trim();


            // =========================
            // FORM VALIDATION
            // =========================

            if (foodName.length < 2) {

                alert(
                    "Please enter a valid food name."
                );

                return;
            }


            if (
                !Number.isFinite(quantity) ||
                quantity <= 0
            ) {

                alert(
                    "Quantity must be greater than 0."
                );

                return;
            }


            if (
                !Number.isFinite(serves) ||
                serves <= 0
            ) {

                alert(
                    "Number of people served must be greater than 0."
                );

                return;
            }


            if (location.length < 2) {

                alert(
                    "Please enter a valid pickup location."
                );

                return;
            }


            // =========================
            // CREATE FOOD OBJECT
            // =========================

            const food = {

                id: Date.now(),

                name: foodName,

                quantity: quantity,

                serves: serves,

                location: location,

                description: description,

                status: "Available"

            };


            // =========================
            // GET EXISTING FOODS
            // =========================

            let foods =
                JSON.parse(
                    localStorage.getItem(
                        "shareBiteFoods"
                    )
                ) || [];


            // =========================
            // ADD NEW FOOD
            // =========================

            foods.push(food);


            // =========================
            // SAVE FOODS
            // =========================

            localStorage.setItem(
                "shareBiteFoods",
                JSON.stringify(foods)
            );


            // =========================
            // ADD CARD TO DONOR DASHBOARD
            // =========================

            addDonationCard(food);


            // =========================
            // RESET FORM
            // =========================

            foodForm.reset();


            // =========================
            // SUCCESS MESSAGE
            // =========================

            alert(
                "Food donation added successfully! 🍱"
            );

        }
    );

}


// =========================
// ADD DONATION CARD
// =========================

function addDonationCard(food) {

    const donationList =
        document.getElementById(
            "donation-list"
        );


    if (!donationList) {
        return;
    }


    const newCard =
        document.createElement("div");


    newCard.className =
        "donation-card";


    newCard.innerHTML = `

        <div class="food-image">
            🍱
        </div>

        <div class="donation-info">

            <h3>
                ${food.name}
            </h3>

            <p>
                Quantity: ${food.quantity}
            </p>

            <p>
                Serves: ${food.serves} people
            </p>

            <p>
                📍 ${food.location}
            </p>

            <span class="status ${
                food.status === "Claimed"
                    ? "claimed"
                    : "available"
            }">

                ${food.status}

            </span>

        </div>

    `;


    donationList.appendChild(
        newCard
    );

}


// =========================
// LOAD DONOR FOODS
// =========================

function loadDonorFoods() {

    const donationList =
        document.getElementById(
            "donation-list"
        );


    if (!donationList) {
        return;
    }


    // Clear existing cards

    donationList.innerHTML = "";


    // Get saved foods

    const foods =
        JSON.parse(
            localStorage.getItem(
                "shareBiteFoods"
            )
        ) || [];


    // No donations

    if (foods.length === 0) {

        donationList.innerHTML =
            "<p>No donations yet.</p>";

        return;
    }


    // Add saved donations

    foods.forEach(
        function (food) {

            addDonationCard(food);

        }
    );

}


// =========================
// RECEIVER DASHBOARD
// =========================

function loadReceiverFoods() {

    const foodList =
        document.getElementById(
            "food-list"
        );


    if (!foodList) {
        return;
    }


    // Clear existing cards

    foodList.innerHTML = "";


    // Get saved foods

    const foods =
        JSON.parse(
            localStorage.getItem(
                "shareBiteFoods"
            )
        ) || [];


    // Only available foods

    const availableFoods =
        foods.filter(
            function (food) {

                return food.status === "Available";

            }
        );


    // No available food

    if (availableFoods.length === 0) {

        foodList.innerHTML =
            "<p>No food is currently available.</p>";

        return;
    }


    // Create cards

    availableFoods.forEach(
        function (food) {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "donation-card food-card";


            // Store unique food ID

            card.setAttribute(
                "data-id",
                food.id
            );


            card.innerHTML = `

                <div class="food-image">
                    🍱
                </div>

                <div class="donation-info">

                    <h3>
                        ${food.name}
                    </h3>

                    <p>
                        👥 Serves:
                        ${food.serves} people
                    </p>

                    <p>
                        📦 Quantity:
                        ${food.quantity}
                    </p>

                    <p>
                        📍 ${food.location}
                    </p>

                    <span class="status available">
                        Available
                    </span>

                    <br><br>

                    <button
                        class="primary-btn claim-btn"
                        onclick="claimFood(this)">

                        Claim Food

                    </button>

                </div>

            `;


            foodList.appendChild(
                card
            );

        }
    );

}


// =========================
// SEARCH FOOD
// =========================

function searchFood() {

    const searchInput =
        document.getElementById(
            "food-search"
        );


    const foodList =
        document.getElementById(
            "food-list"
        );


    if (!searchInput || !foodList) {
        return;
    }


    const searchValue =
        searchInput.value
            .toLowerCase()
            .trim();


    const foodCards =
        document.querySelectorAll(
            ".food-card"
        );


    foodCards.forEach(
        function (card) {

            const foodName =
                card
                    .querySelector("h3")
                    .textContent
                    .toLowerCase();


            if (
                foodName.includes(
                    searchValue
                )
            ) {

                card.style.display =
                    "block";

            } else {

                card.style.display =
                    "none";

            }

        }
    );

}


// =========================
// CLAIM FOOD
// =========================

function claimFood(button) {

    const card =
        button.closest(
            ".food-card"
        );


    if (!card) {
        return;
    }


    // Get unique food ID

    const foodId =
        Number(
            card.getAttribute(
                "data-id"
            )
        );


    // Get saved foods

    let foods =
        JSON.parse(
            localStorage.getItem(
                "shareBiteFoods"
            )
        ) || [];


    // Find correct food

    const food =
        foods.find(
            function (item) {

                return item.id === foodId;

            }
        );


    if (!food) {

        alert(
            "Food information not found."
        );

        return;
    }


    // Change status

    food.status =
        "Claimed";


    // Save claim time

    food.claimedAt =
        new Date().toLocaleString();


    // Save updated foods

    localStorage.setItem(
        "shareBiteFoods",
        JSON.stringify(foods)
    );


    // Refresh available food

    loadReceiverFoods();


    // Refresh claims

    loadMyClaims();


    alert(
        "Food claimed successfully! 🍱"
    );

}


// =========================
// LOAD MY CLAIMS
// =========================

function loadMyClaims() {

    const claimsList =
        document.getElementById(
            "claims-list"
        );


    if (!claimsList) {
        return;
    }


    // Get saved foods

    const foods =
        JSON.parse(
            localStorage.getItem(
                "shareBiteFoods"
            )
        ) || [];


    // Only claimed foods

    const claimedFoods =
        foods.filter(
            function (food) {

                return food.status === "Claimed";

            }
        );


    // No claims

    if (claimedFoods.length === 0) {

        claimsList.innerHTML =
            "<p>No food claimed yet.</p>";

        return;
    }


    // Clear old claims

    claimsList.innerHTML = "";


    // Create claim cards

    claimedFoods.forEach(
        function (food) {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "donation-card";


            card.innerHTML = `

                <div class="food-image">
                    🍱
                </div>

                <div class="donation-info">

                    <h3>
                        ${food.name}
                    </h3>

                    <p>
                        👥 Serves:
                        ${food.serves} people
                    </p>

                    <p>
                        📦 Quantity:
                        ${food.quantity}
                    </p>

                    <p>
                        📍 ${food.location}
                    </p>

                    <p>
                        🕒 Claimed:
                        ${food.claimedAt || "Recently"}
                    </p>

                    <span class="status claimed">
                        Claimed ✓
                    </span>

                </div>

            `;


            claimsList.appendChild(
                card
            );

        }
    );

}


// =========================
// PAGE INITIALIZATION
// =========================

// Load donor donations

loadDonorFoods();


// Load receiver available food

loadReceiverFoods();


// Load receiver claims

loadMyClaims();