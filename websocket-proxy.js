// WebSocket Proxy Server for Telnet and VNC
// يجب تشغيل هذا الخادم على السيرفر

const WebSocket = require('ws');
const net = require('net');
const http = require('http');
const url = require('url');

// إعدادات الخادم
const TELNET_PROXY_PORT = 8081;
const VNC_PROXY_PORT = 8080;

// ==================== Telnet Proxy ====================
const telnetServer = new WebSocket.Server({ port: TELNET_PROXY_PORT });

console.log(`Telnet WebSocket Proxy running on port ${TELNET_PROXY_PORT}`);

telnetServer.on('connection', (ws, req) => {
    const parsedUrl = url.parse(req.url, true);
    const pathParts = parsedUrl.pathname.split('/');

    // Extract host and port from URL: /telnet/host/port
    let targetHost = 'localhost';
    let targetPort = 23;

    if (pathParts.length >= 3) {
        targetHost = pathParts[2] || targetHost;
    }
    if (pathParts.length >= 4) {
        targetPort = parseInt(pathParts[3]) || targetPort;
    }

    console.log(`New Telnet connection to ${targetHost}:${targetPort}`);

    // Connect to Telnet server
    const telnetSocket = new net.Socket();

    telnetSocket.connect(targetPort, targetHost, () => {
        console.log(`Connected to Telnet server ${targetHost}:${targetPort}`);
        ws.send(`\r\n*** Connected to ${targetHost}:${targetPort} ***\r\n`);
    });

    // Forward data from Telnet to WebSocket
    telnetSocket.on('data', (data) => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(data);
        }
    });

    // Forward data from WebSocket to Telnet
    ws.on('message', (message) => {
        if (telnetSocket.writable) {
            telnetSocket.write(message);
        }
    });

    // Handle disconnections
    telnetSocket.on('close', () => {
        console.log('Telnet connection closed');
        if (ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
    });

    telnetSocket.on('error', (err) => {
        console.error('Telnet error:', err.message);
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(`\r\n*** Error: ${err.message} ***\r\n`);
            ws.close();
        }
    });

    ws.on('close', () => {
        console.log('WebSocket connection closed');
        telnetSocket.end();
    });

    ws.on('error', (err) => {
        console.error('WebSocket error:', err.message);
        telnetSocket.end();
    });
});

// ==================== VNC Proxy (WebSockify) ====================
// يتطلب تثبيت: npm install websockify

try {
    const websockify = require('websockify');

    const vncServer = http.createServer();
    websockify(vncServer, {
        target: 'localhost:5900' // Default VNC server
    });

    vncServer.listen(VNC_PROXY_PORT, () => {
        console.log(`VNC WebSocket Proxy running on port ${VNC_PROXY_PORT}`);
    });

} catch (e) {
    console.log('VNC Proxy: websockify not installed. Run: npm install websockify');
}

// ==================== SSH Proxy (Optional) ====================
// يمكن إضافة دعم SSH باستخدام node-ssh أو ssh2

console.log('\nProxy servers started successfully!');
console.log('Make sure to:');
console.log('1. Install dependencies: npm install ws websockify');
console.log('2. Configure your firewall to allow these ports');
console.log('3. Update the WebSocket URLs in the HTML files');