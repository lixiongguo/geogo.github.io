// 波函数塌缩（WFC）算法实现 - 随机地图生成

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// 地形类型
const TILE_TYPES = {
    WATER: 0,
    LAND: 1,
    MOUNTAIN: 2,
    FOREST: 3
};

const TILE_COLORS = {
    0: '#4A90E2', // 水域 - 蓝色
    1: '#7ED321', // 陆地 - 绿色
    2: '#8B572A', // 山脉 - 棕色
    3: '#417505'  // 森林 - 深绿色
};

let grid = [];
let gridSize = 50;
let isGenerating = false;

// 初始化网格（所有单元格都是叠加态）
function initGrid() {
    grid = [];
    for (let y = 0; y < gridSize; y++) {
        grid[y] = [];
        for (let x = 0; x < gridSize; x++) {
            grid[y][x] = {
                possibilities: [0, 1, 2, 3], // 所有可能的地形
                collapsed: false
            };
        }
    }
}

// 计算单元格的熵（可能性数量）
function getEntropy(cell) {
    return cell.possibilities.length;
}

// 选择熵最小的单元格
function selectCell() {
    let minEntropy = Infinity;
    let candidates = [];
    
    for (let y = 0; y < gridSize; y++) {
        for (let x = 0; x < gridSize; x++) {
            if (!grid[y][x].collapsed) {
                const entropy = getEntropy(grid[y][x]);
                if (entropy < minEntropy) {
                    minEntropy = entropy;
                    candidates = [{ x, y }];
                } else if (entropy === minEntropy) {
                    candidates.push({ x, y });
                }
            }
        }
    }
    
    // 随机选择一个候选单元格
    return candidates[Math.floor(Math.random() * candidates.length)];
}

// 塌缩单元格（随机选择一个可能性）
function collapseCell(x, y) {
    const cell = grid[y][x];
    const chosen = cell.possibilities[Math.floor(Math.random() * cell.possibilities.length)];
    cell.possibilities = [chosen];
    cell.collapsed = true;
}

// 传播约束到相邻单元格
function propagate(x, y) {
    const queue = [{ x, y }];
    const directions = [[0, 1], [0, -1], [1, 0], [-1, 0]];
    
    while (queue.length > 0) {
        const current = queue.shift();
        const cell = grid[current.y][current.x];
        const validTypes = cell.possibilities;
        
        for (const [dx, dy] of directions) {
            const nx = current.x + dx;
            const ny = current.y + dy;
            
            if (nx >= 0 && nx < gridSize && ny >= 0 && ny < gridSize) {
                const neighbor = grid[ny][nx];
                if (!neighbor.collapsed) {
                    // 简化：只保留与当前单元格相容的可能性
                    // 实际WFC应该有更复杂的相容性规则
                    const newPossibilities = neighbor.possibilities.filter(p => 
                        validTypes.includes(p)
                    );
                    
                    if (newPossibilities.length < neighbor.possibilities.length) {
                        neighbor.possibilities = newPossibilities;
                        queue.push({ x: nx, y: ny });
                    }
                }
            }
        }
    }
}

// 绘制网格
function drawGrid() {
    const cellSize = canvas.width / gridSize;
    
    for (let y = 0; y < gridSize; y++) {
        for (let x = 0; x < gridSize; x++) {
            const cell = grid[y][x];
            
            if (cell.collapsed) {
                ctx.fillStyle = TILE_COLORS[cell.possibilities[0]];
            } else {
                // 未塌缩的单元格显示为灰色
                ctx.fillStyle = '#ddd';
            }
            
            ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 0.5;
            ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
    }
}

// 生成地图（WFC算法主循环）
function generateMap() {
    if (isGenerating) return;
    
    isGenerating = true;
    gridSize = parseInt(document.getElementById('gridSize').value);
    const iterations = parseInt(document.getElementById('iterations').value);
    
    initGrid();
    
    let step = 0;
    const interval = setInterval(() => {
        if (step >= iterations || allCollapsed()) {
            clearInterval(interval);
            isGenerating = false;
            drawGrid();
            return;
        }
        
        // 选择熵最小的单元格
        const cell = selectCell();
        if (!cell) {
            clearInterval(interval);
            isGenerating = false;
            return;
        }
        
        // 塌缩
        collapseCell(cell.x, cell.y);
        
        // 传播
        propagate(cell.x, cell.y);
        
        // 绘制
        drawGrid();
        
        step++;
    }, 10); // 每10ms执行一步
}

// 检查是否所有单元格都已塌缩
function allCollapsed() {
    for (let y = 0; y < gridSize; y++) {
        for (let x = 0; x < gridSize; x++) {
            if (!grid[y][x].collapsed) {
                return false;
            }
        }
    }
    return true;
}

// 清空地图
function clearMap() {
    initGrid();
    drawGrid();
}

// 初始化
initGrid();
drawGrid();
