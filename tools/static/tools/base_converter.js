document.addEventListener('DOMContentLoaded', () => {
    const inputEl = document.getElementById('input');
    const fromBaseEl = document.getElementById('fromBase');
    const toBaseEl = document.getElementById('toBase');
    const convertBtn = document.getElementById('convert');
    const resultEl = document.getElementById('result');
    const errorText = resultEl.dataset.error || 'Invalid input format';

    function convert() {
        const value = inputEl.value.trim();
        const fromBase = parseInt(fromBaseEl.value, 10);
        const toBase = parseInt(toBaseEl.value, 10);

        if (!value) {
            resultEl.textContent = '-';
            return;
        }

        try {
            const decimal = BigInt(parseInt(value, fromBase));
            if (isNaN(Number(decimal))) throw new Error('Invalid number');
            resultEl.textContent = decimal.toString(toBase).toUpperCase();
        } catch (e) {
            resultEl.textContent = errorText;
        }
    }

    convertBtn.addEventListener('click', convert);
    inputEl.addEventListener('keydown', e => {
        if (e.key === 'Enter') convert();
    });
});
