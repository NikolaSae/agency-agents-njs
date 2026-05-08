// UpdateContractPhase MCP Tool with Security Middleware
// Example implementation showing auth, DLP, and audit integration

const express = require('express');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// Security Configuration
const SECURITY_CONFIG = {
  jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
  auditLogPath: '/var/log/mcp-audit.log',
  dlpPatterns: {
    ssn: /\b\d{3}-\d{2}-\d{4}\b/,
    creditCard: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/,
    email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
  }
};

// Audit Middleware
class AuditMiddleware {
  constructor(config) {
    this.config = config;
    this.logger = this.createLogger();
  }

  createLogger() {
    // In production, use a proper logging library like Winston
    return {
      log: (level, message, metadata = {}) => {
        const entry = {
          timestamp: new Date().toISOString(),
          level,
          message,
          metadata,
          sessionId: crypto.randomUUID(),
          userId: metadata.userId || 'anonymous',
          ipAddress: metadata.ipAddress || 'unknown',
          action: metadata.action || 'unknown'
        };

        console.log(`[${level.toUpperCase()}] ${JSON.stringify(entry)}`);

        // In production: write to secure audit log
        // fs.appendFileSync(this.config.auditLogPath, JSON.stringify(entry) + '\n');
      }
    };
  }

  middleware() {
    return (req, res, next) => {
      const startTime = Date.now();
      const originalSend = res.send;

      res.send = function(data) {
        const duration = Date.now() - startTime;

        this.logger.log('info', 'MCP Tool Access', {
          action: req.path,
          method: req.method,
          userId: req.user?.id,
          ipAddress: req.ip,
          duration,
          statusCode: res.statusCode,
          userAgent: req.get('User-Agent'),
          requestSize: JSON.stringify(req.body || {}).length,
          responseSize: data.length
        });

        originalSend.call(this, data);
      };

      next();
    };
  }
}

// Authentication Middleware
class AuthMiddleware {
  constructor(config) {
    this.config = config;
  }

  middleware() {
    return (req, res, next) => {
      try {
        const authHeader = req.headers.authorization;

        if (!authHeader || !authHeader.startsWith('Bearer ')) {
          return res.status(401).json({
            error: 'Missing or invalid authorization header',
            code: 'AUTH_MISSING'
          });
        }

        const token = authHeader.substring(7);
        const decoded = jwt.verify(token, this.config.jwtSecret);

        // Validate token claims
        if (!decoded.sub || !decoded.roles) {
          return res.status(401).json({
            error: 'Invalid token claims',
            code: 'AUTH_INVALID_CLAIMS'
          });
        }

        // Check if user has required role for contract operations
        if (!decoded.roles.includes('contract_admin') && !decoded.roles.includes('contract_manager')) {
          return res.status(403).json({
            error: 'Insufficient permissions for contract operations',
            code: 'AUTH_INSUFFICIENT_PERMISSIONS'
          });
        }

        req.user = {
          id: decoded.sub,
          roles: decoded.roles,
          department: decoded.department
        };

        next();
      } catch (error) {
        if (error.name === 'TokenExpiredError') {
          return res.status(401).json({
            error: 'Token expired',
            code: 'AUTH_TOKEN_EXPIRED'
          });
        }

        return res.status(401).json({
          error: 'Invalid token',
          code: 'AUTH_INVALID_TOKEN'
        });
      }
    };
  }
}

// Data Loss Prevention Middleware
class DLPMiddleware {
  constructor(config) {
    this.config = config;
  }

