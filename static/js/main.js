    document.addEventListener("DOMContentLoaded", function () {
        const loginForm = document.getElementById("login-form");
        const logoutButton = document.getElementById("logout-button");
        const addGameButton = document.getElementById("add-game");
        const addCustomerButton = document.getElementById("add-customer");

        if (loginForm) {
            loginForm.addEventListener("submit", async function (event) {
                event.preventDefault();

                let username = document.getElementById("username").value.trim();
                let password = document.getElementById("password").value.trim();

                if (!username || !password) {
                    alert("Please enter both username and password.");
                    return;
                }

                try {
                    let response = await fetch("/api/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username, password })
                    });

                    let data = await response.json();

                    if (response.ok) {
                        alert("Login successful!");
                        window.location.href = "/dashboard";
                    } else {
                        alert("Login failed: " + data.error);
                    }
                } catch (error) {
                    console.error("Error during login:", error);
                    alert("An error occurred. Please try again later.");
                }
            });
        }

        if (logoutButton) {
            logoutButton.addEventListener("click", async function () {
                try {
                    let response = await fetch("/logout", { method: "POST" });
                    let data = await response.json();

                    if (response.ok) {
                        alert("Logged out successfully.");
                        window.location.href = "/login";
                    } else {
                        alert("Logout failed: " + data.error);
                    }
                } catch (error) {
                    console.error("Error during logout:", error);
                    alert("An error occurred while logging out.");
                }
            });
        }

        if (addGameButton) {
            addGameButton.addEventListener("click", async function () {
                const title = prompt("Enter game title:");
                const genre = prompt("Enter game genre:");
                const price = parseFloat(prompt("Enter game price:"));
                const quantity = parseInt(prompt("Enter quantity:"));

                if (!title || !genre || isNaN(price) || isNaN(quantity)) {
                    alert("Invalid input. Please try again.");
                    return;
                }

                try {
                    let response = await fetch("/api/games", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ title, genre, price, quantity })
                    });

                    let data = await response.json();
                    alert(data.message);
                    location.reload();
                } catch (error) {
                    console.error("Error adding game:", error);
                    alert("Failed to add game.");
                }
            });
        }

        if (addCustomerButton) {
            addCustomerButton.addEventListener("click", async function () {
                const name = prompt("Enter customer name:");
                const email = prompt("Enter customer email:");
                const phone = prompt("Enter customer phone:");

                if (!name || !email || !phone) {
                    alert("All fields are required.");
                    return;
                }

                try {
                    let response = await fetch("/api/customers", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name, email, phone })
                    });

                    let data = await response.json();
                    alert(data.message);
                    location.reload();
                } catch (error) {
                    console.error("Error adding customer:", error);
                    alert("Failed to add customer.");
                }
            });
        }
    });
