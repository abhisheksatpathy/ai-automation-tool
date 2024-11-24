class WebSocketService {
    constructor() {
        this.ws = null;
        this.listeners = new Set();
    }

    connect(workflowId) {
        this.ws = new WebSocket(`ws://localhost:8000/ws/${workflowId}`);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.notifyListeners(data);
        };

        this.ws.onclose = () => {
            setTimeout(() => this.connect(workflowId), 1000);
        };
    }

    addListener(callback) {
        this.listeners.add(callback);
        return () => this.listeners.delete(callback);
    }

    notifyListeners(data) {
        this.listeners.forEach(listener => listener(data));
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

export const wsService = new WebSocketService();
