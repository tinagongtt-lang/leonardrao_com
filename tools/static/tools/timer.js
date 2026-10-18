document.addEventListener('DOMContentLoaded', () => {
    const minutesInput = document.getElementById('minutes');
    const secondsInput = document.getElementById('seconds');
    const display = document.getElementById('display');
    const startBtn = document.getElementById('start');
    const pauseBtn = document.getElementById('pause');
    const resetBtn = document.getElementById('reset');
    const msgs = document.getElementById('timer-msgs');
    const doneText = msgs ? msgs.dataset.done : "Time's up!";

    let totalSeconds = 0;
    let remaining = 0;
    let interval = null;
    let running = false;

    function pad(n) {
        return n.toString().padStart(2, '0');
    }

    function updateDisplay() {
        const m = Math.floor(remaining / 60);
        const s = remaining % 60;
        display.textContent = `${pad(m)}:${pad(s)}`;
    }

    function getInputSeconds() {
        const m = parseInt(minutesInput.value, 10) || 0;
        const s = parseInt(secondsInput.value, 10) || 0;
        return m * 60 + s;
    }

    function start() {
        if (running) return;
        if (remaining <= 0) {
            remaining = getInputSeconds();
        }
        if (remaining <= 0) return;
        running = true;
        minutesInput.disabled = true;
        secondsInput.disabled = true;
        interval = setInterval(() => {
            remaining--;
            updateDisplay();
            if (remaining <= 0) {
                pause();
                display.textContent = '00:00';
                alert(doneText);
            }
        }, 1000);
    }

    function pause() {
        running = false;
        clearInterval(interval);
        interval = null;
    }

    function reset() {
        pause();
        remaining = getInputSeconds();
        updateDisplay();
        minutesInput.disabled = false;
        secondsInput.disabled = false;
    }

    [minutesInput, secondsInput].forEach(input => input.addEventListener('input', () => {
        if (!running) {
            remaining = getInputSeconds();
            updateDisplay();
        }
    }));

    startBtn.addEventListener('click', start);
    pauseBtn.addEventListener('click', pause);
    resetBtn.addEventListener('click', reset);

    reset();
});
