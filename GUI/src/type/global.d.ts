export {};

declare global {
  interface Window {
    electronAPI: {
      sendToPython: (message: any) => void;
      receiveFromPython: (callback: (data: any) => void) => void;
    };
  }
}