  middleware() {
    return (req, res, next) => {
      // Scan request body for sensitive data
      const requestData = JSON.stringify(req.body || {});
      const violations = this.scanForSensitiveData(requestData);

      if (violations.length > 0) {
        // Log DLP violation
        req.auditLogger?.log('warning', 'DLP Violation Detected', {
          action: 'data_scan',
          violations: violations.map(v => ({ type: v.type, line: v.line })),
          userId: req.user?.id,
          ipAddress: req.ip
        });

        return res.status(400).json({
          error: 'Request contains sensitive data that cannot be processed',
          code: 'DLP_VIOLATION',
          details: violations.map(v => ({ type: v.type, message: v.message }))
        });
      }

      // Sanitize response data
      const originalJson = res.json;
      res.json = function(data) {
        const sanitizedData = this.sanitizeResponseData(data);
        return originalJson.call(this, sanitizedData);
      }.bind(this);

      next();
    };
  }

  scanForSensitiveData(data) {
    const violations = [];
    const lines = data.split('\n');

    lines.forEach((line, index) => {
      Object.entries(this.config.dlpPatterns).forEach(([type, pattern]) => {
        const matches = line.match(pattern);
        if (matches) {
          violations.push({
            type,
            line: index + 1,
            message: `Detected ${type} pattern in request data`
          });
        }
      });
    });

    return violations;
  }

  sanitizeResponseData(data) {
    // Deep clone to avoid modifying original
    const sanitized = JSON.parse(JSON.stringify(data));

    // Remove or mask sensitive fields in response
    const maskSensitive = (obj) => {
      if (typeof obj !== 'object' || obj === null) return obj;

      for (const key in obj) {
        if (key.toLowerCase().includes('ssn') ||
            key.toLowerCase().includes('credit') ||
            key.toLowerCase().includes('password')) {
          obj[key] = '[REDACTED]';
        } else if (typeof obj[key] === 'object') {
          maskSensitive(obj[key]);
        }
      }
      return obj;
    };

    return maskSensitive(sanitized);
  }
}

// Rate Limiting Middleware (simplified)
class RateLimitMiddleware {
  constructor(config) {
    this.config = config;
    this.requests = new Map();
  }

  middleware() {
    return (req, res, next) => {
      const key = req.ip;
      const now = Date.now();
      const windowStart = now - this.config.rateLimit.windowMs;

      if (!this.requests.has(key)) {
        this.requests.set(key, []);
      }

      const userRequests = this.requests.get(key);
      // Remove old requests outside the window
      const validRequests = userRequests.filter(time => time > windowStart);

      if (validRequests.length >= this.config.rateLimit.max) {
        return res.status(429).json({
          error: 'Too many requests',
          code: 'RATE_LIMIT_EXCEEDED'
        });
      }

      validRequests.push(now);
      this.requests.set(key, validRequests);

      next();
    };
  }
}

// UpdateContractPhase MCP Tool Implementation
class UpdateContractPhaseTool {
  constructor(securityConfig) {
    this.config = securityConfig;
    this.audit = new AuditMiddleware(securityConfig);
    this.auth = new AuthMiddleware(securityConfig);
    this.dlp = new DLPMiddleware(securityConfig);
    this.rateLimit = new RateLimitMiddleware(securityConfig);
  }

  // MCP Tool Definition
  getToolDefinition() {
    return {
      name: 'update_contract_phase',
      description: 'Update the phase of a contract with security validation',
      inputSchema: {
        type: 'object',
        properties: {
          contractId: {
            type: 'string',
            description: 'Unique identifier of the contract'
          },
          newPhase: {
            type: 'string',
            enum: ['draft', 'review', 'approved', 'active', 'completed', 'terminated'],
            description: 'New phase for the contract'
          },
          reason: {
            type: 'string',
            description: 'Reason for the phase change'
          },
          metadata: {
            type: 'object',
            description: 'Additional metadata for the update'
          }
        },
        required: ['contractId', 'newPhase']
      }
    };
  }

