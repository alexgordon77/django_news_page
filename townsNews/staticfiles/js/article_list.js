function getDataFromElement(elementId, attr) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.warn(`⚠️ Елемент #${elementId} не знайдено.`);
        return [];
    }
    try {
        return JSON.parse(element.getAttribute(attr) || '[]');
    } catch (error) {
        console.error(`❗️ Помилка при парсингу JSON для #${elementId}:`, error);
        return [];
    }
}

function clearOtherFilters(excludeType) {
    const params = new URLSearchParams(window.location.search);
    if (excludeType === 'author') {
        params.delete('tag');
    } else if (excludeType === 'tag') {
        params.delete('author');
    }
    return params;
}

let activeWord = null;
let isFilterInProgress = false;

function filterByWord(word, type) {
    if (isFilterInProgress) {
        console.log('⏳ Фільтрація вже в процесі, ігноруємо клік');
        return;
    }

    isFilterInProgress = true;
    console.log(`🔍 СТАРТ ФІЛЬТРАЦІЇ: ${word} (${type})`);

    const authorsData = getDataFromElement('author-data', 'data-authors');
    const tagsData = getDataFromElement('tag-data', 'data-tags');

    let value = '';
    if (word === 'Всі автори' || word === 'Всі теги') {
        value = '';
        console.log('🔄 Скидання фільтрів');
    } else {
        if (type === 'author') {
            const author = authorsData.find(a => a.name === word);
            if (!author) {
                console.error(`❌ Автор "${word}" не знайдений`);
                isFilterInProgress = false;
                return;
            }
            value = author.id;
            console.log(`👤 Знайдено автора: ${author.name} (ID: ${author.id})`);
        } else {
            const tag = tagsData.find(t => t.name === word);
            if (!tag) {
                console.error(`❌ Тег "${word}" не знайдений`);
                isFilterInProgress = false;
                return;
            }
            value = tag.id;
            console.log(`🏷️ Знайдено тег: ${tag.name} (ID: ${tag.id})`);
        }
    }

    activeWord = { type, word };
    const params = clearOtherFilters(type);

    if (!value) {
        params.delete(type);
    } else {
        params.set(type, value);
    }

    const newUrl = `${window.location.pathname}?${params.toString()}`;
    console.log(`🌐 Переходимо на: ${newUrl}`);

    // Негайний перехід без затримки
    window.location.href = newUrl;
}

function initSearchToggle() {
    const searchButton = document.getElementById('toggle-search-btn');
    const searchSection = document.getElementById('search-section');
    if (searchButton && searchSection) {
        searchButton.addEventListener('click', () => {
            searchSection.style.display = searchSection.style.display === 'none' ? 'block' : 'none';
        });
    }
}

function lookAtWordLetter(x, y, z, theta) {
    const n = [x, y, z];
    const r = Math.sqrt(x * x + y * y + z * z);
    n[0] /= r; n[1] /= r; n[2] /= r;

    const t = [-Math.sin(theta), 0, Math.cos(theta)];

    const v = [
        n[1]*t[2] - n[2]*t[1],
        n[2]*t[0] - n[0]*t[2],
        n[0]*t[1] - n[1]*t[0]
    ];

    return `matrix3d(
        ${t[0]}, ${t[1]}, ${t[2]}, 0,
        ${v[0]}, ${v[1]}, ${v[2]}, 0,
        ${n[0]}, ${n[1]}, ${n[2]}, 0,
        0, 0, 0, 1
    )`;
}

function getTextWidth(text, font) {
    const canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
    const context = canvas.getContext("2d");
    context.font = font;
    return context.measureText(text).width;
}

// Глобальні змінні для управління анімацією
let hoveredWord = null;
let mouseAuthors = { x: 0, y: 0, over: false };
let mouseTags = { x: 0, y: 0, over: false };

