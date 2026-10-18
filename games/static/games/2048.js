document.addEventListener('DOMContentLoaded', () => {
    const boardEl = document.getElementById('board');
    const scoreEl = document.getElementById('score');
    const messageEl = document.getElementById('message');
    const restartBtn = document.getElementById('restart');
    const cells = Array.from(boardEl.children);

    let board = [];
    let score = 0;
    let playing = true;

    const colors = {
        0: 'bg-slate-800 text-slate-800',
        2: 'bg-slate-600 text-white',
        4: 'bg-slate-500 text-white',
        8: 'bg-amber-500 text-white',
        16: 'bg-amber-600 text-white',
        32: 'bg-orange-500 text-white',
        64: 'bg-orange-600 text-white',
        128: 'bg-yellow-400 text-slate-900',
        256: 'bg-yellow-500 text-slate-900',
        512: 'bg-lime-500 text-slate-900',
        1024: 'bg-green-500 text-white',
        2048: 'bg-sky-500 text-white',
    };

    function init() {
        board = Array(16).fill(0);
        score = 0;
        playing = true;
        messageEl.textContent = '';
        addRandomTile();
        addRandomTile();
        render();
    }

    function addRandomTile() {
        const empty = board.map((v, i) => v === 0 ? i : null).filter(i => i !== null);
        if (empty.length === 0) return;
        const idx = empty[Math.floor(Math.random() * empty.length)];
        board[idx] = Math.random() < 0.9 ? 2 : 4;
    }

    function render() {
        scoreEl.textContent = score;
        cells.forEach((cell, i) => {
            const value = board[i];
            cell.textContent = value || '';
            cell.className = `cell w-14 h-14 sm:w-20 sm:h-20 rounded-lg flex items-center justify-center text-base sm:text-xl md:text-2xl font-bold transition ${colors[value] || 'bg-rose-500 text-white'}`;
        });
    }

    function slideRow(row) {
        let arr = row.filter(v => v);
        for (let i = 0; i < arr.length - 1; i++) {
            if (arr[i] === arr[i + 1]) {
                arr[i] *= 2;
                score += arr[i];
                arr[i + 1] = 0;
            }
        }
        arr = arr.filter(v => v);
        while (arr.length < 4) arr.push(0);
        return arr;
    }

    function getRows() {
        const rows = [];
        for (let r = 0; r < 4; r++) rows.push(board.slice(r * 4, r * 4 + 4));
        return rows;
    }

    function setRows(rows) {
        board = rows.flat();
    }

    function getCols() {
        const cols = [];
        for (let c = 0; c < 4; c++) cols.push([0, 1, 2, 3].map(r => board[r * 4 + c]));
        return cols;
    }

    function setCols(cols) {
        board = Array(16).fill(0);
        cols.forEach((col, c) => col.forEach((v, r) => board[r * 4 + c] = v));
    }

    function boardsEqual(a, b) {
        return a.every((v, i) => v === b[i]);
    }

    function moveLeft() {
        const before = board.slice();
        setRows(getRows().map(slideRow));
        return !boardsEqual(before, board);
    }

    function moveRight() {
        const before = board.slice();
        setRows(getRows().map(r => slideRow(r.reverse()).reverse()));
        return !boardsEqual(before, board);
    }

    function moveUp() {
        const before = board.slice();
        setCols(getCols().map(slideRow));
        return !boardsEqual(before, board);
    }

    function moveDown() {
        const before = board.slice();
        setCols(getCols().map(c => slideRow(c.reverse()).reverse()));
        return !boardsEqual(before, board);
    }

    function hasEmpty() {
        return board.some(v => v === 0);
    }

    function canMerge() {
        for (let r = 0; r < 4; r++) {
            for (let c = 0; c < 4; c++) {
                const i = r * 4 + c;
                if (c < 3 && board[i] === board[i + 1]) return true;
                if (r < 3 && board[i] === board[i + 4]) return true;
            }
        }
        return false;
    }

    function checkStatus() {
        if (board.includes(2048)) {
            playing = false;
            messageEl.textContent = messageEl.dataset.win || 'You reached 2048!';
            return;
        }
        if (!hasEmpty() && !canMerge()) {
            playing = false;
            messageEl.textContent = messageEl.dataset.lose || 'Game over, click restart';
        }
    }

    function handleMove(direction) {
        if (!playing) return;
        let moved = false;
        if (direction === 'left') moved = moveLeft();
        else if (direction === 'right') moved = moveRight();
        else if (direction === 'up') moved = moveUp();
        else if (direction === 'down') moved = moveDown();
        if (moved) {
            addRandomTile();
            render();
            checkStatus();
        }
    }

    document.addEventListener('keydown', e => {
        if (['ArrowLeft', 'a', 'A'].includes(e.key)) { e.preventDefault(); handleMove('left'); }
        else if (['ArrowRight', 'd', 'D'].includes(e.key)) { e.preventDefault(); handleMove('right'); }
        else if (['ArrowUp', 'w', 'W'].includes(e.key)) { e.preventDefault(); handleMove('up'); }
        else if (['ArrowDown', 's', 'S'].includes(e.key)) { e.preventDefault(); handleMove('down'); }
    });

    let touchStartX = 0, touchStartY = 0;
    boardEl.addEventListener('touchstart', e => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }, { passive: true });
    boardEl.addEventListener('touchend', e => {
        const dx = e.changedTouches[0].clientX - touchStartX;
        const dy = e.changedTouches[0].clientY - touchStartY;
        if (Math.max(Math.abs(dx), Math.abs(dy)) < 30) return;
        if (Math.abs(dx) > Math.abs(dy)) handleMove(dx > 0 ? 'right' : 'left');
        else handleMove(dy > 0 ? 'down' : 'up');
    }, { passive: true });

    restartBtn.addEventListener('click', init);

    init();
});
