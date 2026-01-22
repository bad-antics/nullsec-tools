#!/usr/bin/env node
/**
 * NullSec Web Scanner
 * Web application vulnerability scanner
 * Author: bad-antics | GitHub: bad-antics | Discord: discord.gg/killers
 */

const https = require('https');
const http = require('http');
const url = require('url');
const { URL } = require('url');

const BANNER = `
╔═══════════════════════════════════════════════════════════╗
║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║
║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║
║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║
║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║
║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║
║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║
║                 WEB SCANNER (Node.js)                      ║
║            bad-antics | @AnonAntics | discord.gg/killers  ║
╚═══════════════════════════════════════════════════════════╝
`;

// Common security headers to check
const SECURITY_HEADERS = {
    'strict-transport-security': { 
        name: 'HSTS', 
        severity: 'HIGH',
        desc: 'Missing HTTP Strict Transport Security'
    },
    'x-frame-options': { 
        name: 'X-Frame-Options', 
        severity: 'MEDIUM',
        desc: 'Missing clickjacking protection'
    },
    'x-content-type-options': { 
        name: 'X-Content-Type-Options', 
        severity: 'LOW',
        desc: 'Missing MIME type sniffing protection'
    },
    'content-security-policy': { 
        name: 'CSP', 
        severity: 'HIGH',
        desc: 'Missing Content Security Policy'
    },
    'x-xss-protection': { 
        name: 'X-XSS-Protection', 
        severity: 'LOW',
        desc: 'Missing XSS protection header'
    },
    'referrer-policy': { 
        name: 'Referrer-Policy', 
        severity: 'LOW',
        desc: 'Missing referrer policy'
    },
    'permissions-policy': { 
        name: 'Permissions-Policy', 
        severity: 'MEDIUM',
        desc: 'Missing permissions policy'
    }
};

// Common paths to check
const COMMON_PATHS = [
    '/.git/config', '/.env', '/wp-config.php', '/config.php',
    '/.htaccess', '/web.config', '/robots.txt', '/sitemap.xml',
    '/admin', '/administrator', '/phpmyadmin', '/wp-admin',
    '/backup', '/backup.sql', '/dump.sql', '/database.sql',
    '/.svn/entries', '/.DS_Store', '/server-status', '/server-info',
    '/api', '/api/v1', '/graphql', '/swagger.json', '/api-docs'
];

// XSS payloads for basic testing
const XSS_PAYLOADS = [
    '<script>alert(1)</script>',
    '"><script>alert(1)</script>',
    "'-alert(1)-'",
    '<img src=x onerror=alert(1)>'
];

// SQL injection payloads
const SQLI_PAYLOADS = [
    "' OR '1'='1",
    "1' AND '1'='1",
    "1 OR 1=1--",
    "' UNION SELECT NULL--"
];

class WebScanner {
    constructor(targetUrl) {
        this.target = new URL(targetUrl);
        this.results = {
            headers: [],
            paths: [],
            vulns: [],
            info: {}
        };
    }

    async request(path = '/', method = 'GET', headers = {}) {
        return new Promise((resolve, reject) => {
            const protocol = this.target.protocol === 'https:' ? https : http;
            const options = {
                hostname: this.target.hostname,
                port: this.target.port || (this.target.protocol === 'https:' ? 443 : 80),
                path: path,
                method: method,
                headers: {
                    'User-Agent': 'NullSec-WebScan/1.0',
                    ...headers
                },
                rejectUnauthorized: false,
                timeout: 10000
            };

            const req = protocol.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve({ 
                    status: res.statusCode, 
                    headers: res.headers, 
                    body: data 
                }));
            });

