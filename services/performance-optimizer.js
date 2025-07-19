/**
 * Performance Optimization Service
 * Canvas virtualization, Web Workers, and real-time metrics
 */

const EventEmitter = require('events');
const { Worker } = require('worker_threads');
const path = require('path');

class PerformanceOptimizer extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.options = {
            maxCanvasObjects: 1000,
            virtualizationThreshold: 500,
            workerPoolSize: 4,
            metricsInterval: 1000,
            memoryThreshold: 100 * 1024 * 1024, // 100MB
            fpsTarget: 60,
            ...options
        };

        this.metrics = {
            fps: 0,
            frameTime: 0,
            memoryUsage: 0,
            objectCount: 0,
            renderTime: 0,
            updateTime: 0,
            networkLatency: 0,
            cpuUsage: 0,
            history: []
        };

        this.workers = [];
        this.renderOptimizer = new RenderOptimizer(this.options);
        this.memoryManager = new MemoryManager(this.options);
        this.networkOptimizer = new NetworkOptimizer(this.options);
        
        this.setupWorkerPool();
        this.startMetricsCollection();
    }

    setupWorkerPool() {
        for (let i = 0; i < this.options.workerPoolSize; i++) {
            const worker = new Worker(`
                const { parentPort } = require('worker_threads');
                
                // Audio processing worker
                function processAudio(buffer, sampleRate, processingType) {
                    switch (processingType) {
                        case 'fft':
                            return performFFT(buffer);
                        case 'filter':
                            return applyFilter(buffer, sampleRate);
                        case 'analyze':
                            return analyzeSpectrum(buffer);
                        default:
                            return buffer;
                    }
                }
                
                function performFFT(buffer) {
                    // Simplified FFT implementation
                    const N = buffer.length;
                    const real = new Float32Array(N);
                    const imag = new Float32Array(N);
                    
                    // Copy input
                    for (let i = 0; i < N; i++) {
                        real[i] = buffer[i];
                        imag[i] = 0;
                    }
                    
                    // Bit-reverse ordering
                    for (let i = 0; i < N; i++) {
                        let j = 0;
                        for (let k = 0; k < Math.log2(N); k++) {
                            j = (j << 1) | ((i >> k) & 1);
                        }
                        if (j > i) {
                            [real[i], real[j]] = [real[j], real[i]];
                            [imag[i], imag[j]] = [imag[j], imag[i]];
                        }
                    }
                    
                    // FFT computation
                    for (let size = 2; size <= N; size *= 2) {
                        const halfSize = size / 2;
                        const step = 2 * Math.PI / size;
                        
                        for (let i = 0; i < N; i += size) {
                            for (let j = 0; j < halfSize; j++) {
                                const u = real[i + j];
                                const v = imag[i + j];
                                const w_real = Math.cos(step * j);
                                const w_imag = -Math.sin(step * j);
                                const t_real = real[i + j + halfSize] * w_real - imag[i + j + halfSize] * w_imag;
                                const t_imag = real[i + j + halfSize] * w_imag + imag[i + j + halfSize] * w_real;
                                
                                real[i + j] = u + t_real;
                                imag[i + j] = v + t_imag;
                                real[i + j + halfSize] = u - t_real;
                                imag[i + j + halfSize] = v - t_imag;
                            }
                        }
                    }
                    
                    // Return magnitude spectrum
                    const magnitude = new Float32Array(N / 2);
                    for (let i = 0; i < N / 2; i++) {
                        magnitude[i] = Math.sqrt(real[i] * real[i] + imag[i] * imag[i]);
                    }
                    
                    return magnitude;
                }
                
                function applyFilter(buffer, sampleRate) {
                    // Simple low-pass filter
                    const cutoff = 1000; // Hz
                    const rc = 1.0 / (2 * Math.PI * cutoff);
                    const dt = 1.0 / sampleRate;
                    const alpha = dt / (rc + dt);
                    
                    const filtered = new Float32Array(buffer.length);
                    filtered[0] = buffer[0];
                    
                    for (let i = 1; i < buffer.length; i++) {
                        filtered[i] = alpha * buffer[i] + (1 - alpha) * filtered[i - 1];
                    }
                    
                    return filtered;
                }
                
                function analyzeSpectrum(buffer) {
                    const fft = performFFT(buffer);
                    
                    // Find peaks
                    const peaks = [];
                    for (let i = 1; i < fft.length - 1; i++) {
                        if (fft[i] > fft[i - 1] && fft[i] > fft[i + 1] && fft[i] > 0.1) {
                            peaks.push({
                                frequency: i * 44100 / (2 * fft.length),
                                magnitude: fft[i]
                            });
                        }
                    }
                    
                    return {
                        spectrum: fft,
                        peaks: peaks.sort((a, b) => b.magnitude - a.magnitude).slice(0, 10),
                        rms: Math.sqrt(buffer.reduce((sum, x) => sum + x * x, 0) / buffer.length),
                        peak: Math.max(...buffer.map(Math.abs))
                    };
                }
                
                parentPort.on('message', (task) => {
                    try {
                        const result = processAudio(task.data, task.sampleRate, task.type);
                        parentPort.postMessage({
                            id: task.id,
                            result,
                            success: true
                        });
                    } catch (error) {
                        parentPort.postMessage({
                            id: task.id,
                            error: error.message,
                            success: false
                        });
                    }
                });
            `, { eval: true });

            this.workers.push({
                worker,
                busy: false,
                tasks: 0
            });
        }
    }

    async executeInWorker(data, type = 'analyze', sampleRate = 44100) {
        return new Promise((resolve, reject) => {
            // Find available worker
            const availableWorker = this.workers.find(w => !w.busy);
            if (!availableWorker) {
                return reject(new Error('No available workers'));
            }

            availableWorker.busy = true;
            availableWorker.tasks++;

            const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            const timeout = setTimeout(() => {
                reject(new Error('Worker task timeout'));
                availableWorker.busy = false;
            }, 10000);

            availableWorker.worker.once('message', (result) => {
                clearTimeout(timeout);
                availableWorker.busy = false;
                
                if (result.success) {
                    resolve(result.result);
                } else {
                    reject(new Error(result.error));
                }
            });

            availableWorker.worker.postMessage({
                id: taskId,
                data,
                type,
                sampleRate
            });
        });
    }

    startMetricsCollection() {
        setInterval(() => {
            this.collectMetrics();
        }, this.options.metricsInterval);
    }

    collectMetrics() {
        const memUsage = process.memoryUsage();
        const cpuUsage = process.cpuUsage();
        
        this.metrics = {
            ...this.metrics,
            memoryUsage: memUsage.heapUsed,
            cpuUsage: cpuUsage.user + cpuUsage.system,
            timestamp: Date.now()
        };

        // Add to history
        this.metrics.history.push({
            ...this.metrics,
            timestamp: Date.now()
        });

        // Keep only last 1000 entries
        if (this.metrics.history.length > 1000) {
            this.metrics.history = this.metrics.history.slice(-1000);
        }

        // Emit metrics update
        this.emit('metrics-update', this.metrics);

        // Check thresholds and optimize if needed
        this.checkPerformanceThresholds();
    }

    checkPerformanceThresholds() {
        const { memoryUsage, fps, objectCount } = this.metrics;
        
        if (memoryUsage > this.options.memoryThreshold) {
            this.emit('memory-warning', { usage: memoryUsage, threshold: this.options.memoryThreshold });
            this.memoryManager.cleanup();
        }
        
        if (fps < this.options.fpsTarget * 0.8) {
            this.emit('performance-warning', { fps, target: this.options.fpsTarget });
            this.renderOptimizer.optimizeRendering();
        }
        
        if (objectCount > this.options.virtualizationThreshold) {
            this.emit('virtualization-needed', { objectCount, threshold: this.options.virtualizationThreshold });
            this.renderOptimizer.enableVirtualization();
        }
    }

    updateMetrics(type, value) {
        this.metrics[type] = value;
    }

    getMetrics() {
        return this.metrics;
    }

    getPerformanceReport() {
        const history = this.metrics.history.slice(-100); // Last 100 measurements
        
        if (history.length === 0) {
            return null;
        }

        const avgFps = history.reduce((sum, m) => sum + m.fps, 0) / history.length;
        const avgMemory = history.reduce((sum, m) => sum + m.memoryUsage, 0) / history.length;
        const avgRenderTime = history.reduce((sum, m) => sum + m.renderTime, 0) / history.length;
        
        return {
            performance: {
                averageFPS: Math.round(avgFps * 100) / 100,
                averageMemory: Math.round(avgMemory / 1024 / 1024 * 100) / 100, // MB
                averageRenderTime: Math.round(avgRenderTime * 100) / 100,
                objectCount: this.metrics.objectCount,
                status: this.getPerformanceStatus()
            },
            recommendations: this.getOptimizationRecommendations(),
            timestamp: Date.now()
        };
    }

    getPerformanceStatus() {
        const { fps, memoryUsage, renderTime } = this.metrics;
        
        if (fps >= this.options.fpsTarget * 0.9 && 
            memoryUsage < this.options.memoryThreshold * 0.8 && 
            renderTime < 16) {
            return 'excellent';
        } else if (fps >= this.options.fpsTarget * 0.7 && 
                   memoryUsage < this.options.memoryThreshold && 
                   renderTime < 25) {
            return 'good';
        } else if (fps >= this.options.fpsTarget * 0.5) {
            return 'fair';
        } else {
            return 'poor';
        }
    }

    getOptimizationRecommendations() {
        const recommendations = [];
        const { fps, memoryUsage, objectCount, renderTime } = this.metrics;
        
        if (fps < this.options.fpsTarget * 0.8) {
            recommendations.push({
                type: 'performance',
                message: 'Consider reducing object count or enabling object pooling',
                priority: 'high'
            });
        }
        
        if (memoryUsage > this.options.memoryThreshold * 0.8) {
            recommendations.push({
                type: 'memory',
                message: 'Memory usage is high. Run garbage collection or reduce cached objects',
                priority: 'medium'
            });
        }
        
        if (objectCount > this.options.virtualizationThreshold) {
            recommendations.push({
                type: 'rendering',
                message: 'Enable canvas virtualization for better performance with many objects',
                priority: 'high'
            });
        }
        
        if (renderTime > 16) {
            recommendations.push({
                type: 'rendering',
                message: 'Render time is high. Consider using requestAnimationFrame optimization',
                priority: 'medium'
            });
        }
        
        return recommendations;
    }

    destroy() {
        // Clean up workers
        this.workers.forEach(({ worker }) => {
            worker.terminate();
        });
        
        this.renderOptimizer.destroy();
        this.memoryManager.destroy();
        this.networkOptimizer.destroy();
    }
}

