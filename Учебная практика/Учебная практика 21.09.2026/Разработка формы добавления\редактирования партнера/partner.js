const form = document.getElementById("partner-form");
const title = document.getElementById("page-title");
const status = document.getElementById("status");
const saveButton = document.getElementById("save-btn");
const cancelLink = document.getElementById("cancel-link");
const fieldNames = [
    "company_name", "partner_type", "inn", "contact_email",
    "rating", "phone", "address", "director_name"
];

const isNew = window.location.pathname === "/partner/new";
// ID из адреса нужен для загрузки и обновления выбранного партнёра.
const partnerId = isNew ? null : window.location.pathname.split("/").pop();
let initialValues = "";

function getFormData() {
    const data = {};
    for (const name of fieldNames) {
        data[name] = form.elements[name].value.trim();
    }
    return data;
}

function rememberForm() {
    initialValues = JSON.stringify(getFormData());
}

function formChanged() {
    return JSON.stringify(getFormData()) !== initialValues;
}

function checkForm(data) {
    if (!data.company_name) return ["Введите наименование партнёра.", "company_name"];
    if (!data.partner_type) return ["Выберите тип партнёра.", "partner_type"];
    if (!data.inn) return ["Введите ИНН.", "inn"];
    if (!/^[0-9]{10}([0-9]{2})?$/.test(data.inn)) {
        return ["ИНН должен содержать 10 или 12 цифр.", "inn"];
    }
    if (!data.contact_email) return ["Введите email.", "contact_email"];
    if (!form.elements.contact_email.checkValidity()) {
        return ["Введите email в формате name@example.ru.", "contact_email"];
    }
    if (!/^[0-9]+$/.test(data.rating) || !Number.isSafeInteger(Number(data.rating))) {
        return ["Рейтинг должен быть целым числом от 0. Удалите дробную часть или знак минус.", "rating"];
    }
    return null;
}

async function loadPartner() {
    if (isNew) {
        form.elements.rating.value = "0";
        title.textContent = "CRM: Карточка партнёра [Добавление]";
        document.title = title.textContent;
        rememberForm();
        form.elements.company_name.focus();
        return;
    }

    title.textContent = "CRM: Карточка партнёра [Редактирование]";
    document.title = title.textContent;
    status.textContent = "Загрузка данных партнёра…";
    saveButton.disabled = true;
    try {
        const response = await fetch("/api/partners/" + encodeURIComponent(partnerId));
        const partner = await response.json();
        if (!response.ok) throw new Error(partner.error || "Не удалось загрузить данные партнёра.");

        for (const name of fieldNames) {
            form.elements[name].value = partner[name] ?? "";
        }
        rememberForm();
        status.textContent = "";
        saveButton.disabled = false;
        form.elements.company_name.focus();
    } catch (error) {
        status.textContent = "Не удалось загрузить данные партнёра.";
        rememberForm();
        await showAppDialog("error", "Ошибка загрузки", error.message);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = getFormData();
    const error = checkForm(data);
    if (error) {
        await showAppDialog("error", "Ошибка ввода", error[0]);
        form.elements[error[1]].focus();
        return;
    }

    data.rating = Number(data.rating);
    saveButton.disabled = true;
    status.textContent = "Сохранение…";

    try {
        const response = await fetch(
            isNew ? "/api/partners" : "/api/partners/" + encodeURIComponent(partnerId),
            {
                method: isNew ? "POST" : "PUT",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(data)
            }
        );
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Не удалось сохранить партнёра.");

        // Снимаем отметку о правках, чтобы переход не вызвал лишнее предупреждение.
        rememberForm();
        window.location.assign("/?saved=1");
    } catch (error) {
        await showAppDialog("error", "Не удалось сохранить", error.message);
        status.textContent = "";
        saveButton.disabled = false;
    }
});

cancelLink.addEventListener("click", async (event) => {
    if (!formChanged()) return;
    event.preventDefault();

    const answer = await showAppDialog(
        "warning",
        "Несохранённые изменения",
        "Если уйти сейчас, введённые данные будут потеряны.",
        [
            {value: "stay", label: "Остаться"},
            {value: "leave", label: "Покинуть форму", primary: true}
        ]
    );
    if (answer === "leave") {
        rememberForm();
        window.location.assign("/");
    }
});

window.addEventListener("beforeunload", (event) => {
    if (formChanged()) {
        event.preventDefault();
        event.returnValue = "";
    }
});

loadPartner();
