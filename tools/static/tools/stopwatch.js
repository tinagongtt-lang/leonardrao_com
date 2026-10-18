document.addEventListener('DOMContentLoaded', () => {
    const display = document.getElementById('display');
    const startBtn = document.getElementById('start');
    const stopBtn = document.getElementById('stop');
    const lapBtn = document.getElementById('lap');
    const resetBtn = document.getElementById('reset');
    const lapsEl = document.getElementById('laps');

    let startTime = 0;
    let elapsed = 0;
    let interval = null;
    let running = false;
    let lapCount = 0;

    function pad(n, len = 2) {
        return n.toString().padStart(len, '0');
    }

    function format(ms) {
        const total = Math.floor(ms / 10);
        const m = Math.floor(total / 6000);
        const s = Math.floor((total % 6000) / 100);
        const cs = total % 100;
        return `${pad(m)}:${pad(s)}.${pad(cs)}`;
    }

    function update() {
        const now = Date.now();
        elapsed = now - startTime;
        display.textContent = format(elapsed);
    }

    function start() {
        if (running) return;
        startTime = Date.now() - elapsed;
        interval = setInterval(update, 10);
        running = true;
    }

    function stop() {
        if (!running) return;
        clearInterval(interval);
        running = false;
    }

    function lap() {
        if (elapsed === 0) return;
        lapCount++;
        const row = document.createElement('div');
        row.className = 'flex justify-between px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded';
        const prefix = lapsEl.dataset.lap || 'Lap #';
        row.innerHTML = `<span>${prefix}${lapCount}</span><span>${format(elapsed)}</span>`;
        lapsEl.prepend(row);
    }

    function reset() {
        stop();
        elapsed = 0;
        display.textContent = '00:00.00';
        lapsEl.innerHTML = '';
        lapCount = 0;
    }

    startBtn.addEventListener('click', start);
    stopBtn.addEventListener('click', stop);
    lapBtn.addEventListener('click', lap);
    resetBtn.addEventListener('click', reset);
});