class RenderOptimizer {
    constructor(options) {
        this.options = options;
        this.virtualizationEnabled = false;
        this.frameId = null;
        this.renderQueue = [];
        this.objectPool = new Map();
    }

    enableVirtualization() {
        if (!this.virtualizationEnabled) {
            this.virtualizationEnabled = true;
            console.log('Canvas virtualization enabled');
        }
    }

    disableVirtualization() {
        this.virtualizationEnabled = false;
        console.log('Canvas virtualization disabled');
    }

    optimizeRendering() {
        // Implement frame rate limiting
        if (this.frameId) {
            cancelAnimationFrame(this.frameId);
        }
        
        this.frameId = requestAnimationFrame(() => {
            this.processRenderQueue();
        });
    }

    processRenderQueue() {
        const startTime = performance.now();
        
        // Process render queue with time slicing
        const timeSlice = 8; // 8ms budget per frame
        
        while (this.renderQueue.length > 0 && (performance.now() - startTime) < timeSlice) {
            const renderTask = this.renderQueue.shift();
            this.executeRenderTask(renderTask);
        }
        
        // Continue processing if there are more tasks
        if (this.renderQueue.length > 0) {
            this.frameId = requestAnimationFrame(() => {
                this.processRenderQueue();
            });
        }
    }

