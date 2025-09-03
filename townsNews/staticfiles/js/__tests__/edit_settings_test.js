const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const sinon = require("sinon");

// Налаштовуємо jsdom
const { window } = new JSDOM(`<!DOCTYPE html><body>
    <div id="qunit-fixture"></div>
</body>`, { url: "http://localhost" });

const $ = require("jquery")(window);

global.window = window;
global.document = window.document;
global.$ = $;

const { initSettingsForm, handleSliderInput, sliderInputEventHandler, registerDOMContentLoaded } = require("../edit_settings.js");

QUnit.module("Settings Form Tests", hooks => {

    hooks.beforeEach(() => {
        $('#qunit-fixture').empty();
    });

    QUnit.test("Початкове значення слайдера коректно відображається", assert => {
        $('#qunit-fixture').html(`
            <label>Font Size: <span id="font-size-display"></span></label>
            <input type="range" id="id_font_size" min="10" max="50" value="20">
        `);

        const output = document.getElementById("font-size-display");

        initSettingsForm();

        assert.equal(output.textContent.trim(), "20 px", "Початкове значення коректно виведено");
    });

    QUnit.test("Значення змінюється при input події", assert => {
        $('#qunit-fixture').html(`
            <label>Font Size: <span id="font-size-display"></span></label>
            <input type="range" id="id_font_size" min="10" max="50" value="16">
        `);

        const slider = document.getElementById("id_font_size");
        const output = document.getElementById("font-size-display");

        initSettingsForm();

        slider.value = 30;
        slider.dispatchEvent(new window.Event("input"));

        assert.equal(output.textContent.trim(), "30 px", "Значення коректно оновлюється після input");
    });

    QUnit.test("handleSliderInput працює напряму", assert => {
        const slider = { value: 42 };
        const output = { innerHTML: "" };

        handleSliderInput(slider, output);

        assert.equal(output.innerHTML, "42 px", "handleSliderInput напряму працює");
    });

    QUnit.test("sliderInputEventHandler напряму працює", assert => {
        const slider = { value: 55 };
        const output = { innerHTML: "" };

        const handler = sliderInputEventHandler(slider, output);
        handler();

        assert.equal(output.innerHTML, "55 px", "Event handler напряму працює");
    });

    QUnit.test("initSettingsForm напряму виконує всі дії", assert => {
        const slider = document.createElement("input");
        slider.type = "range";
        slider.value = 35;

        const output = document.createElement("span");

        const addEventListenerSpy = sinon.spy(slider, "addEventListener");

        initSettingsForm(slider, output);

        // Перевірка що handleSliderInput відпрацював
        assert.equal(output.innerHTML, "35 px", "handleSliderInput оновив текст");

        // Перевірка, що додали event listener
        assert.ok(addEventListenerSpy.calledOnceWith("input"), "Event listener додано");

        addEventListenerSpy.restore();
    });

    QUnit.test("Відсутність елементів не ламає функцію", assert => {
        $('#qunit-fixture').empty();

        initSettingsForm();

        assert.ok(true, "Функція безпечно завершується без елементів");
    });

    // 🔥 Новий важливий тест, що покриває рядки 17-18
    QUnit.test("initSettingsForm виконує handleSliderInput і додає event listener", assert => {
        $('#qunit-fixture').html(`
            <label>Font Size: <span id="font-size-display"></span></label>
            <input type="range" id="id_font_size" min="10" max="50" value="22">
        `);

        const slider = document.getElementById("id_font_size");
        const output = document.getElementById("font-size-display");

        const addEventListenerSpy = sinon.spy(slider, "addEventListener");

        initSettingsForm();

        // Перевіряємо, що текст змінився — handleSliderInput виконався
        assert.equal(output.textContent.trim(), "22 px", "handleSliderInput оновлює текст");

        // Перевіряємо, що додано event listener
        assert.ok(addEventListenerSpy.calledOnceWith("input"), "Event listener додано");

        addEventListenerSpy.restore();
    });

    QUnit.test("Відсутні обидва елементи — функція завершується", assert => {
        $('#qunit-fixture').empty();

        initSettingsForm();

        assert.ok(true, "Функція безпечно завершується без обох елементів");
    });

    QUnit.test("Відсутній тільки slider — функція завершується", assert => {
        $('#qunit-fixture').html(`
            <label>Font Size: <span id="font-size-display"></span></label>
        `); // Тільки output

        initSettingsForm();

        assert.ok(true, "Функція без слайдера завершується без помилки");
    });

    QUnit.test("Відсутній тільки output — функція завершується", assert => {
        $('#qunit-fixture').html(`
            <input type="range" id="id_font_size" min="10" max="50" value="16">
        `); // Тільки slider

        initSettingsForm();

        assert.ok(true, "Функція без output завершується без помилки");
    });

    QUnit.test("Слайдер отримує event listener", assert => {
        $('#qunit-fixture').html(`
            <label>Font Size: <span id="font-size-display"></span></label>
            <input type="range" id="id_font_size" min="10" max="50" value="25">
        `);

        const slider = document.getElementById("id_font_size");
        const addEventListenerSpy = sinon.spy(slider, "addEventListener");

        initSettingsForm();

        assert.ok(addEventListenerSpy.calledWith("input"), "Event listener додано");

        addEventListenerSpy.restore();
    });

    QUnit.test("DOMContentLoaded викликає initSettingsForm через spy", assert => {
        const spy = sinon.spy();
        const original = document.addEventListener;

        sinon.stub(document, 'addEventListener').callsFake((event, callback) => {
            if (event === 'DOMContentLoaded') {
                spy();
            }
            return original.call(document, event, callback);
        });

        // Імпортуємо файл заново, щоб перевірити під час імпорту
        delete require.cache[require.resolve("../edit_settings.js")];
        require("../edit_settings.js");

        assert.ok(spy.called, "initSettingsForm зареєстровано на DOMContentLoaded");

        document.addEventListener.restore();
    });

    QUnit.test("registerDOMContentLoaded додає listener", assert => {
        const addEventListenerSpy = sinon.spy(document, "addEventListener");

        registerDOMContentLoaded();

        assert.ok(addEventListenerSpy.calledWith('DOMContentLoaded'), "DOMContentLoaded listener додано");

        addEventListenerSpy.restore();
    });
});