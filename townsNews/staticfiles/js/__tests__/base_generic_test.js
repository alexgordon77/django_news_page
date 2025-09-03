const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const sinon = require("sinon");

// Налаштування jsdom
const { window } = new JSDOM(`<!DOCTYPE html><body>
    <div id="sidebar">Sidebar</div>
    <button id="menuBtn">Меню ▼</button>
</body>`, { url: "http://localhost" });

const $ = require("jquery")(window);

global.window = window;
global.document = window.document;
global.$ = $;

const {
    initSidebar,
    handleMenuMouseEnter,
    handleMouseLeave,
    handleSidebarMouseEnter,
    shouldHideSidebar
} = require('../base_generic.js');

QUnit.module("base_generic.js", hooks => {
    let stopStub, slideDownStub, slideUpStub, clearSpy, setTimeoutSpy, clock;
    let menuTimeoutRef;
    let sidebar, menuBtn;

    hooks.beforeEach(() => {
        sidebar = $('<div id="sidebar"></div>');
        menuBtn = $('<button id="menuBtn"></button>');

        stopStub = sinon.stub(sidebar, 'stop').returns(sidebar);
        slideDownStub = sinon.stub(sidebar, 'slideDown').returns(sidebar);
        slideUpStub = sinon.stub(sidebar, 'slideUp').returns(sidebar);

        setTimeoutSpy = sinon.spy(window, 'setTimeout');
        clearSpy = sinon.spy(window, 'clearTimeout');
        clock = sinon.useFakeTimers();

        menuTimeoutRef = { menuTimeout: null };
    });

    hooks.afterEach(() => {
        stopStub.restore();
        slideDownStub.restore();
        slideUpStub.restore();
        setTimeoutSpy.restore();
        clearSpy.restore();
        clock.restore();
    });

    QUnit.test("Sidebar hides on load via initSidebar", assert => {
        const hideStub = sinon.stub(sidebar, 'hide').returns(sidebar);
        const mouseEnterSpy = sinon.spy(sidebar, 'mouseenter');
        const mouseLeaveSpy = sinon.spy(sidebar, 'mouseleave');

        initSidebar(menuBtn, sidebar);

        assert.ok(hideStub.calledOnce, "Sidebar hide() called");
        assert.ok(mouseEnterSpy.calledOnce, "mouseenter handler set");
        assert.ok(mouseLeaveSpy.calledOnce, "mouseleave handler set");

        hideStub.restore();
        mouseEnterSpy.restore();
        mouseLeaveSpy.restore();
    });

    QUnit.test("handleMenuMouseEnter triggers stop and slideDown", assert => {
        handleMenuMouseEnter(sidebar);
        assert.ok(stopStub.calledOnce, "stop called");
        assert.ok(slideDownStub.calledOnce, "slideDown called");
    });

    QUnit.test("shouldHideSidebar returns true when both not hovered", assert => {
        const menuBtnHover = sinon.stub(menuBtn, 'is').withArgs(":hover").returns(false);
        const sidebarHover = sinon.stub(sidebar, 'is').withArgs(":hover").returns(false);

        const result = shouldHideSidebar(menuBtn, sidebar);
        assert.ok(result, "Sidebar should hide");

        menuBtnHover.restore();
        sidebarHover.restore();
    });

    QUnit.test("shouldHideSidebar returns false when menuBtn hovered", assert => {
        const menuBtnHover = sinon.stub(menuBtn, 'is').withArgs(":hover").returns(true);
        const sidebarHover = sinon.stub(sidebar, 'is').withArgs(":hover").returns(false);

        const result = shouldHideSidebar(menuBtn, sidebar);
        assert.notOk(result, "Sidebar should stay");

        menuBtnHover.restore();
        sidebarHover.restore();
    });

    QUnit.test("shouldHideSidebar returns false when sidebar hovered", assert => {
        const menuBtnHover = sinon.stub(menuBtn, 'is').withArgs(":hover").returns(false);
        const sidebarHover = sinon.stub(sidebar, 'is').withArgs(":hover").returns(true);

        const result = shouldHideSidebar(menuBtn, sidebar);
        assert.notOk(result, "Sidebar should stay");

        menuBtnHover.restore();
        sidebarHover.restore();
    });

    QUnit.test("handleMouseLeave hides sidebar if needed", assert => {
        const menuBtnHover = sinon.stub(menuBtn, 'is').withArgs(":hover").returns(false);
        const sidebarHover = sinon.stub(sidebar, 'is').withArgs(":hover").returns(false);

        handleMouseLeave(menuTimeoutRef, menuBtn, sidebar);
        clock.tick(301);

        assert.ok(slideUpStub.calledOnce, "slideUp called");

        menuBtnHover.restore();
        sidebarHover.restore();
    });

    QUnit.test("handleMouseLeave does NOT hide sidebar when hovered", assert => {
        const menuBtnHover = sinon.stub(menuBtn, 'is').withArgs(":hover").returns(true);
        const sidebarHover = sinon.stub(sidebar, 'is').withArgs(":hover").returns(true);

        handleMouseLeave(menuTimeoutRef, menuBtn, sidebar);
        clock.tick(301);

        assert.notOk(slideUpStub.called, "slideUp NOT called");

        menuBtnHover.restore();
        sidebarHover.restore();
    });

    QUnit.test("handleSidebarMouseEnter clears timeout", assert => {
        menuTimeoutRef.menuTimeout = setTimeout(() => {}, 300);
        handleSidebarMouseEnter(menuTimeoutRef);
        assert.ok(clearSpy.calledOnce, "clearTimeout called");
    });

    QUnit.test("initSidebar event handlers are triggered and execute logic", assert => {
        const hideStub = sinon.stub(sidebar, 'hide').returns(sidebar);

        const menuBtnHover = sinon.stub(menuBtn, 'is').withArgs(":hover").returns(false);
        const sidebarHover = sinon.stub(sidebar, 'is').withArgs(":hover").returns(false);

        initSidebar(menuBtn, sidebar);

        // Симуляція подій
        menuBtn.trigger('mouseenter');  // має викликати handleMenuMouseEnter
        menuBtn.trigger('mouseleave');  // має викликати handleMouseLeave
        sidebar.trigger('mouseleave');  // має викликати handleMouseLeave
        sidebar.trigger('mouseenter');  // має викликати handleSidebarMouseEnter

        // Перевірка викликів
        assert.ok(stopStub.calledOnce, "sidebar stop called on mouseenter");
        assert.ok(slideDownStub.calledOnce, "sidebar slideDown called on mouseenter");

        clock.tick(301);
        assert.ok(slideUpStub.calledTwice, "sidebar slideUp called twice on mouseleave");

        assert.ok(clearSpy.calledOnce, "clearTimeout called on sidebar mouseenter");

        hideStub.restore();
        menuBtnHover.restore();
        sidebarHover.restore();
    });

});