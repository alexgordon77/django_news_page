const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const sinon = require("sinon");

// Створюємо DOM
const { window } = new JSDOM(`<!DOCTYPE html><body>
    <div id="qunit-fixture"></div>
</body>`, { url: "http://localhost" });
const $ = require("jquery")(window);

global.window = window;
global.document = window.document;
global.$ = $;
global.URLSearchParams = window.URLSearchParams;

// Мокаємо TagCanvas (бо в тестах його немає)
global.TagCanvas = {
    Start: sinon.stub()
};

// Імпорт функцій з article_list.js
const {
    initTagCanvas,
    resizeCanvas,
    initTagClickHandlers,
    initSearchToggle
} = require("../article_list.js");

QUnit.module("initTagCanvas Tests", hooks => {
    hooks.beforeEach(() => {
        // Створюємо елементи для тесту
        let canvas = document.createElement('canvas');
        canvas.id = 'testCanvas';
        let tags = document.createElement('div');
        tags.id = 'testTags';
        document.body.appendChild(canvas);
        document.body.appendChild(tags);

        // Мокаємо TagCanvas
        window.TagCanvas = {
            Start: sinon.spy()
        };
    });

    hooks.afterEach(() => {
        document.body.innerHTML = '';
        delete window.TagCanvas;
    });

    QUnit.test("should initialize TagCanvas when elements exist", assert => {
        initTagCanvas('testCanvas', 'testTags');
        assert.ok(window.TagCanvas.Start.calledOnce, "TagCanvas.Start called");
    });

    QUnit.test("should not initialize TagCanvas when elements missing", assert => {
        document.getElementById('testCanvas').remove();
        initTagCanvas('testCanvas', 'testTags');
        assert.ok(window.TagCanvas.Start.notCalled, "TagCanvas.Start not called when canvas missing");
    });

    QUnit.test("should catch exception thrown by TagCanvas", assert => {
        window.TagCanvas.Start = function() { throw new Error("Test Error"); };
        let consoleError = sinon.spy(console, 'error');

        initTagCanvas('testCanvas', 'testTags');

        assert.ok(consoleError.calledOnce, "console.error called on exception");

        console.error.restore();
    });
});

QUnit.module("resizeCanvas Tests", hooks => {
    hooks.beforeEach(() => {
        let container = document.createElement('div');
        container.style.width = '500px';
        container.style.height = '400px';

        let canvas = document.createElement('canvas');
        container.appendChild(canvas);
        document.body.appendChild(container);
    });

    hooks.afterEach(() => {
        document.body.innerHTML = '';
    });

    QUnit.test("should resize all canvas elements", assert => {
        resizeCanvas();
        let canvas = document.querySelector('canvas');
        assert.equal(canvas.width, canvas.parentElement.clientWidth, "Canvas width resized");
        assert.equal(canvas.height, canvas.parentElement.clientHeight, "Canvas height resized");
    });
});

QUnit.module("initTagClickHandlers Tests", hooks => {
    hooks.beforeEach(() => {
        let tag1 = document.createElement('div');
        tag1.className = 'tag-item';
        tag1.dataset.tag = 'news';

        let tag2 = document.createElement('div');
        tag2.className = 'tag-item';
        tag2.dataset.author = 'author1';

        document.body.appendChild(tag1);
        document.body.appendChild(tag2);

        window.history.pushState({}, '', '?');
    });

    hooks.afterEach(() => {
        document.body.innerHTML = '';
    });

    QUnit.test("should add active class and update URL search for tag", assert => {
        initTagClickHandlers();
        let tag = document.querySelector('.tag-item[data-tag]');

        tag.click();

        assert.ok(tag.classList.contains('active'), "Tag has active class");
        assert.ok(window.location.search.includes('tag=news'), "URL updated with tag");
    });

    QUnit.test("should add active class and update URL search for author", assert => {
        initTagClickHandlers();
        let author = document.querySelector('.tag-item[data-author]');

        author.click();

        assert.ok(author.classList.contains('active'), "Author has active class");
        assert.ok(window.location.search.includes('author=author1'), "URL updated with author");
    });
});

QUnit.module("initSearchToggle Tests", hooks => {
    hooks.beforeEach(() => {
        let btn = document.createElement('button');
        btn.id = 'toggle-search-btn';
        let section = document.createElement('div');
        section.id = 'search-section';
        section.style.display = 'none';

        document.body.appendChild(btn);
        document.body.appendChild(section);
    });

    hooks.afterEach(() => {
        document.body.innerHTML = '';
    });

    QUnit.test("should toggle search section visibility", assert => {
        initSearchToggle();
        let btn = document.getElementById('toggle-search-btn');
        let section = document.getElementById('search-section');

        btn.click();
        assert.equal(section.style.display, 'block', "Section is visible after first click");

        btn.click();
        assert.equal(section.style.display, 'none', "Section hidden after second click");
    });
});

QUnit.module("mainInit Tests", hooks => {
    hooks.beforeEach(() => {
        // Мокаємо залежності
        sinon.stub(window, 'addEventListener');
        sinon.stub(window, 'resizeCanvas');

        // Створюємо елементи
        ['authorCanvas', 'tagCanvas', 'authorTags', 'tagTags'].forEach(id => {
            let el = document.createElement('div');
            el.id = id;
            document.body.appendChild(el);
        });
    });

    hooks.afterEach(() => {
        window.addEventListener.restore();
        window.resizeCanvas.restore();
        document.body.innerHTML = '';
    });

    QUnit.test("should initialize all components", assert => {
        // Мокаємо внутрішні функції
        sinon.spy(window, 'initTagCanvas');
        sinon.spy(window, 'initTagClickHandlers');
        sinon.spy(window, 'initSearchToggle');

        mainInit();

        assert.ok(window.initTagCanvas.calledTwice, "initTagCanvas called twice");
        assert.ok(window.initTagClickHandlers.calledOnce, "initTagClickHandlers called");
        assert.ok(window.initSearchToggle.calledOnce, "initSearchToggle called");
    });
});