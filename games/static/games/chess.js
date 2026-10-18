(function () {
    'use strict';

    var app = document.getElementById('chess-app');
    if (!app) return;

    var code = app.dataset.code;
    var mode = app.dataset.mode;
    var boardEl = document.getElementById('chess-board');
    var statusEl = document.getElementById('chess-status');

    var state = null;
    var selected = null;
    var ws = null;

    var GLYPHS = {
        K: '\u2654', Q: '\u2655', R: '\u2656', B: '\u2657', N: '\u2658', P: '\u2659',
        k: '\u265A', q: '\u265B', r: '\u265C', b: '\u265D', n: '\u265E', p: '\u265F'
    };

    function squareName(file, rank) {
        return String.fromCharCode(97 + file) + (rank + 1);
    }

    function connect() {
        var proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
        ws = new WebSocket(proto + location.host + '/ws/chess/' + code + '/');

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

    function render() {
        var fen = state ? state.fen : '8/8/8/8/8/8/8/8';
        var rows = fen.split(' ')[0].split('/');
        var flipped = state && state.color === 'black';
        var dests = selected ? legalDests(selected) : {};

        boardEl.innerHTML = '';
        for (var r = 0; r < 8; r++) {
            var rank = flipped ? r : 7 - r;
            for (var f = 0; f < 8; f++) {
                var file = flipped ? 7 - f : f;
                var sq = squareName(file, rank);
                var cell = document.createElement('div');
                var light = (file + rank) % 2 === 1;
                cell.className = 'flex items-center justify-center aspect-square cursor-pointer text-4xl sm:text-5xl ' +
                    (light ? 'bg-amber-100' : 'bg-amber-700');
                if (dests[sq]) cell.className += ' ring-4 ring-inset ring-emerald-500';
                if (selected === sq) cell.className += ' ring-4 ring-inset ring-sky-500';
                if (state && state.last_move && (state.last_move.slice(0, 2) === sq || state.last_move.slice(2, 4) === sq))
                    cell.className += light ? ' bg-amber-200' : ' bg-amber-500';
                cell.dataset.square = sq;
                boardEl.appendChild(cell);
            }
        }

        // place pieces
        var ranks = {};
        for (var ri = 0; ri < 8; ri++) {
            var row = rows[ri];
            var f2 = 0;
            for (var ci = 0; ci < row.length; ci++) {
                var ch = row[ci];
                if (/\d/.test(ch)) { f2 += parseInt(ch, 10); continue; }
                ranks[squareName(f2, 7 - ri)] = ch;
                f2 += 1;
            }
        }
        Array.prototype.forEach.call(boardEl.children, function (cell) {
            var piece = ranks[cell.dataset.square];
            if (piece) {
                cell.textContent = GLYPHS[piece];
                cell.className += /[A-Z]/.test(piece) ? ' piece-white' : ' piece-black';
            }
            cell.addEventListener('click', onCellClick);
        });

        updateStatus();
    }

    function updateStatus() {
        if (!state) return;
        var d = app.dataset;
        var text = '';
        if (state.status === 'waiting') text = d.statusWaiting;
        else if (state.status === 'finished') {
            if (state.result === 'draw') text = d.statusDraw;
            else if (state.result === 'white') text = d.statusWinWhite;
            else text = d.statusWinBlack;
        } else if (state.color === 'spectator') {
            text = d.statusSpectator + ' · ' + (state.turn === 'white' ? d.labelWhite : d.labelBlack);
        } else if (state.turn === state.color) {
            text = d.statusYourTurn + (state.check ? ' · ' + d.statusCheck : '');
        } else {
            text = d.statusTheirTurn + (state.check ? ' · ' + d.statusCheck : '');
        }
        var role = state.color === 'spectator' ? '' :
            '（' + (state.color === 'white' ? d.labelWhite : d.labelBlack) + '）';
        statusEl.textContent = text + role;
    }

    function onCellClick(e) {
        if (!state || state.status !== 'playing') return;
        if (state.color !== 'white' && state.color !== 'black') return;
        if (state.turn !== state.color) return;
        var sq = e.currentTarget.dataset.square;
        var dests = selected ? legalDests(selected) : {};
        if (dests[sq]) {
            var move = selected + sq;
            var piece = pieceAt(selected);
            if (piece && piece.toLowerCase() === 'p') {
                var rank = parseInt(sq[1], 10);
                if (rank === 8 || rank === 1) move += 'q';
            }
            ws.send(JSON.stringify({ type: 'move', move: move }));
            selected = null;
        } else if (pieceAt(sq) && isOwnPiece(sq)) {
            selected = sq;
        } else {
            selected = null;
        }
        render();
    }

    function pieceAt(sq) {
        if (!state) return null;
        var rows = state.fen.split(' ')[0].split('/');
        var file = sq.charCodeAt(0) - 97;
        var rank = parseInt(sq[1], 10);
        var row = rows[8 - rank];
        var f = 0;
        for (var i = 0; i < row.length; i++) {
            var ch = row[i];
            if (/\d/.test(ch)) { f += parseInt(ch, 10); continue; }
            if (f === file) return ch;
            f += 1;
        }
        return null;
    }

    function isOwnPiece(sq) {
        var p = pieceAt(sq);
        if (!p) return false;
        return state.color === 'white' ? /[A-Z]/.test(p) : /[a-z]/.test(p);
    }

    var shareInput = document.getElementById('share-url');
    if (shareInput) {
        shareInput.addEventListener('click', function () { this.select(); });
    }

    connect();
    render();
})();
