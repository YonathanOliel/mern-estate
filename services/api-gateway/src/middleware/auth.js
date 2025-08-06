const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { promisify } = require('util');
const crypto = require('crypto');

class AuthMiddleware {
  constructor(redisClient) {
    this.redis = redisClient;
    this.jwtSecret = process.env.JWT_SECRET || 'your-super-secret-jwt-key';
    this.refreshTokenSecret = process.env.REFRESH_TOKEN_SECRET || 'your-refresh-token-secret';
    this.tokenExpiry = process.env.TOKEN_EXPIRY || '15m';
    this.refreshTokenExpiry = process.env.REFRESH_TOKEN_EXPIRY || '7d';
  }

  // Generate JWT tokens
  generateTokens(user) {
    const payload = {
      id: user.id,
      email: user.email,
      role: user.role,
      permissions: user.permissions || [],
      subscription: user.subscription || 'free'
    };

    const accessToken = jwt.sign(payload, this.jwtSecret, {
      expiresIn: this.tokenExpiry,
      issuer: 'legalgpt',
      audience: 'legalgpt-users'
    });

    const refreshToken = jwt.sign(
      { id: user.id, type: 'refresh' },
      this.refreshTokenSecret,
      {
        expiresIn: this.refreshTokenExpiry,
        issuer: 'legalgpt',
        audience: 'legalgpt-users'
      }
    );

    return { accessToken, refreshToken };
  }

  // Verify JWT token
  async verifyToken(token) {
    try {
      // Check if token is blacklisted
      const isBlacklisted = await this.redis.get(`blacklist:${token}`);
      if (isBlacklisted) {
        throw new Error('Token has been revoked');
      }

      const decoded = jwt.verify(token, this.jwtSecret, {
        issuer: 'legalgpt',
        audience: 'legalgpt-users'
      });

      return decoded;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  // Verify refresh token
  async verifyRefreshToken(refreshToken) {
    try {
      const decoded = jwt.verify(refreshToken, this.refreshTokenSecret, {
        issuer: 'legalgpt',
        audience: 'legalgpt-users'
      });

      // Check if refresh token is still valid in Redis
      const storedToken = await this.redis.get(`refresh:${decoded.id}`);
      if (storedToken !== refreshToken) {
        throw new Error('Refresh token has been revoked');
      }

      return decoded;
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }

  // Store refresh token in Redis
  async storeRefreshToken(userId, refreshToken) {
    const expiry = 7 * 24 * 60 * 60; // 7 days in seconds
    await this.redis.setEx(`refresh:${userId}`, expiry, refreshToken);
  }

  // Blacklist token
  async blacklistToken(token) {
    try {
      const decoded = jwt.decode(token);
      const expiry = decoded.exp - Math.floor(Date.now() / 1000);
      
      if (expiry > 0) {
        await this.redis.setEx(`blacklist:${token}`, expiry, 'true');
      }
    } catch (error) {
      // Token is already invalid, no need to blacklist
    }
  }

  // Revoke refresh token
  async revokeRefreshToken(userId) {
    await this.redis.del(`refresh:${userId}`);
  }

  // Hash password
  async hashPassword(password) {
    const saltRounds = 12;
    return bcrypt.hash(password, saltRounds);
  }

  // Compare password
  async comparePassword(password, hashedPassword) {
    return bcrypt.compare(password, hashedPassword);
  }

  // Generate secure random token
  generateSecureToken(length = 32) {
    return crypto.randomBytes(length).toString('hex');
  }

  // Rate limiting for authentication attempts
  async checkAuthRateLimit(identifier, maxAttempts = 5, windowMs = 15 * 60 * 1000) {
    const key = `auth_attempts:${identifier}`;
    const attempts = await this.redis.incr(key);
    
    if (attempts === 1) {
      await this.redis.expire(key, Math.floor(windowMs / 1000));
    }

    if (attempts > maxAttempts) {
      const ttl = await this.redis.ttl(key);
      throw new Error(`Too many authentication attempts. Try again in ${ttl} seconds.`);
    }

    return attempts;
  }

  // Clear auth rate limit
  async clearAuthRateLimit(identifier) {
    await this.redis.del(`auth_attempts:${identifier}`);
  }

  // Middleware for protecting routes
  authenticate = async (req, res, next) => {
    try {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
          error: 'Access token required',
          code: 'MISSING_TOKEN'
        });
      }

      const token = authHeader.substring(7);
      const decoded = await this.verifyToken(token);
      
      req.user = decoded;
      req.token = token;
      
      next();
    } catch (error) {
      return res.status(401).json({
        error: 'Invalid or expired token',
        code: 'INVALID_TOKEN'
      });
    }
  };

