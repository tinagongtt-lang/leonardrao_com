(function () {
    'use strict';

    var app = document.getElementById('gomoku-app');
    if (!app) return;

    var code = app.dataset.code;
    var boardEl = document.getElementById('gomoku-board');
    var statusEl = document.getElementById('gomoku-status');

    var state = null;
    var ws = null;

    var SVGNS = 'http://www.w3.org/2000/svg';
    var U = 36;
    var PAD = 30;

    function connect() {
        var proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
        ws = new WebSocket(proto + location.host + '/ws/gomoku/' + code + '/');

        ws.onmessage = function (e) {
            var msg = JSON.parse(e.data);
            if (msg.type === 'state' || msg.type === 'error') {
                if (msg.type === 'error') statusEl.textContent = msg.error;
                state = msg.state;
                render();
            }
        };
        ws.onclose = function () {
            setTimeout(connect, 2000);
        };
    }

    function render() {
        var size = state ? state.size : 15;
        var board = state ? state.board : '.'.repeat(size * size);
        var w = (size - 1) * U + 2 * PAD;
        var flipped = state && state.color === 'white';

        boardEl.innerHTML = '';
        var svg = document.createElementNS(SVGNS, 'svg');
        svg.setAttribute('viewBox', '0 0 ' + w + ' ' + w);
        svg.setAttribute('class', 'w-full h-auto rounded-xl shadow-2xl bg-amber-200 dark:bg-amber-300');

        for (var i = 0; i < size; i++) {
            var p = PAD + i * U;
            line(svg, PAD, p, PAD + (size - 1) * U, p);
            line(svg, p, PAD, p, PAD + (size - 1) * U);
        }
        // star points
        [3, 7, 11].forEach(function (sx) {
            [3, 7, 11].forEach(function (sy) {
                var c = document.createElementNS(SVGNS, 'circle');
                var px = flipped ? PAD + (size - 1 - sx) * U : PAD + sx * U;
                c.setAttribute('cx', px);
                c.setAttribute('cy', PAD + sy * U);
                c.setAttribute('r', U * 0.09);
                c.setAttribute('fill', '#78350f');
                svg.appendChild(c);
            });
        });

        if (state && state.last_move && state.last_move !== 'pass') {
            var lm = state.last_move.split(',');
            mark(svg, parseInt(lm[0], 10), parseInt(lm[1], 10), size, flipped);
        }

        for (var y = 0; y < size; y++) {
            for (var x = 0; x < size; x++) {
                var v = board[y * size + x];
                var dX = flipped ? size - 1 - x : x;
                var cx = PAD + dX * U;
                var cy = PAD + y * U;
                if (v === 'b' || v === 'w') {
                    var c2 = document.createElementNS(SVGNS, 'circle');
                    c2.setAttribute('cx', cx); c2.setAttribute('cy', cy);
                    c2.setAttribute('r', U * 0.46);
                    c2.setAttribute('fill', v === 'b' ? '#0f172a' : '#f8fafc');
                    c2.setAttribute('stroke', v === 'b' ? '#334155' : '#64748b');
                    c2.setAttribute('stroke-width', '1.5');
                    c2.setAttribute('pointer-events', 'none');
                    svg.appendChild(c2);
                }
                var hit = document.createElementNS(SVGNS, 'circle');
                hit.setAttribute('cx', cx); hit.setAttribute('cy', cy);
                hit.setAttribute('r', U * 0.48);
                hit.setAttribute('fill', 'transparent');
                hit.setAttribute('cursor', 'pointer');
                hit.dataset.x = x; hit.dataset.y = y;
                hit.addEventListener('click', onPointClick);
                svg.appendChild(hit);
            }
        }

        boardEl.appendChild(svg);
        updateStatus();
    }

    function line(svg, x1, y1, x2, y2) {
        var l = document.createElementNS(SVGNS, 'line');
        l.setAttribute('x1', x1); l.setAttribute('y1', y1);
        l.setAttribute('x2', x2); l.setAttribute('y2', y2);
        l.setAttribute('stroke', '#78350f');
        l.setAttribute('stroke-width', '1.5');
        svg.appendChild(l);
    }

    function mark(svg, x, y, size, flipped) {
        var cx = PAD + (flipped ? size - 1 - x : x) * U;
        var cy = PAD + y * U;
        var c = document.createElementNS(SVGNS, 'circle');
        c.setAttribute('cx', cx); c.setAttribute('cy', cy);
        c.setAttribute('r', U * 0.16);
        c.setAttribute('fill', 'none');
        c.setAttribute('stroke', '#f97316');
        c.setAttribute('stroke-width', '3');
        svg.appendChild(c);
    }

    function updateStatus() {
        if (!state) return;
        var d = app.dataset;
        var text = '';
        if (state.status === 'waiting') text = d.statusWaiting;
        else if (state.status === 'finished') {
            if (state.result === 'draw') text = d.statusDraw;
            else text = state.result === 'black' ? d.statusWinBlack : d.statusWinWhite;
        } else if (state.color === 'spectator') {
            text = d.statusSpectator + ' · ' + (state.turn === 'black' ? d.labelBlack : d.labelWhite);
        } else if (state.turn === state.color) {
            text = d.statusYourTurn;
        } else {
            text = d.statusTheirTurn;
        }
        var role = state.color === 'spectator' ? '' :
            '（' + (state.color === 'black' ? d.labelBlack : d.labelWhite) + '）';
        statusEl.textContent = text + role;
        var canAct = state.status === 'playing' &&
            (state.color === 'black' || state.color === 'white') && state.turn === state.color;
        var btn = document.getElementById('gomoku-resign');
        if (btn) {
            btn.disabled = !canAct;
            btn.classList.toggle('opacity-50', !canAct);
            btn.classList.toggle('cursor-not-allowed', !canAct);
        }
    }

    function onPointClick(e) {
        if (!state || state.status !== 'playing') return;
        if (state.color !== 'black' && state.color !== 'white') return;
        if (state.turn !== state.color) return;
        var x = parseInt(e.currentTarget.dataset.x, 10);
        var y = parseInt(e.currentTarget.dataset.y, 10);
        ws.send(JSON.stringify({ type: 'move', move: x + ',' + y }));
    }

    var resignBtn = document.getElementById('gomoku-resign');
    if (resignBtn) resignBtn.addEventListener('click', function () {
        ws.send(JSON.stringify({ type: 'move', move: 'resign' }));
    });

    var shareInput = document.getElementById('share-url');
    if (shareInput) {
        shareInput.addEventListener('click', function () { this.select(); });
    }

    connect();
    render();
})();
