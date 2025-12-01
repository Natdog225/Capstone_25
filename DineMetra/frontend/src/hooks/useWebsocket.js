import { useEffect, useRef, useState, useCallback } from 'react';

const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 5;

export const useWebSocket = (url, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  const connect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }

    console.log(`WebSocket: Connecting to ${url}...`);
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket: Connected');
      setIsConnected(true);
      setReconnectAttempts(0);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket: Message received:', data);
        onMessage?.(data);
      } catch (error) {
        console.error('WebSocket: Failed to parse message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket: Error:', error);
      setIsConnected(false);
    };

    ws.current.onclose = () => {
      console.log('WebSocket: Disconnected');
      setIsConnected(false);

      // Attempt reconnection
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        console.log(`WebSocket: Reconnecting in ${RECONNECT_DELAY}ms... (Attempt ${reconnectAttempts + 1})`);
        reconnectTimeout.current = setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connect();
        }, RECONNECT_DELAY);
      } else {
        console.error('WebSocket: Max reconnection attempts reached');
      }
    };
  }, [url, onMessage, reconnectAttempts]);

  useEffect(() => {
    connect();

    return () => {
      console.log('WebSocket: Cleaning up connection');
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket: Cannot send message, not connected');
    }
  }, []);

  return {
    isConnected,
    reconnectAttempts,
    sendMessage
  };
};