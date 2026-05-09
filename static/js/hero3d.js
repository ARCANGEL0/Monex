import * as THREE from "three";

const SPINNER_SIZE = 226;
const SPINNER_CENTER = { x: 113, y: 150.65 };
const ROTATION_MS = (288 / 30) * 1000;
const CYCLE_MS = (92 / 30) * 1000;
const PHASE_WINDOW = 0.5;
const OPACITY_OFFSET = 12 / 96;
const FILL_OFFSET = 30 / 96;
const INSET_DELAY = 0.5;

const GOLD = 0xd4af37;

const TRIANGLES = [
  { phase: 0, points: [[22.5, 180.1], [0, 225.1], [45, 225.1]] },
  { phase: 1, points: [[67.6, 180.1], [45.1, 225.1], [90.1, 225.1]] },
  { phase: 2, points: [[45.07, 225.099], [22.57, 180.099], [67.57, 180.099]] },
  { phase: 3, points: [[90.07, 225.099], [67.57, 180.099], [112.57, 180.099]] },
  { phase: 4, points: [[112.6, 180.1], [90.1, 225.1], [135.1, 225.1]] },
  { phase: 5, points: [[135.07, 225.099], [112.57, 180.099], [157.57, 180.099]] },
  { phase: 6, points: [[45.07, 135.1], [67.57, 180.1], [22.57, 180.1]] },
  { phase: 7, points: [[157.6, 180.1], [135.1, 225.1], [180.1, 225.1]] },
  { phase: 8, points: [[180.07, 225.099], [157.57, 180.099], [202.57, 180.099]] },
  { phase: 9, points: [[202.6, 180.1], [180.1, 225.1], [225.1, 225.1]] },
  { phase: 10, points: [[67.6, 180.099], [90.1, 135.099], [45.1, 135.099]] },
  { phase: 11, points: [[180.07, 135.1], [202.57, 180.1], [157.57, 180.1]] },
  { phase: 12, points: [[67.6, 90.1], [90.1, 135.1], [45.1, 135.1]] },
  { phase: 13, points: [[157.6, 180.099], [135.1, 135.099], [180.1, 135.099]] },
  { phase: 14, points: [[157.6, 90.1], [180.1, 135.1], [135.1, 135.1]] },
  { phase: 15, points: [[90.07, 135.099], [112.57, 90.099], [67.57, 90.099]] },
  { phase: 15, points: [[135.07, 135.099], [112.57, 90.099], [157.57, 90.099]] },
  { phase: 16, points: [[135.07, 45], [157.57, 90], [112.57, 90]] },
  { phase: 17, points: [[90.07, 45], [112.57, 90], [67.57, 90]] },
  { phase: 18, points: [[135.07, 45], [90.07, 45], [112.57, 90]] },
  { phase: 19, points: [[112.6, 0.1], [135.1, 45.1], [90.1, 45.1]] },
];

let activeHero = null;
let mountTimer = 0;
let mountFrame = 0;

function buildTriangle(points) {
  const [a, b, c] = points;
  const centroid = {
    x: (a[0] + b[0] + c[0]) / 3,
    y: (a[1] + b[1] + c[1]) / 3,
  };
  const vertices = [a, b, c].map(([x, y]) => new THREE.Vector3(x - centroid.x, -(y - centroid.y), 0));
  return {
    centroid,
    geometry: new THREE.BufferGeometry().setFromPoints(vertices),
  };
}

