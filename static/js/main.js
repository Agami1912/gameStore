document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const logoutButton = document.getElementById("logout-button");
    const addGameButton = document.getElementById("add-game");
    const addCustomerButton = document.getElementById("add-customer");
    const loanGameButton = document.getElementById("loan-game");
    const returnGameButton = document.getElementById("return-game");
    const loanList = document.getElementById("loan-list");
    const gameList = document.getElementById("game-list");
    const customerList = document.getElementById("customer-list");

    // Function to fetch and display games
    async function loadGames() {
    if (!gameList) return;
    try {
        let response = await fetch("/api/games");
        let games = await response.json();
        gameList.innerHTML = ""; // Clear previous entries

        games.forEach(game => {
            let listItem = document.createElement("li");
            listItem.textContent = `ID: ${game.id} - ${game.title} - ${game.genre} - $${game.price} - Quantity: ${game.quantity}`;
            gameList.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error loading games:", error);
    }
}
    // Function to fetch and display customers
    async function loadCustomers() {
    if (!customerList) return;
    try {
        let response = await fetch("/api/customers");
        let customers = await response.json();
        customerList.innerHTML = ""; // Clear previous entries

        customers.forEach(customer => {
            let listItem = document.createElement("li");
            listItem.textContent = `ID: ${customer.id} - ${customer.name} - ${customer.email} - ${customer.phone}`;
            customerList.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error loading customers:", error);
    }
   }
    async function loadLoans() {
    try {
        let response = await fetch("/api/loans", { method: "GET" });
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        let loans = await response.json();
        displayLoans(loans);
    } catch (error) {
        console.error("Failed to load loans:", error);
    }
}


    // Load games and customers when the page loads
    loadGames();
    loadCustomers();
    loadLoans();


    // Login event
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

    // Logout event
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

    // Add game event
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
                loadGames(); // Reload the game list
            } catch (error) {
                console.error("Error adding game:", error);
                alert("Failed to add game.");
            }
        });
    }
       // Loan Game button event
if (loanGameButton) {
    loanGameButton.addEventListener("click", async function () {
        const gameId = prompt("Enter Game ID to loan:");
        const customerId = prompt("Enter Customer ID:");

        if (!gameId || !customerId) {
            alert("Both Game ID and Customer ID are required.");
            return;
        }

        try {
            let response = await fetch("/api/loans", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ game_id: gameId, customer_id: customerId })
            });

            let data = await response.json();
            alert(data.message);  // Show the success or failure message
            loadLoans();  // Refresh the loan list
        } catch (error) {
            console.error("Error loaning game:", error);
            alert("Failed to loan game.");
        }
    });
}


    // החזרת משחק
    if (returnGameButton) {
        returnGameButton.addEventListener("click", async function () {
            const loanId = prompt("Enter Loan ID to return:");

            if (!loanId) {
                alert("Loan ID is required.");
                return;
            }

            try {
                let response = await fetch(`/api/loans/${loanId}/return`, { method: "POST" });

                let data = await response.json();
                alert(data.message);
                loadLoans(); // מרענן את הרשימה
            } catch (error) {
                console.error("Error returning game:", error);
                alert("Failed to return game.");
            }
        });
    }
   function displayLoans(loans) {
    const loanList = document.getElementById("loan-list");
    if (!loanList) {
        console.error("Loan list element not found");
        return;
    }
    loanList.innerHTML = ""; // Clear the list first

    loans.forEach(loan => {
        let listItem = document.createElement("li");
        const returnDate = loan.return_date ? new Date(loan.return_date).toLocaleDateString() : "Not returned";
        listItem.textContent = `Game ID: ${loan.game_id}, Customer ID: ${loan.customer_id}, Loan Date: ${new Date(loan.loan_date).toLocaleDateString()}, Return Date: ${returnDate}`;
        loanList.appendChild(listItem);
    });
}



    // Add customer event
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
                loadCustomers(); // Reload the customer list
            } catch (error) {
                console.error("Error adding customer:", error);
                alert("Failed to add customer.");
            }

        });
    }

});
