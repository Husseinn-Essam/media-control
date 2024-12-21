import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Settings = () => {
  const [selectedCamera, setSelectedCamera] = useState<number>(0);
  const [selectedColorMode, setSelectedColorMode] = useState<string>("HSV");
  const [boundedRatio, setBoundedRatio] = useState<number>(0.25);
  
  const navigate = useNavigate();
  const handleNavigate = () => {
    navigate("/");
  };

    const submitSettings = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/settings",
          {
            method: "POST",
            body: JSON.stringify({
              camera: selectedCamera,
              color_mode: selectedColorMode,
              bounded_ratio: boundedRatio,
            }),
          }
        );
        const data = await response.json();
        console.log("Settings:", data);
      } catch (error) {
        console.error("Error fetching settings:", error);
      }
    };


  return (
    <div>
      <h1>System Settings</h1>
      <div className="flex flex-col gap-4 w-full min-w-[300px]">
        <div className="flex flex-row justify-between items-center">
          <label>Selected Camera</label>
          <select
            className="mt-2 mb-2 p-2 border-none text-white rounded"
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(Number(e.target.value))}
          >
            <option value={0}>Camera 0</option>
            <option value={1}>Camera 1</option>
          </select>
        </div>
        <div className="flex flex-row justify-between items-center">
          <label>Color Mode</label>
          <select
            className="mt-2 mb-2 p-2 border-none text-white rounded"
            value={selectedColorMode}
            onChange={(e) => setSelectedColorMode(e.target.value)}
          >
            <option value="HSV">HSV</option>
            <option value="YcRcb">YcRcb</option>
          </select>
        </div>
        <div className="flex flex-row justify-between items-center">
          <label className="mr-4">Bounding Box Ratio</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={boundedRatio}
            onChange={(e) => setBoundedRatio(Number(e.target.value))}
            className="mt-2 mb-2 p-2 border-none text-white rounded w-14"
          />
        </div>
      </div>
      <div className="flex flex-col justify-center">
      <button
        onClick={submitSettings}
        className="mt-4 p-2 border-none text-white rounded cursor-pointer bg-blue-500 hover:bg-blue-700"
      >
        Confirm Changes
      </button>
      <button
        onClick={handleNavigate}
        className="mt-4 p-2 border-none text-white rounded cursor-pointer"
      >
        go back
      </button>
      </div>
    </div>
  );
};

export default Settings;
