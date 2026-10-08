const form = document.getElementById("partner-form");
const title = document.getElementById("page-title");
const status = document.getElementById("status");
const saveButton = document.getElementById("save-btn");
const backLink = document.getElementById("back-link");
const historyLink = document.getElementById("history-link");
const fieldNames = [
    "partner_name", "partner_type", "rating", "inn",
    "address", "director_name", "phone", "email"
];

const isNew = window.location.pathname === "/partner/new";
// ID из адреса нужен для загрузки и обновления выбранного партнёра.
const partnerId = isNew ? null : encodeURIComponent(window.location.pathname.split("/").pop());
const historyUrl = "/partner/" + partnerId + "/history";
// «Назад» ведёт в то окно, из которого открыли форму, и к тому же партнёру.
const cameFromHistory = new URLSearchParams(window.location.search).get("from") === "history";
const backUrl = cameFromHistory ? historyUrl : "/";
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
    const again = "Нажмите «Сохранить» ещё раз.";
    if (!data.partner_name) {
        return ["Не заполнено наименование партнёра.", "partner_name", ["Введите название организации в поле «Наименование».", again]];
    }
    if (!data.partner_type) {
        return ["Не выбран тип партнёра.", "partner_type", ["Откройте список «Тип партнёра».", "Выберите подходящий вариант.", again]];
    }
    if (!/^[0-9]+$/.test(data.rating)) {
        return ["Рейтинг должен быть целым неотрицательным числом.", "rating", ["Введите в поле «Рейтинг» число от 0 без знака минус и дробной части.", again]];
    }
    if (!/^[0-9]{10}([0-9]{2})?$/.test(data.inn)) {
        return ["ИНН должен содержать 10 или 12 цифр.", "inn", ["Проверьте ИНН по документам партнёра.", "Введите 10 цифр для организации или 12 для ИП.", again]];
    }
    if (!data.email || !form.elements.email.checkValidity()) {
        return ["Email не заполнен или введён с ошибкой.", "email", ["Введите адрес в формате name@example.ru.", again]];
    }
    return null;
}

async function loadPartner() {
    backLink.href = backUrl;
    if (isNew) {
        form.elements.rating.value = "0";
        title.textContent = "CRM: Карточка партнёра [Добавление]";
        document.title = title.textContent;
        rememberForm();
        form.elements.partner_name.focus();
        return;
    }

    title.textContent = "CRM: Карточка партнёра [Редактирование]";
    document.title = title.textContent;
    historyLink.href = historyUrl;
    historyLink.hidden = false;
    status.textContent = "Загрузка данных партнёра…";
    saveButton.disabled = true;
    try {
        const partner = await apiRequest("/api/partners/" + partnerId);

        for (const name of fieldNames) {
            form.elements[name].value = partner[name] ?? "";
        }
        rememberForm();
        status.textContent = "";
        saveButton.disabled = false;
        form.elements.partner_name.focus();
    } catch (error) {
        status.textContent = "Не удалось загрузить данные партнёра.";
        rememberForm();
        await showError("Ошибка загрузки", error);
    }
}

async function confirmLeave(event) {
    if (!formChanged()) {
        return;
    }
    event.preventDefault();
    const target = event.currentTarget.href;
    const answer = await showAppDialog(
        "warning",
        "Несохранённые изменения",
        "Изменения в форме не сохранены. Если покинуть форму, они будут потеряны безвозвратно.",
        [
            {value: "stay", label: "Остаться"},
            {value: "leave", label: "Покинуть форму", primary: true}
        ]
    );
    if (answer === "leave") {
        rememberForm();
        window.location.assign(target);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = getFormData();
    const error = checkForm(data);
    if (error) {
        await showAppDialog("error", "Ошибка ввода", error[0], null, error[2]);
        form.elements[error[1]].focus();
        return;
    }

    data.rating = Number(data.rating);
    saveButton.disabled = true;
    status.textContent = "Сохранение…";

    try {
        await apiRequest(
            isNew ? "/api/partners" : "/api/partners/" + partnerId,
            {
                method: isNew ? "POST" : "PUT",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(data)
            }
        );

        // Снимаем отметку о правках, чтобы переход не вызвал лишнее предупреждение.
        rememberForm();
        // Главное окно при открытии заново читает список из БД.
        window.location.assign("/?saved=1");
    } catch (error) {
        await showError("Не удалось сохранить", error);
        status.textContent = "";
        saveButton.disabled = false;
    }
});

backLink.addEventListener("click", confirmLeave);
historyLink.addEventListener("click", confirmLeave);

window.addEventListener("beforeunload", (event) => {
    if (formChanged()) {
        event.preventDefault();
        event.returnValue = "";
    }
});

loadPartner();
