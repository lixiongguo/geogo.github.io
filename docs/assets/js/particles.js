class Particle {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
     this.mouse = {
      x: undefined,
      y: undefined,
      radius: 100
    };
    this.init();
    this.handleMouseMove();
  }

  init() {
    this.resize();
    window.addEventListener('resize', () => this.resize());
    
    // 初始化500个粒子
    for(let i = 0; i < 500; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        radius: Math.random() * 2,
        dx: (Math.random() - 0.5) * 0.5,
        dy: (Math.random() - 0.5) * 0.5
      });
    }
    
    this.animate();
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    for(let i = 0; i < this.particles.length; i++) {
      const particle = this.particles[i];
      
      // 鼠标交互
      if(this.mouse.x !== undefined && this.mouse.y !== undefined) {
        const dx = this.mouse.x - particle.x;
        const dy = this.mouse.y - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if(distance < this.mouse.radius) {
          particle.x -= dx / 20;
          particle.y -= dy / 20;
        }
      }
      
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(255,255,255,0.5)';
      this.ctx.fill();
      
      // 运动逻辑
      particle.x += particle.dx;
      particle.y += particle.dy;
      
      // 边界反弹
      if(particle.x < 0 || particle.x > this.canvas.width) particle.dx *= -1;
      if(particle.y < 0 || particle.y > this.canvas.height) particle.dy *= -1;
    }
    
    requestAnimationFrame(() => this.animate());
  }
  handleMouseMove() {
    this.canvas.addEventListener('mousemove', (event) => {
      this.mouse.x = event.x;
      this.mouse.y = event.y;
    });
    
    this.canvas.addEventListener('mouseleave', () => {
      this.mouse.x = undefined;
      this.mouse.y = undefined;
    });
  }
  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }
}

// 初始化
const canvas = document.getElementById('particle-canvas');
new Particle(canvas);