function createSphericalTextWord(
    word,
    centerPhi,
    centerTheta,
    sphereRadius,
    container,
    fontSize = 15,
    onClick,
    boostZ = 0
) {
    const font = `${fontSize}px Arial, sans-serif`;
    const letters = Array.from(word);
    const n = letters.length;
    const letterSpacingPx = fontSize * 0.19;
    const widths = letters.map(ch => getTextWidth(ch === ' ' ? '\u00A0' : ch, font));
    const totalWidth = widths.reduce((a, b) => a + b, 0) + letterSpacingPx * (n - 1);
    let offset = -totalWidth / 2;

    // Визначаємо чи під курсором саме це слово
    const isHovered = hoveredWord === word;
    const activeColor = isHovered ? '#ff4500' : '#ffa500';
    const activeFontSize = isHovered ? fontSize + 6 : fontSize;

    // Головний контейнер для літер
    const wordSpan = document.createElement('span');
    wordSpan.className = 'word tagcloud--item';
    wordSpan.style.position = 'absolute';
    wordSpan.style.fontSize = activeFontSize + 'px';
    wordSpan.style.left = '0';
    wordSpan.style.top = '0';
    wordSpan.style.display = 'inline-block';
    wordSpan.style.whiteSpace = 'nowrap';
    wordSpan.style.pointerEvents = 'none';
    wordSpan.style.width = totalWidth + 'px';
    wordSpan.style.height = (activeFontSize * 1.5) + 'px';
    wordSpan.style.transition = 'font-size 0.18s';

    // Генеруємо літери
    for (let i = 0; i < n; i++) {
        const char = letters[i];
        const w = widths[i];
        const frac = offset + w / 2;
        const arc = frac / sphereRadius;
        const phi = centerPhi;
        const theta = centerTheta - arc;
        const x = sphereRadius * Math.sin(phi) * Math.cos(theta);
        const y = sphereRadius * Math.cos(phi);
        const z = sphereRadius * Math.sin(phi) * Math.sin(theta) + boostZ;

        if (z < 0) { offset += w; if (i < n - 1) offset += letterSpacingPx; continue; }

        const matrix = lookAtWordLetter(x, y, z, theta);
        const letterSpan = document.createElement('span');
        letterSpan.className = 'letter';
        letterSpan.textContent = char === ' ' ? '\u00A0' : char;
        letterSpan.style.position = 'absolute';
        letterSpan.style.left = '0';
        letterSpan.style.top = '0';
        letterSpan.style.transform = `
            translate3d(${x + container.offsetWidth / 2}px, ${y + container.offsetHeight / 2}px, ${z}px)
            ${matrix}
            rotateZ(180deg)
        `;
        letterSpan.style.userSelect = 'none';
        letterSpan.style.pointerEvents = 'none';
        letterSpan.style.color = activeColor;
        letterSpan.style.transition = 'color 0.2s';

        wordSpan.appendChild(letterSpan);

        offset += w;
        if (i < n - 1) offset += letterSpacingPx;
    }

    // Прозора зона для кліку/hover (над словом)
    const clickArea = document.createElement('div');
    clickArea.className = 'word-click-area';
    clickArea.setAttribute('data-word', word);
    clickArea.style.position = 'absolute';
    clickArea.style.width = totalWidth + 'px';
    clickArea.style.height = (activeFontSize * 1.5) + 'px';
    clickArea.style.background = 'transparent';
    clickArea.style.pointerEvents = 'auto';
    clickArea.style.zIndex = '100';
    clickArea.style.left = '0';
    clickArea.style.top = '0';

    // Центр clickArea співпадає з центром слова
    const areaX = sphereRadius * Math.sin(centerPhi) * Math.cos(centerTheta);
    const areaY = sphereRadius * Math.cos(centerPhi);
    const areaZ = sphereRadius * Math.sin(centerPhi) * Math.sin(centerTheta) + boostZ;
    clickArea.style.transform = `
        translate3d(${areaX + container.offsetWidth / 2 - totalWidth / 2}px,
                    ${areaY + container.offsetHeight / 2 - activeFontSize / 2}px,
                    ${areaZ + 2}px)
    `;

    // Клік — лише для фільтрації
    clickArea.addEventListener('pointerdown', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (typeof onClick === 'function') {
            onClick(word);
        }
    });

    container.appendChild(wordSpan);
    container.appendChild(clickArea);
}

