/**
 * Cross-platform prebuild script for Netlify deployment.
 * Copies backend code, ML models, and requirements into netlify/functions/
 * so the Python serverless function has access to everything it needs.
 *
 * Works on both Windows (local deploy) and Linux (Netlify CI).
 */
import { cpSync, mkdirSync, rmSync, copyFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const funcsDir = join(__dirname, 'netlify', 'functions');

console.log('🔧 Preparing backend files for Netlify Functions...');

// 1. Ensure models directory exists
mkdirSync(join(funcsDir, 'models'), { recursive: true });

// 2. Remove stale copies of backend code
rmSync(join(funcsDir, 'app'), { recursive: true, force: true });
rmSync(join(funcsDir, 'disease_references'), { recursive: true, force: true });

// 3. Copy backend application code
cpSync(join(__dirname, '..', 'Backend', 'app'), join(funcsDir, 'app'), { recursive: true });
cpSync(join(__dirname, '..', 'Backend', 'disease_references'), join(funcsDir, 'disease_references'), { recursive: true });

// 4. Copy ML model artifacts
copyFileSync(
  join(__dirname, '..', 'AI', 'models', 'isolation_forest.pkl'),
  join(funcsDir, 'models', 'isolation_forest.pkl')
);
copyFileSync(
  join(__dirname, '..', 'AI', 'models', 'risk_scaler.pkl'),
  join(funcsDir, 'models', 'risk_scaler.pkl')
);

// 5. Copy Python requirements
copyFileSync(
  join(__dirname, 'requirements.txt'),
  join(funcsDir, 'requirements.txt')
);

console.log('✅ Backend files copied to netlify/functions/');
