const API_BASE = '/api';
let micActive = false;
let lastResponseText = '';
let lastDbText = '';
let holoState = 'idle';

document.addEventListener('DOMContentLoaded', () => {
    initTime();
    initHologram();
    initMicButton();
    startPolling();
});

function initTime() {
    const now = new Date();
    document.getElementById('init-time').textContent = now.toLocaleTimeString();
}

function initMicButton() {
    const micBtn = document.getElementById('mic-button');
    const micLabel = document.getElementById('mic-label');
    const audioViz = document.getElementById('audio-visualizer');

    micBtn.addEventListener('click', async () => {
        try {
            await fetch(`${API_BASE}/toggle_mic`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
        } catch (error) {
            console.error('Mic toggle error:', error);
        }
    });
}

async function startPolling() {
    while (true) {
        try {
            const response = await fetch(`${API_BASE}/state`, {
                cache: 'no-store'
            });
            const data = await response.json();

            updateStatus(data.assistant_status || 'Available...');
            updateMicUI(data.mic === 'True');
            updateChat(data.responses || '');
            updateDataStream(data.database || '');
            updateHoloState(data.assistant_status, data.mic === 'True');

        } catch (error) {
            console.error('Polling error:', error);
        }

        await sleep(700);
    }
}

function updateStatus(status) {
    document.getElementById('assistant-status').textContent = status;
}

function updateMicUI(isActive) {
    const micBtn = document.getElementById('mic-button');
    const micLabel = document.getElementById('mic-label');
    const audioViz = document.getElementById('audio-visualizer');

    micActive = isActive;

    if (isActive) {
        micBtn.classList.add('active');
        micLabel.textContent = 'LISTENING...';
        audioViz.classList.add('active');
    } else {
        micBtn.classList.remove('active');
        micLabel.textContent = 'PRESS TO SPEAK';
        audioViz.classList.remove('active');
    }
}

function updateChat(responseText) {
    if (!responseText || responseText === lastResponseText) return;
    lastResponseText = responseText;

    const chatContainer = document.getElementById('chat-container');
    const lines = responseText.split('\n').filter(l => l.trim());

    lines.forEach(line => {
        const trimmed = line.trim();
        if (!trimmed) return;

        const isUser = trimmed.includes(':') && !trimmed.startsWith('Jarvis:');
        const parts = trimmed.split(':', 2);

        if (parts.length >= 2) {
            const sender = parts[0].trim();
            const content = parts.slice(1).join(':').trim();

            const existingMessages = Array.from(chatContainer.querySelectorAll('.message-content'));
            const alreadyExists = existingMessages.some(msg => msg.textContent === content);

            if (!alreadyExists) {
                addChatMessage(sender, content, isUser ? 'user' : 'assistant');
            }
        }
    });

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function updateDataStream(dbText) {
    if (!dbText || dbText === lastDbText) return;
    lastDbText = dbText;

    const logContainer = document.getElementById('data-stream');
    const lines = dbText.split('\n').slice(-5);

    logContainer.innerHTML = '';

    lines.forEach((line, index) => {
        const div = document.createElement('div');
        div.className = 'log-entry';
        div.textContent = line.trim() || '> ...';
        div.style.animationDelay = `${index * 0.1}s`;
        logContainer.appendChild(div);
    });
}

function addChatMessage(sender, content, type = 'system') {
    const chatContainer = document.getElementById('chat-container');
    const now = new Date();

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;

    const header = document.createElement('div');
    header.className = 'message-header';

    const senderSpan = document.createElement('span');
    senderSpan.className = 'message-sender';
    senderSpan.textContent = sender.toUpperCase();

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = now.toLocaleTimeString();

    header.appendChild(senderSpan);
    header.appendChild(timeSpan);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(header);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function updateHoloState(status, micOn) {
    const statusLower = (status || '').toLowerCase();

    if (statusLower.includes('listening') || micOn) {
        holoState = 'listening';
    } else if (statusLower.includes('thinking') || statusLower.includes('processing') || statusLower.includes('searching')) {
        holoState = 'thinking';
    } else if (statusLower.includes('answering') || statusLower.includes('replying')) {
        holoState = 'answering';
    } else {
        holoState = 'idle';
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

let scene, camera, renderer;
let coreParticles, orbitRings, energyField;
let holoTime = 0;

function initHologram() {
    const canvas = document.getElementById('hologram-canvas');
    if (!canvas) return;

    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.z = 120;

    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const ambientLight = new THREE.AmbientLight(0x00d9ff, 0.1);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x00ffcc, 1, 100);
    pointLight.position.set(0, 0, 50);
    scene.add(pointLight);

    createCoreParticles();
    createOrbitRings();
    createEnergyField();

    window.addEventListener('resize', onWindowResize);

    animateHologram();
}

function createCoreParticles() {
    const particleCount = 1500;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
        const radius = Math.random() * 25 + 5;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(Math.random() * 2 - 1);

        positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
        positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = radius * Math.cos(phi);

        const color = new THREE.Color();
        color.setHSL(0.5 + Math.random() * 0.1, 1, 0.7);
        colors[i * 3] = color.r;
        colors[i * 3 + 1] = color.g;
        colors[i * 3 + 2] = color.b;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 1.2,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    coreParticles = new THREE.Points(geometry, material);
    scene.add(coreParticles);
}

function createOrbitRings() {
    orbitRings = new THREE.Group();

    for (let i = 0; i < 4; i++) {
        const radius = 30 + i * 15;
        const geometry = new THREE.RingGeometry(radius - 0.5, radius + 0.5, 128);
        const material = new THREE.MeshBasicMaterial({
            color: 0x00d9ff,
            transparent: true,
            opacity: 0.15 + i * 0.05,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending
        });

        const ring = new THREE.Mesh(geometry, material);
        ring.rotation.x = Math.PI / 2 + (Math.random() - 0.5) * 0.5;
        ring.rotation.y = (Math.random() - 0.5) * 0.3;

        orbitRings.add(ring);
    }

    scene.add(orbitRings);
}

function createEnergyField() {
    const geometry = new THREE.SphereGeometry(15, 32, 32);
    const material = new THREE.MeshBasicMaterial({
        color: 0x00ffcc,
        transparent: true,
        opacity: 0.1,
        wireframe: true,
        blending: THREE.AdditiveBlending
    });

    energyField = new THREE.Mesh(geometry, material);
    scene.add(energyField);
}

function animateHologram() {
    requestAnimationFrame(animateHologram);
    holoTime += 0.01;

    if (coreParticles) {
        coreParticles.rotation.y += 0.001;
        coreParticles.rotation.x += 0.0005;

        const positions = coreParticles.geometry.attributes.position.array;
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            const z = positions[i + 2];

            const distance = Math.sqrt(x * x + y * y + z * z);
            const wave = Math.sin(holoTime * 2 + distance * 0.1) * 0.5;

            positions[i] += Math.sin(holoTime + i) * 0.02;
            positions[i + 1] += Math.cos(holoTime + i) * 0.02;
            positions[i + 2] += wave * 0.01;
        }
        coreParticles.geometry.attributes.position.needsUpdate = true;
    }

    if (orbitRings) {
        orbitRings.rotation.y += 0.002;
        orbitRings.rotation.x += 0.001;

        orbitRings.children.forEach((ring, index) => {
            ring.rotation.z += (index % 2 === 0 ? 0.003 : -0.003);
        });
    }

    if (energyField) {
        energyField.rotation.x += 0.003;
        energyField.rotation.y += 0.002;

        const baseScale = 1;
        let scaleMultiplier = 1;
        let opacityMultiplier = 1;

        if (holoState === 'listening') {
            scaleMultiplier = 1 + Math.sin(holoTime * 5) * 0.2;
            opacityMultiplier = 1.5;
            energyField.material.color.setHex(0x00ffcc);
        } else if (holoState === 'thinking') {
            scaleMultiplier = 1 + Math.sin(holoTime * 8) * 0.15;
            opacityMultiplier = 2;
            energyField.material.color.setHex(0x0099ff);
            if (coreParticles) {
                coreParticles.rotation.y += 0.005;
            }
        } else if (holoState === 'answering') {
            scaleMultiplier = 1 + Math.sin(holoTime * 10) * 0.25;
            opacityMultiplier = 2.5;
            energyField.material.color.setHex(0x00d9ff);
        } else {
            scaleMultiplier = 1 + Math.sin(holoTime * 2) * 0.05;
            opacityMultiplier = 1;
            energyField.material.color.setHex(0x00ffcc);
        }

        energyField.scale.set(baseScale * scaleMultiplier, baseScale * scaleMultiplier, baseScale * scaleMultiplier);
        energyField.material.opacity = 0.1 * opacityMultiplier;
    }

    renderer.render(scene, camera);
}

function onWindowResize() {
    const canvas = document.getElementById('hologram-canvas');
    if (!canvas) return;

    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
}
