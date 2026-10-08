const pageTitle = document.getElementById("page-title");
const statusEl = document.getElementById("status");
const tableWrap = document.getElementById("table-wrap");
const salesBody = document.getElementById("sales-body");
const partnerId = encodeURIComponent(window.location.pathname.split("/")[2]);

document.getElementById("edit-link").href = "/partner/" + partnerId + "?from=history";

async function loadHistory() {
    try {
        const data = await apiRequest("/api/partners/" + partnerId + "/sales");

        pageTitle.textContent = "CRM: История продаж — " + data.partner;
        document.title = pageTitle.textContent;
        salesBody.replaceChildren();
        for (const sale of data.sales) {
            const row = document.createElement("tr");
            const values = [
                sale.product_name,
                sale.sale_date.split("-").reverse().join("."),
                Number(sale.quantity).toLocaleString("ru-RU")
            ];
            for (const value of values) {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            }
            salesBody.appendChild(row);
        }
        tableWrap.hidden = data.sales.length === 0;
        statusEl.textContent = data.sales.length === 0 ? "У партнёра пока нет продаж." : "Записей: " + data.sales.length;
    } catch (error) {
        statusEl.textContent = "Не удалось загрузить историю продаж.";
        await showError("Ошибка загрузки", error);
    }
}

loadHistory();