            req.on('error', reject);
            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Timeout'));
            });
            req.end();
        });
    }

    async checkSecurityHeaders() {
        console.log('\n[*] Checking security headers...');
        try {
            const res = await this.request('/');
            
            for (const [header, info] of Object.entries(SECURITY_HEADERS)) {
                if (!res.headers[header]) {
                    this.results.headers.push({
                        header: info.name,
                        status: 'MISSING',
                        severity: info.severity,
                        description: info.desc
                    });
                    console.log(`  [!] ${info.severity}: ${info.desc}`);
                } else {
                    console.log(`  [+] ${info.name}: Present`);
                }
            }

            // Check for information disclosure headers
            const sensitiveHeaders = ['server', 'x-powered-by', 'x-aspnet-version'];
            for (const h of sensitiveHeaders) {
                if (res.headers[h]) {
                    console.log(`  [!] INFO: ${h} = ${res.headers[h]}`);
                    this.results.info[h] = res.headers[h];
                }
            }
        } catch (err) {
            console.log(`  [-] Error: ${err.message}`);
        }
    }

    async checkCommonPaths() {
        console.log('\n[*] Checking common paths...');
        
        for (const path of COMMON_PATHS) {
            try {
                const res = await this.request(path);
                if (res.status === 200 || res.status === 403) {
                    const status = res.status === 200 ? 'ACCESSIBLE' : 'FORBIDDEN';
                    console.log(`  [${res.status === 200 ? '+' : '!'}] ${path} (${res.status})`);
                    this.results.paths.push({ path, status: res.status });
                }
            } catch (err) {
                // Ignore errors for path checking
            }
        }
    }

    async checkSSL() {
        console.log('\n[*] Checking SSL/TLS configuration...');
        
        if (this.target.protocol !== 'https:') {
            console.log('  [!] HIGH: Site not using HTTPS');
            this.results.vulns.push({
                type: 'NO_HTTPS',
                severity: 'HIGH',
                description: 'Site does not use HTTPS'
            });
            return;
        }

        try {
            const res = await this.request('/');
            console.log('  [+] HTTPS enabled');
            
            // Check HSTS
            if (!res.headers['strict-transport-security']) {
                console.log('  [!] HSTS not configured');
            }
        } catch (err) {
            console.log(`  [-] SSL Error: ${err.message}`);
        }
    }

    async runScan() {
        console.log(BANNER);
        console.log(`[*] Target: ${this.target.href}`);
        console.log(`[*] Started: ${new Date().toISOString()}`);
        
        await this.checkSSL();
        await this.checkSecurityHeaders();
        await this.checkCommonPaths();
        
        this.printSummary();
    }

    printSummary() {
        console.log('\n' + '═'.repeat(60));
        console.log(' SCAN SUMMARY');
        console.log('═'.repeat(60));
        
        const missingHeaders = this.results.headers.filter(h => h.status === 'MISSING');
        const accessiblePaths = this.results.paths.filter(p => p.status === 200);
        
        console.log(`\n[*] Missing Security Headers: ${missingHeaders.length}`);
        for (const h of missingHeaders) {
            console.log(`    - [${h.severity}] ${h.header}`);
        }
        
        console.log(`\n[*] Accessible Sensitive Paths: ${accessiblePaths.length}`);
        for (const p of accessiblePaths) {
            console.log(`    - ${p.path}`);
        }
        
        if (Object.keys(this.results.info).length > 0) {
            console.log('\n[*] Information Disclosure:');
            for (const [key, value] of Object.entries(this.results.info)) {
                console.log(`    - ${key}: ${value}`);
            }
        }
        
        console.log('\n' + '═'.repeat(60));
        console.log(`[*] Scan completed: ${new Date().toISOString()}`);
    }
}

// Main
const args = process.argv.slice(2);
if (args.length === 0) {
    console.log(BANNER);
    console.log('Usage: nullsec-webscan <target_url>');
    console.log('\nExample: nullsec-webscan https://example.com');
    process.exit(1);
}

const scanner = new WebScanner(args[0]);
scanner.runScan().catch(err => {
    console.error(`[-] Error: ${err.message}`);
    process.exit(1);
});
