function safeDiscount(partner) {
  if (partner.discount_percent === null || partner.discount_percent === undefined) {
    return 0;
  }
  return Number(partner.discount_percent) || 0;
}

function createPartnerCard(partner) {
  const typeName = partner.partner_type ?? "";
  const name = partner.name ?? "";
  const director = partner.director_name ?? "";
  const phone = partner.phone ?? "";
  const rating = partner.rating ?? 0;
  const discount = safeDiscount(partner);

  const article = document.createElement("article");
  article.className = "partner-card";

  const top = document.createElement("div");
  top.className = "partner-card__top";

  const title = document.createElement("h2");
  title.className = "partner-card__title";
  title.textContent = `${typeName} | ${name}`;

  const discountEl = document.createElement("p");
  discountEl.className = "partner-card__discount";
  discountEl.textContent = `${discount}%`;

  top.appendChild(title);
  top.appendChild(discountEl);

  const details = document.createElement("ul");
  details.className = "partner-card__details";

  const directorItem = document.createElement("li");
  directorItem.textContent = director;
  const phoneItem = document.createElement("li");
  phoneItem.textContent = phone;
  const ratingItem = document.createElement("li");
  ratingItem.textContent = `Рейтинг: ${rating}`;

  details.appendChild(directorItem);
  details.appendChild(phoneItem);
  details.appendChild(ratingItem);

  article.appendChild(top);
  article.appendChild(details);
  return article;
}

function showStatus(message, isError) {
  const status = document.getElementById("status");
  if (!status) {
    return;
  }
  status.hidden = !message;
  status.textContent = message;
  status.classList.toggle("status--error", Boolean(isError));
}

async function loadPartners() {
  const container = document.getElementById("partners");
  if (!container) {
    return;
  }
  showStatus("Загрузка партнеров...", false);
  try {
    const response = await fetch("/api/partners");
    const payload = await response.json();
    if (!response.ok) {
      const errorMessage = payload && payload.error ? payload.error : "Ошибка загрузки";
      showStatus(errorMessage, true);
      container.innerHTML = "";
      return;
    }
    const partners = Array.isArray(payload) ? payload : [];
    container.innerHTML = "";
    if (partners.length === 0) {
      showStatus("Партнеры не найдены", false);
      return;
    }
    showStatus("", false);
    for (const partner of partners) {
      container.appendChild(createPartnerCard(partner ?? {}));
    }
  } catch (error) {
    showStatus("Не удалось загрузить данные из API", true);
    container.innerHTML = "";
  }
}

document.addEventListener("DOMContentLoaded", loadPartners);
