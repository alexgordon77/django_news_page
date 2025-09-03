document.addEventListener('DOMContentLoaded', () => {
    initAdminPanelFeatures();
    moveAddButtonToActions();
    updateStaffStatus();
    updateStaffFilter();
    initSidebarToggle();

    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.dataset.url;
            if (url) loadContent(url);
        });
    });

    const homeLink = document.querySelector('.nav-link[href="/admin/"]');
    if (homeLink) {
        homeLink.addEventListener('click', function (e) {
            e.preventDefault();
            loadContent('/admin/');
        });
    }


    const savedArticleForm = document.getElementById('savedarticle_form');

    if (savedArticleForm) {
        // Додаємо заголовок
        const heading = document.createElement('h1');
        heading.textContent = 'Додати збережену статтю';
        savedArticleForm.prepend(heading);

        // Підсвічування кнопок при натисканні
        const buttons = savedArticleForm.querySelectorAll('.submit-row input[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = '#004085';
            });
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = '#007bff';
            });
        });
    }

    const articleForm = document.getElementById('article_form');

    if (articleForm) {
        // Додаємо заголовок
        const heading = document.createElement('h1');
        heading.textContent = 'Додати / Редагувати статтю';
        articleForm.prepend(heading);

        // Підсвічування кнопок при натисканні
        const buttons = articleForm.querySelectorAll('.submit-row input[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = '#004085';
            });
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = '#007bff';
            });
        });
    }

    const commentForm = document.getElementById('comment_form');

    if (commentForm) {
        // Додаємо заголовок
        const heading = document.createElement('h1');
        heading.textContent = 'Додати коментар';
        commentForm.prepend(heading);

        // Підсвічування кнопок при натисканні
        const buttons = commentForm.querySelectorAll('.submit-row input[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = '#004085';
            });
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = '#007bff';
            });
        });
    }

    const userForm = document.getElementById('user_form');

    if (userForm) {
        // Додаємо заголовок форми
        const heading = document.createElement('h1');
        heading.textContent = "Додати користувача";
        heading.style.textAlign = "center";
        heading.style.fontWeight = "bold";
        userForm.prepend(heading);

        // Стилізація кнопок
        const buttons = userForm.querySelectorAll('.submit-row input[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = '#004085';
            });
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = '#007bff';
            });
        });

        // Додаємо hover-ефект для кнопки "Видалити"
        const deleteLink = userForm.querySelector('.submit-row .deletelink');
        if (deleteLink) {
            deleteLink.addEventListener('mouseover', () => {
                deleteLink.style.backgroundColor = '#b52d3a';
            });
            deleteLink.addEventListener('mouseout', () => {
                deleteLink.style.backgroundColor = '#dc3545';
            });
        }
    }

    const groupForm = document.getElementById('group_form');

    if (groupForm) {
        // Додаємо заголовок форми
        const heading = document.createElement('h1');
        heading.textContent = "Додати нову групу";
        heading.style.textAlign = "center";
        heading.style.fontWeight = "bold";
        groupForm.prepend(heading);

        // Підсвічування кнопок при натисканні
        const buttons = groupForm.querySelectorAll('.submit-row input[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = '#004085';
            });
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = '#007bff';
            });
        });
    }

    const form = document.getElementById('author_form');

    if (form) {
        // Додаємо заголовок форми
        const heading = document.createElement('h1');
        heading.textContent = "Додати нового автора";
        heading.style.textAlign = "center";
        heading.style.marginBottom = "20px";
        heading.style.fontWeight = "bold";
        form.prepend(heading);

        // Підсвічування кнопок при натисканні
        const buttons = form.querySelectorAll('.submit-row input[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = '#004085';
            });
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = '#007bff';
            });
        });
    }

    const tagForm = document.getElementById('tag_form');

    if (tagForm) {
        // Додаємо заголовок форми
        const heading = document.createElement('h1');
        heading.textContent = "Додати новий тег";
        heading.style.textAlign = "center";
        heading.style.marginBottom = "20px";
        heading.style.fontWeight = "bold";
        tagForm.prepend(heading);

        // Підсвічування кнопок при натисканні
        const buttons = tagForm.querySelectorAll('.submit-row input[type="submit"]');
        buttons.forEach(button => {
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = '#004085';
            });
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = '#007bff';
            });
        });
    }



    window.addEventListener('popstate', function () {
        const currentUrl = window.location.href;
        loadContent(currentUrl);
    });

    window.addEventListener('resize', adjustContentLayout);

    // Ініціалізація фільтрів
    initFilterDetails();
    updateAddAuthorButton();
    rearrangeContent();
    adjustContentLayout();
    styleFilterButtons();
    // Оновлюємо назви фільтрів
    updateFilterTitles();
});

