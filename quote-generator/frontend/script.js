const quoteText = document.getElementById("quoteText");
const quoteAuthor = document.getElementById("quoteAuthor");
const newQuoteBtn = document.getElementById("newQuoteBtn");

const emailInput = document.getElementById("emailInput");
const subscribeBtn = document.getElementById("subscribeBtn");

const unsubscribeEmailInput = document.getElementById("unsubscribeEmailInput");
const unsubscribeBtn = document.getElementById("unsubscribeBtn");

const quoteTextInput = document.getElementById("quoteTextInput");
const quoteAuthorInput = document.getElementById("quoteAuthorInput");
const apiKeyInput = document.getElementById("apiKeyInput");
const addQuoteBtn = document.getElementById("addQuoteBtn");

// --- Toast helper ---
function showToast(message, type = "info") {
    let background = "#444";
    if (type === "success") background = "#1abc9c";
    else if (type === "error") background = "#c0392b";
    else if (type === "info") background = "#2980b9";

    Toastify({
        text: message,
        duration: 4000,
        close: true,
        gravity: "top",
        position: "center",
        stopOnFocus: true,
        style: {
            background,
            borderRadius: "12px",
            boxShadow: "0 6px 16px rgba(0, 0, 0, 0.2)",
            padding: "14px 24px",
            fontWeight: "600",
            fontSize: "16px",
            color: "#fff",
            animation: "fadein 0.5s ease-in-out",
        },
        onClick: () => { }
    }).showToast();
}

// --- Fetch New Quote ---
async function fetchQuote() {
    try {
        quoteText.innerText = "Loading...";
        quoteAuthor.innerText = "";

        const response = await fetch("https://7xn7ze7pp6.execute-api.us-east-1.amazonaws.com/Prod/quote/");
        const data = await response.json();

        // OLD (incorrect)
        // quoteText.innerText = `"${data.text}"`;

        // ✅ NEW (correct)
        quoteText.innerText = `"${data.quote}"`;
        quoteAuthor.innerText = data.author ? `– ${data.author}` : "– Unknown";
    } catch (error) {
        quoteText.innerText = "Failed to load quote.";
        quoteAuthor.innerText = "";
        showToast("Error loading quote.", "error");
    }
}


// --- Subscribe ---
async function subscribe() {
    const email = emailInput.value.trim();
    const emailRegex = /^[\w.-]+@[\w.-]+\.\w+$/;

    // Frontend validation
    if (!email || !emailRegex.test(email)) {
        return showToast("Please enter a valid email.", "error");
    }

    try {
        const response = await fetch("https://7xn7ze7pp6.execute-api.us-east-1.amazonaws.com/Prod/subscribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
        });

        // Handle backend errors (e.g., duplicate email)
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Subscription failed.");
        }

        const result = await response.json();
        showToast(result.message || "Subscribed successfully!", "success");
        emailInput.value = "";
    } catch (err) {
        showToast(err.message || "Subscription failed.", "error"); // Shows backend error
    }
}

// --- Unsubscribe ---
async function unsubscribe() {
    const email = unsubscribeEmailInput.value.trim();
    const emailRegex = /^[\w.-]+@[\w.-]+\.\w+$/;

    // Frontend validation
    if (!email || !emailRegex.test(email)) {
        return showToast("Please enter a valid email.", "error");
    }

    try {
        const response = await fetch("https://7xn7ze7pp6.execute-api.us-east-1.amazonaws.com/Prod/unsubscribe", {
            method: "DELETE",  // Match your API method
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Unsubscribe failed.");
        }

        const result = await response.json();
        showToast(result.message || "Unsubscribed successfully!", "success");
        unsubscribeEmailInput.value = "";
    } catch (err) {
        showToast(err.message || "Unsubscribe failed.", "error");
    }
}

// --- Add Quote (Admin Only) ---
async function addQuote() {
    const text = quoteTextInput.value.trim();
    const author = quoteAuthorInput.value.trim() || "Unknown";
    const apiKey = apiKeyInput.value.trim();

    if (!text) return showToast("Quote text is required", "error");
    if (!apiKey) return showToast("API key is required", "error");

    try {
        const response = await fetch(
            "https://7xn7ze7pp6.execute-api.us-east-1.amazonaws.com/Prod/add-quote",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": apiKey
                },
                body: JSON.stringify({
                    quotes: [{ text, author }]
                })
            }
        );

        // First check if we got any response at all
        if (!response) {
            throw new Error("No response from server");
        }

        // Then check for 403 specifically
        if (response.status === 403) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { error: "Invalid API key" };
            }
            throw new Error(errorData.error || "Invalid API key");
        }

        // Then check for other errors
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { error: `Server error: ${response.status}` };
            }
            throw new Error(errorData.error || "Request failed");
        }

        // If we got here, it was successful
        const data = await response.json();
        showToast(data.message || "Quote added successfully!", "success");
        quoteTextInput.value = "";
        quoteAuthorInput.value = "";

    } catch (error) {
        // Special handling for network errors
        if (error.message.includes("Failed to fetch")) {
            showToast("Could not connect to server. Please check your internet connection.", "error");
        }
        // Handling for our custom errors
        else if (error.message.includes("API key")) {
            showToast(error.message, "error");
        }
        // All other errors
        else {
            showToast(error.message || "An unexpected error occurred", "error");
        }
        console.error("Add quote error:", error);
    }
}




// --- Event Listeners ---
newQuoteBtn.addEventListener("click", fetchQuote);
subscribeBtn.addEventListener("click", subscribe);
unsubscribeBtn.addEventListener("click", unsubscribe);
addQuoteBtn.addEventListener("click", addQuote);

// --- Load first quote on page load ---
window.addEventListener("load", fetchQuote);
