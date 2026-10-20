// ===== ANIMATED BACKGROUND (particle network) =====
const canvas = document.getElementById('bgCanvas');
const ctx = canvas.getContext('2d');
let particles = [];
const PARTICLE_COUNT = 60;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

class Particle {
    constructor() {
        this.reset();
    }
    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.4;
        this.vy = (Math.random() - 0.5) * 0.4;
        this.radius = Math.random() * 1.5 + 0.5;
        this.opacity = Math.random() * 0.4 + 0.1;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;
        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
    }
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 212, 255, ${this.opacity})`;
        ctx.fill();
    }
}

for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(new Particle());
}

function drawConnections() {
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 150) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.strokeStyle = `rgba(0, 180, 255, ${0.06 * (1 - dist / 150)})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }
}

function animateBg() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Gradient overlay
    const grad = ctx.createRadialGradient(
        canvas.width * 0.3, canvas.height * 0.3, 0,
        canvas.width * 0.3, canvas.height * 0.3, canvas.width * 0.7
    );
    grad.addColorStop(0, 'rgba(0, 60, 120, 0.08)');
    grad.addColorStop(1, 'transparent');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => { p.update(); p.draw(); });
    drawConnections();
    requestAnimationFrame(animateBg);
}
animateBg();


// ===== PAGE NAVIGATION =====
function switchPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const page = document.getElementById(`page-${pageName}`);
    const navBtn = document.querySelector(`.nav-item[data-page="${pageName}"]`);

    if (page) page.classList.add('active');
    if (navBtn) navBtn.classList.add('active');

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}


// ===== CHAT FUNCTIONALITY =====
const API_BASE = 'http://localhost:8000/api'; // Backend URL

