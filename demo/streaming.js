// Elements
const scene = document.getElementById('scene');
const finalPhone = document.getElementById('final-phone');
const titleOverlay = document.getElementById('title-overlay');
const scrollHint = document.getElementById('scroll-hint');
const video = document.getElementById('demo-video');
const phoneVideo = document.getElementById('phone-video');

let isPlaying = false;
let isCasting = false;
let isMuted = false;
let volume = 75;

// ===== Scroll-driven animation =====
const SCALE_START = 3.5;
const SCALE_END = 1;
const TY_START = 180;
const TY_END = 0;

// Phone keyframes:
// Start: landscape, centered below person's head (in their hands)
// End: portrait, right side of viewport
function getPhoneStart() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    return {
        x: vw * 0.5 - 75,   // centered-ish
        y: vh * 0.55,        // below center (in hands area)
        rotation: 90,        // landscape
        scale: 0.7,
        opacity: 1,
    };
}

function getPhoneEnd() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    return {
        x: vw - 220,         // right side
        y: vh * 0.5 - 160,   // vertically centered
        rotation: 0,          // portrait
        scale: 1,
        opacity: 1,
    };
}

function lerp(a, b, t) {
    return a + (b - a) * t;
}

function onScroll() {
    const scrollTop = window.scrollY;
    const maxScroll = document.getElementById('scroll-driver').offsetHeight - window.innerHeight;
    const progress = Math.min(1, Math.max(0, scrollTop / maxScroll));

    // Ease
    const eased = 1 - Math.pow(1 - progress, 2.5);

    // Scene zoom
    const scale = lerp(SCALE_START, SCALE_END, eased);
    const ty = lerp(TY_START, TY_END, eased);
    scene.style.transform = `scale(${scale}) translateY(${ty}px)`;

    // Phone animation
    const ps = getPhoneStart();
    const pe = getPhoneEnd();

    // Phone easing — starts moving later, finishes with the scene
    const phoneProgress = Math.min(1, Math.max(0, (eased - 0.15) / 0.85));
    const phoneEased = 1 - Math.pow(1 - phoneProgress, 2);

    const px = lerp(ps.x, pe.x, phoneEased);
    const py = lerp(ps.y, pe.y, phoneEased);
    const pr = lerp(ps.rotation, pe.rotation, phoneEased);
    const psc = lerp(ps.scale, pe.scale, phoneEased);

    finalPhone.style.left = px + 'px';
    finalPhone.style.top = py + 'px';
    finalPhone.style.transform = `rotate(${pr}deg) scale(${psc})`;
    finalPhone.style.opacity = 1;

    // Switch phone content: watching → precast when zoomed out enough
    const watchingView = document.getElementById('watching-view');
    const precastView = document.getElementById('precast-view');
    const remoteView = document.getElementById('remote-view');

    if (!isCasting) {
        if (eased > 0.8) {
            watchingView.classList.add('hidden');
            precastView.classList.remove('hidden');
        } else {
            watchingView.classList.remove('hidden');
            precastView.classList.add('hidden');
        }
    }

    // Title + scroll hint
    if (eased > 0.85) {
        titleOverlay.classList.add('visible');
        scrollHint.classList.add('hidden');
    } else {
        titleOverlay.classList.remove('visible');
        scrollHint.classList.remove('hidden');
    }
}

window.addEventListener('scroll', onScroll, { passive: true });
window.addEventListener('resize', onScroll);
onScroll();

// ===== Cast to TV =====
function castToTV() {
    if (isCasting) return;
    isCasting = true;

    document.getElementById('watching-view').classList.add('hidden');
    document.getElementById('precast-view').classList.add('hidden');
    document.getElementById('remote-view').classList.remove('hidden');

    document.getElementById('tv-off').classList.add('hidden');
    document.getElementById('tv-playing').classList.add('active');
    document.getElementById('tv-cast-badge').classList.add('visible');

    video.currentTime = phoneVideo ? phoneVideo.currentTime : 0;
    video.play().catch(() => {});
    isPlaying = true;
    document.getElementById('playpause-icon').innerHTML = '&#x23F8;&#xFE0E;';
}

function stopCast() {
    isCasting = false;
    isPlaying = false;
    video.pause();
    video.currentTime = 0;

    document.getElementById('tv-playing').classList.remove('active');
    document.getElementById('tv-off').classList.remove('hidden');
    document.getElementById('tv-cast-badge').classList.remove('visible');
    document.getElementById('tv-paused-icon').classList.remove('visible');

    document.getElementById('watching-view').classList.add('hidden');
    document.getElementById('precast-view').classList.remove('hidden');
    document.getElementById('remote-view').classList.add('hidden');
}

// ===== Remote controls =====
function togglePlay() {
    if (!isCasting) return;
    isPlaying = !isPlaying;
    if (isPlaying) {
        video.play().catch(() => {});
        document.getElementById('playpause-icon').innerHTML = '&#x23F8;&#xFE0E;';
        document.getElementById('tv-paused-icon').classList.remove('visible');
    } else {
        video.pause();
        document.getElementById('playpause-icon').innerHTML = '&#x25B6;&#xFE0E;';
        document.getElementById('tv-paused-icon').classList.add('visible');
    }
}

function adjustVolume(delta) {
    volume = Math.max(0, Math.min(100, volume + delta * 10));
    video.volume = volume / 100;
    document.getElementById('volume-fill').style.width = volume + '%';
    document.getElementById('volume-pct').textContent = volume + '%';
    const popup = document.getElementById('volume-popup');
    popup.classList.add('visible');
    clearTimeout(window._vt);
    window._vt = setTimeout(() => popup.classList.remove('visible'), 1500);
}

function toggleMute() {
    isMuted = !isMuted;
    video.muted = isMuted;
    const btn = document.getElementById('btn-mute');
    btn.style.borderColor = isMuted ? '#e74c3c' : '';
    btn.style.color = isMuted ? '#e74c3c' : '';
}

function toggleFullscreen() {
    const tv = document.getElementById('tv-screen');
    if (document.fullscreenElement) document.exitFullscreen();
    else tv.requestFullscreen().catch(() => {});
}

function seek(s) {
    if (!isCasting) return;
    video.currentTime = Math.max(0, Math.min(video.duration, video.currentTime + s));
}
