const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const slowDown = require('express-slow-down');
const morgan = require('morgan');
const { createProxyMiddleware } = require('http-proxy-middleware');
const swaggerUi = require('swagger-ui-express');
const swaggerJsdoc = require('swagger-jsdoc');
const Redis = require('redis');
const winston = require('winston');
require('dotenv').config();

const authMiddleware = require('./middleware/auth');
const rateLimitMiddleware = require('./middleware/rateLimit');
const loggingMiddleware = require('./middleware/logging');
const metricsMiddleware = require('./middleware/metrics');
const circuitBreakerMiddleware = require('./middleware/circuitBreaker');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 8000;

// Initialize Redis client
const redis = Redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  password: process.env.REDIS_PASSWORD
});

redis.on('error', (err) => {
  console.error('Redis connection error:', err);
});

redis.connect().catch(console.error);

// Configure Winston logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'api-gateway' },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Swagger configuration
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'LegalGPT Enterprise API',
      version: '2.0.0',
      description: 'Advanced Legal AI Platform - Enterprise API Gateway',
      contact: {
        name: 'LegalGPT Support',
        email: 'support@legalgpt.co.il'
      }
    },
    servers: [
      {
        url: process.env.API_BASE_URL || 'http://localhost:8000',
        description: 'Development server'
      }
    ],
    components: {
      securitySchemes: {
        BearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        }
      }
    },
    security: [{ BearerAuth: [] }]
  },
  apis: ['./src/routes/*.js', './src/schemas/*.js']
};

const specs = swaggerJsdoc(swaggerOptions);

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"]
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

// Compression and parsing
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging
app.use(morgan('combined', {
  stream: { write: message => logger.info(message.trim()) }
}));

// Rate limiting
const globalRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: 15 * 60
  },
  standardHeaders: true,
  legacyHeaders: false,
  store: rateLimitMiddleware.createRedisStore(redis)
});

app.use('/api/', globalRateLimit);

// Slow down repeated requests
const speedLimiter = slowDown({
  windowMs: 15 * 60 * 1000, // 15 minutes
  delayAfter: 100, // allow 100 requests per 15 minutes, then...
  delayMs: 500 // begin adding 500ms of delay per request above 100
});

app.use('/api/', speedLimiter);

// Custom middleware
app.use(loggingMiddleware(logger));
app.use(metricsMiddleware);

// API Documentation
app.use('/docs', swaggerUi.serve, swaggerUi.setup(specs, {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'LegalGPT API Documentation'
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    version: process.env.npm_package_version || '2.0.0'
  });
});

// Microservices proxy configuration
const services = {
  'legal-ai': {
    target: process.env.LEGAL_AI_SERVICE_URL || 'http://legal_ai_service:8001',
    pathRewrite: { '^/api/v2/ai': '' },
    changeOrigin: true,
    timeout: 30000
  },
  'document': {
    target: process.env.DOCUMENT_SERVICE_URL || 'http://document_service:8002',
    pathRewrite: { '^/api/v2/documents': '' },
    changeOrigin: true,
    timeout: 15000
  },
  'user': {
    target: process.env.USER_SERVICE_URL || 'http://user_service:8003',
    pathRewrite: { '^/api/v2/users': '' },
    changeOrigin: true,
    timeout: 10000
  },
  'payment': {
    target: process.env.PAYMENT_SERVICE_URL || 'http://payment_service:8004',
    pathRewrite: { '^/api/v2/payments': '' },
    changeOrigin: true,
    timeout: 10000
  },
  'analytics': {
    target: process.env.ANALYTICS_SERVICE_URL || 'http://analytics_service:8005',
    pathRewrite: { '^/api/v2/analytics': '' },
    changeOrigin: true,
    timeout: 5000
  }
};

// Setup proxy routes with circuit breaker
Object.keys(services).forEach(serviceName => {
  const serviceConfig = services[serviceName];
  
  app.use(`/api/v2/${serviceName}`, 
    circuitBreakerMiddleware(serviceName),
    createProxyMiddleware({
      ...serviceConfig,
      onError: (err, req, res) => {
        logger.error(`Proxy error for ${serviceName}:`, err);
        res.status(503).json({
          error: 'Service temporarily unavailable',
          service: serviceName,
          timestamp: new Date().toISOString()
        });
      },
      onProxyReq: (proxyReq, req, res) => {
        // Add correlation ID for tracing
        proxyReq.setHeader('X-Correlation-ID', req.headers['x-correlation-id'] || 
          require('crypto').randomUUID());
        
        // Add user context if authenticated
        if (req.user) {
          proxyReq.setHeader('X-User-ID', req.user.id);
          proxyReq.setHeader('X-User-Role', req.user.role);
        }
      },
      onProxyRes: (proxyRes, req, res) => {
        // Add security headers
        proxyRes.headers['X-Content-Type-Options'] = 'nosniff';
        proxyRes.headers['X-Frame-Options'] = 'DENY';
        proxyRes.headers['X-XSS-Protection'] = '1; mode=block';
      }
    })
  );
});

// Authentication routes (handled directly by gateway)
app.use('/api/v2/auth', require('./routes/auth'));

// WebSocket support for real-time features
const http = require('http');
const socketIo = require('socket.io');

const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    methods: ['GET', 'POST']
  }
});

// WebSocket authentication middleware
io.use(async (socket, next) => {
  try {
    const token = socket.handshake.auth.token;
    const user = await authMiddleware.verifyToken(token);
    socket.user = user;
    next();
  } catch (error) {
    next(new Error('Authentication error'));
  }
});

io.on('connection', (socket) => {
  logger.info(`User ${socket.user.id} connected to WebSocket`);
  
  socket.join(`user:${socket.user.id}`);
  
  socket.on('disconnect', () => {
    logger.info(`User ${socket.user.id} disconnected from WebSocket`);
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  
  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === 'production' 
      ? 'Internal server error' 
      : err.message,
    timestamp: new Date().toISOString(),
    requestId: req.headers['x-correlation-id']
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.originalUrl,
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  
  server.close(() => {
    logger.info('HTTP server closed');
  });
  
  await redis.quit();
  process.exit(0);
});

// Start server
server.listen(PORT, () => {
  logger.info(`🚀 LegalGPT API Gateway running on port ${PORT}`);
  logger.info(`📚 API Documentation: http://localhost:${PORT}/docs`);
  logger.info(`💓 Health Check: http://localhost:${PORT}/health`);
});

module.exports = { app, server, io };