const form = document.getElementById("calculator-form");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const calculateBtn = document.getElementById("calculate-btn");

function fillSelect(name, rows, idField) {
    const select = form.elements[name];
    select.replaceChildren();
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = name === "material_type_id" ? "Выберите материал" : "Выберите тип продукции";
    select.appendChild(placeholder);
    for (const row of rows) {
        const option = document.createElement("option");
        option.value = row[idField];
        option.textContent = row.type_name;
        select.appendChild(option);
    }
}

async function loadCatalogs() {
    try {
        const response = await fetch("/api/catalogs");
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Не удалось загрузить справочники.");
        }
        fillSelect("product_type_id", data.product_types, "product_type_id");
        fillSelect("material_type_id", data.material_types, "material_type_id");
        calculateBtn.disabled = false;
        statusEl.textContent = "Выберите типы и укажите размеры и количество изделий.";
    } catch (error) {
        statusEl.textContent = "Не удалось загрузить справочники.";
        await showAppDialog("error", "Ошибка загрузки", error.message);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    resultEl.textContent = "";
    const data = {
        product_type_id: Number(form.elements.product_type_id.value),
        material_type_id: Number(form.elements.material_type_id.value),
        quantity: Number(form.elements.quantity.value),
        param_1: Number(form.elements.param_1.value),
        param_2: Number(form.elements.param_2.value)
    };
    if (!Number.isInteger(data.quantity) || data.quantity <= 0) {
        statusEl.textContent = "Количество изделий должно быть целым числом больше нуля.";
        return;
    }
    if (!Number.isFinite(data.param_1) || !Number.isFinite(data.param_2) || data.param_1 <= 0 || data.param_2 <= 0) {
        statusEl.textContent = "Длина и ширина изделия должны быть положительными числами.";
        return;
    }
    if (!data.product_type_id || !data.material_type_id) {
        statusEl.textContent = "Выберите тип продукции и материал.";
        return;
    }

    calculateBtn.disabled = true;
    statusEl.textContent = "Расчёт…";
    try {
        const response = await fetch("/api/materials/calculate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
        const answer = await response.json();
        if (!response.ok) {
            throw new Error(answer.error || "Не удалось выполнить расчёт.");
        }
        if (answer.result === -1) {
            statusEl.textContent = "Расчёт невозможен: проверьте выбранные типы и введённые значения.";
        } else {
            statusEl.textContent = "Расчёт завершён.";
            resultEl.textContent = "Необходимое количество материала: " + answer.result + " ед.";
        }
    } catch (error) {
        statusEl.textContent = "Не удалось выполнить расчёт.";
        await showAppDialog("error", "Ошибка расчёта", error.message);
    } finally {
        calculateBtn.disabled = false;
    }
});

loadCatalogs();