function createLayer() {
  const group = new THREE.Group();
  const triangles = TRIANGLES.map(({ phase, points }) => {
    const meshGroup = new THREE.Group();
    const { centroid, geometry } = buildTriangle(points);
    meshGroup.position.set(centroid.x - SPINNER_CENTER.x, SPINNER_CENTER.y - centroid.y, 0);

    const shellMaterial = new THREE.LineBasicMaterial({
      color: GOLD,
      transparent: true,
      opacity: 0,
    });
    const shell = new THREE.LineLoop(geometry, shellMaterial);
    shell.renderOrder = 2;
    meshGroup.add(shell);

    const trailMaterial = new THREE.LineBasicMaterial({
      color: GOLD,
      transparent: true,
      opacity: 0,
    });
    const trail = new THREE.LineLoop(geometry.clone(), trailMaterial);
    trail.position.z = 0.02;
    trail.renderOrder = 1;
    meshGroup.add(trail);

    group.add(meshGroup);
    return { geometry, phase, shell, trail };
  });

  return { group, triangles };
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function easeInOut(t) {
  const clamped = Math.min(1, Math.max(0, t));
  return 0.5 - (Math.cos(Math.PI * clamped) * 0.5);
}

function layerScale(progress) {
  if (progress < 0.5) {
    return lerp(1, 0.4, easeInOut(progress / 0.5));
  }
  return lerp(0.4, 0.16, easeInOut((progress - 0.5) / 0.5));
}

function shellOpacity(progress, phase) {
  const base = (phase / 19) * PHASE_WINDOW;
  if (progress <= base) return 0;
  if (progress < base + OPACITY_OFFSET) {
    return easeInOut((progress - base) / OPACITY_OFFSET);
  }
  return 1;
}

function trailProgress(progress, phase) {
  const base = (phase / 19) * PHASE_WINDOW;
  if (progress <= base) return 1;
  if (progress < base + FILL_OFFSET) {
    return 1 - easeInOut((progress - base) / FILL_OFFSET);
  }
  return 0;
}

function createHero(canvas) {
  const renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
    powerPreference: "high-performance",
  });
  renderer.setClearAlpha(0);

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -100, 100);
  camera.position.z = 10;

  const root = new THREE.Group();
  const layerA = createLayer();
  const layerB = createLayer();
  root.add(layerA.group);
  root.add(layerB.group);
  scene.add(root);

  const resizeObserver = new ResizeObserver(() => resize());
  resizeObserver.observe(canvas);
  if (canvas.parentElement) resizeObserver.observe(canvas.parentElement);

  let frameId = 0;
  let destroyed = false;
  const startedAt = performance.now();

  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(rect.width, rect.height, false);

    camera.left = -rect.width / 2;
    camera.right = rect.width / 2;
    camera.top = rect.height / 2;
    camera.bottom = -rect.height / 2;
    camera.updateProjectionMatrix();

    const heroScale = Math.min((rect.height * 0.9) / SPINNER_SIZE, (rect.width * (rect.width < 720 ? 0.38 : 0.24)) / SPINNER_SIZE);
    root.scale.setScalar(heroScale);
    root.position.set(rect.width * (rect.width < 720 ? 0.16 : 0.27), 0, 0);
  }

  function render(now) {
    if (destroyed) return;
    if (!canvas.isConnected) {
      destroy();
      return;
    }

    const elapsed = now - startedAt;
    const rotateProgress = (elapsed % ROTATION_MS) / ROTATION_MS;
    const cycleProgress = (elapsed % CYCLE_MS) / CYCLE_MS;

    root.rotation.z = -rotateProgress * Math.PI * 2;

    [
      { layer: layerA, phase: INSET_DELAY },
      { layer: layerB, phase: 0 },
    ].forEach(({ layer, phase }) => {
      const progress = (cycleProgress + phase) % 1;
      const scale = layerScale(progress);

      layer.group.scale.setScalar(scale);
      layer.triangles.forEach((triangle) => {
        const reveal = shellOpacity(progress, triangle.phase);
        triangle.shell.material.opacity = reveal;

        const trail = trailProgress(progress, triangle.phase);
        triangle.trail.scale.setScalar(0.16 + (0.84 * trail));
        triangle.trail.material.opacity = reveal * trail * 0.42;
      });
    });

    renderer.render(scene, camera);
    frameId = window.requestAnimationFrame(render);
  }

  function destroy() {
    if (destroyed) return;
    destroyed = true;
    window.cancelAnimationFrame(frameId);
    resizeObserver.disconnect();

    [layerA, layerB].forEach((layer) => {
      layer.triangles.forEach((triangle) => {
        triangle.geometry.dispose();
        triangle.trail.geometry.dispose();
        triangle.shell.material.dispose();
        triangle.trail.material.dispose();
      });
    });
    renderer.forceContextLoss();
    renderer.dispose();
  }

  resize();
  frameId = window.requestAnimationFrame(render);

  return { canvas, destroy };
}

function mountHero() {
  const canvas = document.getElementById("hero-3d");

  if (!canvas) {
    if (activeHero && !activeHero.canvas.isConnected) {
      activeHero.destroy();
      activeHero = null;
    }
    return;
  }

  if (activeHero?.canvas === canvas) return;

  if (activeHero) {
    activeHero.destroy();
    activeHero = null;
  }

  try {
    activeHero = createHero(canvas);
  } catch (error) {
    console.error("Failed to initialize hero spinner", error);
  }
}

function queueMountHero() {
  window.clearTimeout(mountTimer);
  window.cancelAnimationFrame(mountFrame);
  mountFrame = window.requestAnimationFrame(() => {
    mountFrame = window.requestAnimationFrame(() => {
      mountHero();
    });
  });
  mountTimer = window.setTimeout(() => {
    mountHero();
  }, 80);
}

document.addEventListener("DOMContentLoaded", queueMountHero);
document.body.addEventListener("htmx:afterSwap", (event) => {
  if (event.detail?.target?.id === "content") {
    queueMountHero();
  }
});
document.body.addEventListener("htmx:afterSettle", (event) => {
  if (event.detail?.target?.id === "content") {
    queueMountHero();
  }
});
window.addEventListener("pagehide", () => {
  window.clearTimeout(mountTimer);
  window.cancelAnimationFrame(mountFrame);
  if (activeHero) {
    activeHero.destroy();
    activeHero = null;
  }
});
