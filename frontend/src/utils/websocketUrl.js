export const getWebSocketUrl = (path) => {
    const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
    let wsProtocol = 'ws://';
  
    if (baseUrl.startsWith('https://')) {
      wsProtocol = 'wss://';
    } else if (baseUrl.startsWith('http://')) {
      wsProtocol = 'ws://';
    }
  
    const baseUrlWithoutProtocol = baseUrl.replace(/^https?:\/\//, '');
  
    return `${wsProtocol}${baseUrlWithoutProtocol}${path}`;
  };
  