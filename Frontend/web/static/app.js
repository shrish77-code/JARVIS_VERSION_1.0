// app.js - Golden hologram + state-based animation
const API = "/api";
let micOn = false;
let lastResponse = "";
async function apiGet(path){ const r = await fetch(API+path, {cache:'no-store'}); return r.json(); }
async function apiPost(path, data={}){ const r = await fetch(API+path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)}); return r.json(); }

async function poll(){
  try {
    const s = await apiGet('/state');
    document.getElementById('assistant-status').textContent = s.assistant_status || '—';
    document.getElementById('data-stream').textContent = s.database || '';
    const comm = s.responses || '';
    const commEl = document.getElementById('comm');
    if(comm && comm !== lastResponse){
      const ts = new Date().toLocaleTimeString();
      commEl.innerText += `[${ts}] ${comm}\n\n`;
      commEl.scrollTop = commEl.scrollHeight;
      lastResponse = comm;
    }
    micOn = (s.mic === 'True' || s.mic === 'true');
    updateMicUI();
    updateHoloState(s.assistant_status, micOn);
  } catch(e) {
    // ignore
  } finally {
    setTimeout(poll, 700);
  }
}

function updateMicUI(){
  const btn = document.getElementById('mic-btn');
  const label = document.getElementById('mic-label');
  if(micOn){
    btn.style.boxShadow = '0 18px 60px rgba(255,160,60,0.25)';
    label.textContent = 'Listening...';
    label.style.color = '#ffd66b';
  } else {
    btn.style.boxShadow = '';
    label.textContent = 'Press to speak';
    label.style.color = '#9bdcf6';
  }
}

// toggle mic
document.addEventListener('DOMContentLoaded', ()=>{
  document.getElementById('mic-btn').addEventListener('click', async ()=>{
    await apiPost('/toggle_mic', {});
  });
  poll();
  initHologram();
});

// ---------------------------
// HOLOGRAM: Three.js golden sphere with layered rings and particles
// ---------------------------
let renderer, scene, camera;
let ringGroup, particleCloud, coreSphere, sparkPoints;
let holoState = 'Available';

function initHologram(){
  const canvas = document.getElementById('holo');
  renderer = new THREE.WebGLRenderer({canvas:canvas, alpha:true, antialias:true});
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  resize();

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(40, canvas.clientWidth / Math.max(1, canvas.clientHeight), 0.1, 1000);
  camera.position.z = 90;

  // soft ambient
  const ambient = new THREE.AmbientLight(0xffffff, 0.04);
  scene.add(ambient);

  // layered rotating rings
  ringGroup = new THREE.Group();
  for(let i=0;i<5;i++){
    const r = 18 + i*4;
    const geom = new THREE.RingGeometry(r - 0.25, r + 0.25, 256, 1);
    const mat = new THREE.MeshBasicMaterial({color:0xffcc66, transparent:true, opacity:0.06 + i*0.02, side:THREE.DoubleSide});
    const mesh = new THREE.Mesh(geom, mat);
    mesh.rotation.x = Math.PI/2;
    mesh.rotation.z = (i%2===0?0.2:-0.15) * i;
    ringGroup.add(mesh);
  }
  scene.add(ringGroup);

  // inner core sphere (glowing)
  const coreGeo = new THREE.SphereGeometry(6, 32, 16);
  const coreMat = new THREE.MeshBasicMaterial({color:0xffb84d, transparent:true, opacity:0.12});
  coreSphere = new THREE.Mesh(coreGeo, coreMat);
  scene.add(coreSphere);

  // particle cloud (thin lines)
  const pCount = 1200;
  const positions = new Float32Array(pCount * 3);
  for(let i=0;i<pCount;i++){
    const a = Math.random() * Math.PI * 2;
    const r = 8 + Math.random()*30;
    positions[i*3+0] = Math.cos(a)*r + (Math.random()-0.5)*1.2;
    positions[i*3+1] = Math.sin(a)*r + (Math.random()-0.5)*1.2;
    positions[i*3+2] = (Math.random()-0.5)*6;
  }
  const pGeom = new THREE.BufferGeometry();
  pGeom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const pMat = new THREE.PointsMaterial({size:0.5, color:0xffcc66, transparent:true, opacity:0.95});
  particleCloud = new THREE.Points(pGeom, pMat);
  scene.add(particleCloud);

  // spark lines (for thinking)
  const sparks = new Float32Array(500 * 3);
  for(let i=0;i<500;i++){
    sparks[i*3+0] = (Math.random()-0.5)*40;
    sparks[i*3+1] = (Math.random()-0.5)*40;
    sparks[i*3+2] = (Math.random()-0.5)*10;
  }
  const sGeom = new THREE.BufferGeometry();
  sGeom.setAttribute('position', new THREE.BufferAttribute(sparks, 3));
  sparkPoints = new THREE.Points(sGeom, new THREE.PointsMaterial({size:1.2, color:0xffa84d, transparent:true, opacity:0.0}));
  scene.add(sparkPoints);

  window.addEventListener('resize', resize);
  animate();
}

