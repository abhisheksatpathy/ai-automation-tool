class WebSocketService {
    constructor() {
        this.ws = null;
        this.listeners = new Set();
    }

    connect(workflowId) {
        const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
        let wsProtocol = 'ws://';

        if (baseUrl.startsWith('https://')) {
            wsProtocol = 'wss://';
        } else if (baseUrl.startsWith('http://')) {
            wsProtocol = 'ws://';
        }

        // Remove the protocol part ('http://' or 'https://') from the baseUrl
        const baseUrlWithoutProtocol = baseUrl.replace(/^https?:\/\//, '');

        const wsUrl = `${wsProtocol}${baseUrlWithoutProtocol}/ws/${workflowId}`;

        console.log(`Connecting to WebSocket at ${wsUrl}`);

        this.ws = new WebSocket(wsUrl);

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.notifyListeners(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket closed, reconnecting...');
            setTimeout(() => this.connect(workflowId), 1000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    addListener(callback) {
        this.listeners.add(callback);
        return () => this.listeners.delete(callback);
    }

    notifyListeners(data) {
        this.listeners.forEach((listener) => listener(data));
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

export const wsService = new WebSocketService();
