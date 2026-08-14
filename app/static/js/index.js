const i18n =
    window.SYMPTOMTRACKER_I18N || {};

const medicationButton =
    document.getElementById("medication-button");

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


async function addDefaultMedication() {
    medicationButton.disabled = true;

    showStatus(
        (i18n.saving || "Saving..."),
        true
    );

    try {
        const response = await fetch(
            "api/events/default-medication",
            {
                method: "POST",
            }
        );

        const data = await response.json();

        if (!response.ok || !data.ok) {
            throw new Error(
                data.message || i18n.saveFailed || "Save failed."
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
            error.message || i18n.genericError || "An error occurred.",
            false
        );

        medicationButton.disabled = false;
    }
}


medicationButton.addEventListener(
    "click",
    addDefaultMedication
);
