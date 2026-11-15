import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { stepTo, validWaypoint } from './motion.mjs';

const viewport = document.querySelector('#viewport');
const ui = {
  connection: document.querySelector('#connection'),
  position: document.querySelector('#position'),
  target: document.querySelector('#target'),
  speed: document.querySelector('#speed'),
  progress: document.querySelector('#progress'),
  motion: document.querySelector('#motion-status'),
};

// 1. Scene 创建3D场景 Camera 观察角度 Renderer 把3D场景绘制到网页
const scene = new THREE.Scene();
scene.background = new THREE.Color('#0f2137');
scene.fog = new THREE.Fog('#0f2137', 24, 40);
const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 100);
camera.position.set(9, 9, 12);
camera.lookAt(0, 0, 0);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.shadowMap.enabled = true;
viewport.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 0, 0);

scene.add(new THREE.HemisphereLight('#b8d7ff', '#243146', 2.2));
const sun = new THREE.DirectionalLight('#ffffff', 3.2);
sun.position.set(4, 12, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -12;
sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;
sun.shadow.camera.bottom = -12;
scene.add(sun);

const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(30, 30),
  new THREE.MeshStandardMaterial({ color: '#20374b', roughness: 0.9 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.51;
floor.receiveShadow = true;
scene.add(floor);
const grid = new THREE.GridHelper(22, 22, '#386186', '#2d4867');
grid.position.y = -0.49;
scene.add(grid);
const axes = new THREE.AxesHelper(4);
axes.position.y = -0.48;
scene.add(axes);

// 添加灯光、地面、网格、方块
const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: '#46aaff', metalness: 0.18, roughness: 0.38 })
);
cube.castShadow = true;
scene.add(cube);

//管理运动路径
let queue = [];
let waypointIndex = 0;
let waypointTotal = 0;
let markerGroup = new THREE.Group();
scene.add(markerGroup);


function clearMarkers() {
  for (const child of [...markerGroup.children]) {
    markerGroup.remove(child);
    child.geometry?.dispose();
    child.material?.dispose();
  }
}

function showPath(points) {
  clearMarkers();
  for (const point of points) {
    const dot = new THREE.Mesh(
      new THREE.SphereGeometry(0.13, 12, 10),
      new THREE.MeshBasicMaterial({ color: '#ffbf5b' })
    );
    dot.position.set(point.x, point.y, point.z);
    markerGroup.add(dot);
  }
}

function acceptWaypoints(points) {
  queue = points.map(point => ({ ...point }));
  waypointIndex = 0;
  waypointTotal = queue.length;
  showPath(points);
  ui.motion.textContent = `正在前往 ${queue.length} 个路径点`;
  updateUI();
}

function updateUI() {
  ui.position.textContent = [cube.position.x, cube.position.y, cube.position.z]
    .map(n => n.toFixed(2)).join(', ');
  ui.progress.textContent = `${waypointIndex} / ${waypointTotal}`;
  if (queue.length) {
    const p = queue[0];
    ui.target.textContent = `(${p.x}, ${p.y}, ${p.z})`;
    ui.speed.textContent = `${p.speed.toFixed(2)} 单位/秒`;
  } else {
    ui.target.textContent = waypointTotal ? '已到达所有目标' : '等待指令';
    ui.speed.textContent = '0.00 单位/秒';
  }
}

// WebSocket 接收 C++ 控制命令
function connect() {
  const socket = new WebSocket('ws://127.0.0.1:9002');
  socket.addEventListener('open', () => {
    ui.connection.textContent = '● WebSocket 已连接';
    ui.connection.className = 'status online';
  });
  socket.addEventListener('message', (event) => {
    let msg;
    try { msg = JSON.parse(event.data); } catch { return; }
    if (msg.type === 'move' && validWaypoint(msg.target)) {
      acceptWaypoints([msg.target]);
    } else if (msg.type === 'path' && Array.isArray(msg.waypoints) &&
               msg.waypoints.length >= 1 && msg.waypoints.length <= 20 &&
               msg.waypoints.every(validWaypoint)) {
      acceptWaypoints(msg.waypoints);
    }
  });
  socket.addEventListener('close', () => {
    ui.connection.textContent = '● WebSocket 已断开';
    ui.connection.className = 'status offline';
    window.setTimeout(connect, 2000);
  });
  socket.addEventListener('error', () => socket.close());
}
connect();


// 控制方块移动
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05); 
  if (queue.length) {
    const p = queue[0];
    const result = stepTo(
      [cube.position.x, cube.position.y, cube.position.z],
      [p.x, p.y, p.z], p.speed, dt
    );
    cube.position.set(...result.position);
    if (result.arrived) {
      queue.shift();
      waypointIndex++;
      if (!queue.length) ui.motion.textContent = '已完成整条路径';
      else ui.motion.textContent = `已到达路径点 ${waypointIndex}，前往下一个点`;
    }
  }
  controls.update();
  updateUI();
  renderer.render(scene, camera);
}


//自适应窗口大小
const resizeObserver = new ResizeObserver(() => {
  const width = Math.max(1, viewport.clientWidth);
  const height = Math.max(1, viewport.clientHeight);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
});
resizeObserver.observe(viewport);
animate();
