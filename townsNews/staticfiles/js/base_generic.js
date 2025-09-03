// --------------------- Sidebar ---------------------
function handleMenuMouseEnter(sidebar) {
    sidebar.stop(true, true).slideDown(300);
}

function shouldHideSidebar(menuBtn, sidebar) {
    return !menuBtn.is(":hover") && !sidebar.is(":hover");
}

function handleMouseLeave(menuTimeoutRef, menuBtn, sidebar) {
    menuTimeoutRef.menuTimeout = setTimeout(function () {
        if (shouldHideSidebar(menuBtn, sidebar)) {
            sidebar.slideUp(300);
        }
    }, 300);
}

function handleSidebarMouseEnter(menuTimeoutRef) {
    clearTimeout(menuTimeoutRef.menuTimeout);
}

function initSidebar(menuBtn = $("#menuBtn"), sidebar = $("#sidebar")) {
    let menuTimeoutRef = { menuTimeout: null };
    sidebar.hide();

    menuBtn.mouseenter(() => handleMenuMouseEnter(sidebar));
    menuBtn.add(sidebar).mouseleave(() => handleMouseLeave(menuTimeoutRef, menuBtn, sidebar));
    sidebar.mouseenter(() => handleSidebarMouseEnter(menuTimeoutRef));
}

// --------------------- Display Modes ---------------------
let displayMode = 0; // 0 - weather, 1 - currency, 2 - time
let clockInterval = null;

// --------------------- Weather ---------------------
function loadWeather() {
    if (clockInterval) {
        clearInterval(clockInterval);
        clockInterval = null;
    }

    const block = $('#weather-block');
    block.addClass('fade-out');

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            console.log(lat)
            console.log(lon)

            $.ajax({
                url: '/api/weather/',
                method: 'GET',
                data: { lat: lat, lon: lon },
                success: function (data) {
                    if (data.temp !== undefined && data.icon !== undefined) {
                        setTimeout(() => {
                            block
                                .removeClass('currency-view time-view')
                                .addClass('weather-view')
                                .html(
                                    '<span>' + data.temp + '°C</span>' +
                                    '<img src="https://openweathermap.org/img/wn/' + data.icon + '@2x.png" ' +
                                    'alt="Погода" title="' + data.description + '" style="height: 60px; margin-top: -6%" />'
                                )
                                .removeClass('fade-out');
                        }, 300);
                    }
                },
                error: function () {
                    block.text('Погода недоступна').removeClass('fade-out');
                }
            });

        }, function (error) {
            block.text('Не вдалося отримати геолокацію').removeClass('fade-out');
        });
    } else {
        block.text('Геолокація не підтримується браузером').removeClass('fade-out');
    }
}

// --------------------- Currency ---------------------
function loadCurrencyRates() {
    if (clockInterval) {
        clearInterval(clockInterval);
        clockInterval = null;
    }

    const block = $('#weather-block');
    block.addClass('fade-out');

    $.ajax({
        url: '/api/currency_rates/',
        method: 'GET',
        success: function (data) {
            if (data.usd !== undefined && data.eur !== undefined) {
                setTimeout(() => {
                    block
                        .removeClass('weather-view time-view')
                        .addClass('currency-view')
                        .html(
                            '<div class="currency-line">$ ' + data.usd.buy + '/' + data.usd.sell + '</div>' +
                            '<div class="currency-line">€ ' + data.eur.buy + '/' + data.eur.sell + '</div>'
                        )
                        .removeClass('fade-out');
                }, 300);
            }
        },
        error: function () {
            block.text('Курси валют недоступні').removeClass('fade-out');
        }
    });
}

// --------------------- Time ---------------------
function loadKyivTime() {
    if (clockInterval) {
        clearInterval(clockInterval);
    }

    const block = $('#weather-block');
    block.addClass('fade-out');

    setTimeout(() => {
        block
            .removeClass('weather-view currency-view')
            .addClass('time-view')
            .html('<div class="time-line" id="kyiv-clock">00:00:00</div>')
            .removeClass('fade-out');

        updateClock();
        clockInterval = setInterval(updateClock, 1000);
    }, 300);
}

function updateClock() {
    const now = new Date();
    const options = {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    };

    const formatter = new Intl.DateTimeFormat('uk-UA', options);
    const formattedTime = formatter.format(now);

    $('#kyiv-clock').text(formattedTime);
}

// Mobile Sidebar Menu
$(function () {
    // Додаємо кнопку закриття тільки для мобільної версії (ширина ≤ 768px)
    function addSidebarCloseBtnIfMobile() {
        if ($(window).width() <= 768) {
            if ($('#sidebar').find('#closeSidebar').length === 0) {
                $('#sidebar').prepend('<button id="closeSidebar" style="float:right;font-size:22px;background:none;border:none;cursor:pointer;">✕</button>');
            }
        } else {
            $('#closeSidebar').remove(); // При переході на десктоп ховаємо
        }
    }

    // Відкрити sidebar по кліку на "Меню" в мобільному меню
    $('#menuBtnMobile').on('click', function(e) {
        e.preventDefault();
        addSidebarCloseBtnIfMobile();
        $('#sidebar').addClass('active').show();
    });

    // Закрити sidebar по ✕
    $(document).on('click', '#closeSidebar', function () {
        $('#sidebar').removeClass('active').hide();
    });

    // Клік поза sidebar закриває його (лише для мобільних)
    $(document).on('click touchstart', function(e) {
        if (
            $('#sidebar').hasClass('active') &&
            $(window).width() <= 768 &&
            !$(e.target).closest('#sidebar, #menuBtnMobile').length
        ) {
            $('#sidebar').removeClass('active').hide();
        }
    });

    // При зміні розміру вікна — оновлюємо видимість кнопки ✕
    $(window).on('resize', addSidebarCloseBtnIfMobile);

    // Одразу викликаємо для правильного стану
    addSidebarCloseBtnIfMobile();
});

// --------------------- Main ---------------------
$(document).ready(function () {
    initSidebar();
    loadWeather();

    setInterval(function () {
        displayMode = (displayMode + 1) % 3;

        if (displayMode === 0) {
            loadWeather();
        } else if (displayMode === 1) {
            loadCurrencyRates();
        } else {
            loadKyivTime();
        }
    }, 30000);
});

// --------------------- Export for Node.js (testing) ---------------------
if (typeof module !== 'undefined') {
    module.exports = {
        initSidebar,
        handleMenuMouseEnter,
        handleMouseLeave,
        handleSidebarMouseEnter,
        shouldHideSidebar,
        loadWeather,
        loadCurrencyRates,
        loadKyivTime,
        updateClock
    };
}