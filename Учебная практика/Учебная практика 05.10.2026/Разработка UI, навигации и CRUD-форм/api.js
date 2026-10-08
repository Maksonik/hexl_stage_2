const CONNECTION_STEPS = [
    "Убедитесь, что сервер приложения запущен (python3 server.py).",
    "Проверьте подключение к сети.",
    "Повторите действие."
];

function appError(message, steps) {
    const error = new Error(message);
    error.steps = steps || [];
    return error;
}

// Любой сбой запроса превращается в ошибку с текстом и шагами исправления для окна сообщения.
async function apiRequest(url, options) {
    let response;
    try {
        response = await fetch(url, {cache: "no-store", ...options});
    } catch (error) {
        throw appError("Сервер приложения не отвечает.", CONNECTION_STEPS);
    }
    let data;
    try {
        data = await response.json();
    } catch (error) {
        throw appError("Сервер вернул ответ, который не удалось прочитать.", CONNECTION_STEPS);
    }
    if (!response.ok) {
        throw appError(data.error || "Не удалось выполнить запрос.", data.steps);
    }
    return data;
}

function showError(heading, error) {
    return showAppDialog("error", heading, error.message, null, error.steps);
}
