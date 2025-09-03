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