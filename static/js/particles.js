/**
 * Particle Animation System
 * 动态粒子背景效果 - 参考 OrcaTerm/腾讯云风格
 *
 * 功能：
 * - 粒子漂浮动画
 * - 粒子间连线
 * - 鼠标交互效果
 * - 自动适应窗口大小
 */

(function() {
    'use strict';

    // 粒子系统配置 - 深色终端风格
    const CONFIG = {
        // 粒子数量（根据屏幕大小自动调整）
        particleCount: {
            base: 100,
            density: 0.00015
        },
        // 粒子颜色 - 深色/终端风格
        colors: {
            primary: 'rgba(200, 200, 200, 0.8)',      // 浅灰白
            secondary: 'rgba(150, 150, 150, 0.7)',    // 中灰
            accent: 'rgba(100, 100, 100, 0.6)',       // 深灰
            highlight: 'rgba(0, 255, 136, 0.9)',      // 终端绿高亮
            cyan: 'rgba(0, 200, 255, 0.8)',           // 青色
        },
        // 粒子大小范围
        size: {
            min: 1,
            max: 3
        },
        // 粒子速度
        speed: {
            min: 0.3,
            max: 1.0
        },
        // 连线配置
        lines: {
            enable: true,
            distance: 120,
            opacity: 0.12
        },
        // 鼠标交互
        mouse: {
            enable: true,
            radius: 200,
            mode: 'grab'  // 'grab' 或 'repulse'
        },
        // 动画帧率
        fps: 60
    };

    // 粒子类
    class Particle {
        constructor(canvas, config) {
            this.canvas = canvas;
            this.config = config;
            this.reset();
        }

        reset() {
            this.x = Math.random() * this.canvas.width;
            this.y = Math.random() * this.canvas.height;
            this.size = Math.random() * (this.config.size.max - this.config.size.min) + this.config.size.min;
            this.speedX = (Math.random() - 0.5) * (this.config.speed.max - this.config.speed.min) + this.config.speed.min;
            this.speedY = (Math.random() - 0.5) * (this.config.speed.max - this.config.speed.min) + this.config.speed.min;

            // 随机选择颜色
            const colorKeys = Object.keys(this.config.colors);
            const randomColor = colorKeys[Math.floor(Math.random() * colorKeys.length)];
            this.color = this.config.colors[randomColor];

            this.opacity = Math.random() * 0.5 + 0.3;
            this.originalSize = this.size;
        }

        update(mouse) {
            // 移动粒子
            this.x += this.speedX;
            this.y += this.speedY;

            // 边界检测
            if (this.x < 0 || this.x > this.canvas.width) {
                this.speedX = -this.speedX;
            }
            if (this.y < 0 || this.y > this.canvas.height) {
                this.speedY = -this.speedY;
            }

            // 鼠标交互
            if (this.config.mouse.enable && mouse.x !== null) {
                const dx = this.x - mouse.x;
                const dy = this.y - mouse.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.config.mouse.radius) {
                    const force = (this.config.mouse.radius - distance) / this.config.mouse.radius;

                    if (this.config.mouse.mode === 'repulse') {
                        // 排斥效果
                        this.x += dx * force * 0.02;
                        this.y += dy * force * 0.02;
                    } else {
                        // 吸引效果
                        this.size = this.originalSize + force * 2;
                    }
                } else {
                    this.size = this.originalSize;
                }
            }
        }

        draw(ctx) {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.opacity;
            ctx.fill();
            ctx.globalAlpha = 1;
        }
    }

    // 粒子系统类
    class ParticleSystem {
        constructor(containerId, options = {}) {
            this.container = document.getElementById(containerId);
            if (!this.container) {
                console.warn(`Particle container "${containerId}" not found`);
                return;
            }

            this.config = { ...CONFIG, ...options };
            this.particles = [];
            this.mouse = { x: null, y: null };
            this.animationId = null;
            this.isRunning = false;

            this.init();
        }

        init() {
            this.createCanvas();
            this.createParticles();
            this.bindEvents();
            this.start();
        }

        createCanvas() {
            this.canvas = document.createElement('canvas');
            this.canvas.className = 'particle-canvas';
            this.ctx = this.canvas.getContext('2d');
            this.container.appendChild(this.canvas);
            this.resize();
        }

        resize() {
            const rect = this.container.getBoundingClientRect();
            this.canvas.width = rect.width;
            this.canvas.height = rect.height;
            this.canvas.style.width = rect.width + 'px';
            this.canvas.style.height = rect.height + 'px';

            // 根据屏幕大小调整粒子数量
            const area = this.canvas.width * this.canvas.height;
            const count = Math.floor(this.config.particleCount.base + area * this.config.particleCount.density);

            // 如果粒子数量变化较大，重新创建粒子
            if (Math.abs(count - this.particles.length) > 20) {
                this.particles = [];
                this.createParticles(count);
            }
        }

        createParticles(count = null) {
            if (count === null) {
                const area = this.canvas.width * this.canvas.height;
                count = Math.floor(this.config.particleCount.base + area * this.config.particleCount.density);
            }

            for (let i = 0; i < count; i++) {
                this.particles.push(new Particle(this.canvas, this.config));
            }
        }

        bindEvents() {
            // 鼠标移动
            this.container.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                this.mouse.x = e.clientX - rect.left;
                this.mouse.y = e.clientY - rect.top;
            });

            // 鼠标离开
            this.container.addEventListener('mouseleave', () => {
                this.mouse.x = null;
                this.mouse.y = null;
            });

            // 窗口大小改变
            let resizeTimeout;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => this.resize(), 100);
            });
        }

        drawLines() {
            if (!this.config.lines.enable) return;

            for (let i = 0; i < this.particles.length; i++) {
                for (let j = i + 1; j < this.particles.length; j++) {
                    const dx = this.particles[i].x - this.particles[j].x;
                    const dy = this.particles[i].y - this.particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < this.config.lines.distance) {
                        const opacity = (1 - distance / this.config.lines.distance) * this.config.lines.opacity;
                        this.ctx.beginPath();
                        this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                        this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                        this.ctx.strokeStyle = `rgba(150, 150, 150, ${opacity})`;
                        this.ctx.lineWidth = 0.5;
                        this.ctx.stroke();
                    }
                }
            }

            // 鼠标连线 - 使用终端绿色高亮
            if (this.config.mouse.enable && this.mouse.x !== null) {
                for (let i = 0; i < this.particles.length; i++) {
                    const dx = this.particles[i].x - this.mouse.x;
                    const dy = this.particles[i].y - this.mouse.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < this.config.mouse.radius) {
                        const opacity = (1 - distance / this.config.mouse.radius) * 0.4;
                        this.ctx.beginPath();
                        this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                        this.ctx.lineTo(this.mouse.x, this.mouse.y);
                        this.ctx.strokeStyle = `rgba(0, 255, 136, ${opacity})`;
                        this.ctx.lineWidth = 1;
                        this.ctx.stroke();
                    }
                }
            }
        }

        animate() {
            if (!this.isRunning) return;

            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

            // 更新和绘制粒子
            for (const particle of this.particles) {
                particle.update(this.mouse);
                particle.draw(this.ctx);
            }

            // 绘制连线
            this.drawLines();

            this.animationId = requestAnimationFrame(() => this.animate());
        }

        start() {
            if (this.isRunning) return;
            this.isRunning = true;
            this.animate();
        }

        stop() {
            this.isRunning = false;
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
                this.animationId = null;
            }
        }

        destroy() {
            this.stop();
            if (this.canvas && this.canvas.parentNode) {
                this.canvas.parentNode.removeChild(this.canvas);
            }
        }
    }

    // 浮动光晕效果
    class FloatingGlow {
        constructor(containerId) {
            this.container = document.getElementById(containerId);
            if (!this.container) return;

            this.createGlows();
        }

        createGlows() {
            const glowColors = [
                'rgba(0, 82, 217, 0.1)',
                'rgba(38, 111, 232, 0.08)',
                'rgba(0, 168, 112, 0.06)'
            ];

            for (let i = 0; i < 3; i++) {
                const glow = document.createElement('div');
                glow.className = 'floating-glow';
                glow.style.cssText = `
                    position: absolute;
                    width: ${200 + Math.random() * 200}px;
                    height: ${200 + Math.random() * 200}px;
                    background: radial-gradient(circle, ${glowColors[i]} 0%, transparent 70%);
                    border-radius: 50%;
                    pointer-events: none;
                    animation: float${i + 1} ${15 + i * 5}s ease-in-out infinite;
                    left: ${Math.random() * 80}%;
                    top: ${Math.random() * 80}%;
                `;
                this.container.appendChild(glow);
            }
        }
    }

    // 添加浮动动画关键帧
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float1 {
            0%, 100% { transform: translate(0, 0) scale(1); }
            25% { transform: translate(50px, -30px) scale(1.1); }
            50% { transform: translate(100px, 20px) scale(0.9); }
            75% { transform: translate(30px, 50px) scale(1.05); }
        }
        @keyframes float2 {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(-40px, 60px) scale(1.1); }
            66% { transform: translate(80px, -20px) scale(0.95); }
        }
        @keyframes float3 {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(-60px, -40px) scale(1.15); }
        }
    `;
    document.head.appendChild(style);

    // 暴露到全局
    window.ParticleSystem = ParticleSystem;
    window.FloatingGlow = FloatingGlow;

    // 自动初始化
    document.addEventListener('DOMContentLoaded', function() {
        // 初始化粒子系统
        const particleContainer = document.getElementById('particles-container');
        if (particleContainer) {
            window.particleSystem = new ParticleSystem('particles-container');
        }

        // 初始化浮动光晕
        const glowContainer = document.getElementById('glow-container');
        if (glowContainer) {
            window.floatingGlow = new FloatingGlow('glow-container');
        }
    });

})();
