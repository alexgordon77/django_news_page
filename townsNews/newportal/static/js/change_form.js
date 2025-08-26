function handleDropdownChange(selectedUrl = null) {
    selectedUrl = selectedUrl !== null ? selectedUrl : $('#report-dropdown').val();

    if (selectedUrl) {
        $.ajax({
            url: selectedUrl,
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: handleAjaxSuccess,
            error: handleAjaxError
        });
    } else {
        $('#report-content').html('<h3 class="text-center text-muted">Результати звіту з’являться тут</h3>');
    }
}

function handleAjaxSuccess(response) {
    console.log("Отримана відповідь:", response);
    $('#report-content').html(response.html || '<p>Звіт не повернув дані.</p>');
}

function handleAjaxError() {
    $('#report-content').html('<p class="text-danger">Не вдалося завантажити звіт. Спробуйте пізніше.</p>');
}

function initReportDropdown() {
    $('#report-dropdown').change(() => handleDropdownChange());
}

// Для продакшена:
$(document).ready(function () {
    initReportDropdown();
});

// Для тестів:
if (typeof module !== 'undefined') {
    module.exports = {
        initReportDropdown,
        handleDropdownChange,
        handleAjaxSuccess,
        handleAjaxError
    };
}