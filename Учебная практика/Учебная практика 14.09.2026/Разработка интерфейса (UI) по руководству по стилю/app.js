const API_URL = "api/partners";

const cardsEl = document.getElementById("cards");
const statusEl = document.getElementById("status");
const refreshBtn = document.getElementById("refresh-btn");

function inferRole(companyName) {
    if (companyName.startsWith("ИП ")) {
        return "Индивидуальный предприниматель";
    }
    return "Директор";
}

function renderPartners(partners) {
    cardsEl.innerHTML = "";
    for (const partner of partners) {
        const card = document.createElement("div");
        card.className = "card";

        const info = document.createElement("div");
        info.className = "card-info";

        const title = document.createElement("div");
        title.className = "card-title";
        title.textContent = partner.company_name;

        const role = document.createElement("div");
        role.className = "card-role";
        role.textContent = inferRole(partner.company_name);

        const phone = document.createElement("div");
        phone.className = "card-phone";
        phone.textContent = partner.phone || "—";

        const rating = document.createElement("div");
        rating.className = "card-rating";
        rating.textContent = "Рейтинг: " + (partner.rating === null ? "—" : partner.rating);

        info.appendChild(title);
        info.appendChild(role);
        info.appendChild(phone);
        info.appendChild(rating);

        const discount = document.createElement("div");
        discount.className = "card-discount";
        discount.textContent = partner.discount_percent + "%";

        card.appendChild(info);
        card.appendChild(discount);
        cardsEl.appendChild(card);
    }
    if (partners.length === 0) {
        const msg = document.createElement("div");
        msg.className = "empty-message";
        msg.textContent = "Партнеры не найдены";
        cardsEl.appendChild(msg);
    }
}

async function loadPartners() {
    statusEl.textContent = "Загрузка данных...";
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error("HTTP " + response.status);
        }
        const partners = await response.json();
        renderPartners(partners);
        statusEl.textContent = "Данные обновлены: " + partners.length + " партнер(ов)";
    } catch (error) {
        statusEl.textContent = "Ошибка загрузки: " + error.message;
    }
}

refreshBtn.addEventListener("click", loadPartners);

loadPartners();