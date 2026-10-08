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
        // ID партнёра передаётся в другие окна через адрес страницы.
        const url = "/partner/" + encodeURIComponent(partner.partner_id);
        const item = document.createElement("li");
        const card = document.createElement("div");
        card.className = "card";
        const info = document.createElement("div");
        info.className = "card-info";
        addText(info, "span", "card-role", partner.partner_type);
        addText(info, "span", "card-title", partner.partner_name);
        addText(info, "span", "card-detail", "Директор: " + (partner.director_name || "—"));
        addText(info, "span", "card-detail", "Телефон: " + (partner.phone || "—"));
        addText(info, "span", "card-detail", "Email: " + partner.email);
        addText(info, "span", "card-detail", "Рейтинг: " + partner.rating);
        const summary = document.createElement("div");
        summary.className = "card-summary";
        addText(summary, "span", "card-volume", partner.total_quantity.toLocaleString("ru-RU") + " шт.");
        addText(summary, "span", "card-discount", "Скидка " + partner.discount_percent + "%");
        card.append(info, summary);
        const actions = document.createElement("div");
        actions.className = "card-actions";
        addText(actions, "a", "button button-secondary", "Редактировать").href = url;
        addText(actions, "a", "button button-secondary", "История продаж").href = url + "/history";
        item.append(card, actions);
        cardsEl.appendChild(item);
    }
    if (partners.length === 0) {
        addText(cardsEl, "li", "empty-message", "Партнёры не найдены");
    }
}

async function loadPartners() {
    statusEl.textContent = "Загрузка данных…";
    refreshBtn.disabled = true;
    try {
        const result = await apiRequest("/api/partners");
        renderPartners(result);
        statusEl.textContent = "Данные обновлены: " + result.length + " партнёров";
    } catch (error) {
        statusEl.textContent = "Не удалось загрузить список партнёров.";
        await showError("Не удалось загрузить данные", error);
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
