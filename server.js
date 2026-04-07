require('dotenv').config();

const app = require('./src/app');
const ocrManager = require('./src/utils/ocrManager');

const PORT = process.env.PORT ? Number(process.env.PORT) : 3000;

// Initialize OCR manager and start server
async function startServer() {
    try {
        console.log('Initializing OCR service...');
        await ocrManager.initialize();
        console.log('OCR service initialized and ready!');

        app.listen(PORT, () => {
            console.log(`Server listening on port ${PORT}`);
        });
    } catch (err) {
        console.error('Failed to initialize OCR service:', err.message);
        console.error('Server startup aborted.');
        process.exit(1);
    }
}

startServer();

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('Shutting down gracefully...');
    await ocrManager.shutdown();
    process.exit(0);
});