function createSphereWithSphericalWords(containerId, words, onClick, radius = 60, fontSize = 10, mouse) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.addEventListener('mousemove', (e) => {
        const rect = container.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
        mouse.over = true;
    });
    container.addEventListener('mouseleave', () => {
        mouse.over = false;
        hoveredWord = null;
        container.style.cursor = 'default'; // повернути курсор
    });

    const placed = [];
    function isTooClose(phi, theta, arcLength) {
        return placed.some(pos => {
            let dPhi = Math.abs(pos.phi - phi);
            let dTheta = Math.abs(pos.theta - theta);
            dTheta = Math.min(dTheta, 2 * Math.PI - dTheta);
            const minDist = (pos.arcLength + arcLength) * 0.7;
            return dPhi < minDist && dTheta < minDist;
        });
    }

    const items = [];
    for (const word of words) {
        const letterSpacing = fontSize * 0.25;
        const arcLength = (letterSpacing * word.length) / radius;
        let phi, theta, attempt = 0;
        const maxAttempts = 200;
        do {
            phi = Math.acos(2 * Math.random() - 1);
            theta = 2 * Math.PI * Math.random();
            attempt++;
        } while (isTooClose(phi, theta, arcLength) && attempt < maxAttempts);
        placed.push({ phi, theta, arcLength });
        items.push({ word, phi, theta });
    }

    let globalY = 0, globalX = 0;
    function animate() {
        setTimeout(() => { container.innerHTML = ''; }, 0);

        hoveredWord = null; // Скидаємо hover на початку кожного кадру

        globalY += 0.007;
        globalX += 0.005;

        const sinY = Math.sin(globalY), cosY = Math.cos(globalY);
        const sinX = Math.sin(globalX), cosX = Math.cos(globalX);

        let pointerIsSet = false;

        items.forEach(item => {
            let { word, phi, theta } = item;
            let y = radius * Math.cos(phi);
            let x = radius * Math.sin(phi) * Math.cos(theta);
            let z = radius * Math.sin(phi) * Math.sin(theta);

            // Обертання по X і Y
            let y1 = y * cosX - z * sinX;
            let z1 = y * sinX + z * cosX;
            let x1 = x;
            let x2 = x1 * cosY + z1 * sinY;
            let z2 = -x1 * sinY + z1 * cosY;
            let y2 = y1;

            // Координати центру слова
            let projectedX = x2 + container.offsetWidth / 2;
            let projectedY = y2 + container.offsetHeight / 2;
            let totalWidth = fontSize * 0.8 * word.length;
            let totalHeight = fontSize * 1.5;

            // Hover — перевіряємо попадання миші в зону слова
            if (
                mouse.over &&
                mouse.x >= projectedX - totalWidth / 2 &&
                mouse.x <= projectedX + totalWidth / 2 &&
                mouse.y >= projectedY - totalHeight / 2 &&
                mouse.y <= projectedY + totalHeight / 2
            ) {
                hoveredWord = word;
                pointerIsSet = true;
            }

            // Boost-ефект при наведенні
            let dist = mouse.over
                ? Math.sqrt((projectedX - mouse.x) ** 2 + (projectedY - mouse.y) ** 2)
                : 9999;
            let boostZ = 0, boostFont = 0;
            if (dist < 45) {
                let boost = 1 - (dist / 45);
                boostZ = 22 * boost;
                boostFont = 6 * boost;
            }

            createSphericalTextWord(
                word,
                Math.acos(y2 / radius),
                Math.atan2(z2, x2),
                radius,
                container,
                fontSize + boostFont,
                onClick,
                boostZ
            );
        });

        // Курсор pointer тільки якщо є hoveredWord
        container.style.cursor = pointerIsSet ? 'pointer' : 'default';

        requestAnimationFrame(animate);
    }
    animate();
}

function mainInit() {
    console.log('🚀 Ініціалізація додатку');

    const authorsData = getDataFromElement('author-data', 'data-authors');
    const tagsData = getDataFromElement('tag-data', 'data-tags');

    console.log(`📊 Завантажено ${authorsData.length} авторів та ${tagsData.length} тегів`);

    if (authorsData.length === 0 && tagsData.length === 0) {
        console.warn('⚠️ Немає даних для відображення!');
        return;
    }

    const authorWords = ['Всі автори', ...authorsData.map(a => a.name)];
    const tagWords = ['Всі теги', ...tagsData.map(t => t.name)];

    // Відновлюємо activeWord
    const params = new URLSearchParams(window.location.search);
    const authorId = params.get('author');
    const tagId = params.get('tag');

    if (authorId) {
        const author = authorsData.find(a => String(a.id) === String(authorId));
        if (author) {
            activeWord = { type: 'author', word: author.name };
            console.log(`🔍 Активний автор: ${author.name}`);
        }
    } else if (tagId) {
        const tag = tagsData.find(t => String(t.id) === String(tagId));
        if (tag) {
            activeWord = { type: 'tag', word: tag.name };
            console.log(`🔍 Активний тег: ${tag.name}`);
        }
    } else {
        activeWord = null;
        console.log('🔍 Фільтри не активні');
    }

    // Створюємо сфери
    createSphereWithSphericalWords(
        'author-container',
        authorWords,
        word => { filterByWord(word, 'author'); },
        60, 10, mouseAuthors
    );

    createSphereWithSphericalWords(
        'tag-container',
        tagWords,
        word => { filterByWord(word, 'tag'); },
        60, 10, mouseTags
    );

    initSearchToggle();
    console.log('✅ Ініціалізація завершена');
}

// Скидання при завантаженні
window.addEventListener('load', () => {
    isFilterInProgress = false;
});

// Глобальний обробник для дебагу
document.addEventListener('click', (e) => {
    console.log(`🌐 Глобальний клік: ${e.target.tagName}.${e.target.className}`);
});

if (typeof window !== 'undefined' && !window.__TESTING__) {
    document.addEventListener('DOMContentLoaded', mainInit);
}