function getCurrentTime() {
    return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function addMessage(text, type = 'agent') {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;

    if (type === 'agent') {
        msgDiv.innerHTML = `
            <div class="message-avatar">
                <svg viewBox="0 0 24 24" fill="none"><rect x="2" y="2" width="20" height="20" rx="6" fill="url(#msgGrad)"/><path d="M8 12h8M12 8v8" stroke="white" stroke-width="1.5" stroke-linecap="round"/><defs><linearGradient id="msgGrad" x1="0" y1="0" x2="24" y2="24"><stop offset="0%" stop-color="#00d4ff"/><stop offset="100%" stop-color="#7c3aed"/></linearGradient></defs></svg>
            </div>
            <div class="message-content">
                <div class="message-bubble">${text}</div>
                <span class="message-time">${getCurrentTime()}</span>
            </div>`;
    } else {
        msgDiv.innerHTML = `
            <div class="message-content">
                <div class="message-bubble"><p>${escapeHtml(text)}</p></div>
                <span class="message-time">${getCurrentTime()}</span>
            </div>`;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function showTyping() {
    const container = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message agent';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none"><rect x="2" y="2" width="20" height="20" rx="6" fill="url(#msgGrad)"/><path d="M8 12h8M12 8v8" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg>
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="typing-indicator"><span></span><span></span><span></span></div>
            </div>
        </div>`;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function removeTyping() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    input.value = '';
    input.style.height = 'auto';

    showTyping();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        removeTyping();

        if (response.ok) {
            const data = await response.json();
            addMessage(`<p>${data.reply}</p>`);
        } else {
            throw new Error('API error');
        }
    } catch (err) {
        removeTyping();
        // Fallback: simulated response for demo
        const demoReply = getDemoReply(text);
        addMessage(`<p>${demoReply}</p>`);
    }
}

function sendQuick(text) {
    document.getElementById('chatInput').value = text;
    sendMessage();
}

function handleChatKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function clearChat() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = '';
    addMessage(`<p>Chat cleared. How can I help you today?</p>
        <div class="quick-actions">
            <button class="quick-btn" onclick="sendQuick('How can I send money from Bangladesh to China cheaply?')">💸 Cheap remittance</button>
            <button class="quick-btn" onclick="sendQuick('Help me create a monthly budget for studying in China')">📊 Budget planning</button>
        </div>`);
}

// Demo replies (when backend is not connected)
function getDemoReply(query) {
    const q = query.toLowerCase();
    if (q.includes('remittance') || q.includes('send money') || q.includes('cheaply')) {
        return `For sending money from Bangladesh to China, here are your best options:

<strong>1. Wise (TransferWise)</strong> — Best exchange rate, low fees (~$4-5 for $500). Delivery: 1-2 hours.<br><br>
<strong>2. Remitly</strong> — Fast delivery (minutes), slightly higher markup. Good for urgent transfers.<br><br>
<strong>3. Bank Wire (SWIFT)</strong> — Most banks charge $25-40 per transfer. Slowest (3-5 days) but most traditional.<br><br>
<strong>Tip:</strong> For regular tuition payments, Wise offers the best value. For one-time large transfers, compare rates on the Remittance Compare tool in the sidebar.`;
    }
    if (q.includes('tuition') || q.includes('payment method')) {
        return `For Chinese university tuition payments, here are the common methods:

<strong>1. Bank Wire (SWIFT)</strong> — Most accepted. Your university will provide bank details (account number, SWIFT code). Fees: $25-40 from Bangladesh.<br><br>
<strong>2. Flywire</strong> — Many Chinese universities partner with Flywire. Tracks your payment, competitive rates. Recommended for first-time payments.<br><br>
<strong>3. WeChat Pay / Alipay</strong> — After arrival, useful for campus payments, dining, transport. Need Chinese bank account to set up.<br><br>
<strong>Tip:</strong> Always confirm with your university's finance office which methods they accept before sending.`;
    }
    if (q.includes('budget') || q.includes('monthly')) {
        return `Here's a suggested monthly budget for a student in China (Tier-1 city like Hangzhou/Shenzhen):

<strong>Accommodation:</strong> ¥800-2,000 (dorm ¥800, off-campus ¥1,500-2,000)<br>
<strong>Food:</strong> ¥1,000-1,500 (campus canteen ¥15-25/meal)<br>
<strong>Transport:</strong> ¥200-500 (metro ¥3-7/trip, bus ¥2)<br>
<strong>Study Materials:</strong> ¥200-500<br>
<strong>Phone/Internet:</strong> ¥100-200<br>
<strong>Entertainment:</strong> ¥300-500<br><br>
<strong>Total: ¥2,600-5,200/month (~$360-720 USD)</strong><br><br>
Use the Budget Tracker tool to track your actual spending and get AI insights!`;
    }
    if (q.includes('exchange rate') || q.includes('bdt') || q.includes('cny')) {
        return `Current approximate exchange rates:<br><br>
<strong>1 BDT = 0.0828 CNY</strong><br>
<strong>1 USD = 121.45 BDT</strong><br>
<strong>1 USD = 7.245 CNY</strong><br>
<strong>1 CNY = 16.76 BDT</strong><br><br>
Rates fluctuate — use the Currency Converter tool for real-time rates. <strong>Tip:</strong> CNY has been relatively stable against USD recently.`;
    }

    return `Thanks for your question! I can help with cross-border finance, currency conversion, remittance comparison, tuition payments, and budget planning for international students. Could you tell me more about what specific information you need?`;
}


// ===== CURRENCY CONVERTER =====
const exchangeRates = {
    BDT: 1, USD: 0.00824, CNY: 0.05970, EUR: 0.00762,
    GBP: 0.00652, JPY: 1.2350, INR: 0.6930, MYR: 0.03890,
    SGD: 0.01107, AUD: 0.01272, CAD: 0.01128, KRW: 11.28
};

function convertCurrency() {
    const from = document.getElementById('fromCurrency').value;
    const to = document.getElementById('toCurrency').value;
    const amount = parseFloat(document.getElementById('fromAmount').value) || 0;

    const inUSD = amount * (exchangeRates['USD'] / exchangeRates[from]);
    const result = inUSD * (exchangeRates[to] / exchangeRates['USD']);

    const symbols = { BDT: '৳', USD: '$', CNY: '¥', EUR: '€', GBP: '£', JPY: '¥', INR: '₹', MYR: 'RM', SGD: 'S$', AUD: 'A$', CAD: 'C$', KRW: '₩' };

    const sym = symbols[to] || '';
    document.getElementById('conversionResult').innerHTML =
        `<span class="result-amount">${sym} ${result.toFixed(2)}</span>`;

    const rate = (exchangeRates[to] / exchangeRates[from]);
    document.getElementById('rateDisplay').textContent =
        `1 ${from} = ${rate.toFixed(6)} ${to}`;
}

function swapCurrencies() {
    const fromEl = document.getElementById('fromCurrency');
    const toEl = document.getElementById('toCurrency');
    const temp = fromEl.value;
    fromEl.value = toEl.value;
    toEl.value = temp;
    convertCurrency();
}

function setConversion(from, to) {
    document.getElementById('fromCurrency').value = from;
    document.getElementById('toCurrency').value = to;
    convertCurrency();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}


// ===== REMITTANCE COMPARE =====
function compareRemittance() {
    const amount = parseFloat(document.getElementById('remitAmount').value) || 500;
    // In production, this would call the backend API
    // For demo, update displayed values based on amount
    const results = document.getElementById('remitResults');
    results.style.opacity = '0';
    setTimeout(() => {
        results.style.opacity = '1';
        results.style.transition = 'opacity 0.4s';
    }, 200);
}


// ===== BUDGET TRACKER =====
let expenses = [];

function addExpense() {
    const desc = document.getElementById('expenseDesc').value.trim();
    const amount = parseFloat(document.getElementById('expenseAmount').value);
    const category = document.getElementById('expenseCategory').value;

    if (!desc || !amount) return;

    expenses.push({ desc, amount, category, date: new Date() });

    // Clear inputs
    document.getElementById('expenseDesc').value = '';
    document.getElementById('expenseAmount').value = '';

    // Show confirmation
    const btn = document.querySelector('.add-expense .primary-btn');
    const original = btn.textContent;
    btn.textContent = '✓ Added!';
    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    setTimeout(() => {
        btn.textContent = original;
        btn.style.background = '';
    }, 1500);
}


// ===== LIVE RATE SIMULATION =====
function simulateLiveRate() {
    const el = document.getElementById('usdBdt');
    if (!el) return;
    const base = 121.45;
    const change = (Math.random() - 0.5) * 0.3;
    const newRate = (base + change).toFixed(2);
    el.textContent = newRate;

    const changeEl = el.nextElementSibling;
    if (changeEl) {
        const pct = ((change / base) * 100).toFixed(2);
        changeEl.textContent = `${pct >= 0 ? '+' : ''}${pct}%`;
        changeEl.className = `rate-change ${pct >= 0 ? 'positive' : 'negative'}`;
    }
}
setInterval(simulateLiveRate, 5000);


// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    convertCurrency();
});
