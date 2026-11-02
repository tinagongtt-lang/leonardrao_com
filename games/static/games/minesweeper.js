(function () {
    const boardEl = document.getElementById('board');
    const statusEl = document.getElementById('status');
    const timerEl = document.getElementById('timer');
    const leftEl = document.getElementById('mines-left');

    const LEVELS = { easy: [9, 9, 10], medium: [16, 16, 40], hard: [30, 16, 99] };
    const COLORS = ['', 'text-blue-600', 'text-emerald-600', 'text-red-500', 'text-indigo-600',
                    'text-orange-600', 'text-cyan-600', 'text-fuchsia-600', 'text-slate-600'];

    let W, H, M, mines, revealed, flagged, started, over, seconds, timer;

    function neighbors(i) {
        const r = Math.floor(i / W), c = i % W, out = [];
        for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
            if (!dr && !dc) continue;
            const nr = r + dr, nc = c + dc;
            if (nr >= 0 && nr < H && nc >= 0 && nc < W) out.push(nr * W + nc);
        }
        return out;
    }

    function placeMines(safe) {
        mines = new Array(W * H).fill(false);
        const forbidden = new Set([safe, ...neighbors(safe)]);
        const cells = [];
        for (let i = 0; i < W * H; i++) if (!forbidden.has(i)) cells.push(i);
        for (let n = 0; n < M; n++) {
            const j = Math.floor(Math.random() * cells.length);
            mines[cells.splice(j, 1)[0]] = true;
        }
    }

    function count(i) {
        return neighbors(i).filter(n => mines[n]).length;
    }

    function reveal(i) {
        if (revealed[i] || flagged[i] || over) return;
        revealed[i] = true;
        if (mines[i]) { lose(i); return; }
        if (count(i) === 0) neighbors(i).forEach(reveal);
    }

    function lose(hit) {
        over = true;
        clearInterval(timer);
        mines.forEach((m, i) => { if (m) revealed[i] = true; });
        statusEl.textContent = '踩到雷了，再来一局吧';
        statusEl.className = 'mt-6 text-lg font-semibold text-red-500';
        render(hit);
    }

    function checkWin() {
        if (revealed.filter(Boolean).length === W * H - M) {
            over = true;
            clearInterval(timer);
            statusEl.textContent = '全部排完，用时 ' + seconds + ' 秒';
            statusEl.className = 'mt-6 text-lg font-semibold text-emerald-600';
        }
    }

    function render(hit) {
        boardEl.style.gridTemplateColumns = `repeat(${W}, minmax(0, 1fr))`;
        boardEl.style.width = W * 26 + 'px';
        boardEl.innerHTML = '';
        for (let i = 0; i < W * H; i++) {
            const cell = document.createElement('div');
            let cls = 'w-[26px] h-[26px] flex items-center justify-center text-sm font-bold cursor-pointer ';
            if (revealed[i]) {
                cls += 'bg-slate-100 dark:bg-slate-800 ';
                if (mines[i]) {
                    cell.textContent = '💣';
                    if (i === hit) cls += '!bg-red-400 ';
                } else {
                    const n = count(i);
                    cell.textContent = n || '';
                    cell.className = cls + COLORS[n];
                    boardEl.appendChild(cell);
                    continue;
                }
            } else {
                cls += 'bg-slate-400 dark:bg-slate-600 hover:bg-slate-350 ';
                if (flagged[i]) cell.textContent = '🚩';
            }
            cell.className = cls;
            cell.dataset.i = i;
            cell.addEventListener('click', () => {
                if (over) return;
                if (!started) { placeMines(i); started = true; timer = setInterval(() => timerEl.textContent = ++seconds, 1000); }
                reveal(i);
                if (!over) checkWin();
                render();
            });
            cell.addEventListener('contextmenu', e => {
                e.preventDefault();
                if (over || revealed[i]) return;
                flagged[i] = !flagged[i];
                leftEl.textContent = M - flagged.filter(Boolean).length;
                render();
            });
            boardEl.appendChild(cell);
        }
    }

    function start() {
        [W, H, M] = LEVELS[document.getElementById('level').value];
        revealed = new Array(W * H).fill(false);
        flagged = new Array(W * H).fill(false);
        mines = new Array(W * H).fill(false);
        started = over = false;
        seconds = 0;
        timerEl.textContent = '0';
        leftEl.textContent = M;
        statusEl.textContent = '';
        clearInterval(timer);
        render();
    }

    document.getElementById('restart').addEventListener('click', start);
    document.getElementById('level').addEventListener('change', start);
    start();
})();