// Функція для оновлення статусів в таблиці
    const updateStaffStatus = () => {
        const staffCells = document.querySelectorAll('td.field-is_staff');

        staffCells.forEach(cell => {
            const iconYes = cell.querySelector('img[alt="True"]');
            const iconNo = cell.querySelector('img[alt="False"]');

            if (iconYes) {
                cell.innerHTML = 'Адмін'; // Заміна галочки на "Адмін"
            } else if (iconNo) {
                cell.innerHTML = 'Користувач'; // Заміна хрестика на "Користувач"
            }
        });
    };

    // Функція для оновлення текстів у фільтрі "Статус персоналу"
    const updateStaffFilter = () => {
        const staffFilter = document.querySelector('details[data-filter-title="статус персоналу"] ul');

        if (staffFilter) {
            staffFilter.querySelectorAll('li > a').forEach(link => {
                const url = new URL(link.href, window.location.origin);
                const isStaffExact = url.searchParams.get('is_staff__exact');

                if (isStaffExact === '1') {
                    link.innerHTML = link.innerHTML.replace('Так', 'Адмін'); // Заміна "Так" на "Адмін"
                } else if (isStaffExact === '0') {
                    link.innerHTML = link.innerHTML.replace('Ні', 'Користувач'); // Заміна "Ні" на "Користувач"
                }
            });
        }
    };


// Функція переміщення кнопки "Додати автора" в блок "actions"
function moveAddButtonToActions() {
    const addButton = document.querySelector('.addlink'); // Знаходимо кнопку "Додати автора"
    const actionsContainer = document.querySelector('.actions'); // Знаходимо блок "actions"

    if (addButton && actionsContainer) {
        // Перевіряємо, чи кнопка вже переміщена
        if (!actionsContainer.contains(addButton)) {
            actionsContainer.appendChild(addButton); // Додаємо кнопку в кінець блока дій
            addButton.style.marginLeft = "auto"; // Вирівнюємо кнопку праворуч
            addButton.style.marginTop = "10px";
            addButton.style.padding = "10px 16px"; // Робимо кнопки схожими
        }
    }
}

// **Функція для заміни назв фільтрів**
function updateFilterTitles() {
    const filterHeader = document.getElementById('changelist-filter-header');
    if (filterHeader) {
        filterHeader.textContent = 'Фільтр'; // Заміна "Відфільтрувати" на "Фільтр"
    }

    const filterTitles = {
        "За Дата збереження": "Дата збереження",
        "За Дата створення": "Дата створення",
        "За user": "Користувач",
        "За Автор": "Автор",
        "За Дата публікації": "Дата публікації",
        "За Теги": "Тег",
        "За статус персоналу": "Статус персоналу",
        "За статус суперкористувача": "Статус суперюзера",
        "За активний": "Активний",
        "За групи": "Групи",
    };

    document.querySelectorAll('#changelist-filter summary').forEach(summary => {
        const originalText = summary.textContent.trim();
        if (filterTitles[originalText]) {
            summary.textContent = filterTitles[originalText];
        }
    });
}

