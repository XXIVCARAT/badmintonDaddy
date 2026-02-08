/**
 * Badminton Daddy - Game Logic and UI Control
 */

// ============ STATE MANAGEMENT ============

const state = {
    scoreA: 0,
    scoreB: 0,
    serverTeam: 'A',
    gamePoint: 21,
    mode: 'doubles',
    players: { A1: '', A2: '', B1: '', B2: '' },
    posA1: 1,  // 1 = Right (Even), 0 = Left (Odd)
    posB1: 1,
    history: []
};


// ============ GAME INITIALIZATION ============

function startGame() {
    state.mode = document.getElementById('game-mode-select').value;
    state.gamePoint = parseInt(document.getElementById('match-point-select').value);
    state.players.A1 = document.getElementById('pA1').value || 'A1';
    state.players.B1 = document.getElementById('pB1').value || 'B1';
    
    if (state.mode === 'doubles') {
        state.players.A2 = document.getElementById('pA2').value || 'A2';
        state.players.B2 = document.getElementById('pB2').value || 'B2';
    } else {
        state.players.A2 = '';
        state.players.B2 = '';
    }
    
    // Reset positions
    state.posA1 = 1;
    state.posB1 = 1;
    
    // Hide setup, show game area
    document.getElementById('player-setup').classList.add('d-none');
    document.getElementById('active-game-area').classList.remove('d-none');
    updateCourt();
}


function resetGame() {
    const hasActiveScore = state.scoreA > 0 || state.scoreB > 0;
    if (hasActiveScore && !confirm("Discard current game?")) {
        return;
    }
    
    // Reset state
    state.scoreA = 0;
    state.scoreB = 0;
    state.history = [];
    state.serverTeam = 'A';
    
    // Hide game area, show setup
    document.getElementById('player-setup').classList.remove('d-none');
    document.getElementById('active-game-area').classList.add('d-none');
    document.getElementById('save-btn-area').classList.add('d-none');
    
    // Remove winner glow
    document.getElementById('score-box-A').classList.remove('winner-glow');
    document.getElementById('score-box-B').classList.remove('winner-glow');
    
    // Show/hide doubles inputs based on mode
    const mode = document.getElementById('game-mode-select').value;
    document.querySelectorAll('.doubles-only').forEach(el => {
        el.style.display = mode === 'doubles' ? 'flex' : 'none';
    });
}


// ============ SCORING LOGIC ============

function addPoint(team) {
    if (checkWin()) {
        return;
    }
    
    // Save state for undo
    state.history.push(JSON.parse(JSON.stringify(state)));
    
    const isServerWin = (team === state.serverTeam);
    
    // Update score
    if (team === 'A') {
        state.scoreA++;
    } else {
        state.scoreB++;
    }
    
    // Update positions and serve
    if (state.mode === 'doubles') {
        if (isServerWin) {
            // Server wins: same server continues, swap sides
            if (team === 'A') {
                state.posA1 = 1 - state.posA1;
            } else {
                state.posB1 = 1 - state.posB1;
            }
        } else {
            // Receiver wins: service changes
            state.serverTeam = team;
        }
    } else {
        // Singles: service always changes on opponent score
        state.serverTeam = team;
    }
    
    // Haptic feedback if available
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
    
    updateCourt();
    checkWin();
}


function undoPoint() {
    if (state.history.length === 0) {
        return;
    }
    
    let lastState = state.history.pop();
    Object.assign(state, lastState);
    
    // Hide save button and winner glow
    document.getElementById('save-btn-area').classList.add('d-none');
    document.getElementById('score-box-A').classList.remove('winner-glow');
    document.getElementById('score-box-B').classList.remove('winner-glow');
    
    updateCourt();
}


function forceSwapPositions() {
    if (state.serverTeam === 'A') {
        state.posA1 = 1 - state.posA1;
    } else {
        state.posB1 = 1 - state.posB1;
    }
    updateCourt();
}


function checkWin() {
    const sA = state.scoreA;
    const sB = state.scoreB;
    const limit = state.gamePoint;
    const hardCap = limit + 9;  // 21st point wins even if not +2
    
    let winner = null;
    
    if ((sA >= limit && sA >= sB + 2) || sA === hardCap) {
        winner = 'A';
    } else if ((sB >= limit && sB >= sA + 2) || sB === hardCap) {
        winner = 'B';
    }
    
    if (winner) {
        document.getElementById('save-btn-area').classList.remove('d-none');
        document.getElementById('score-box-' + winner).classList.add('winner-glow');
        return true;
    }
    
    return false;
}


