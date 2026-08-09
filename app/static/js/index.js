const cetirizineButton =
    document.getElementById("cetirizine-button");

const statusBox =
    document.getElementById("status");


function showStatus(message, success = true) {
    statusBox.textContent = message;

    statusBox.className =
        success
            ? "status status-success"
            : "status status-error";

    statusBox.hidden = false;
}


async function addCetirizine() {
    cetirizineButton.disabled = true;

    showStatus(
        "Mentés...",
        true
    );

    try {
        const response = await fetch(
            "api/events/cetirizine",
            {
                method: "POST",
            }
        );

        const data = await response.json();

        if (!response.ok || !data.ok) {
            throw new Error(
                data.message || "Sikertelen mentés."
            );
        }

        showStatus(
            data.message,
            true
        );

        window.setTimeout(
            () => {
                window.location.reload();
            },
            500
        );

    } catch (error) {
        console.error(error);

        showStatus(
            error.message || "Hiba történt.",
            false
        );

        cetirizineButton.disabled = false;
    }
}


cetirizineButton.addEventListener(
    "click",
    addCetirizine
);
