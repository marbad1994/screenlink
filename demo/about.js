const viewport = document.getElementById('viewport');
const bwBg = document.getElementById('bw-bg');
const colorImg = document.getElementById('color-img');
const cartoonImg = document.getElementById('cartoon-img');
const scrollContent = document.getElementById('scroll-content');
const marcusFloat = document.getElementById('marcus-float');
const chatZone = document.getElementById('chat-zone');
const tlItems = document.querySelectorAll('.tl-item');

function lerp(a, b, t) { return a + (b - a) * t; }
function clamp(v, min, max) { return Math.min(max, Math.max(min, v)); }
function easeOut(t) { return 1 - Math.pow(1 - t, 2.5); }
function easeInOut(t) { return t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t+2,2)/2; }

function onScroll() {
    const scrollTop = window.scrollY;
    const driverH = document.querySelector('.scroll-driver').offsetHeight;
    const maxScroll = driverH - window.innerHeight;
    const p = clamp(scrollTop / maxScroll, 0, 1);
    const vh = window.innerHeight;

    // Content scroll — map scroll to content translateY
    const contentProgress = clamp(p / 0.8, 0, 1);
    const contentHeight = scrollContent.scrollHeight;
    const contentY = -easeOut(contentProgress) * (contentHeight - vh + 60);
    scrollContent.style.transform = `translateY(${contentY}px)`;

    // Timeline spacing — gentle growth from 40 to 70px
    const gap = lerp(40, 70, easeOut(contentProgress));
    tlItems.forEach(item => { item.style.marginBottom = gap + 'px'; });

    // Marcus photo — slides down gently
    const marcusY = lerp(60, vh - 480, easeInOut(clamp(p / 0.85, 0, 1)));
    marcusFloat.style.top = marcusY + 'px';

    // Color → Cartoon transition (40% to 75%)
    const transP = clamp((p - 0.35) / 0.4, 0, 1);
    const te = easeInOut(transP);

    bwBg.style.opacity = te;
    colorImg.style.opacity = 1 - te;
    cartoonImg.style.opacity = te;

    // Desaturation
    if (transP > 0 && transP < 1) {
        scrollContent.style.filter = `saturate(${Math.round(100 - te * 100)}%)`;
    } else {
        scrollContent.style.filter = transP >= 1 ? 'saturate(0%)' : '';
    }

    viewport.setAttribute('data-world', te > 0.5 ? 'cartoon' : 'color');

    // Chat appears
    chatZone.classList.toggle('visible', p > 0.8);
}

window.addEventListener('scroll', onScroll, { passive: true });
window.addEventListener('resize', onScroll);
onScroll();

// Typing sim
setTimeout(() => {
    const msg = document.getElementById('typing-msg');
    if (msg) msg.innerHTML = "I built this with AWS Bedrock — Claude as the foundation model, my CV and projects indexed in a Knowledge Base with vector embeddings, and a Bedrock Agent that chains retrieval with reasoning. Fully serverless on Lambda.";
}, 8000);