    executeRenderTask(task) {
        // Execute render task with object pooling
        try {
            if (task.type === 'draw-object') {
                this.drawObjectWithPooling(task.object, task.context);
            } else if (task.type === 'update-transform') {
                this.updateTransform(task.object, task.transform);
            }
        } catch (error) {
            console.error('Render task error:', error);
        }
    }

    drawObjectWithPooling(object, context) {
        // Use object pooling for frequent operations
        const poolKey = `${object.type}_${object.id}`;
        
        if (!this.objectPool.has(poolKey)) {
            this.objectPool.set(poolKey, {
                lastUsed: Date.now(),
                renderData: this.createRenderData(object)
            });
        }
        
        const pooledObject = this.objectPool.get(poolKey);
        pooledObject.lastUsed = Date.now();
        
        // Render using pooled data
        this.renderWithPooledData(pooledObject.renderData, context);
    }

    createRenderData(object) {
        // Create optimized render data
        return {
            vertices: object.vertices,
            colors: object.colors,
            indices: object.indices,
            boundingBox: this.calculateBoundingBox(object),
            compiled: true
        };
    }

    calculateBoundingBox(object) {
        if (!object.vertices || object.vertices.length === 0) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }
        
        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;
        
        for (let i = 0; i < object.vertices.length; i += 2) {
            const x = object.vertices[i];
            const y = object.vertices[i + 1];
            
            minX = Math.min(minX, x);
            minY = Math.min(minY, y);
            maxX = Math.max(maxX, x);
            maxY = Math.max(maxY, y);
        }
        
