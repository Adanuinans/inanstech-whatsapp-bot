// whatsapp_bridge/index.js
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(bodyParser.json());

let sock = null;
let isConnected = false;
let currentQR = null;
let messageCallback = null;
let messages = [];

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info');
    
    sock = makeWASocket({
        printQRInTerminal: false,
        auth: state,
        browser: ['Inanstech Bot', 'Chrome', '1.0.0']
    });
    
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            currentQR = qr;
            console.log('\n📱 QR Code received!');
            qrcode.generate(qr, { small: true });
            console.log('\n');
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed:', lastDisconnect?.error);
            if (shouldReconnect) {
                console.log('Reconnecting...');
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            isConnected = true;
            currentQR = null;
            console.log('✅ WhatsApp connected successfully!');
        }
    });
    
    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('messages.upsert', async ({ messages: newMessages }) => {
        for (const msg of newMessages) {
            if (!msg.message) continue;
            
            const from = msg.key.remoteJid;
            const messageText = msg.message.conversation || 
                                msg.message.extendedTextMessage?.text || 
                                '';
            
            if (messageText && !msg.key.fromMe && !from.includes('@g.us')) {
                console.log(`\n📨 Message from ${from}: ${messageText}`);
                
                const messageObj = {
                    from,
                    text: messageText,
                    timestamp: new Date().toISOString(),
                    type: 'incoming'
                };
                messages.push(messageObj);
                
                if (messageCallback) {
                    try {
                        const reply = await messageCallback(from, messageText);
                        if (reply) {
                            await sock.sendMessage(from, { text: reply });
                            console.log(`✅ Reply sent to ${from}`);
                            messages.push({
                                from,
                                text: reply,
                                timestamp: new Date().toISOString(),
                                type: 'outgoing'
                            });
                        }
                    } catch (err) {
                        console.error('Callback error:', err);
                    }
                }
            }
        }
    });
}

app.get('/api/qr', (req, res) => {
    if (isConnected) {
        res.json({ connected: true });
    } else if (currentQR) {
        res.json({ qr: currentQR, connected: false });
    } else {
        res.json({ connected: false });
    }
});

app.get('/api/status', (req, res) => {
    res.json({ connected: isConnected });
});

app.get('/api/messages', (req, res) => {
    res.json(messages.slice(-100));
});

app.post('/api/send', async (req, res) => {
    const { to, message } = req.body;
    if (sock && isConnected) {
        try {
            await sock.sendMessage(to, { text: message });
            res.json({ success: true });
        } catch (error) {
            res.json({ success: false, error: error.message });
        }
    } else {
        res.json({ success: false, error: 'Not connected' });
    }
});

connectToWhatsApp();

app.listen(PORT, () => {
    console.log(`\n🔗 WhatsApp bridge running on port ${PORT}`);
});