function styleFilterButtons() {
    const showCountsBtn = document.querySelector('#changelist-filter-extra-actions h3 a.viewlink');
    const hideCountsBtn = document.querySelector('#changelist-filter-extra-actions h3 a.hidelink');
    const clearFiltersBtn = Array.from(document.querySelectorAll('#changelist-filter-extra-actions h3 a'))
        .find(a => a.textContent.includes("Очистити всі фільтри"));

    function styleButton(button, backgroundColor) {
        if (!button) return;
        button.style.backgroundColor = backgroundColor;
        button.style.color = "white";
        button.style.padding = "6px 10px";
        button.style.fontSize = "0.9rem";
        button.style.borderRadius = "6px";
        button.style.width = "100%";
        button.style.textAlign = "center";
        button.style.marginBottom = "10px";
        button.style.border = "none";
        button.style.transition = "background-color 0.3s ease";
    }

    if (showCountsBtn) {
        showCountsBtn.textContent = "Показати кількість";
        styleButton(showCountsBtn, "#007bff");
        showCountsBtn.addEventListener('mouseover', () => {
            showCountsBtn.style.backgroundColor = "#0056b3";
        });
        showCountsBtn.addEventListener('mouseout', () => {
            showCountsBtn.style.backgroundColor = "#007bff";
        });
    }

    if (hideCountsBtn) {
        hideCountsBtn.textContent = "Приховати кількість";
        styleButton(hideCountsBtn, "#007bff");
        hideCountsBtn.addEventListener('mouseover', () => {
            hideCountsBtn.style.backgroundColor = "#0056b3";
        });
        hideCountsBtn.addEventListener('mouseout', () => {
            hideCountsBtn.style.backgroundColor = "#007bff";
        });
    }

    if (clearFiltersBtn) {
        styleButton(clearFiltersBtn, "#dc3545");
        clearFiltersBtn.textContent = "✖ Очистити всі фільтри";
        clearFiltersBtn.addEventListener('mouseover', () => {
            clearFiltersBtn.style.backgroundColor = "#b52d3a";
        });
        clearFiltersBtn.addEventListener('mouseout', () => {
            clearFiltersBtn.style.backgroundColor = "#dc3545";
        });
    }
}

function initFilterDetails() {
    const filterDetails = document.querySelectorAll('#changelist-filter details');

    filterDetails.forEach((detail, index) => {
        const savedState = localStorage.getItem(`filter-open-${index}`);
        if (savedState === "true") {
            detail.setAttribute('open', '');
        } else {
            detail.removeAttribute('open');
        }
    });

    filterDetails.forEach((detail, index) => {
        const summary = detail.querySelector('summary');
        summary.addEventListener('click', (e) => {
            e.preventDefault();
            const isOpen = detail.hasAttribute('open');
            detail.toggleAttribute('open');
            localStorage.setItem(`filter-open-${index}`, isOpen ? "false" : "true");
        });
    });
}

function rearrangeContent() {
    const contentMain = document.getElementById('content-main');
    const changeList = document.querySelector('.changelist-form-container');
    const filterNav = document.getElementById('changelist-filter');

    if (!contentMain || !changeList || !filterNav || contentMain.querySelector('.content-wrapper')) return;

    const contentWrapper = document.createElement('div');
    contentWrapper.classList.add('content-wrapper');

    contentWrapper.appendChild(changeList.parentElement);
    contentWrapper.appendChild(filterNav);
    contentMain.replaceChildren(contentWrapper);

    contentWrapper.style.display = 'grid';
    contentWrapper.style.gridTemplateColumns = '3fr 1fr';
    contentWrapper.style.gap = '20px';
    contentWrapper.style.alignItems = 'start';
    contentMain.style.overflow = 'hidden';

    filterNav.style.height = 'auto';
    filterNav.style.minWidth = '200px';
}

