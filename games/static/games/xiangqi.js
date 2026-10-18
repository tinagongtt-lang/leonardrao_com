(function () {
    'use strict';

    var app = document.getElementById('xiangqi-app');
    if (!app) return;

    var code = app.dataset.code;
    var boardEl = document.getElementById('xiangqi-board');
    var statusEl = document.getElementById('xiangqi-status');

    var state = null;
    var selected = null;
    var ws = null;

    var CHARS = {
        k: '将', a: '士', b: '象', n: '馬', r: '車', c: '砲', p: '卒',
        K: '帅', A: '仕', B: '相', N: '马', R: '车', C: '炮', P: '兵'
    };

    var U = 50;          // cell unit in px
    var PAD = 40;        // padding around board
    var W = 8 * U + 2 * PAD;
    var H = 9 * U + 2 * PAD;

    var SVGNS = 'http://www.w3.org/2000/svg';

    function sq(file, rank) {
        return String.fromCharCode(97 + file) + rank;
    }

    // file 0..8 -> x, rank 0..9 -> y (rank 0 = red home, drawn at bottom)
    function xy(file, rank, flipped) {
        var x = flipped ? 8 - file : file;
        var y = flipped ? rank : 9 - rank;
        return [PAD + x * U, PAD + y * U];
    }

    function connect() {
        var proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
        ws = new WebSocket(proto + location.host + '/ws/xiangqi/' + code + '/');

        ws.onmessage = function (e) {
            var msg = JSON.parse(e.data);
            if (msg.type === 'state') {
                state = msg.state;
                render();
            } else if (msg.type === 'error') {
                state = msg.state;
                statusEl.textContent = msg.error;
                render();
            }
        };
        ws.onclose = function () {
            setTimeout(connect, 2000);
        };
    }

    function legalDests(from) {
        if (!state || !state.legal_moves) return {};
        var dests = {};
        state.legal_moves.forEach(function (m) {
            if (m.slice(0, 2) === from) dests[m.slice(2, 4)] = true;
        });
        return dests;
    }

    function line(svg, x1, y1, x2, y2) {
        var l = document.createElementNS(SVGNS, 'line');
        l.setAttribute('x1', x1); l.setAttribute('y1', y1);
        l.setAttribute('x2', x2); l.setAttribute('y2', y2);
        l.setAttribute('stroke', '#78350f');
        l.setAttribute('stroke-width', '1.5');
        svg.appendChild(l);
    }

    function drawBoard(svg) {
        var x0 = PAD, y0 = PAD, x1 = PAD + 8 * U, y1 = PAD + 9 * U;
        var midY1 = PAD + 4 * U, midY2 = PAD + 5 * U;

        // horizontal lines
        for (var y = 0; y <= 9; y++) {
            line(svg, x0, PAD + y * U, x1, PAD + y * U);
        }
        // vertical lines: full for edge files, split at river for inner
        for (var x = 0; x <= 8; x++) {
            var px = PAD + x * U;
            if (x === 0 || x === 8) {
                line(svg, px, y0, px, y1);
            } else {
                line(svg, px, y0, px, midY1);
                line(svg, px, midY2, px, y1);
            }
        }
        // palace diagonals: black palace (files 3-5, ranks 7-9 top), red (ranks 0-2 bottom)
        line(svg, PAD + 3 * U, y0, PAD + 5 * U, y0 + 2 * U);
        line(svg, PAD + 5 * U, y0, PAD + 3 * U, y0 + 2 * U);
        line(svg, PAD + 3 * U, y1 - 2 * U, PAD + 5 * U, y1);
        line(svg, PAD + 5 * U, y1 - 2 * U, PAD + 3 * U, y1);

        // river text
        var t1 = document.createElementNS(SVGNS, 'text');
        t1.setAttribute('x', PAD + 2 * U);
        t1.setAttribute('y', PAD + 4.5 * U + 8);
        t1.setAttribute('text-anchor', 'middle');
        t1.setAttribute('font-size', '26');
        t1.setAttribute('fill', '#78350f');
        t1.setAttribute('font-family', 'KaiTi, STKaiti, serif');
        t1.textContent = '楚 河';
        svg.appendChild(t1);
        var t2 = document.createElementNS(SVGNS, 'text');
        t2.setAttribute('x', PAD + 6 * U);
        t2.setAttribute('y', PAD + 4.5 * U + 8);
        t2.setAttribute('text-anchor', 'middle');
        t2.setAttribute('font-size', '26');
        t2.setAttribute('fill', '#78350f');
        t2.setAttribute('font-family', 'KaiTi, STKaiti, serif');
        t2.textContent = '漢 界';
        svg.appendChild(t2);
    }

    function render() {
        var fen = state ? state.fen : '9/9/9/9/9/9/9/9/9/9 w';
        var rows = fen.split(' ')[0].split('/');
        var flipped = state && state.color === 'black';
        var dests = selected ? legalDests(selected) : {};

        var pieces = {};
        for (var ri = 0; ri < rows.length && ri < 10; ri++) {
            var row = rows[ri];
            var f = 0;
            for (var ci = 0; ci < row.length; ci++) {
                var ch = row[ci];
                if (/\d/.test(ch)) { f += parseInt(ch, 10); continue; }
                pieces[sq(f, 9 - ri)] = ch;
                f += 1;
            }
        }

        boardEl.innerHTML = '';
        var svg = document.createElementNS(SVGNS, 'svg');
        svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
        svg.setAttribute('class', 'w-full h-auto rounded-xl shadow-2xl bg-amber-100 dark:bg-amber-200');
        drawBoard(svg);

        // highlights
        function halo(square, color, width) {
            var file = square.charCodeAt(0) - 97;
            var rank = parseInt(square[1], 10);
            var p = xy(file, rank, flipped);
            var c = document.createElementNS(SVGNS, 'circle');
            c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]);
            c.setAttribute('r', U * 0.46);
            c.setAttribute('fill', 'none');
            c.setAttribute('stroke', color);
            c.setAttribute('stroke-width', width || 3);
            svg.appendChild(c);
        }
        if (state && state.last_move) {
            halo(state.last_move.slice(0, 2), '#f59e0b');
            halo(state.last_move.slice(2, 4), '#f59e0b');
        }
        if (selected) halo(selected, '#0ea5e9');
        Object.keys(dests).forEach(function (d) { halo(d, '#10b981', 2); });

        // pieces + click targets
        for (var file = 0; file < 9; file++) {
            for (var rank = 0; rank < 10; rank++) {
                var square = sq(file, rank);
                var p = xy(file, rank, flipped);
                var hit = document.createElementNS(SVGNS, 'circle');
                hit.setAttribute('cx', p[0]); hit.setAttribute('cy', p[1]);
                hit.setAttribute('r', U * 0.48);
                hit.setAttribute('fill', 'transparent');
                hit.setAttribute('cursor', 'pointer');
                hit.dataset.square = square;
                hit.addEventListener('click', onCellClick);
                svg.appendChild(hit);

                var pc = pieces[square];
                if (pc) {
                    var g = document.createElementNS(SVGNS, 'g');
                    g.setAttribute('pointer-events', 'none');
                    var c = document.createElementNS(SVGNS, 'circle');
                    c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]);
                    c.setAttribute('r', U * 0.42);
                    c.setAttribute('fill', '#fef3c7');
                    c.setAttribute('stroke', /[A-Z]/.test(pc) ? '#b91c1c' : '#1e293b');
                    c.setAttribute('stroke-width', '2');
                    g.appendChild(c);
                    var t = document.createElementNS(SVGNS, 'text');
                    t.setAttribute('x', p[0]); t.setAttribute('y', p[1] + 1);
                    t.setAttribute('text-anchor', 'middle');
                    t.setAttribute('dominant-baseline', 'central');
                    t.setAttribute('font-size', U * 0.52);
                    t.setAttribute('font-weight', 'bold');
                    t.setAttribute('fill', /[A-Z]/.test(pc) ? '#b91c1c' : '#1e293b');
                    t.setAttribute('font-family', 'KaiTi, STKaiti, serif');
                    t.textContent = CHARS[pc] || pc;
                    g.appendChild(t);
                    svg.appendChild(g);
                }
            }
        }

        boardEl.appendChild(svg);
        updateStatus();
    }

    function updateStatus() {
        if (!state) return;
        var d = app.dataset;
        var text = '';
        if (state.status === 'waiting') text = d.statusWaiting;
        else if (state.status === 'finished') {
            if (state.result === 'red') text = d.statusWinRed;
            else text = d.statusWinBlack;
        } else if (state.color === 'spectator') {
            text = d.statusSpectator + ' · ' + (state.turn === 'red' ? d.labelRed : d.labelBlack);
        } else if (state.turn === state.color) {
            text = d.statusYourTurn + (state.check ? ' · ' + d.statusCheck : '');
        } else {
            text = d.statusTheirTurn + (state.check ? ' · ' + d.statusCheck : '');
        }
        var role = state.color === 'spectator' ? '' :
            '（' + (state.color === 'red' ? d.labelRed : d.labelBlack) + '）';
        statusEl.textContent = text + role;
    }

    function onCellClick(e) {
        if (!state || state.status !== 'playing') return;
        if (state.color !== 'red' && state.color !== 'black') return;
        if (state.turn !== state.color) return;
        var square = e.currentTarget.dataset.square;
        var dests = selected ? legalDests(selected) : {};
        if (dests[square]) {
            ws.send(JSON.stringify({ type: 'move', move: selected + square }));
            selected = null;
        } else if (pieceAt(square) && isOwnPiece(square)) {
            selected = square;
        } else {
            selected = null;
        }
        render();
    }

    function pieceAt(square) {
        if (!state) return null;
        var rows = state.fen.split(' ')[0].split('/');
        var file = square.charCodeAt(0) - 97;
        var rank = parseInt(square[1], 10);
        var row = rows[9 - rank];
        if (!row) return null;
        var f = 0;
        for (var i = 0; i < row.length; i++) {
            var ch = row[i];
            if (/\d/.test(ch)) { f += parseInt(ch, 10); continue; }
            if (f === file) return ch;
            f += 1;
        }
        return null;
    }

    function isOwnPiece(square) {
        var p = pieceAt(square);
        if (!p) return false;
        return state.color === 'red' ? /[A-Z]/.test(p) : /[a-z]/.test(p);
    }

    var shareInput = document.getElementById('share-url');
    if (shareInput) {
        shareInput.addEventListener('click', function () { this.select(); });
    }

    connect();
    render();
})();
