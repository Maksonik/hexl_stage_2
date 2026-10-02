const pageTitle = document.getElementById("page-title");
const statusEl = document.getElementById("status");
const tableWrap = document.getElementById("table-wrap");
const salesBody = document.getElementById("sales-body");
const partnerId = window.location.pathname.split("/")[2];

async function loadHistory() {
    try {
        const response = await fetch("/api/partners/" + encodeURIComponent(partnerId) + "/sales");
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Не удалось загрузить историю продаж.");
        }

        pageTitle.textContent = "CRM: История реализации продукции — " + data.partner;
        document.title = pageTitle.textContent;
        salesBody.replaceChildren();
        for (const sale of data.sales) {
            const row = document.createElement("tr");
            const values = [
                sale.product_name,
                Number(sale.quantity).toLocaleString("ru-RU"),
                sale.sale_date.split("-").reverse().join(".")
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
        await showAppDialog("error", "Ошибка загрузки", error.message);
    }
}

loadHistory();