        return {
            x: minX,
            y: minY,
            width: maxX - minX,
            height: maxY - minY
        };
    }

    renderWithPooledData(renderData, context) {
        // Optimized rendering using compiled data
        context.save();
        
        // Use efficient rendering methods
        if (renderData.compiled) {
            this.renderCompiled(renderData, context);
        } else {
            this.renderDirect(renderData, context);
        }
        
        context.restore();
    }

    renderCompiled(renderData, context) {
        // Efficient compiled rendering
        const { vertices, colors, indices } = renderData;
        
        context.beginPath();
        
        for (let i = 0; i < indices.length; i += 3) {
            const i1 = indices[i] * 2;
            const i2 = indices[i + 1] * 2;
            const i3 = indices[i + 2] * 2;
            
            context.moveTo(vertices[i1], vertices[i1 + 1]);
            context.lineTo(vertices[i2], vertices[i2 + 1]);
            context.lineTo(vertices[i3], vertices[i3 + 1]);
            context.closePath();
        }
        
        context.fillStyle = `rgb(${colors[0]}, ${colors[1]}, ${colors[2]})`;
        context.fill();
    }

    renderDirect(renderData, context) {
        // Direct rendering fallback
        const { vertices, colors } = renderData;
        
        context.fillStyle = `rgb(${colors[0]}, ${colors[1]}, ${colors[2]})`;
        context.fillRect(vertices[0], vertices[1], vertices[2] - vertices[0], vertices[3] - vertices[1]);
    }

    updateTransform(object, transform) {
        // Efficiently update object transform
        object.transform = {
            ...object.transform,
            ...transform
        };
        
        // Mark for re-render
        this.renderQueue.push({
            type: 'draw-object',
            object,
            priority: 'normal'
        });
    }

    cleanObjectPool() {
        const now = Date.now();
        const maxAge = 60000; // 1 minute
        
        for (const [key, pooledObject] of this.objectPool) {
            if (now - pooledObject.lastUsed > maxAge) {
                this.objectPool.delete(key);
            }
        }
    }

    destroy() {
        if (this.frameId) {
            cancelAnimationFrame(this.frameId);
        }
        this.objectPool.clear();
        this.renderQueue = [];
    }
}

class MemoryManager {
    constructor(options) {
        this.options = options;
        this.cache = new Map();
        this.weakRefs = new Set();
        
        // Start cleanup interval
        setInterval(() => {
            this.cleanup();
        }, 30000); // Every 30 seconds
    }

    cleanup() {
        // Force garbage collection if available
        if (global.gc) {
            global.gc();
        }
        
        // Clear expired cache entries
        this.cleanCache();
        
        // Clean weak references
        this.cleanWeakReferences();
        
        console.log('Memory cleanup completed');
    }

    cleanCache() {
        const now = Date.now();
        const maxAge = 300000; // 5 minutes
        
        for (const [key, entry] of this.cache) {
            if (now - entry.timestamp > maxAge) {
                this.cache.delete(key);
            }
        }
    }

    cleanWeakReferences() {
        const validRefs = new Set();
        
        for (const ref of this.weakRefs) {
            if (ref.deref()) {
                validRefs.add(ref);
            }
        }
        
        this.weakRefs = validRefs;
    }

