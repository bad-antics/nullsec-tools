#!/usr/bin/env node
/**
 * NullSec Directory Fuzzer
 * Fast async directory/file enumeration tool
 * Author: bad-antics | GitHub: bad-antics | Discord: discord.gg/killers
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const BANNER = `
╔═══════════════════════════════════════════════════════════╗
║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║
║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║
║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║
║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║
║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║
║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║
║                  DIRECTORY FUZZER (Node.js)                ║
║            bad-antics | @AnonAntics | discord.gg/killers  ║
╚═══════════════════════════════════════════════════════════╝
`;

const DEFAULT_WORDLIST = [
    'admin', 'administrator', 'backup', 'config', 'dashboard', 'db', 'debug',
    'dev', 'development', 'docs', 'download', 'files', 'hidden', 'images',
    'includes', 'js', 'css', 'lib', 'login', 'logs', 'media', 'old', 'panel',
    'private', 'public', 'scripts', 'secret', 'secure', 'server', 'static',
    'temp', 'test', 'tmp', 'upload', 'uploads', 'user', 'users', 'var', 'www',
    'api', 'v1', 'v2', 'graphql', 'rest', 'data', 'assets', 'vendor', 'node_modules',
    '.git', '.svn', '.env', 'wp-admin', 'wp-content', 'wp-includes', 'phpmyadmin',
    'cgi-bin', 'server-status', 'info.php', 'phpinfo.php', 'robots.txt', 'sitemap.xml'
];

const EXTENSIONS = ['', '.php', '.html', '.txt', '.bak', '.old', '.asp', '.aspx', '.jsp'];

class DirFuzzer {
    constructor(target, options = {}) {
        this.target = new URL(target);
        this.wordlist = options.wordlist || DEFAULT_WORDLIST;
        this.extensions = options.extensions || EXTENSIONS;
        this.threads = options.threads || 20;
        this.timeout = options.timeout || 5000;
        this.results = [];
        this.stats = { requests: 0, found: 0, errors: 0 };
    }

    async request(urlPath) {
        return new Promise((resolve) => {
            const protocol = this.target.protocol === 'https:' ? https : http;
            const options = {
                hostname: this.target.hostname,
                port: this.target.port || (this.target.protocol === 'https:' ? 443 : 80),
                path: urlPath,
                method: 'GET',
                headers: { 'User-Agent': 'NullSec-DirFuzz/1.0' },
                rejectUnauthorized: false,
                timeout: this.timeout
            };

            const req = protocol.request(options, (res) => {
                this.stats.requests++;
                resolve({ path: urlPath, status: res.statusCode, size: res.headers['content-length'] || 0 });
            });

            req.on('error', () => {
                this.stats.requests++;
                this.stats.errors++;
                resolve(null);
            });

            req.on('timeout', () => {
                req.destroy();
                this.stats.requests++;
                this.stats.errors++;
                resolve(null);
            });

            req.end();
        });
    }

    async fuzz() {
        console.log(BANNER);
        console.log(`[*] Target: ${this.target.href}`);
        console.log(`[*] Wordlist: ${this.wordlist.length} words`);
        console.log(`[*] Extensions: ${this.extensions.join(', ') || 'none'}`);
        console.log(`[*] Threads: ${this.threads}`);
        console.log(`[*] Starting fuzzing...\n`);

        const paths = [];
        for (const word of this.wordlist) {
            for (const ext of this.extensions) {
                paths.push(`/${word}${ext}`);
            }
        }

        const startTime = Date.now();
        const chunks = [];
        for (let i = 0; i < paths.length; i += this.threads) {
            chunks.push(paths.slice(i, i + this.threads));
        }

        for (const chunk of chunks) {
            const results = await Promise.all(chunk.map(p => this.request(p)));
            for (const res of results) {
                if (res && (res.status === 200 || res.status === 301 || res.status === 302 || res.status === 403)) {
                    this.stats.found++;
                    this.results.push(res);
                    const status = res.status === 200 ? '\x1b[32m' : res.status === 403 ? '\x1b[33m' : '\x1b[36m';
                    console.log(`${status}[${res.status}]\x1b[0m ${res.path} (${res.size} bytes)`);
                }
            }
        }

        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
        const rps = (this.stats.requests / elapsed).toFixed(0);

        console.log(`\n${'═'.repeat(60)}`);
        console.log(` SCAN COMPLETE`);
        console.log(`${'═'.repeat(60)}`);
        console.log(`[*] Requests: ${this.stats.requests}`);
        console.log(`[*] Found: ${this.stats.found}`);
        console.log(`[*] Errors: ${this.stats.errors}`);
        console.log(`[*] Time: ${elapsed}s (${rps} req/s)`);

        return this.results;
    }
}

// Parse args
const args = process.argv.slice(2);
if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
    console.log(BANNER);
    console.log('Usage: nullsec-dirfuzz <target> [options]');
    console.log('\nOptions:');
    console.log('  -w <file>    Custom wordlist file');
    console.log('  -x <ext>     Extensions (comma-separated)');
    console.log('  -t <num>     Threads (default: 20)');
    console.log('  -o <file>    Output results to file');
    console.log('\nExamples:');
    console.log('  nullsec-dirfuzz https://example.com');
    console.log('  nullsec-dirfuzz https://example.com -w wordlist.txt -t 50');
    process.exit(0);
}

const target = args[0];
const options = {};

for (let i = 1; i < args.length; i++) {
    if (args[i] === '-w' && args[i + 1]) {
        try {
            options.wordlist = fs.readFileSync(args[++i], 'utf-8').split('\n').filter(l => l.trim());
        } catch (e) {
            console.error(`[-] Cannot read wordlist: ${e.message}`);
            process.exit(1);
        }
    } else if (args[i] === '-x' && args[i + 1]) {
        options.extensions = args[++i].split(',').map(e => e.startsWith('.') ? e : `.${e}`);
    } else if (args[i] === '-t' && args[i + 1]) {
        options.threads = parseInt(args[++i]);
    }
}

const fuzzer = new DirFuzzer(target, options);
fuzzer.fuzz().catch(err => {
    console.error(`[-] Error: ${err.message}`);
    process.exit(1);
});
