import { getWebSocketUrl } from '../utils/websocketUrl';

class WebSocketService {
    constructor() {
        this.ws = null;
        this.listeners = new Set();
    }

    connect(workflowId) {
        const wsUrl = getWebSocketUrl(`/ws/${workflowId}`);
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
