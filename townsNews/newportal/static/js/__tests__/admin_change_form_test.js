const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const sinon = require("sinon");

const { window } = new JSDOM(`<!DOCTYPE html><body>
    <select id="report-dropdown">
        <option value="">Select Report</option>
        <option value="/report/1">Report 1</option>
    </select>
    <div id="report-content"></div>
</body>`, { url: "http://localhost" });

const $ = require("jquery")(window);

global.window = window;
global.document = window.document;
global.$ = $;
global.XMLHttpRequest = window.XMLHttpRequest;
global.console = window.console;

const {
    initReportDropdown,
    handleDropdownChange,
    handleAjaxSuccess,
    handleAjaxError
} = require("../change_form.js");

QUnit.module("initReportDropdown Tests", hooks => {
    let ajaxStub;
    let consoleLogStub;

    hooks.beforeEach(() => {
        $('#report-dropdown').off();
        $('#report-content').empty();
        ajaxStub = sinon.stub($, "ajax");
        consoleLogStub = sinon.stub(console, "log");
        initReportDropdown();
    });

    hooks.afterEach(() => {
        ajaxStub.restore();
        consoleLogStub.restore();
        $('#report-content').empty();
        $('#report-dropdown').val('');
    });

    QUnit.test("Default message shown when dropdown is empty", assert => {
        $('#report-dropdown').val('');
        handleDropdownChange();

        assert.strictEqual(
            $('#report-content').html().trim(),
            '<h3 class="text-center text-muted">Результати звіту з’являться тут</h3>',
            "Показано дефолтне повідомлення"
        );

        assert.notOk(ajaxStub.called, "AJAX не викликається");
    });

    QUnit.test("AJAX called when dropdown has value", assert => {
        $('#report-dropdown').val('/report/1');
        handleDropdownChange();

        assert.ok(ajaxStub.calledOnce, "AJAX викликано");
    });

    QUnit.test("handleAjaxSuccess inserts response HTML", assert => {
        handleAjaxSuccess({ html: '<p>Дані</p>' });

        assert.ok(consoleLogStub.calledOnce, "console.log called");
        assert.strictEqual($('#report-content').html().trim(), '<p>Дані</p>', "Контент вставлено");
    });

    QUnit.test("handleAjaxSuccess handles empty response", assert => {
        handleAjaxSuccess({});

        assert.strictEqual(
            $('#report-content').html().trim(),
            '<p>Звіт не повернув дані.</p>',
            "Показано повідомлення про відсутність даних"
        );
    });

    QUnit.test("handleAjaxError shows error message", assert => {
        handleAjaxError();

        assert.strictEqual(
            $('#report-content').html().trim(),
            '<p class="text-danger">Не вдалося завантажити звіт. Спробуйте пізніше.</p>',
            "Показано повідомлення про помилку"
        );
    });

    QUnit.test("handleDropdownChange напряму викликає ajax, якщо є URL", assert => {
        ajaxStub.restore(); // Щоб точно бачити виклик
        const ajaxSpy = sinon.spy($, "ajax");

        handleDropdownChange("/report/1");

        assert.ok(ajaxSpy.calledOnce, "AJAX викликано з переданим URL");
        assert.equal(ajaxSpy.firstCall.args[0].url, "/report/1", "URL передано коректно");

        ajaxSpy.restore();
    });

    QUnit.test("handleDropdownChange напряму показує дефолтне повідомлення, якщо URL пустий", assert => {
        $('#report-content').empty();

        handleDropdownChange('');

        assert.strictEqual(
            $('#report-content').html().trim(),
            '<h3 class="text-center text-muted">Результати звіту з’являться тут</h3>',
            "Показано дефолтне повідомлення при пустому URL"
        );
    });
});