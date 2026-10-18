import * as THREE from 'three';

const CELL_SIZE = 1;
const WALL_HEIGHT = 1.2;
const MAZE_SIZE = 15;
const PLAYER_RADIUS = 0.25;
const MOVE_SPEED = 0.06;

function generateMaze(size) {
    const maze = Array.from({ length: size }, () => Array(size).fill(1));
    const stack = [];
    const start = { x: 1, z: 1 };
    maze[start.z][start.x] = 0;
    stack.push(start);

    const dirs = [
        { x: 0, z: -2 }, { x: 0, z: 2 },
        { x: -2, z: 0 }, { x: 2, z: 0 },
    ];

    while (stack.length) {
        const current = stack[stack.length - 1];
        const neighbors = [];
        for (const d of dirs) {
            const nx = current.x + d.x;
            const nz = current.z + d.z;
            if (nx > 0 && nx < size - 1 && nz > 0 && nz < size - 1 && maze[nz][nx] === 1) {
                neighbors.push({ x: nx, z: nz, dx: d.x / 2, dz: d.z / 2 });
            }
        }
        if (neighbors.length) {
            const next = neighbors[Math.floor(Math.random() * neighbors.length)];
            maze[next.z][next.x] = 0;
            maze[current.z + next.dz][current.x + next.dx] = 0;
            stack.push({ x: next.x, z: next.z });
        } else {
            stack.pop();
        }
    }
    return maze;
}

class MazeGame {
    constructor() {
        this.canvas = document.getElementById('maze');
        this.winEl = document.getElementById('win');
        this.resetBtn = document.getElementById('reset');
        this.keys = {};
        this.won = false;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0f172a);

        this.camera = new THREE.PerspectiveCamera(75, this.canvas.width / this.canvas.height, 0.1, 100);

        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        this.renderer.setSize(this.canvas.width, this.canvas.height);
        this.renderer.shadowMap.enabled = true;