  // Middleware for role-based access control
  authorize = (requiredRoles) => {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({
          error: 'Authentication required',
          code: 'AUTH_REQUIRED'
        });
      }

      const userRole = req.user.role;
      const hasRequiredRole = Array.isArray(requiredRoles) 
        ? requiredRoles.includes(userRole)
        : requiredRoles === userRole;

      if (!hasRequiredRole) {
        return res.status(403).json({
          error: 'Insufficient permissions',
          code: 'INSUFFICIENT_PERMISSIONS',
          required: requiredRoles,
          current: userRole
        });
      }

      next();
    };
  };

  // Middleware for permission-based access control
  requirePermission = (requiredPermission) => {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({
          error: 'Authentication required',
          code: 'AUTH_REQUIRED'
        });
      }

      const userPermissions = req.user.permissions || [];
      const hasPermission = userPermissions.includes(requiredPermission);

      if (!hasPermission) {
        return res.status(403).json({
          error: 'Permission denied',
          code: 'PERMISSION_DENIED',
          required: requiredPermission,
          current: userPermissions
        });
      }

      next();
    };
  };

  // Middleware for subscription-based access control
  requireSubscription = (requiredPlan) => {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({
          error: 'Authentication required',
          code: 'AUTH_REQUIRED'
        });
      }

      const userSubscription = req.user.subscription || 'free';
      const subscriptionHierarchy = ['free', 'basic', 'premium', 'enterprise'];
      
      const userLevel = subscriptionHierarchy.indexOf(userSubscription);
      const requiredLevel = subscriptionHierarchy.indexOf(requiredPlan);

      if (userLevel < requiredLevel) {
        return res.status(402).json({
          error: 'Subscription upgrade required',
          code: 'SUBSCRIPTION_REQUIRED',
          required: requiredPlan,
          current: userSubscription,
          upgradeUrl: '/pricing'
        });
      }

      next();
    };
  };

  // Optional authentication middleware
  optionalAuth = async (req, res, next) => {
    try {
      const authHeader = req.headers.authorization;
      
      if (authHeader && authHeader.startsWith('Bearer ')) {
        const token = authHeader.substring(7);
        const decoded = await this.verifyToken(token);
        req.user = decoded;
        req.token = token;
      }
      
      next();
    } catch (error) {
      // Continue without authentication
      next();
    }
  };

  // Generate API key for service-to-service communication
  generateApiKey(serviceId) {
    const payload = {
      serviceId,
      type: 'api_key',
      iat: Math.floor(Date.now() / 1000)
    };

    return jwt.sign(payload, this.jwtSecret, {
      issuer: 'legalgpt',
      audience: 'legalgpt-services'
    });
  }

  // Verify API key
  verifyApiKey = async (req, res, next) => {
    try {
      const apiKey = req.headers['x-api-key'];
      
      if (!apiKey) {
        return res.status(401).json({
          error: 'API key required',
          code: 'MISSING_API_KEY'
        });
      }

      const decoded = jwt.verify(apiKey, this.jwtSecret, {
        issuer: 'legalgpt',
        audience: 'legalgpt-services'
      });

      if (decoded.type !== 'api_key') {
        throw new Error('Invalid API key type');
      }

      req.service = decoded;
      next();
    } catch (error) {
      return res.status(401).json({
        error: 'Invalid API key',
        code: 'INVALID_API_KEY'
      });
    }
  };
}

module.exports = AuthMiddleware;