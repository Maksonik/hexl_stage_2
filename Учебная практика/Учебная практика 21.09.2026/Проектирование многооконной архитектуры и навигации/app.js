const cardsEl = document.getElementById("cards");
const statusEl = document.getElementById("status");
const refreshBtn = document.getElementById("refresh-btn");

function addText(parent, tagName, className, text) {
    const element = document.createElement(tagName);
    element.className = className;
    // Данные из БД выводим как текст, не интерпретируя их как HTML.
    element.textContent = text;
    parent.appendChild(element);
    return element;
}

function renderPartners(partners) {
    cardsEl.replaceChildren();
    for (const partner of partners) {
        const item = document.createElement("li");
        const card = document.createElement("a");
        card.className = "card";
        card.href = "/partner/" + encodeURIComponent(partner.partner_id);
        const info = document.createElement("span");
        info.className = "card-info";
        addText(info, "span", "card-title", partner.company_name);
        addText(info, "span", "card-role", partner.partner_type);
        addText(info, "span", "card-detail", "Телефон: " + (partner.phone || "—"));
        addText(info, "span", "card-detail", "Email: " + partner.contact_email);
        addText(info, "span", "card-detail", "ИНН: " + partner.inn);
        addText(info, "span", "card-detail", "Рейтинг: " + partner.rating);
        const summary = document.createElement("span");
        summary.className = "card-summary";
        addText(summary, "span", "card-volume", partner.total_quantity.toLocaleString("ru-RU") + " шт.");
        addText(summary, "span", "card-discount", "Скидка " + partner.discount_percent + "%");
        card.append(info, summary);
        item.appendChild(card);
        cardsEl.appendChild(item);
    }
    if (partners.length === 0) {
        const item = document.createElement("li");
        item.className = "empty-message";
        item.textContent = "Партнёры не найдены";
        cardsEl.appendChild(item);
    }
}

async function loadPartners() {
    statusEl.textContent = "Загрузка данных…";
    refreshBtn.disabled = true;
    try {
        const response = await fetch("/api/partners");
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || "Не удалось загрузить данные.");
        }
        renderPartners(result);
        statusEl.textContent = "Данные обновлены: " + result.length + " партнёров";
    } catch (error) {
        statusEl.textContent = "Не удалось загрузить список партнёров.";
        await showAppDialog("error", "Не удалось загрузить данные", error.message);
    } finally {
        refreshBtn.disabled = false;
    }
}

refreshBtn.addEventListener("click", loadPartners);
loadPartners();

// Подтверждение показываем после возврата из формы сохранения.
if (new URLSearchParams(window.location.search).has("saved")) {
    showAppDialog("info", "Сохранено", "Данные партнёра сохранены.");
}
