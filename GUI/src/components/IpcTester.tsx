
// this will only be used if we use ipc
import { useState, useEffect } from 'react';

export const IpcTester = () => {
    const [data, setData] = useState<string>("");
    const [input, setInput] = useState<string>("");
  
    useEffect(() => {
      // this will listen to data incoming from the python code
      window.electronAPI.receiveFromPython((response) => {
        // this line will output twice , because of useeffect so its totally okay
        console.log(response);
        
        setData(response.msgContent);
      });
    }, []);

 // event handler for sending data to python
 const handleSend = () => {
    window.electronAPI.sendToPython({ message: input });
  };

  return (
    <div>   
      <input
        type="text"
        placeholder="Test IPCs"
        className="p-2 rounded-md border-white"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button onClick={handleSend} className="mt-4 p-2 border-none text-white rounded cursor-pointer">
        Send to Python
      </button>
      {data && (
        <div className="mt-4">
          <h2>Response from Python:</h2>
          <p>{data}</p>
        </div>
      )}
    </div>
  );
};
