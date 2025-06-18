const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_BACKEND_URL = 'http://localhost:5000';

app.use('/ask', createProxyMiddleware({
    target: PYTHON_BACKEND_URL,
    changeOrigin: true, 

    onProxyReq: (proxyReq, req, res) => {
        console.log(`[Proxy] Requesting: ${req.method} ${req.url} -> ${proxyReq.protocol}//${proxyReq.host}${proxyReq.path}`);
    },
    onError: (err, req, res) => {
        console.error('[Proxy] Error:', err);
        res.status(500).send('Proxy Error: Could not connect to the Python backend.');
    }
}));

app.use(express.static(path.join(__dirname, '..', 'frontend')));

app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Express server running at http://localhost:${PORT}/`);
  console.log(`Python backend expected at ${PYTHON_BACKEND_URL}`);
});