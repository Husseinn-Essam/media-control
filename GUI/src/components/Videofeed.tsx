import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const VideoFeed = () => {
  const [gesture, setGesture] = useState<string>("No gesture detected");
  const [motionDetected, setMotionDetected] = useState<string>("N/A");
  const [motionLastDetected, setMotionLastDetected] = useState<string>("N/A");
  const [direction, setDirection] = useState<string>("N/A");
  const [loading, setLoading] = useState<boolean>(false); // Keep loading to control state

  const navigate = useNavigate();
  const handleNavigate = () => {
    navigate("/"); 
  };

  useEffect(() => {
    // Function to fetch gesture data
    const fetchGesture = async () => {
      try {
        setLoading(true); // Set loading to true when fetching
        const response = await fetch(
          "http://localhost:5000/recognize_gesture",
          {
            method: "POST",
          }
        );
        const data = await response.json();
        
        // Set the data from the response
        setGesture(data.gesture || gesture); // Retain previous gesture if no new gesture is fetched
        setMotionDetected(data.motion_detected || motionDetected);
        setMotionLastDetected(data.motion_last_detected || motionLastDetected);
        setDirection(data.direction || direction);
        setLoading(false); // Set loading to false after fetching is complete
      } catch (error) {
        console.error("Error fetching gesture:", error);
        setLoading(false); // Ensure loading is set to false if an error occurs
      }
    };

    // Set up polling every 500ms to keep fetching gesture data
    const intervalId = setInterval(() => {
      fetchGesture();
    }, 500);

    // Cleanup function to stop polling when the component unmounts
    return () => clearInterval(intervalId);
  }, [gesture, motionDetected, motionLastDetected, direction]); // Depend on state to retain last values

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
       
          <div className="flex flex-row gap-4">
            <p>Detected Gesture: {gesture}</p>
            <p>Motion Detected: {motionDetected}</p>
            <p>Last Motion Detected: {motionLastDetected}</p>
            <p>Direction: {direction}</p>
          </div>
       
      </div>
      <button
        onClick={handleNavigate}
        className="mt-4 p-2 border-none text-white rounded cursor-pointer"
      >
        Go Back
      </button>
    </div>
  );
};

export default VideoFeed;