function adjustContentLayout() {
    const mainContent = document.querySelector('main.container-fluid');
    const sidebar = document.getElementById('sidebar');

    if (!sidebar || !mainContent) return;

    const isSidebarOpened = !sidebar.classList.contains('collapsed');
    const sidebarWidth = 250;
    const padding = 20;

    if (isSidebarOpened) {
        mainContent.style.marginLeft = `${sidebarWidth}px`;
        mainContent.style.width = `calc(100% - ${sidebarWidth + padding}px)`;
    } else {
        mainContent.style.marginLeft = "0px";
        mainContent.style.width = `calc(100% - ${padding}px)`;
    }
}

function initAdminPanelFeatures() {
    const moduleHeaders = document.querySelectorAll('.module h2');
    moduleHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            content.style.display = content.style.display === 'none' ? 'block' : 'none';
        });
    });

    document.querySelectorAll('.messagelist li').forEach(message => {
        setTimeout(() => message.style.display = 'none', 5000);
    });

    initSidebarToggle();
    initThemeToggle();
    initReportDropdown();
    updateAddAuthorButton();
}

function loadContent(url) {
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => {
            if (!response.ok) throw new Error('Помилка завантаження даних');
            return response.text();
        })
        .then(html => {
            const tempDom = document.createElement('div');
            tempDom.innerHTML = html;
            const newContent = tempDom.querySelector('main.container-fluid') || tempDom;
            const contentContainer = document.querySelector('main.container-fluid');

            if (contentContainer) {
                contentContainer.innerHTML = newContent.innerHTML;
                history.pushState(null, '', url);

                // 🔹 Повторна ініціалізація всіх функцій після завантаження звіту
                initAdminPanelFeatures();
                rearrangeContent();
                adjustContentLayout();
                initFilterDetails();
                styleFilterButtons();
                updateFilterTitles();
                initThemeToggle();
                moveAddButtonToActions();
                updateStaffStatus();
                updateStaffFilter();
                initSidebarToggle();

                // 🔹 Якщо завантажено звіт, перевіряємо наявність `prohibited-words-url`
                if (document.getElementById('prohibited-words-url')) {
                    console.log("🔄 Повторне завантаження `prohibited_words_report.js`");

                    // Видаляємо попередній екземпляр скрипта, якщо він існує
                    delete window.refreshWordsList;
                    delete window.refreshTable;
                    delete window.attachDeleteEvent;

                    $.getScript("/static/js/prohibited_words_report.js")
                        .done(function () {
                            console.log("✅ Завантажено `prohibited_words_report.js`");
                            if (typeof window.refreshWordsList === "function" && typeof window.refreshTable === "function") {
                                window.refreshWordsList();
                                window.refreshTable();
                            }
                        })
                        .fail(function () {
                            console.error("❌ Не вдалося завантажити `prohibited_words_report.js`");
                        });
                }
            }
        })
        .catch(error => {
            console.error("Помилка:", error);
            document.querySelector('main.container-fluid').innerHTML = '<p class="text-danger">Не вдалося завантажити дані. Спробуйте ще раз.</p>';
        });
}

function updateAddAuthorButton() {
    const currentPath = window.location.pathname;
    const isAuthorPage = currentPath.includes("/admin/newportal/author/");
    const addLink = document.querySelector('.addlink');

    if (isAuthorPage && addLink && addLink.textContent.trim() === "Додати автори") {
        addLink.textContent = "Додати автора";
    }
}


// <<<РОБОТА САЙДБАРУ В ШАБЛОНІ base.html>>>
function initSidebarToggle() {
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("sidebar");

    if (!sidebarToggle || !sidebar) {
        console.error("Не знайдено sidebar або sidebar-toggle!");
        return;
    }

    // Сайдбар за замовчуванням закритий (але якщо є збережений стан, використовуємо його)
    let sidebarState = localStorage.getItem('sidebarState') || "collapsed";

    // Встановлюємо відповідний стан
    applySidebarState(sidebarState);

    // Додаємо обробник подій на кнопку
    sidebarToggle.removeEventListener('click', toggleSidebar);
    sidebarToggle.addEventListener('click', toggleSidebar);
}

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const isSidebarHidden = sidebar.classList.contains("collapsed");

    if (isSidebarHidden) {
        openSidebar();
    } else {
        closeSidebar();
    }

    adjustContentLayout();
}

