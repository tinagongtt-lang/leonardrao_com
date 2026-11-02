(function () {
    const boardEl = document.getElementById('board');
    const statusEl = document.getElementById('status');
    const timerEl = document.getElementById('timer');
    const HOLES = { easy: 35, medium: 45, hard: 55 };

    let solution, puzzle, givens, sel = null, timer = null, seconds = 0, done = false;

    function emptyGrid() {
        return Array.from({ length: 9 }, () => Array(9).fill(0));
    }

    function valid(g, r, c, n) {
        for (let i = 0; i < 9; i++) {
            if (g[r][i] === n || g[i][c] === n) return false;
        }
        const br = r - r % 3, bc = c - c % 3;
        for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
            if (g[br + i][bc + j] === n) return false;
        }
        return true;
    }

    function fill(g) {
        for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) {
            if (!g[r][c]) {
                const nums = [1, 2, 3, 4, 5, 6, 7, 8, 9].sort(() => Math.random() - 0.5);
                for (const n of nums) {
                    if (valid(g, r, c, n)) {
                        g[r][c] = n;
                        if (fill(g)) return true;
                        g[r][c] = 0;
                    }
                }
                return false;
            }
        }
        return true;
    }

    function genPuzzle() {
        solution = emptyGrid();
        fill(solution);
        puzzle = solution.map(row => row.slice());
        let holes = HOLES[document.getElementById('difficulty').value];
        const pos = Array.from({ length: 81 }, (_, i) => i).sort(() => Math.random() - 0.5);
        for (const p of pos) {
            if (!holes) break;
            puzzle[Math.floor(p / 9)][p % 9] = 0;
            holes--;
        }
        givens = puzzle.map(row => row.map(v => v !== 0));
    }

    function render() {
        boardEl.innerHTML = '';
        for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) {
            const cell = document.createElement('div');
            const isSel = sel && sel[0] === r && sel[1] === c;
            const v = puzzle[r][c];
            let cls = 'w-9 h-9 sm:w-11 sm:h-11 flex items-center justify-center text-lg cursor-pointer bg-white dark:bg-slate-800 ';
            if ((c + 1) % 3 === 0 && c < 8) cls += 'mr-1 ';
            if ((r + 1) % 3 === 0 && r < 8) cls += 'mb-1 ';
            if (isSel) {
                cls += '!bg-sky-200 dark:!bg-sky-700 ';
            } else if (sel && (r === sel[0] || c === sel[1] ||
                    (Math.floor(r / 3) === Math.floor(sel[0] / 3) && Math.floor(c / 3) === Math.floor(sel[1] / 3)))) {
                cls += '!bg-sky-50 dark:!bg-slate-700 ';
            }
            if (givens[r][c]) {
                cls += 'font-bold text-slate-900 dark:text-slate-100 ';
            } else if (v) {
                cls += v === solution[r][c] ? 'text-sky-600 dark:text-sky-400 ' : 'text-red-500 ';
            }
            cell.className = cls;
            cell.textContent = v || '';
            cell.dataset.r = r;
            cell.dataset.c = c;
            cell.addEventListener('click', () => {
                if (done) return;
                sel = [r, c];
                render();
            });
            boardEl.appendChild(cell);
        }
    }

    function enter(n) {
        if (!sel || done || givens[sel[0]][sel[1]]) return;
        puzzle[sel[0]][sel[1]] = n;
        render();
        checkWin();
    }

    function checkWin() {
        for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) {
            if (puzzle[r][c] !== solution[r][c]) return;
        }
        done = true;
        clearInterval(timer);
        statusEl.textContent = '完成！用时 ' + timerEl.textContent;
        statusEl.classList.add('text-emerald-600');
    }

    function tick() {
        seconds++;
        timerEl.textContent = String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
    }

    function start() {
        done = false;
        sel = null;
        seconds = 0;
        timerEl.textContent = '00:00';
        statusEl.textContent = '';
        statusEl.classList.remove('text-emerald-600');
        clearInterval(timer);
        timer = setInterval(tick, 1000);
        genPuzzle();
        render();
    }

    document.querySelectorAll('.num-btn').forEach(b => {
        b.addEventListener('click', () => enter(parseInt(b.dataset.num)));
    });
    document.getElementById('erase').addEventListener('click', () => enter(0));
    document.getElementById('restart').addEventListener('click', start);
    document.getElementById('difficulty').addEventListener('change', start);
    document.addEventListener('keydown', e => {
        if (e.key >= '1' && e.key <= '9') enter(parseInt(e.key));
        else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') enter(0);
    });

    start();
})();