        this.initLights();
        this.initGame();
        this.bindEvents();
        this.animate();
    }

    initLights() {
        const ambient = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambient);
        const dir = new THREE.DirectionalLight(0xffffff, 0.8);
        dir.position.set(10, 20, 10);
        dir.castShadow = true;
        this.scene.add(dir);
    }

    clearScene() {
        for (let i = this.scene.children.length - 1; i >= 0; i--) {
            const obj = this.scene.children[i];
            if (obj.isMesh) this.scene.remove(obj);
        }
        this.initLights();
    }

    initGame() {
        this.maze = generateMaze(MAZE_SIZE);
        this.clearScene();
        this.won = false;
        this.winEl.classList.add('hidden');

        const wallGeo = new THREE.BoxGeometry(CELL_SIZE, WALL_HEIGHT, CELL_SIZE);
        const wallMat = new THREE.MeshStandardMaterial({ color: 0x475569 });
        const floorGeo = new THREE.PlaneGeometry(CELL_SIZE, CELL_SIZE);
        const floorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b });

        this.walls = [];
        for (let z = 0; z < MAZE_SIZE; z++) {
            for (let x = 0; x < MAZE_SIZE; x++) {
                const fx = x * CELL_SIZE;
                const fz = z * CELL_SIZE;
                if (this.maze[z][x] === 1) {
                    const wall = new THREE.Mesh(wallGeo, wallMat);
                    wall.position.set(fx, WALL_HEIGHT / 2, fz);
                    wall.castShadow = true;
                    wall.receiveShadow = true;
                    this.scene.add(wall);
                    this.walls.push(wall);
                } else {
                    const floor = new THREE.Mesh(floorGeo, floorMat);
                    floor.rotation.x = -Math.PI / 2;
                    floor.position.set(fx, 0, fz);
                    floor.receiveShadow = true;
                    this.scene.add(floor);
                }
            }
        }

        this.playerPos = new THREE.Vector3(1 * CELL_SIZE, 0.5, 1 * CELL_SIZE);
        this.camera.position.copy(this.playerPos);
        this.camera.rotation.y = Math.PI / 2;

        this.goalX = MAZE_SIZE - 2;
        this.goalZ = MAZE_SIZE - 2;
        const goalGeo = new THREE.BoxGeometry(CELL_SIZE * 0.6, CELL_SIZE * 0.6, CELL_SIZE * 0.6);
        const goalMat = new THREE.MeshStandardMaterial({ color: 0x34d399, emissive: 0x10b981, emissiveIntensity: 0.5 });
        this.goal = new THREE.Mesh(goalGeo, goalMat);
        this.goal.position.set(this.goalX * CELL_SIZE, 0.5, this.goalZ * CELL_SIZE);
        this.scene.add(this.goal);
    }

    bindEvents() {
        document.addEventListener('keydown', e => {
            this.keys[e.key.toLowerCase()] = true;
            if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].includes(e.key.toLowerCase())) {
                e.preventDefault();
            }
        });
        document.addEventListener('keyup', e => {
            this.keys[e.key.toLowerCase()] = false;
        });
        this.resetBtn.addEventListener('click', () => this.initGame());

        const resize = () => {
            const parent = this.canvas.parentElement;
            const width = Math.min(800, parent.clientWidth);
            const height = Math.floor(width * 0.75);
            this.canvas.width = width;
            this.canvas.height = height;
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(width, height);
        };
        window.addEventListener('resize', resize);
        resize();
    }

    isWall(x, z) {
        const gx = Math.round(x / CELL_SIZE);
        const gz = Math.round(z / CELL_SIZE);
        if (gx < 0 || gx >= MAZE_SIZE || gz < 0 || gz >= MAZE_SIZE) return true;
        return this.maze[gz][gx] === 1;
    }

    canMove(pos) {
        const offsets = [
            { x: -PLAYER_RADIUS, z: -PLAYER_RADIUS },
            { x: PLAYER_RADIUS, z: -PLAYER_RADIUS },
            { x: -PLAYER_RADIUS, z: PLAYER_RADIUS },
            { x: PLAYER_RADIUS, z: PLAYER_RADIUS },
        ];
        return offsets.every(o => !this.isWall(pos.x + o.x, pos.z + o.z));
    }

    updateMovement() {
        if (this.won) return;
        const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(this.camera.quaternion);
        forward.y = 0;
        forward.normalize();
        const right = new THREE.Vector3(1, 0, 0).applyQuaternion(this.camera.quaternion);
        right.y = 0;
        right.normalize();

        const move = new THREE.Vector3();
        if (this.keys['w'] || this.keys['arrowup']) move.add(forward);
        if (this.keys['s'] || this.keys['arrowdown']) move.sub(forward);
        if (this.keys['a'] || this.keys['arrowleft']) move.sub(right);
        if (this.keys['d'] || this.keys['arrowright']) move.add(right);

        if (move.lengthSq() === 0) return;
        move.normalize().multiplyScalar(MOVE_SPEED);

        const nextX = this.playerPos.clone();
        nextX.x += move.x;
        if (this.canMove(nextX)) this.playerPos.x = nextX.x;

        const nextZ = this.playerPos.clone();
        nextZ.z += move.z;
        if (this.canMove(nextZ)) this.playerPos.z = nextZ.z;

        this.camera.position.x = this.playerPos.x;
        this.camera.position.z = this.playerPos.z;

        const dx = this.goalX * CELL_SIZE - this.playerPos.x;
        const dz = this.goalZ * CELL_SIZE - this.playerPos.z;
        if (Math.hypot(dx, dz) < 0.6) {
            this.won = true;
            this.winEl.classList.remove('hidden');
        }
    }

    updateCameraRotation() {
        if (this.keys['arrowleft']) this.camera.rotation.y += 0.04;
        if (this.keys['arrowright']) this.camera.rotation.y -= 0.04;
        this.camera.rotation.x = 0;
        this.camera.rotation.z = 0;
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.updateMovement();
        this.updateCameraRotation();
        this.renderer.render(this.scene, this.camera);
    }
}

new MazeGame();
