const DIALOG_ICONS = {
    error: "×",
    warning: "!",
    info: "i"
};

function showAppDialog(type, heading, message, actions) {
    let dialog = document.getElementById("app-dialog");
    if (!dialog) {
        dialog = document.createElement("dialog");
        dialog.id = "app-dialog";
        dialog.className = "app-dialog";
        dialog.setAttribute("aria-labelledby", "app-dialog-title");
        dialog.innerHTML = '<div class="dialog-heading"><span class="dialog-icon" aria-hidden="true"></span><h2 id="app-dialog-title"></h2></div><p class="dialog-message"></p><form method="dialog" class="dialog-actions"></form>';
        document.body.appendChild(dialog);
    }

    const icon = dialog.querySelector(".dialog-icon");
    const title = dialog.querySelector("#app-dialog-title");
    const text = dialog.querySelector(".dialog-message");
    const actionForm = dialog.querySelector(".dialog-actions");
    icon.textContent = DIALOG_ICONS[type] || DIALOG_ICONS.info;
    title.textContent = heading;
    text.textContent = message;
    dialog.dataset.kind = type;
    actionForm.replaceChildren();

    const choices = actions || [{value: "ok", label: "Понятно", primary: true}];
    for (const choice of choices) {
        const button = document.createElement("button");
        button.type = "submit";
        button.value = choice.value;
        button.textContent = choice.label;
        button.className = choice.primary ? "button" : "button button-secondary";
        actionForm.appendChild(button);
    }

    return new Promise((resolve) => {
        dialog.addEventListener("close", () => resolve(dialog.returnValue), {once: true});
        dialog.showModal();
        actionForm.querySelector("button:last-child").focus();
    });
}