function resize(){
  const canvas = document.getElementById('holo');
  const w = canvas.clientWidth || canvas.width || 800;
  const h = canvas.clientHeight || canvas.height || 600;
  renderer.setSize(w, h, true);
  if(camera) {
    camera.aspect = w / Math.max(1, h);
    camera.updateProjectionMatrix();
  }
}

let tStart = Date.now();
function animate(){
  requestAnimationFrame(animate);
  const t = (Date.now() - tStart) / 1000;

  // base subtle motion
  ringGroup.rotation.y = Math.sin(t * 0.12) * 0.12;
  ringGroup.rotation.x = 0.08 * Math.sin(t * 0.08);
  particleCloud.rotation.z = -t * 0.07;

  // state-driven tweaks
  if(holoState === 'Available'){
    coreSphere.material.opacity = 0.10;
    particleCloud.material.opacity = 0.7;
    sparkPoints.material.opacity = 0.0;
    for(let i=0;i<ringGroup.children.length;i++){
      ringGroup.children[i].material.opacity = 0.04 + i*0.01;
    }
  } else if(holoState === 'Listening'){
    const pulse = 0.6 + Math.abs(Math.sin(t * 3.6)) * 1.6;
    coreSphere.material.opacity = 0.18 + Math.abs(Math.sin(t * 2.2)) * 0.16;
    particleCloud.material.opacity = 0.95;
    sparkPoints.material.opacity = 0.12;
    // ring glow stronger
    for(let i=0;i<ringGroup.children.length;i++){
      ringGroup.children[i].material.opacity = 0.08 + i*0.03 + Math.abs(Math.sin(t * (1.2 + i*0.1)))*0.06;
      ringGroup.children[i].rotation.z += 0.006 * (i%2===0 ? 1 : -1);
    }
  } else if(holoState === 'Thinking'){
    coreSphere.material.opacity = 0.14 + Math.abs(Math.sin(t * 6)) * 0.12;
    particleCloud.material.opacity = 0.9;
    sparkPoints.material.opacity = 0.45;
    // fast rotation
    ringGroup.rotation.y += 0.01 + 0.01 * Math.sin(t*2.2);
    sparkPoints.rotation.y += 0.02;
  } else if(holoState === 'Replying'){
    const burst = 1 + Math.abs(Math.sin(t*8)) * 0.8;
    coreSphere.material.opacity = 0.22 + Math.abs(Math.sin(t*6))*0.2;
    particleCloud.material.opacity = 1.0;
    sparkPoints.material.opacity = 0.32;
    ringGroup.rotation.y += 0.015;
    // scale core slightly
    coreSphere.scale.set(1 + 0.06*Math.sin(t*12), 1 + 0.06*Math.cos(t*12), 1);
  }

  renderer.render(scene, camera);
}

function updateHoloState(assistantStatus, micState){
  // Map status text to holoState
  let s = (assistantStatus || '').toLowerCase();
  if(s.includes('listening') || micState) holoState = 'Listening';
  else if(s.includes('thinking') || s.includes('processing')) holoState = 'Thinking';
  else if(s.includes('answering') || s.includes('reply')) holoState = 'Replying';
  else holoState = 'Available';
}
