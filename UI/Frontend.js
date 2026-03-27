const net = require('net');

function sendQuestion(question) {
    return new Promise((resolve, reject) => {
        const client = new net.Socket();

        let responseData = '';

        client.connect(50001, '127.0.0.1', () => {
            console.log('[INFO] Connected to Python server');

            const payload = JSON.stringify({
                message: question
            });

            client.write(payload);
        });

        // Collect response
        client.on('data', (data) => {
            responseData += data.toString();
        });

        client.on('end', () => {
            try {
                const parsed = JSON.parse(responseData);
                resolve(parsed.response);
            } catch (err) {
                reject('Invalid JSON response');
            }
        });

        client.on('error', (err) => {
            reject(err.message);
        });

        // ⏱️ 2-minute timeout
        client.setTimeout(120000);

        client.on('timeout', () => {
            client.destroy();
            reject('Request timed out after 2 minutes');
        });
    });
}

// Usage
sendQuestion("What is BACnet?")
    .then(res => console.log("[RESPONSE]", res))
    .catch(err => console.error("[ERROR]", err));