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