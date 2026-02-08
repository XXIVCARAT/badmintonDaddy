/**
 * Badminton Daddy - Game Logic and UI Control
 * Modern ES6+ implementation with API client integration
 */

// ============ GAME STATE MANAGEMENT ============

class GameState {
    constructor() {
        this.reset();
    }

    reset() {
        this.scoreA = 0;
        this.scoreB = 0;
        this.serverTeam = 'A';
        this.gamePoint = 21;
        this.mode = 'doubles';
        this.players = { A1: '', A2: '', B1: '', B2: '' };
        this.posA1 = 1;  // 1 = Right (Even), 0 = Left (Odd)
        this.posB1 = 1;
        this.history = [];
    }

    addPoint(team) {
        if (this.checkWin()) {
            return false;
        }

        // Save state for undo
        this.history.push(this.clone());

        const isServerWin = (team === this.serverTeam);

        // Update score
        if (team === 'A') {
            this.scoreA++;
        } else {
            this.scoreB++;
        }

        // Update positions and serve
        if (this.mode === 'doubles') {
            if (isServerWin) {
                // Server wins: same server continues, swap sides
                if (team === 'A') {
                    this.posA1 = 1 - this.posA1;
                } else {
                    this.posB1 = 1 - this.posB1;
                }
            } else {
                // Receiver wins: service changes
                this.serverTeam = team;
            }
        } else {
            // Singles: service always changes on opponent score
            this.serverTeam = team;
        }

        // Haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }

        return true;
    }

    undoPoint() {
        if (this.history.length === 0) {
            return false;
        }

        const lastState = this.history.pop();
        Object.assign(this, lastState);
        return true;
    }

    checkWin() {
        const sA = this.scoreA;
        const sB = this.scoreB;
        const limit = this.gamePoint;
        const hardCap = limit + 9;

        if ((sA >= limit && sA >= sB + 2) || sA === hardCap) {
            return 'A';
        } else if ((sB >= limit && sB >= sA + 2) || sB === hardCap) {
            return 'B';
        }

        return null;
    }

    clone() {
        const cloned = new GameState();
        Object.assign(cloned, this);
        cloned.history = [...this.history];
        cloned.players = { ...this.players };
        return cloned;
    }

    getWinners() {
        const winner = this.checkWin();
        if (!winner) return null;

        if (winner === 'A') {
            return {
                winners: [this.players.A1, this.players.A2].filter(Boolean),
                losers: [this.players.B1, this.players.B2].filter(Boolean),
            };
        } else {
            return {
                winners: [this.players.B1, this.players.B2].filter(Boolean),
                losers: [this.players.A1, this.players.A2].filter(Boolean),
            };
        }
    }
}

// Global game state
const state = new GameState();


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
    if (hasActiveScore && !confirm('Discard current game?')) {
        return;
    }

    // Reset state
    state.reset();

    // Hide game area, show setup
    document.getElementById('player-setup').classList.remove('d-none');
    document.getElementById('active-game-area').classList.add('d-none');
    document.getElementById('save-btn-area').classList.add('d-none');

    // Remove winner glow
    document.getElementById('score-box-A').classList.remove('winner-glow');
    document.getElementById('score-box-B').classList.remove('winner-glow');

    // Show/hide doubles inputs based on mode
    const mode = document.getElementById('game-mode-select').value;
    document.querySelectorAll('.doubles-only').forEach((el) => {
        el.style.display = mode === 'doubles' ? 'flex' : 'none';
    });
}

// ============ SCORING LOGIC ============

function addPoint(team) {
    if (state.checkWin()) {
        return;
    }

    state.addPoint(team);
    updateCourt();
    checkWin();
}

function undoPoint() {
    if (!state.undoPoint()) {
        return;
    }

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
    const winner = state.checkWin();
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

// Initialize API client
const api = new BadmintonAPIClient('/api');

async function saveLiveMatch() {
    try {
        // Get winners from current state
        const matchResult = state.getWinners();
        if (!matchResult) {
            alert('No winner determined yet.');
            return;
        }

        // Show loading state
        const saveBtn = document.querySelector('#save-btn-area button');
        const originalText = saveBtn.textContent;
        saveBtn.textContent = 'Saving...';
        saveBtn.disabled = true;

        // Call API
        const response = await api.saveMatch(
            matchResult.winners,
            matchResult.losers,
            state.mode
        );

        // Reset UI
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;

        alert('✓ Match Saved!');

        // Clear manual entry form
        document.getElementById('manual-w1').value = '';
        document.getElementById('manual-w2').value = '';
        document.getElementById('manual-l1').value = '';
        document.getElementById('manual-l2').value = '';

        // Reset game
        resetGame();

        // Reload rankings
        try {
            const rankings = await api.getRankings();
            document.getElementById('standings').innerHTML = rankings;
        } catch (err) {
            console.error('Error loading rankings:', err);
        }
    } catch (error) {
        console.error('Error saving match:', error);
        alert('Error: ' + (error.message || 'Failed to save match'));
        // Reset button state
        const saveBtn = document.querySelector('#save-btn-area button');
        saveBtn.textContent = 'Save Match';
        saveBtn.disabled = false;
    }
}

async function submitManualMatch() {
    try {
        const w1 = document.getElementById('manual-w1').value.trim();
        const w2 = document.getElementById('manual-w2').value.trim();
        const l1 = document.getElementById('manual-l1').value.trim();
        const l2 = document.getElementById('manual-l2').value.trim();

        if (!w1 || !l1) {
            alert('Please enter at least one winner and one loser');
            return;
        }

        const winners = [w1, w2].filter(Boolean);
        const losers = [l1, l2].filter(Boolean);
        const type = (winners.length > 1 || losers.length > 1) ? 'doubles' : 'singles';

        // Show loading state
        const submitBtn = document.querySelector('[onclick="submitManualMatch()"]');
        const originalText = submitBtn ? submitBtn.textContent : 'Submit';
        if (submitBtn) {
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;
        }

        // Call API
        await api.saveMatch(winners, losers, type);

        // Reset UI
        if (submitBtn) {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }

        alert('✓ Match Saved!');

        // Clear form
        document.getElementById('manual-w1').value = '';
        document.getElementById('manual-w2').value = '';
        document.getElementById('manual-l1').value = '';
        document.getElementById('manual-l2').value = '';

        // Reload rankings
        try {
            const rankings = await api.getRankings();
            document.getElementById('standings').innerHTML = rankings;
        } catch (err) {
            console.error('Error loading rankings:', err);
        }
    } catch (error) {
        console.error('Error submitting match:', error);
        alert('Error: ' + (error.message || 'Failed to submit match'));
        // Reset button state
        const submitBtn = document.querySelector('[onclick="submitManualMatch()"]');
        if (submitBtn) {
            submitBtn.textContent = 'Submit';
            submitBtn.disabled = false;
        }
    }
}