  // Main handler with integrated security middleware
  async handle(input, context) {
    const { contractId, newPhase, reason, metadata } = input;

    try {
      // Validate input
      if (!contractId || !newPhase) {
        throw new Error('Missing required parameters: contractId and newPhase');
      }

      // Business logic validation
      const validPhases = ['draft', 'review', 'approved', 'active', 'completed', 'terminated'];
      if (!validPhases.includes(newPhase)) {
        throw new Error(`Invalid phase: ${newPhase}`);
      }

      // Simulate contract lookup and update
      const contract = await this.getContract(contractId);
      if (!contract) {
        throw new Error(`Contract not found: ${contractId}`);
      }

      // Check phase transition rules
      if (!this.isValidPhaseTransition(contract.currentPhase, newPhase)) {
        throw new Error(`Invalid phase transition from ${contract.currentPhase} to ${newPhase}`);
      }

      // Update contract
      const updatedContract = await this.updateContractPhase(contractId, newPhase, {
        reason,
        metadata,
        updatedBy: context.user.id,
        timestamp: new Date().toISOString()
      });

      // Audit the successful update
      context.auditLogger.log('info', 'Contract Phase Updated', {
        action: 'update_contract_phase',
        contractId,
        oldPhase: contract.currentPhase,
        newPhase,
        userId: context.user.id,
        reason
      });

      return {
        success: true,
        contract: {
          id: updatedContract.id,
          previousPhase: contract.currentPhase,
          currentPhase: updatedContract.currentPhase,
          updatedAt: updatedContract.updatedAt
        }
      };

    } catch (error) {
      // Audit the error
      context.auditLogger.log('error', 'Contract Phase Update Failed', {
        action: 'update_contract_phase',
        contractId,
        newPhase,
        userId: context.user?.id,
        error: error.message
      });

      throw error;
    }
  }

  // Mock contract database operations
  async getContract(contractId) {
    // In real implementation, query database
    return {
      id: contractId,
      currentPhase: 'review',
      // ... other contract data
    };
  }

  async updateContractPhase(contractId, newPhase, updateInfo) {
    // In real implementation, update database with transaction
    return {
      id: contractId,
      currentPhase: newPhase,
      updatedAt: new Date().toISOString(),
      updateHistory: [updateInfo]
    };
  }

  isValidPhaseTransition(fromPhase, toPhase) {
    const transitions = {
      draft: ['review', 'terminated'],
      review: ['draft', 'approved', 'terminated'],
      approved: ['active', 'terminated'],
      active: ['completed', 'terminated'],
      completed: [], // Terminal state
      terminated: [] // Terminal state
    };

    return transitions[fromPhase]?.includes(toPhase) || false;
  }

  // Express route setup with middleware chain
  setupRoutes(app) {
    const toolPath = '/mcp/tools/update_contract_phase';

    app.post(toolPath,
      this.rateLimit.middleware(),
      this.auth.middleware(),
      this.dlp.middleware(),
      this.audit.middleware(),
      async (req, res) => {
        try {
          // Add audit logger to request for use in handler
          req.auditLogger = this.audit.logger;

          const result = await this.handle(req.body, {
            user: req.user,
            auditLogger: this.audit.logger
          });

          res.json(result);
        } catch (error) {
          res.status(400).json({
            error: error.message,
            code: 'TOOL_EXECUTION_ERROR'
          });
        }
      }
    );
  }
}

// Example usage and server setup
function createSecureMCPTool() {
  const tool = new UpdateContractPhaseTool(SECURITY_CONFIG);

  const app = express();
  app.use(express.json());

  // Setup the tool routes with security middleware
  tool.setupRoutes(app);

  // Health check endpoint
  app.get('/health', (req, res) => {
    res.json({ status: 'healthy', tool: 'update_contract_phase' });
  });

  return app;
}

// Export for use in MCP server
module.exports = {
  UpdateContractPhaseTool,
  createSecureMCPTool,
  SECURITY_CONFIG
};

// Example of how to start the server:
/*
const app = createSecureMCPTool();
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Secure MCP UpdateContractPhase tool running on port ${PORT}`);
});
*/