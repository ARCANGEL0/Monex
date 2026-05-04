import * as THREE from "three";

// hud-style hex field + spinning sigil that lives in the dashboard hero strip

(function () {
  const canvas = document.getElementById("hero-3d");
  if (!canvas) return;

  const scene = new THREE.Scene();
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));

  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 12);

  function resize() {
    const r = canvas.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    renderer.setSize(r.width, r.height, false);
    camera.aspect = r.width / r.height;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener("resize", resize);

  const GOLD = 0xfcd34d;
  const HOT = 0xf59e0b;

  // ambient hex field - pulses at random phases
  const field = new THREE.Group();
  const hexGeo = new THREE.RingGeometry(0.5, 0.55, 6, 1);
  const hexes = [];
  for (let x = -18; x <= 18; x += 1.8) {
    for (let y = -3.2; y <= 3.2; y += 1.5) {
      const mat = new THREE.MeshBasicMaterial({
        color: GOLD,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.15 + Math.random() * 0.3,
      });
      const h = new THREE.Mesh(hexGeo, mat);
      h.position.set(
        x + (Math.random() - 0.5) * 0.4,
        y + (Math.random() - 0.5) * 0.4,
        -2 - Math.random() * 3
      );
      h.rotation.z = Math.PI / 2;
      h.userData = {
        phase: Math.random() * Math.PI * 2,
        speed: 0.4 + Math.random() * 0.6,
      };
      hexes.push(h);
      field.add(h);
    }
  }
  scene.add(field);

  // central spinning sigil - 3 nested hex rings + bright core
  const sigil = new THREE.Group();
  sigil.position.x = 6;
  const rings = [];
  for (let i = 0; i < 3; i++) {
    const r = 0.7 + i * 0.42;
    const g = new THREE.RingGeometry(r, r + 0.05, 6, 1);
    const m = new THREE.MeshBasicMaterial({
      color: i === 0 ? HOT : GOLD,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.9 - i * 0.18,
    });
    const ring = new THREE.Mesh(g, m);
    ring.rotation.z = Math.PI / 2;
    ring.userData = { dir: i % 2 ? 1 : -1, speedMult: i + 1 };
    rings.push(ring);
    sigil.add(ring);
  }
  // bright hex core
  const coreGeo = new THREE.CircleGeometry(0.25, 6);
  const coreMat = new THREE.MeshBasicMaterial({ color: GOLD, transparent: true, opacity: 0.95 });
  const core = new THREE.Mesh(coreGeo, coreMat);
  core.rotation.z = Math.PI / 2;
  sigil.add(core);
  scene.add(sigil);

  // mouse parallax
  let mouseX = 0;
  canvas.parentElement.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
  });
  canvas.parentElement.addEventListener("mouseleave", () => { mouseX = 0; });

  let t = 0;
  function tick() {
    t += 0.016;

    rings.forEach((r) => {
      r.rotation.z += 0.008 * r.userData.dir * r.userData.speedMult;
    });
    core.material.opacity = 0.65 + 0.3 * Math.sin(t * 2.2);

    hexes.forEach((h) => {
      const p = h.userData.phase;
      h.material.opacity = 0.1 + 0.28 * Math.abs(Math.sin(t * h.userData.speed + p));
    });

    // gentle parallax sway
    field.position.x = Math.sin(t * 0.18) * 0.5 + mouseX * 0.4;
    sigil.position.y = Math.sin(t * 0.6) * 0.12;

    renderer.render(scene, camera);
    requestAnimationFrame(tick);
  }
  tick();
})();