    addToCache(key, value, maxAge = 300000) {
        this.cache.set(key, {
            value,
            timestamp: Date.now(),
            maxAge
        });
    }

    getFromCache(key) {
        const entry = this.cache.get(key);
        if (!entry) return null;
        
        const now = Date.now();
        if (now - entry.timestamp > entry.maxAge) {
            this.cache.delete(key);
            return null;
        }
        
        return entry.value;
    }

    addWeakReference(object) {
        this.weakRefs.add(new WeakRef(object));
    }

    getMemoryStats() {
        const usage = process.memoryUsage();
        return {
            heapUsed: usage.heapUsed,
            heapTotal: usage.heapTotal,
            external: usage.external,
            rss: usage.rss,
            cacheSize: this.cache.size,
            weakRefsCount: this.weakRefs.size
        };
    }

    destroy() {
        this.cache.clear();
        this.weakRefs.clear();
    }
}

class NetworkOptimizer {
    constructor(options) {
        this.options = options;
        this.requestCache = new Map();
        this.compressionEnabled = true;
        this.batchRequests = [];
        this.batchTimer = null;
    }

    optimizeRequest(url, options = {}) {
        // Check cache first
        const cacheKey = `${url}_${JSON.stringify(options)}`;
        const cached = this.requestCache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < 30000) {
            return Promise.resolve(cached.data);
        }
        
        // Batch similar requests
        if (options.batch) {
            return this.addToBatch(url, options);
        }
        
        // Make optimized request
        return this.makeOptimizedRequest(url, options);
    }

    addToBatch(url, options) {
        return new Promise((resolve, reject) => {
            this.batchRequests.push({ url, options, resolve, reject });
            
            if (this.batchTimer) {
                clearTimeout(this.batchTimer);
            }
            
            this.batchTimer = setTimeout(() => {
                this.processBatch();
            }, 50); // 50ms batch window
        });
    }

    async processBatch() {
        const requests = [...this.batchRequests];
        this.batchRequests = [];
        
        try {
            // Group similar requests
            const groups = this.groupRequests(requests);
            
            // Process each group
            for (const group of groups) {
                await this.processBatchGroup(group);
            }
        } catch (error) {
            // Reject all pending requests
            requests.forEach(req => req.reject(error));
        }
    }

    groupRequests(requests) {
        const groups = new Map();
        
        for (const request of requests) {
            const baseUrl = request.url.split('?')[0];
            if (!groups.has(baseUrl)) {
                groups.set(baseUrl, []);
            }
            groups.get(baseUrl).push(request);
        }
        
        return Array.from(groups.values());
    }

    async processBatchGroup(group) {
        // Process grouped requests efficiently
        const baseUrl = group[0].url.split('?')[0];
        const batchData = group.map(req => ({
            id: Math.random().toString(36).substr(2, 9),
            url: req.url,
            options: req.options
        }));
        
        try {
            const response = await fetch(`${baseUrl}/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ requests: batchData })
            });
            
            const results = await response.json();
            
            // Resolve individual requests
            group.forEach((request, index) => {
                const result = results[index];
                if (result.success) {
                    request.resolve(result.data);
                } else {
                    request.reject(new Error(result.error));
                }
            });
        } catch (error) {
            // Fallback to individual requests
            for (const request of group) {
                try {
                    const result = await this.makeOptimizedRequest(request.url, request.options);
                    request.resolve(result);
                } catch (individualError) {
                    request.reject(individualError);
                }
            }
        }
    }

    async makeOptimizedRequest(url, options) {
        const fetchOptions = {
            ...options,
            headers: {
                'Accept-Encoding': 'gzip, deflate, br',
                ...options.headers
            }
        };
        
        const response = await fetch(url, fetchOptions);
        const data = await response.json();
        
        // Cache successful responses
        const cacheKey = `${url}_${JSON.stringify(options)}`;
        this.requestCache.set(cacheKey, {
            data,
            timestamp: Date.now()
        });
        
        return data;
    }

    destroy() {
        this.requestCache.clear();
        if (this.batchTimer) {
            clearTimeout(this.batchTimer);
        }
        this.batchRequests = [];
    }
}

module.exports = {
    PerformanceOptimizer,
    RenderOptimizer,
    MemoryManager,
    NetworkOptimizer
};
