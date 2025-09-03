function handleSliderInput(slider, output) {
    output.innerHTML = slider.value + ' px';
}

function sliderInputEventHandler(slider, output) {
    return function () {
        handleSliderInput(slider, output);
    };
}

function initSettingsForm() {
    let slider = document.getElementById('id_font_size');
    let output = document.getElementById('font-size-display');
    if (!slider || !output) return;
    output.innerHTML = slider.value + ' px';
    slider.addEventListener('input', function() {
        output.innerHTML = slider.value + ' px';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initSettingsForm();
});

// Для можливості тестування
function registerDOMContentLoaded() {
    if (typeof window !== 'undefined') {
        document.addEventListener('DOMContentLoaded', initSettingsForm);
    }
}

module.exports = {
    initSettingsForm,
    handleSliderInput,
    sliderInputEventHandler,
    registerDOMContentLoaded
};

if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    registerDOMContentLoaded();
}