// ============ COURT DISPLAY ============

function updateCourt() {
    // Update scores
    document.getElementById('scoreA').innerText = state.scoreA;
    document.getElementById('scoreB').innerText = state.scoreB;
    
    const sA = state.scoreA;
    const sB = state.scoreB;
    
    // Get service boxes
    const aBoxL = document.getElementById('pos-A-L');
    const aBoxR = document.getElementById('pos-A-R');
    const bBoxL = document.getElementById('pos-B-L');
    const bBoxR = document.getElementById('pos-B-R');
    
    // Reset all boxes
    [aBoxL, aBoxR, bBoxL, bBoxR].forEach(el => {
        el.className = 'service-box';
    });
    
    if (state.mode === 'singles') {
        // Singles: players alternate sides based on score
        aBoxL.innerText = (sA % 2 !== 0) ? state.players.A1 : '';
        aBoxR.innerText = (sA % 2 === 0) ? state.players.A1 : '';
        
        bBoxL.innerText = (sB % 2 !== 0) ? state.players.B1 : '';
        bBoxR.innerText = (sB % 2 === 0) ? state.players.B1 : '';
        
        // Highlight server
        if (state.serverTeam === 'A') {
            (sA % 2 === 0) ? aBoxR.classList.add('active-server') : aBoxL.classList.add('active-server');
        } else {
            (sB % 2 === 0) ? bBoxR.classList.add('active-server') : bBoxL.classList.add('active-server');
        }
    } else {
        // Doubles: players have fixed partnership
        const pA1 = state.players.A1;
        const pA2 = state.players.A2;
        const pB1 = state.players.B1;
        const pB2 = state.players.B2;
        
        // Arrange team A
        if (state.posA1 === 1) {
            aBoxR.innerText = pA1;
            aBoxL.innerText = pA2;
        } else {
            aBoxL.innerText = pA1;
            aBoxR.innerText = pA2;
        }
        
        // Arrange team B
        if (state.posB1 === 1) {
            bBoxR.innerText = pB1;
            bBoxL.innerText = pB2;
        } else {
            bBoxL.innerText = pB1;
            bBoxR.innerText = pB2;
        }
        
        // Highlight server
        const servingScore = (state.serverTeam === 'A') ? sA : sB;
        if (state.serverTeam === 'A') {
            (servingScore % 2 === 0) ? aBoxR.classList.add('active-server') : aBoxL.classList.add('active-server');
        } else {
            (servingScore % 2 === 0) ? bBoxR.classList.add('active-server') : bBoxL.classList.add('active-server');
        }
    }
}


// ============ MATCH SAVING ============

function saveLiveMatch() {
    // Determine winners and losers
    const winners = (state.scoreA > state.scoreB)
        ? [state.players.A1, state.players.A2]
        : [state.players.B1, state.players.B2];
    
    const losers = (state.scoreA > state.scoreB)
        ? [state.players.B1, state.players.B2]
        : [state.players.A1, state.players.A2];
    
    sendMatchData(winners.filter(Boolean), losers.filter(Boolean), state.mode);
}


function submitManualMatch() {
    const w1 = document.getElementById('manual-w1').value.trim();
    const w2 = document.getElementById('manual-w2').value.trim();
    const l1 = document.getElementById('manual-l1').value.trim();
    const l2 = document.getElementById('manual-l2').value.trim();
    
    if (!w1 || !l1) {
        alert("Please enter at least one winner and one loser");
        return;
    }
    
    const winners = [w1, w2].filter(Boolean);
    const losers = [l1, l2].filter(Boolean);
    const type = (winners.length > 1 || losers.length > 1) ? 'doubles' : 'singles';
    
    sendMatchData(winners, losers, type);
}


function sendMatchData(winners, losers, type) {
    const payload = {
        winners: winners,
        losers: losers,
        type: type
    };
    
    fetch('/api/save-match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert("✓ Match Saved!");
            // Clear manual entry form
            document.getElementById('manual-w1').value = '';
            document.getElementById('manual-w2').value = '';
            document.getElementById('manual-l1').value = '';
            document.getElementById('manual-l2').value = '';
            // Reset game
            resetGame();
            // Reload rankings
            document.getElementById('standings').innerHTML = '<p>Loading...</p>';
            fetch('/update-rankings')
                .then(r => r.text())
                .then(html => {
                    document.getElementById('standings').innerHTML = html;
                });
        } else {
            alert("Error: " + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Error saving match. Check console for details.");
    });
}
