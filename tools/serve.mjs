// Lokaler Testserver wie beim Webhoster (.htaccess): Kompression, Cache-Header, CSP. Aufruf: node tools/serve.mjs [port]
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { gzipSync, brotliCompressSync } from 'node:zlib';
import { extname, join, normalize } from 'node:path';
const root = process.cwd();
const port = +(process.argv[2] || 8791);
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'application/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.png': 'image/png' };
const long = { '.woff2': 31536000, '.css': 31536000, '.js': 31536000, '.webp': 2592000, '.jpg': 2592000, '.svg': 2592000 };
createServer(async (req, res) => {
  try {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (p.endsWith('/')) p += 'index.html';
    const f = normalize(join(root, p));
    if (!f.startsWith(root)) throw 0;
    await stat(f);
    let body = await readFile(f);
    const ext = extname(f);
    const h = { 'Content-Type': types[ext] || 'application/octet-stream', 'Cache-Control': long[ext] ? `public, max-age=${long[ext]}` : 'no-cache',
      'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; object-src 'none'" };
    const ae = req.headers['accept-encoding'] || '';
    if (/\.(html|css|js|json|svg)$/.test(ext)) {
      if (ae.includes('br')) { body = brotliCompressSync(body); h['Content-Encoding'] = 'br'; }
      else if (ae.includes('gzip')) { body = gzipSync(body); h['Content-Encoding'] = 'gzip'; }
      h['Vary'] = 'Accept-Encoding';
    }
    res.writeHead(200, h); res.end(body);
  } catch (e) { res.writeHead(404); res.end('404'); }
}).listen(port, () => console.log('http://localhost:' + port));
