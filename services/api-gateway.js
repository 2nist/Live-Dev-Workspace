/**
 * API Gateway - Central service coordination and routing
 * Professional-grade microservices architecture
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { createProxyMiddleware } = require('http-proxy-middleware');
const jwt = require('jsonwebtoken');
const WebSocket = require('ws');
const EventEmitter = require('events');

class APIGateway extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.app = express();
        this.services = new Map();
        this.healthChecks = new Map();
        this.metrics = {
            requests: 0,
            errors: 0,
            latency: [],
            activeConnections: 0
        };
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupWebSocket();
        this.setupHealthChecks();
    }

    setupMiddleware() {
        // Security
        this.app.use(helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
                    styleSrc: ["'self'", "'unsafe-inline'"],
                    imgSrc: ["'self'", "data:", "blob:"],
                    connectSrc: ["'self'", "ws:", "wss:"]
                }
            }
        }));

        // CORS
        this.app.use(cors({
            origin: process.env.FRONTEND_URL || 'http://localhost:3000',
            credentials: true,
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        }));

        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 1000, // requests per window
            message: {
                error: 'Too many requests',
                retryAfter: '15 minutes'
            },
            standardHeaders: true,
            legacyHeaders: false
        });
        this.app.use(limiter);

        // Body parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

        // Request logging and metrics
        this.app.use((req, res, next) => {
            const startTime = Date.now();
            this.metrics.requests++;
            
            res.on('finish', () => {
                const duration = Date.now() - startTime;
                this.metrics.latency.push(duration);
                
                // Keep only last 1000 measurements
                if (this.metrics.latency.length > 1000) {
                    this.metrics.latency = this.metrics.latency.slice(-1000);
                }
                
                if (res.statusCode >= 400) {
                    this.metrics.errors++;
                }
            });
            
            next();
        });
    }

    setupRoutes() {
        // Authentication middleware
        const authenticateToken = (req, res, next) => {
            const authHeader = req.headers['authorization'];
            const token = authHeader && authHeader.split(' ')[1];

            if (!token) {
                return res.status(401).json({ error: 'Access token required' });
            }

            jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret', (err, user) => {
                if (err) {
                    return res.status(403).json({ error: 'Invalid token' });
                }
                req.user = user;
                next();
            });
        };

        // Health check
        this.app.get('/health', (req, res) => {
            const healthStatus = {
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                services: Object.fromEntries(this.healthChecks),
                metrics: {
                    ...this.metrics,
                    avgLatency: this.metrics.latency.length > 0 
                        ? this.metrics.latency.reduce((a, b) => a + b) / this.metrics.latency.length 
                        : 0
                }
            };
            res.json(healthStatus);
        });

        // API documentation
        this.app.get('/api/docs', (req, res) => {
            res.json({
                name: 'ALSE API Gateway',
                version: '2.0.0',
                description: 'Professional-grade Ableton Live development platform',
                endpoints: {
                    '/api/v1/patches': 'Patch management service',
                    '/api/v1/live': 'Ableton Live bridge service', 
                    '/api/v1/templates': 'Template management service',
                    '/api/v1/ai': 'AI assistance service',
                    '/api/v1/test': 'Testing and validation service',
                    '/ws': 'WebSocket real-time communication'
                },
                authentication: 'Bearer token required for protected endpoints',
                rateLimit: '1000 requests per 15 minutes'
            });
        });

        // Service proxies
        this.setupServiceProxy('/api/v1/patches', 'patch-service', 8001);
        this.setupServiceProxy('/api/v1/live', 'live-bridge', 8002);
        this.setupServiceProxy('/api/v1/templates', 'template-service', 8003);
        this.setupServiceProxy('/api/v1/ai', 'ai-service', 8004);
        this.setupServiceProxy('/api/v1/test', 'test-service', 8005);

        // Error handling
        this.app.use((err, req, res, next) => {
            console.error('Gateway error:', err);
            this.metrics.errors++;
            
            res.status(err.status || 500).json({
                error: 'Internal server error',
                message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong',
                timestamp: new Date().toISOString()
            });
        });

        // 404 handler
        this.app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Endpoint not found',
                path: req.originalUrl,
                method: req.method,
                availableEndpoints: [
                    '/health',
                    '/api/docs',
                    '/api/v1/patches',
                    '/api/v1/live',
                    '/api/v1/templates', 
                    '/api/v1/ai',
                    '/api/v1/test'
                ]
            });
        });
    }

    setupServiceProxy(path, serviceName, port) {
        const proxyOptions = {
            target: `http://localhost:${port}`,
            changeOrigin: true,
            pathRewrite: {
                [`^${path}`]: ''
            },
            onError: (err, req, res) => {
                console.error(`Proxy error for ${serviceName}:`, err.message);
                this.healthChecks.set(serviceName, 'unhealthy');
                
                res.status(503).json({
                    error: 'Service unavailable',
                    service: serviceName,
                    message: 'The requested service is currently unavailable'
                });
            },
            onProxyReq: (proxyReq, req, res) => {
                // Add service identification header
                proxyReq.setHeader('X-Gateway-Service', serviceName);
                proxyReq.setHeader('X-Request-ID', `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
            },
            onProxyRes: (proxyRes, req, res) => {
                // Mark service as healthy on successful response
                this.healthChecks.set(serviceName, 'healthy');
                
                // Add response headers
                proxyRes.headers['X-Gateway-Response'] = 'true';
                proxyRes.headers['X-Service-Name'] = serviceName;
            }
        };

        this.app.use(path, createProxyMiddleware(proxyOptions));
        
        // Register service
        this.services.set(serviceName, { port, path, status: 'unknown' });
        console.log(`Registered service proxy: ${serviceName} -> ${path} (port ${port})`);
    }

    setupWebSocket() {
        this.wss = new WebSocket.Server({ 
            port: 8080,
            perMessageDeflate: false,
            maxPayload: 1024 * 1024 // 1MB max message size
        });

        this.wss.on('connection', (ws, req) => {
            this.metrics.activeConnections++;
            console.log(`WebSocket connection established. Active: ${this.metrics.activeConnections}`);

            // Connection metadata
            ws.id = `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            ws.isAlive = true;
            ws.subscribedChannels = new Set();

            // Authentication for WebSocket
            ws.on('message', (message) => {
                try {
                    const data = JSON.parse(message);
                    
                    if (data.type === 'authenticate') {
                        this.authenticateWebSocket(ws, data.token);
                    } else if (data.type === 'subscribe') {
                        this.handleSubscription(ws, data.channel);
                    } else if (data.type === 'unsubscribe') {
                        this.handleUnsubscription(ws, data.channel);
                    } else if (ws.authenticated) {
                        this.handleWebSocketMessage(ws, data);
                    } else {
                        ws.send(JSON.stringify({
                            type: 'error',
                            message: 'Authentication required'
                        }));
                    }
                } catch (error) {
                    console.error('WebSocket message error:', error);
                    ws.send(JSON.stringify({
                        type: 'error',
                        message: 'Invalid message format'
                    }));
                }
            });

            // Handle connection close
            ws.on('close', () => {
                this.metrics.activeConnections--;
                console.log(`WebSocket connection closed. Active: ${this.metrics.activeConnections}`);
            });

            // Ping/pong for connection health
            ws.on('pong', () => {
                ws.isAlive = true;
            });

            // Send welcome message
            ws.send(JSON.stringify({
                type: 'welcome',
                message: 'Connected to ALSE Gateway',
                connectionId: ws.id,
                timestamp: new Date().toISOString()
            }));
        });

        // Health check ping interval
        const pingInterval = setInterval(() => {
            this.wss.clients.forEach((ws) => {
                if (!ws.isAlive) {
                    ws.terminate();
                    return;
                }
                
                ws.isAlive = false;
                ws.ping();
            });
        }, 30000);

        this.wss.on('close', () => {
            clearInterval(pingInterval);
        });

        console.log('WebSocket server listening on port 8080');
    }

    authenticateWebSocket(ws, token) {
        try {
            const user = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret');
            ws.authenticated = true;
            ws.user = user;
            
            ws.send(JSON.stringify({
                type: 'authenticated',
                user: { id: user.id, username: user.username },
                timestamp: new Date().toISOString()
            }));
        } catch (error) {
            ws.send(JSON.stringify({
                type: 'authentication_failed',
                message: 'Invalid token'
            }));
        }
    }

    handleSubscription(ws, channel) {
        if (!ws.authenticated) {
            ws.send(JSON.stringify({
                type: 'error', 
                message: 'Authentication required for subscriptions'
            }));
            return;
        }

        ws.subscribedChannels.add(channel);
        ws.send(JSON.stringify({
            type: 'subscribed',
            channel,
            timestamp: new Date().toISOString()
        }));
        
        console.log(`Client ${ws.id} subscribed to ${channel}`);
    }

    handleUnsubscription(ws, channel) {
        ws.subscribedChannels.delete(channel);
        ws.send(JSON.stringify({
            type: 'unsubscribed',
            channel,
            timestamp: new Date().toISOString()
        }));
        
        console.log(`Client ${ws.id} unsubscribed from ${channel}`);
    }

    handleWebSocketMessage(ws, data) {
        // Broadcast to relevant services or other clients
        this.emit('websocket-message', {
            connectionId: ws.id,
            user: ws.user,
            data,
            timestamp: new Date().toISOString()
        });
    }

    broadcast(channel, message) {
        const payload = JSON.stringify({
            type: 'broadcast',
            channel,
            data: message,
            timestamp: new Date().toISOString()
        });

        this.wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN && 
                client.subscribedChannels.has(channel)) {
                client.send(payload);
            }
        });
    }

    setupHealthChecks() {
        // Check service health every 30 seconds
        setInterval(async () => {
            for (const [serviceName, serviceInfo] of this.services) {
                try {
                    const response = await fetch(`http://localhost:${serviceInfo.port}/health`, {
                        timeout: 5000
                    });
                    
                    if (response.ok) {
                        this.healthChecks.set(serviceName, 'healthy');
                    } else {
                        this.healthChecks.set(serviceName, 'unhealthy');
                    }
                } catch (error) {
                    this.healthChecks.set(serviceName, 'unreachable');
                }
            }
        }, 30000);
    }

    start(port = 8000) {
        return new Promise((resolve, reject) => {
            this.server = this.app.listen(port, (err) => {
                if (err) {
                    reject(err);
                    return;
                }
                
                console.log(`🚀 API Gateway running on port ${port}`);
                console.log(`📊 Health endpoint: http://localhost:${port}/health`);
                console.log(`📚 API docs: http://localhost:${port}/api/docs`);
                console.log(`🔌 WebSocket server: ws://localhost:8080`);
                
                this.emit('started', { port });
                resolve(this);
            });
        });
    }

    stop() {
        return new Promise((resolve) => {
            if (this.server) {
                this.server.close(() => {
                    console.log('API Gateway stopped');
                    resolve();
                });
            }
            
            if (this.wss) {
                this.wss.close(() => {
                    console.log('WebSocket server stopped');
                });
            }
        });
    }
}

module.exports = APIGateway;

// Start gateway if run directly
if (require.main === module) {
    const gateway = new APIGateway({
        environment: process.env.NODE_ENV || 'development',
        jwtSecret: process.env.JWT_SECRET || 'fallback-secret',
        frontendUrl: process.env.FRONTEND_URL || 'http://localhost:3000'
    });

    gateway.start(process.env.PORT || 8000).catch(console.error);

    // Graceful shutdown
    process.on('SIGTERM', async () => {
        console.log('Received SIGTERM, shutting down gracefully');
        await gateway.stop();
        process.exit(0);
    });

    process.on('SIGINT', async () => {
        console.log('Received SIGINT, shutting down gracefully');
        await gateway.stop();
        process.exit(0);
    });
}
