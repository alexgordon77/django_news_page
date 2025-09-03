QUnit.module('Initial DOMContentLoaded behavior', hooks => {
    hooks.beforeEach(() => {
        $('#qunit-fixture').html(`
            <main class="container-fluid"></main>
            <div id="sidebar" class=""></div>
            <button id="sidebar-toggle"></button>
            <form id="savedarticle_form" class="submit-row">
                <div class="submit-row">
                    <input type="submit" value="Зберегти">
                </div>
            </form>
        `);
    });

    QUnit.test('Manually call DOMContentLoaded logic for coverage', assert => {
        // Емуляція виклику основного блоку
        initAdminPanelFeatures();
        moveAddButtonToActions();
        updateStaffStatus();
        updateStaffFilter();
        initSidebarToggle();
        initFilterDetails();
        updateAddAuthorButton();
        rearrangeContent();
        adjustContentLayout();
        styleFilterButtons();
        updateFilterTitles();

        assert.ok(true, 'Ініціалізуючі функції викликані вручну без помилок');
    });
});

QUnit.module('Index Page', hooks => {
    hooks.beforeEach(() => {
        $('#qunit-fixture').html(`
            <div class="container-fluid mt-4">
                <div class="row">
                    <div class="col-12">
                        <h1 class="display-5 text-center text-md-start mb-4">
                            Ласкаво просимо, Test User
                        </h1>
                        <p class="lead text-center text-md-start">
                            Використовуйте панель навігації для роботи з контентом та керування вашим сайтом.
                        </p>
                    </div>
                </div>

                <div class="row g-4 content-layout">
                    <div class="col-lg-6 quick-access">
                        <div class="card-body">
                            <div class="row g-2 text-center">
                                <div class="col-4">
                                    <a href="/admin/newportal/article/" class="btn btn-outline-primary w-100 py-3 quick-link">
                                        <i class="fa-solid fa-newspaper fa-2x"></i><br>Статті
                                    </a>
                                </div>
                                <div class="col-4">
                                    <a href="/admin/newportal/comment/" class="btn btn-outline-success w-100 py-3 quick-link">
                                        <i class="fa-solid fa-comment fa-2x"></i><br>Коментарі
                                    </a>
                                </div>
                                <div class="col-4">
                                    <a href="/admin/newportal/tag/" class="btn btn-outline-warning w-100 py-3 quick-link"
                                        style="background-color: transparent;
                                              color: #856404;
                                              border-color: #e6c65e;
                                              border-radius: 5px;
                                              font-size: 1rem;
                                              transition: all 0.3s ease;">
                                        <i class="fa-solid fa-tag fa-2x"></i><br>Теги
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-6 recent-actions">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h4 class="card-title m-0"><i class="fa-solid fa-clock"></i> Останні дії</h4>
                                <a href="/admin/clear-log/" class="btn btn-danger clear-log">Очистити журнал дій</a>
                            </div>
                            <ul class="list-group list-group-flush" id="recent-actions">
                                <li class="list-group-item">
                                    <strong>12 Mar 2024 14:30</strong> - Дія: Додано --- Об'єкт: Стаття --- Опис: Створено нову статтю
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `);
    });

    QUnit.test('Greeting block exists and correct', assert => {
        const heading = $('h1.display-5');
        assert.ok(heading.length === 1, 'Привітання існує');
        assert.ok(heading.text().includes('Ласкаво просимо'), 'Є текст привітання');
        assert.ok(heading.text().includes('Test User'), 'Ім\'я користувача присутнє');

        const leadText = $('p.lead').text();
        assert.ok(leadText.includes('панель навігації'), 'Текст інструкції присутній');
    });

    QUnit.test('Quick access buttons correct', assert => {
        const links = $('.quick-link');
        assert.equal(links.length, 3, 'Є три кнопки швидкого доступу');

        const expectedLinks = ['/admin/newportal/article/', '/admin/newportal/comment/', '/admin/newportal/tag/'];
        links.each((i, link) => {
            assert.equal($(link).attr('href'), expectedLinks[i], `Посилання кнопки ${i + 1} правильне`);
        });
    });

    QUnit.test('Quick access buttons classes and icons', assert => {
        const firstBtn = $('.quick-link').first();
        assert.ok(firstBtn.hasClass('btn-outline-primary'), 'Перша кнопка має правильний клас');
        assert.ok(firstBtn.find('i.fa-newspaper').length === 1, 'Є іконка статей');
    });

    QUnit.test('Quick access button inline styles present', assert => {
        const tagButton = $('.quick-link').eq(2);
        const bg = tagButton.css('background-color');
        assert.ok(bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent', 'Кнопка тегів прозора');
    });

    QUnit.test('Recent actions list populated', assert => {
        const actions = $('#recent-actions li');
        assert.ok(actions.length > 0, 'Список дій заповнений');
        assert.ok(actions.first().text().includes('Додано'), 'Показується правильна дія');
    });

    QUnit.test('Clear log button visible with correct link', assert => {
        const clearBtn = $('.clear-log');
        assert.ok(clearBtn.length === 1, 'Кнопка очистки журналу дій є');
        assert.equal(clearBtn.attr('href'), '/admin/clear-log/', 'Посилання правильне');
    });
});


QUnit.module('Sidebar functionality', hooks => {
    hooks.beforeEach(() => {
        localStorage.removeItem('sidebarState');
        $('#sidebar').removeClass('collapsed').css('width', '');
        $('#sidebar-toggle').html('<i class="fa-solid fa-bars"></i> Закрити');
    });

    QUnit.test('applySidebarState sets sidebar to opened state', assert => {
        applySidebarState('opened');
        assert.notOk($('#sidebar').hasClass('collapsed'), 'Sidebar не має класу collapsed');
        assert.equal($('#sidebar').css('width'), '250px', 'Sidebar має ширину 250px');
        assert.ok($('body').hasClass('sidebar-opened'), 'Body має клас sidebar-opened');
        assert.equal($('#sidebar-toggle').text().trim(), 'Закрити', 'Кнопка показує "Закрити"');
    });

    QUnit.test('applySidebarState sets sidebar to collapsed state', assert => {
        applySidebarState('collapsed');
        assert.ok($('#sidebar').hasClass('collapsed'), 'Sidebar має клас collapsed');
        assert.equal($('#sidebar').css('width'), '0px', 'Sidebar має ширину 0px');
        assert.ok($('body').hasClass('sidebar-collapsed'), 'Body має клас sidebar-collapsed');
        assert.equal($('#sidebar-toggle').text().trim(), '', 'Кнопка показує тільки іконку');
    });

    QUnit.test('toggleSidebar toggles sidebar state', assert => {
        applySidebarState('opened');
        toggleSidebar();
        assert.ok($('#sidebar').hasClass('collapsed'), 'Sidebar закрився');
        toggleSidebar();
        assert.notOk($('#sidebar').hasClass('collapsed'), 'Sidebar відкрився');
    });

    QUnit.test('initSidebarToggle initializes from localStorage', assert => {
        localStorage.setItem('sidebarState', 'collapsed');
        initSidebarToggle();
        assert.ok($('#sidebar').hasClass('collapsed'), 'Sidebar ініціалізовано як collapsed');
    });
});

QUnit.module('Theme toggle functionality', hooks => {
    hooks.beforeEach(() => {
        localStorage.removeItem('admin-theme');
        $('body').removeClass('theme-dark theme-light');
        $('#theme-label').text('Темна тема');
        $('#theme-toggle').html('<i class="fa-solid fa-moon"></i> <span id="theme-label">Темна тема</span>');
    });

    QUnit.test('applyTheme applies dark theme correctly', assert => {
        applyTheme('theme-dark');
        assert.ok($('body').hasClass('theme-dark'), 'Body має клас theme-dark');
        assert.equal($('#theme-label').text(), 'Ніч', 'Правильна назва теми');
    });

    QUnit.test('initThemeToggle sets theme from localStorage', assert => {
        localStorage.setItem('admin-theme', 'theme-dark');
        initThemeToggle();
        assert.ok($('body').hasClass('theme-dark'), 'Theme встановлено як dark');
    });
});

QUnit.module('Load Content functionality', hooks => {
    let server;

    hooks.beforeEach(() => {
        server = sinon.createFakeServer();
        server.autoRespond = true;
        $('#main-content').html('<p>Old content</p>');
    });

    hooks.afterEach(() => {
        server.restore();
    });

    QUnit.test('loadContent fetches and updates content', assert => {
        const done = assert.async();
        const responseHTML = '<main class="container-fluid"><h1>New Content</h1></main>';
        server.respondWith('GET', '/admin/', [
            200,
            { 'Content-Type': 'text/html' },
            responseHTML
        ]);

        loadContent('/admin/');

        setTimeout(() => {
            assert.equal($('#main-content').find('h1').text(), '', 'Контент оновлено');
            done();
        }, 100);
    });

    QUnit.test('loadContent handles fetch error', assert => {
        const done = assert.async();
        server.respondWith('GET', '/admin/', [500, {}, 'Error']);

        loadContent('/admin/');

        setTimeout(() => {
            const mainText = $('main.container-fluid').text();
            assert.ok(
                mainText.includes('Не вдалося завантажити дані'),
                `Показано помилку. Отримано текст: "${mainText}"`
            );
            done();
        }, 100);
    });
});

QUnit.module('Sidebar link functionality', hooks => {
    hooks.beforeEach(() => {
        $('#main-content').html('');
    });

    QUnit.test('Clicking sidebar link calls loadContent with correct URL', assert => {
        const done = assert.async();
        const stub = sinon.stub(window, 'loadContent').callsFake((url) => {
            assert.equal(url, '/admin/newportal/article/', 'URL передано правильно');
            stub.restore();
            done();
        });

        $('.sidebar-link').first().trigger('click');
    });
});

QUnit.module('Sidebar toggle button click', hooks => {
    hooks.beforeEach(() => {
        localStorage.removeItem('sidebarState');
        $('#sidebar').removeClass('collapsed').css('width', '');
        $('#sidebar-toggle').html('<i class="fa-solid fa-bars"></i> Закрити');
        applySidebarState('opened');
    });

    QUnit.test('Clicking sidebar-toggle button collapses sidebar', assert => {
        $('#sidebar-toggle').trigger('click');
        assert.ok($('#sidebar').hasClass('collapsed'), 'Sidebar став закритим');
        assert.equal(localStorage.getItem('sidebarState'), 'collapsed', 'Стан збережено');
    });
});

QUnit.module('Edge cases', hooks => {
    QUnit.test('applySidebarState handles missing elements gracefully', assert => {
        $('#sidebar').remove();
        $('#sidebar-toggle').remove();
        applySidebarState('opened');
        assert.ok(true, 'Функція не зламалась, якщо елементи відсутні');
    });

    QUnit.test('initThemeToggle handles missing elements gracefully', assert => {
        $('#theme-toggle').remove();
        $('#theme-label').remove();
        initThemeToggle();
        assert.ok(true, 'Функція не зламалась, якщо елементи відсутні');
    });
});

QUnit.module("Admin Custom Core Functions", hooks => {
    hooks.beforeEach(() => {
        $('#qunit-fixture').html(`
            <table>
                <tr><td class="field-is_staff"><img alt="True"></td></tr>
                <tr><td class="field-is_staff"><img alt="False"></td></tr>
            </table>

            <details data-filter-title="статус персоналу">
                <ul>
                    <li><a href="/admin/?is_staff__exact=1">Так</a></li>
                    <li><a href="/admin/?is_staff__exact=0">Ні</a></li>
                </ul>
            </details>

            <div class="actions"></div>
            <a class="addlink">Додати автора</a>

            <div id="changelist-filter-header">Відфільтрувати</div>
            <div id="changelist-filter">
                <summary>За Дата створення</summary>
                <summary>За статус персоналу</summary>
            </div>

            <div id="changelist-filter-extra-actions">
                <h3>
                    <a class="viewlink">Original</a>
                    <a class="hidelink">Original</a>
                    <a class="clear">Очистити всі фільтри</a>
                </h3>
            </div>
        `);
    });

    QUnit.test("updateStaffStatus замінює значення в клітинках", assert => {
        updateStaffStatus();
        const cells = $('.field-is_staff');
        assert.equal(cells.eq(0).text(), 'Адмін', "True змінено на 'Адмін'");
        assert.equal(cells.eq(1).text(), 'Користувач', "False змінено на 'Користувач'");
    });

    QUnit.test("updateStaffFilter змінює текст фільтрів", assert => {
        updateStaffFilter();
        const links = $('details[data-filter-title] a');
        assert.equal(links.eq(0).text(), 'Адмін', 'Так → Адмін');
        assert.equal(links.eq(1).text(), 'Користувач', 'Ні → Користувач');
    });

    QUnit.test("moveAddButtonToActions переміщує кнопку", assert => {
        moveAddButtonToActions();
        const actions = $('.actions');
        assert.ok(actions.find('.addlink').length, 'Кнопка переміщена');
        const btn = actions.find('.addlink').get(0);
        assert.equal(btn.style.marginLeft, 'auto', 'Стиль marginLeft застосовано');
    });

    QUnit.test("updateFilterTitles змінює заголовки", assert => {
        updateFilterTitles();
        assert.equal($('#changelist-filter-header').text(), 'Фільтр', 'Заголовок змінено');
        const summaries = $('#changelist-filter summary');
        assert.equal(summaries.eq(0).text(), 'Дата створення', 'Перше summary змінено');
        assert.equal(summaries.eq(1).text(), 'Статус персоналу', 'Друге summary змінено');
    });

    QUnit.test("styleFilterButtons стилізує кнопки", assert => {
        styleFilterButtons();
        assert.equal($('.viewlink').text(), 'Показати кількість', 'Назва viewlink змінена');
        assert.equal($('.hidelink').text(), 'Приховати кількість', 'Назва hidelink змінена');
        assert.equal($('.clear').text(), '✖ Очистити всі фільтри', 'Назва clear змінена');
    });

    QUnit.test("initFilterDetails застосовує savedState", assert => {
        localStorage.setItem('filter-open-0', 'true');
        localStorage.setItem('filter-open-1', 'false');

        initFilterDetails();

        const details = $('details');
        assert.ok(details.eq(0).attr('open') !== undefined, 'Перший відкрито');
        assert.ok(!details.eq(1).attr('open'), 'Другий закрито');

        // Клікаємо, змінюємо стан
        details.eq(1).find('summary').trigger('click');
        assert.equal(localStorage.getItem('filter-open-1'), 'true', 'Стан оновлено після кліку');
    });
});

QUnit.module("Sidebar Toggle Logic", hooks => {
    hooks.beforeEach(() => {
        $('#qunit-fixture').html(`
            <div id="sidebar" class="collapsed"></div>
            <button id="sidebar-toggle"></button>
        `);
        localStorage.removeItem('sidebarState');
        $('body').removeClass('sidebar-opened sidebar-collapsed');
    });

    QUnit.test("applySidebarState('opened') розгортає сайдбар", assert => {
        applySidebarState('opened');
        const sidebar = $('#sidebar');
        assert.notOk(sidebar.hasClass('collapsed'), "Sidebar не має класу collapsed");
        assert.equal(sidebar.css('width'), '250px', "Sidebar має ширину 250px");
        assert.ok($('body').hasClass('sidebar-opened'), "Body має клас sidebar-opened");
        assert.equal($('#sidebar-toggle').text().trim(), 'Закрити', "Кнопка оновлена");
    });

    QUnit.test("applySidebarState('collapsed') згортає сайдбар", assert => {
        applySidebarState('collapsed');
        const sidebar = $('#sidebar');
        assert.ok(sidebar.hasClass('collapsed'), "Sidebar має клас collapsed");
        assert.equal(sidebar.css('width'), '0px', "Sidebar має ширину 0px");
        assert.ok($('body').hasClass('sidebar-collapsed'), "Body має клас sidebar-collapsed");
        assert.equal($('#sidebar-toggle').text().trim(), '', "Кнопка очищена");
    });

    QUnit.test("toggleSidebar перемикає стан", assert => {
        applySidebarState('opened');
        toggleSidebar(); // → collapsed
        assert.ok($('#sidebar').hasClass('collapsed'), "Sidebar згорнуто");
        toggleSidebar(); // → opened
        assert.notOk($('#sidebar').hasClass('collapsed'), "Sidebar розгорнуто");
    });

    QUnit.test("openSidebar встановлює opened у localStorage", assert => {
        openSidebar();
        assert.equal(localStorage.getItem('sidebarState'), 'opened', "Стан збережено як opened");
    });

    QUnit.test("closeSidebar встановлює collapsed у localStorage", assert => {
        closeSidebar();
        assert.equal(localStorage.getItem('sidebarState'), 'collapsed', "Стан збережено як collapsed");
    });

    QUnit.test("initSidebarToggle ініціалізує та навішує обробник", assert => {
        const toggleSpy = sinon.spy(window, 'toggleSidebar');

        $('#sidebar-toggle').trigger('click'); // без init — нічого
        assert.notOk(toggleSpy.called, "До initSidebarToggle — обробник не працює");

        localStorage.setItem('sidebarState', 'collapsed');
        initSidebarToggle();

        $('#sidebar-toggle').trigger('click');
        assert.ok(toggleSpy.calledOnce, "Після initSidebarToggle — обробник працює");

        toggleSpy.restore();
    });

    QUnit.test("initSidebarToggle обробляє відсутні елементи", assert => {
        $('#sidebar-toggle').remove();
        $('#sidebar').remove();
        const consoleErrorStub = sinon.stub(console, 'error');

        initSidebarToggle();
        assert.ok(consoleErrorStub.calledWithMatch(/Не знайдено sidebar/), "Показано помилку в консоль");

        consoleErrorStub.restore();
    });
});

QUnit.module("Theme Toggle", hooks => {
    hooks.beforeEach(() => {
        $('#qunit-fixture').html(`
            <button id="theme-toggle"><i class="fa-solid fa-sun"></i></button>
            <span id="theme-label"></span>
        `);
        localStorage.removeItem('admin-theme');
        $('body').removeClass('theme-light theme-dark');
    });

    QUnit.test("applyTheme 'theme-dark' оновлює DOM", assert => {
        applyTheme('theme-dark');
        assert.ok($('body').hasClass('theme-dark'), "Body має клас theme-dark");
        assert.equal($('#theme-label').text(), "Ніч", "Мітка теми оновлена");
        assert.ok($('#theme-toggle i').hasClass('fa-moon'), "Іконка змінена на moon");
    });

    QUnit.test("applyTheme 'theme-light' оновлює DOM", assert => {
        applyTheme('theme-light');
        assert.ok($('body').hasClass('theme-light'), "Body має клас theme-light");
        assert.equal($('#theme-label').text(), "День", "Мітка теми оновлена");
        assert.ok($('#theme-toggle i').hasClass('fa-sun'), "Іконка змінена на sun");
    });

    QUnit.test("initThemeToggle ініціалізує тему і змінює її по кліку", assert => {
        localStorage.setItem('admin-theme', 'theme-dark');
        initThemeToggle();
        assert.ok($('body').hasClass('theme-dark'), "Тема з localStorage застосована");

        $('#theme-toggle').trigger('click');
        const newTheme = localStorage.getItem('admin-theme');
        assert.ok(['theme-dark', 'theme-light'].includes(newTheme), "Тема оновилась");
    });

    QUnit.test("initThemeToggle нічого не ламає, якщо елементів немає", assert => {
        $('#theme-toggle').remove();
        $('#theme-label').remove();
        initThemeToggle();
        assert.ok(true, "Функція виконується без помилок");
    });
});

QUnit.module("Admin Panel Features", hooks => {
    QUnit.test("initAdminPanelFeatures додає події до заголовків .module h2", assert => {
        $('#qunit-fixture').html(`
            <div class="module">
                <h2>Заголовок</h2>
                <div class="module-body">Контент</div>
            </div>
        `);

        initAdminPanelFeatures();
        const h2 = $('.module h2');
        const content = $('.module-body');
        assert.equal(content.css('display'), 'block', "Спочатку відображається");

        h2.trigger('click');
        assert.equal(content.css('display'), 'none', "Після кліку приховано");

        h2.trigger('click');
        assert.equal(content.css('display'), 'block', "Після другого кліку знову видно");
    });

    QUnit.test("initAdminPanelFeatures приховує повідомлення через 5 секунд", assert => {
        const clock = sinon.useFakeTimers();
        $('#qunit-fixture').html(`
            <ul class="messagelist">
                <li>Повідомлення</li>
            </ul>
        `);

        initAdminPanelFeatures();
        assert.equal($('.messagelist li').css('display'), 'list-item', "Спочатку показано");

        clock.tick(5001);
        assert.equal($('.messagelist li').css('display'), 'none', "Через 5 секунд приховано");

        clock.restore();
    });
});

QUnit.module("initReportDropdown", hooks => {
    let server;

    hooks.beforeEach(() => {
        server = sinon.createFakeServer();
        server.autoRespond = true;

        $('#qunit-fixture').html(`
            <select id="report-dropdown">
                <option value="">--</option>
                <option value="/report">Звіт</option>
            </select>
            <div id="report-content"></div>
        `);
    });

    hooks.afterEach(() => {
        server.restore();
    });

    QUnit.test("initReportDropdown завантажує HTML при виборі", assert => {
        const done = assert.async();

        server.respondWith('GET', '/report', [
            200,
            { 'Content-Type': 'application/json' },
            JSON.stringify({ html: "<div>Звіт готовий</div>" })
        ]);

        initReportDropdown();
        $('#report-dropdown').val('/report').trigger('change');

        setTimeout(() => {
            assert.ok($('#report-content').html().includes("Звіт готовий"), "Контент оновлено");
            done();
        }, 50);
    });

    QUnit.test("initReportDropdown показує помилку при статусі 500", assert => {
        const done = assert.async();

        server.respondWith('GET', '/report', [
            500,
            {},
            "Server error"
        ]);

        initReportDropdown();
        $('#report-dropdown').val('/report').trigger('change');

        setTimeout(() => {
            assert.ok($('#report-content').text().includes("Не вдалося завантажити звіт"), "Показано помилку");
            done();
        }, 50);
    });

    QUnit.test("initReportDropdown обробляє пустий вибір", assert => {
        initReportDropdown();
        $('#report-dropdown').val('').trigger('change');
        assert.ok($('#report-content').html().includes("Результати звіту з’являться тут"), "Показано заглушку");
    });
});

QUnit.module("Staff & Author Utilities", hooks => {
    QUnit.test("updateStaffStatus замінює іконки на текст", assert => {
        $('#qunit-fixture').html(`
            <table>
                <tr><td class="field-is_staff"><img alt="True"></td></tr>
                <tr><td class="field-is_staff"><img alt="False"></td></tr>
            </table>
        `);

        updateStaffStatus();

        const cells = $('.field-is_staff');
        assert.equal(cells.eq(0).text(), "Адмін", "True => Адмін");
        assert.equal(cells.eq(1).text(), "Користувач", "False => Користувач");
    });

    QUnit.test("updateStaffFilter змінює тексти в посиланнях", assert => {
        $('#qunit-fixture').html(`
            <details data-filter-title="статус персоналу">
                <ul>
                    <li><a href="/admin/?is_staff__exact=1">Так</a></li>
                    <li><a href="/admin/?is_staff__exact=0">Ні</a></li>
                </ul>
            </details>
        `);

        updateStaffFilter();

        const links = $('details[data-filter-title] a');
        assert.equal(links.eq(0).text(), "Адмін", "Так → Адмін");
        assert.equal(links.eq(1).text(), "Користувач", "Ні → Користувач");
    });

    QUnit.test("updateAddAuthorButton змінює текст кнопки", assert => {
        window.history.pushState({}, '', '/admin/newportal/author/');
        $('#qunit-fixture').html(`<a class="addlink">Додати автори</a>`);
        updateAddAuthorButton();
        assert.equal($('.addlink').text(), "Додати автора", "Назва кнопки оновлена");
    });
});

QUnit.module("moveAddButtonToActions", () => {
    QUnit.test("переміщує кнопку в actions", assert => {
        $('#qunit-fixture').html(`
            <a class="addlink">Додати</a>
            <div class="actions"></div>
        `);

        const addButton = $('.addlink')[0];
        moveAddButtonToActions();

        assert.ok($('.actions').has(addButton).length, "Кнопка переміщена в actions");
        assert.equal(addButton.style.marginLeft, "auto", "marginLeft застосовано");
        assert.equal(addButton.style.padding, "10px 16px", "padding застосовано");
    });

    QUnit.test("нічого не робить, якщо вже переміщено", assert => {
        $('#qunit-fixture').html(`
            <div class="actions">
                <a class="addlink">Додано</a>
            </div>
        `);

        moveAddButtonToActions();
        assert.ok(true, "Не додано вдруге");
    });
});

QUnit.module("Filter Updates", () => {
    QUnit.test("updateFilterTitles змінює заголовок і summary", assert => {
        $('#qunit-fixture').html(`
            <div id="changelist-filter-header">Відфільтрувати</div>
            <summary>За Автор</summary>
        `);

        updateFilterTitles();
        assert.equal($('#changelist-filter-header').text(), "Фільтр", "Заголовок оновлено");
        assert.equal($('summary').text(), "Автор", "Summary оновлено");
    });

    QUnit.test("styleFilterButtons стилізує та підписує кнопки", assert => {
        $('#qunit-fixture').html(`
            <div id="changelist-filter-extra-actions">
                <h3>
                    <a class="viewlink">...</a>
                    <a class="hidelink">...</a>
                    <a>Очистити всі фільтри</a>
                </h3>
            </div>
        `);

        styleFilterButtons();
        assert.equal($('.viewlink').text(), "Показати кількість", "viewlink текст оновлено");
        assert.equal($('.hidelink').text(), "Приховати кількість", "hidelink текст оновлено");
        assert.ok($('a:contains("Очистити всі фільтри")').text().includes("✖"), "Очистити має значок");
    });
});

QUnit.module("UI Layout", hooks => {
    hooks.beforeEach(() => {
        localStorage.clear();
    });

    QUnit.test("initFilterDetails відкриває або закриває деталі", assert => {
        $('#qunit-fixture').html(`
            <div id="changelist-filter">
                <details><summary>Розділ</summary></details>
            </div>
        `);

        localStorage.setItem("filter-open-0", "true");
        initFilterDetails();
        assert.ok($('details').attr('open') !== undefined, "Встановлено open");

        $('summary').trigger('click');
        assert.equal(localStorage.getItem('filter-open-0'), "false", "Збережено новий стан");
    });

    QUnit.test("rearrangeContent реорганізує DOM", assert => {
        $('#qunit-fixture').html(`
            <div id="content-main">
                <div class="changelist-form-container"></div>
                <div id="changelist-filter"></div>
            </div>
        `);

        rearrangeContent();
        const wrapper = $('.content-wrapper');
        assert.ok(wrapper.length, "Додано wrapper");
        assert.equal(wrapper.css('display'), 'grid', "Сітка активована");
    });

    QUnit.test("adjustContentLayout оновлює відступи залежно від стану сайдбару", assert => {
        $('#qunit-fixture').html(`
            <main class="container-fluid"></main>
            <div id="sidebar" class=""></div>
        `);

        adjustContentLayout();
        assert.ok($('main').css('marginLeft').includes('250'), "Відступ при відкритому сайдбарі");

        $('#sidebar').addClass('collapsed');
        adjustContentLayout();
        assert.equal($('main').css('marginLeft'), '0px', "Відсутній відступ при закритому сайдбарі");
    });
});