function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.split('=')[1]);
            }
        });
    }
    return cookieValue;
}

function prohibitedWordsModule(REPORTS_URL, csrftoken) {

    function onWordsListSuccess(response) {
        if (response.prohibited_words && response.prohibited_words.length > 0) {
            const newWordsList = response.prohibited_words.map(word => `
                <li class="word-item">
                    <span class="word-text">${word}</span>
                    <button class="delete-word-button" data-word="${word}" data-url="${REPORTS_URL}">
                        <i class="fa fa-x"></i>
                    </button>
                </li>`).join("");
            $('#prohibited-words-list').html(newWordsList);
            attachDeleteEvent();
        } else {
            $('#prohibited-words-list').html("<li>Список порожній</li>");
        }
    }

    function onWordsListError() {
        $('#prohibited-words-list').html("<li>Помилка завантаження</li>");
    }

    function onTableSuccess(response) {
        if (response.prohibited_words_data && response.prohibited_words_data.length > 0) {
            const newTableContent = response.prohibited_words_data.map(data => `
                <tr>
                    <td><a class="article-link" href="/admin/newportal/article/${data.id}/change/">${data.title}</a></td>
                    <td>${data.words}</td>
                </tr>`).join("");
            $('#articles-table-body').html(newTableContent);
        } else {
            $('#articles-table-body').html('<tr><td colspan="2" class="text-center">Немає даних</td></tr>');
        }
    }

    function onTableError() {
        $('#articles-table-body').html('<tr><td colspan="2" class="text-center">Помилка завантаження</td></tr>');
    }

    function onDeleteSuccess(response) {
        if (response.status === "success") {
            refreshWordsList();
            refreshTable();
        }
    }

    function onDeleteError() {
        // nothing for test
    }

    function refreshWordsList() {
        $.ajax({
            url: REPORTS_URL,
            type: "GET",
            dataType: "json",
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: onWordsListSuccess,
            error: onWordsListError
        });
    }

    function refreshTable() {
        $.ajax({
            url: REPORTS_URL,
            type: "GET",
            dataType: "json",
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: onTableSuccess,
            error: onTableError
        });
    }

    // 🔽 Винесли окремо обробник
    function handleDeleteButtonClick() {
        const wordToDelete = $(this).data("word");
        const url = $(this).data("url");

        if (!wordToDelete) return;

        $.ajax({
            url: url,
            type: "DELETE",
            data: JSON.stringify({ word: wordToDelete }),
            contentType: "application/json",
            headers: { "X-CSRFToken": csrftoken },
            success: onDeleteSuccess,
            error: onDeleteError
        });
    }

    function attachDeleteEvent() {
        $(".delete-word-button").off("click").on("click", handleDeleteButtonClick);
    }

    function onAddWordSuccess() {
        refreshWordsList();
        refreshTable();
        $("#search-word").val("");
    }

    function onAddWordError() {
        // nothing
    }

    function addWord(newWord) {
        if (newWord) {
            $.ajax({
                url: REPORTS_URL,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ new_word: newWord }),
                headers: { "X-CSRFToken": csrftoken },
                success: onAddWordSuccess,
                error: onAddWordError
            });
        }
    }

    return {
        refreshWordsList,
        refreshTable,
        attachDeleteEvent,
        addWord,
        onWordsListSuccess,
        onWordsListError,
        onTableSuccess,
        onTableError,
        onDeleteSuccess,
        onDeleteError,
        onAddWordSuccess,
        onAddWordError,
        handleDeleteButtonClick
    };
}

// Експорт
if (typeof module !== 'undefined') {
    module.exports = { prohibitedWordsModule, getCookie };
}