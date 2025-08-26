const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const sinon = require("sinon");
const { assert } = require("qunit");

const { window } = new JSDOM(`<!DOCTYPE html><body>
    <div id="prohibited-words-url" data-url="/fake-url/"></div>
    <ul id="prohibited-words-list"></ul>
    <table>
        <tbody id="articles-table-body"></tbody>
    </table>
    <input type="text" id="search-word">
</body>`, { url: "http://localhost" });

const $ = require("jquery")(window);

global.window = window;
global.document = window.document;
global.$ = $;

const {
    prohibitedWordsModule,
    getCookie
} = require("../prohibited_words_report.js");

QUnit.module("Prohibited Words Report Tests", hooks => {
    let xhr;
    let requests = [];
    let module;
    const csrftoken = "dummy_csrf_token";

    hooks.beforeEach(() => {
        xhr = sinon.useFakeXMLHttpRequest();
        requests = [];
        xhr.onCreate = req => requests.push(req);

        const REPORTS_URL = "/fake-url/";
        document.cookie = `csrftoken=${csrftoken}`;

        module = prohibitedWordsModule(REPORTS_URL, csrftoken);

        $("#prohibited-words-list").html("");
        $("#articles-table-body").html("");
        $("#search-word").val("");
    });

    hooks.afterEach(() => {
        xhr.restore();
    });

    // --- getCookie ---
    QUnit.test("getCookie() - отримання значення cookie", assert => {
        document.cookie = "test_cookie=test_value";
        assert.equal(getCookie("test_cookie"), "test_value");
        assert.equal(getCookie("nonexistent_cookie"), null);
    });

    // --- refreshWordsList Success/Error (direct) ---
    QUnit.test("onWordsListSuccess - список слів", assert => {
        const response = { prohibited_words: ["badword", "word2"] };
        module.onWordsListSuccess(response);
        assert.equal($("#prohibited-words-list .word-item").length, 2, "Слова додані");
    });

    QUnit.test("onWordsListSuccess - порожній список", assert => {
        module.onWordsListSuccess({ prohibited_words: [] });
        assert.ok($("#prohibited-words-list").text().includes("Список порожній"));
    });

    QUnit.test("onWordsListError", assert => {
        module.onWordsListError();
        assert.ok($("#prohibited-words-list").text().includes("Помилка завантаження"));
    });

    // --- refreshTable Success/Error (direct) ---
    QUnit.test("onTableSuccess - є дані", assert => {
        const response = { prohibited_words_data: [{ id: 1, title: "Article", words: "bad" }] };
        module.onTableSuccess(response);
        assert.equal($("#articles-table-body tr").length, 1, "Додано рядок таблиці");
    });

    QUnit.test("onTableSuccess - порожні дані", assert => {
        module.onTableSuccess({ prohibited_words_data: [] });
        assert.ok($("#articles-table-body").text().includes("Немає даних"));
    });

    QUnit.test("onTableError", assert => {
        module.onTableError();
        assert.ok($("#articles-table-body").text().includes("Помилка завантаження"));
    });

    // --- Delete Success/Error (direct) ---
    QUnit.test("onDeleteSuccess - успіх", assert => {
        const refreshWordsSpy = sinon.spy(module, "refreshWordsList");
        const refreshTableSpy = sinon.spy(module, "refreshTable");
        module.onDeleteSuccess({ status: "success" });
        assert.ok(refreshWordsSpy.calledOnce, "refreshWordsList викликано");
        assert.ok(refreshTableSpy.calledOnce, "refreshTable викликано");
        refreshWordsSpy.restore();
        refreshTableSpy.restore();
    });

    QUnit.test("onDeleteError", assert => {
        module.onDeleteError();
        assert.ok(true, "onDeleteError нічого не ламає");
    });

    // --- AddWord Success/Error (direct) ---
    QUnit.test("onAddWordSuccess", assert => {
        const refreshWordsSpy = sinon.spy(module, "refreshWordsList");
        const refreshTableSpy = sinon.spy(module, "refreshTable");
        $("#search-word").val("someword");

        module.onAddWordSuccess();

        assert.equal($("#search-word").val(), "", "Поле очищене");
        assert.ok(refreshWordsSpy.calledOnce, "refreshWordsList викликано");
        assert.ok(refreshTableSpy.calledOnce, "refreshTable викликано");

        refreshWordsSpy.restore();
        refreshTableSpy.restore();
    });

    QUnit.test("onAddWordError", assert => {
        module.onAddWordError();
        assert.ok(true, "onAddWordError нічого не ламає");
    });

    // --- Оригінальні AJAX-повні функції ---
    QUnit.test("refreshWordsList - Ajax call", assert => {
        const done = assert.async();
        module.refreshWordsList();
        assert.equal(requests.length, 1, "AJAX GET відправлено");

        requests[0].respond(200, { "Content-Type": "application/json" }, JSON.stringify({
            prohibited_words: ["badword"]
        }));

        setTimeout(() => {
            assert.equal($("#prohibited-words-list .word-item").length, 1);
            done();
        }, 0);
    });

    QUnit.test("refreshTable - Ajax call", assert => {
        const done = assert.async();
        module.refreshTable();
        assert.equal(requests.length, 1, "AJAX GET відправлено");

        requests[0].respond(200, { "Content-Type": "application/json" }, JSON.stringify({
            prohibited_words_data: [{ id: 1, title: "Article", words: "bad" }]
        }));

        setTimeout(() => {
            assert.equal($("#articles-table-body tr").length, 1);
            done();
        }, 0);
    });

    QUnit.test("addWord - Ajax POST", assert => {
        const done = assert.async();
        const refreshSpy = sinon.spy(module, "refreshWordsList");

        module.addWord("newword");

        requests[0].respond(200, { "Content-Type": "application/json" }, JSON.stringify({ status: "success" }));

        setTimeout(() => {
            assert.ok(refreshSpy.called, "refreshWordsList викликано");
            refreshSpy.restore();
            done();
        }, 0);
    });

    QUnit.test("attachDeleteEvent - Ajax DELETE", assert => {
        const done = assert.async();

        $("#prohibited-words-list").html(`
            <li class="word-item">
                <button class="delete-word-button" data-word="word1" data-url="/fake-url/"></button>
            </li>
        `);

        const refreshSpy = sinon.spy(module, "refreshWordsList");

        module.attachDeleteEvent();
        $(".delete-word-button").trigger("click");

        requests[0].respond(200, { "Content-Type": "application/json" }, JSON.stringify({ status: "success" }));

        setTimeout(() => {
            assert.ok(refreshSpy.called, "refreshWordsList викликано");
            refreshSpy.restore();
            done();
        }, 0);
    });

    QUnit.test("attachDeleteEvent - не викликає Ajax, якщо wordToDelete пустий", assert => {
        const done = assert.async();

        // Додаємо кнопку без data-word
        $("#prohibited-words-list").html(`
            <li class="word-item">
                <button class="delete-word-button" data-url="/fake-url/"></button>
            </li>
        `);

        module.attachDeleteEvent();

        $(".delete-word-button").trigger("click");

        setTimeout(() => {
            // AJAX виклик не повинен бути зроблений
            assert.equal(requests.length, 0, "AJAX НЕ викликаний без слова");
            done();
        }, 0);
    });

    QUnit.test("handleDeleteButtonClick - не викликає Ajax, якщо wordToDelete немає", assert => {
        const done = assert.async();

        // Створюємо кнопку без data-word
        const button = $('<button class="delete-word-button" data-url="/fake-url/"></button>');

        // Spy на $.ajax
        const ajaxSpy = sinon.spy($, "ajax");

        module.handleDeleteButtonClick.call(button[0]); // Викликаємо в контексті кнопки

        setTimeout(() => {
            assert.ok(ajaxSpy.notCalled, "AJAX не викликано при пустому wordToDelete");
            ajaxSpy.restore();
            done();
        }, 0);
    });

    QUnit.test("handleDeleteButtonClick - викликає Ajax, якщо wordToDelete є", assert => {
        const done = assert.async();

        const button = $('<button class="delete-word-button" data-word="testword" data-url="/fake-url/"></button>');

        const ajaxSpy = sinon.spy($, "ajax");

        module.handleDeleteButtonClick.call(button[0]);

        setTimeout(() => {
            assert.ok(ajaxSpy.calledOnce, "AJAX викликано");
            ajaxSpy.restore();
            done();
        }, 0);
    });
});