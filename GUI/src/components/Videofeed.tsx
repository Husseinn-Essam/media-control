import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const VideoFeed = () => {
  const [gesture, setGesture] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const handleNavigate = () => {
    navigate("/"); 
  };
  // useEffect(() => {
  //   // Function to fetch gesture data
  //   const fetchGesture = async () => {
  //     try {
  //       setLoading(true);
  //       const response = await fetch(
  //         "http://localhost:5000/recognize_gesture",
  //         {
  //           method: "POST",
  //         }
  //       );
  //       const data = await response.json();
  //       setGesture(data.gesture);
  //       console.log("Gesture:", data.gesture);
        
  //       setLoading(false);
  //     } catch (error) {
  //       console.error("Error fetching gesture:", error);
  //       setLoading(false);
  //     }
  //   };

  //   // Set up polling every second
  //   const intervalId = setInterval(() => {
  //     fetchGesture();
  //   }, 1000);

  //   // Cleanup function to stop polling when component unmounts
  //   return () => clearInterval(intervalId);
  // }, []);
  return (
    <div>
      <h1>Live Video Feed</h1>
      <img
        src="http://localhost:5000/video_feed"
        alt="Video Stream"
        style={{ width: "100%", height: "auto" }}
      />
      <div>
        <h1>Gesture Recognition</h1>
        {loading ? (
          <p>Loading gesture...</p>
        ) : (
          <p>Detected Gesture: {gesture || "No gesture detected"}</p>
        )}
      </div>
      <button
        onClick={handleNavigate}
        className="mt-4 p-2 border-none text-white rounded cursor-pointer
          text-xl px-6 py-3 font-semibold">Go Back</button>
    </div>
  );
};

export default VideoFeed;