// Функція для оновлення тексту кнопки та зміни сайдбару
function applySidebarState(state) {
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");

    if (!sidebar || !sidebarToggle) return;

    if (state === 'opened') {
        sidebar.classList.remove("collapsed");
        sidebar.style.width = "250px";
        document.body.classList.add("sidebar-opened");
        document.body.classList.remove("sidebar-collapsed");
        sidebarToggle.innerHTML = '<i class="fa-solid fa-bars"></i> Закрити';
    } else {
        sidebar.classList.add("collapsed");
        sidebar.style.width = "0px";
        document.body.classList.add("sidebar-collapsed");
        document.body.classList.remove("sidebar-opened");
        sidebarToggle.innerHTML = '<i class="fa-solid fa-bars"></i>';
    }

    //  Додаємо корекцію розміщення контенту
    adjustContentLayout();
}

//  Функція відкриття сайдбару
function openSidebar() {
    localStorage.setItem('sidebarState', 'opened');
    applySidebarState('opened');
}

//  Функція закриття сайдбару
function closeSidebar() {
    localStorage.setItem('sidebarState', 'collapsed');
    applySidebarState('collapsed');
}

// <<<ПЕРЕМИКАЧ ТЕМИ>>>
function initThemeToggle() {
    const themeToggleBtn = document.getElementById("theme-toggle");
    const savedTheme = localStorage.getItem("admin-theme") || "theme-light";

    applyTheme(savedTheme);

    if (!themeToggleBtn) return;

    const newThemeToggleBtn = themeToggleBtn.cloneNode(true);
    themeToggleBtn.parentNode.replaceChild(newThemeToggleBtn, themeToggleBtn);

    newThemeToggleBtn.addEventListener("click", () => {
        const currentTheme = document.body.classList.contains("theme-light") ? "theme-dark" : "theme-light";
        localStorage.setItem("admin-theme", currentTheme);
        applyTheme(currentTheme);
    });
}

// <<<ЗАСТОСУВАННЯ ТЕМИ>>>
function applyTheme(theme) {
    const body = document.body;
    const themeLabel = document.getElementById("theme-label");
    const themeToggleBtn = document.getElementById("theme-toggle");

    body.classList.remove("theme-light", "theme-dark");
    body.classList.add(theme);

    if (themeLabel && themeToggleBtn) {
        if (theme === "theme-dark") {
            themeLabel.textContent = "Ніч";
            themeToggleBtn.querySelector("i").classList.replace("fa-sun", "fa-moon");
        } else {
            themeLabel.textContent = "День";
            themeToggleBtn.querySelector("i").classList.replace("fa-moon", "fa-sun");
        }
    }
}

function initReportDropdown() {
    const reportDropdown = document.getElementById("report-dropdown");

    if (reportDropdown) {
        reportDropdown.addEventListener("change", function () {
            const selectedUrl = this.value;
            if (selectedUrl) {
                fetch(selectedUrl, {
                    method: "GET",
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                    .then(response => {
                        if (!response.ok) throw new Error("Помилка завантаження звіту");
                        return response.json();
                    })
                    .then(responseJson => {
                        if (responseJson.html) {
                            const reportContent = document.getElementById("report-content");
                            reportContent.innerHTML = responseJson.html;
                        } else {
                            document.getElementById("report-content").innerHTML = "<p>Звіт не повернув HTML-контент.</p>";
                        }
                    })
                    .catch(() => {
                        document.getElementById("report-content").innerHTML = "<p class='text-danger'>Не вдалося завантажити звіт. Спробуйте пізніше.</p>";
                    });
            } else {
                document.getElementById("report-content").innerHTML = "<h3>Результати звіту з’являться тут</h3>";
            }
        });
    }
}


