import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface Action {
  internal: string;
  display: string;
}

interface Gesture {
  internal: string;
  display: string;
}

interface GestureMappings {
  [key: string]: string;
}

const GestureMap = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [gestureMappings, setGestureMappings] = useState<GestureMappings>({
    oneFinger: "unmapped",
    twoFinger: "unmapped",
    threeFinger: "unmapped",
    fourFinger: "unmapped",
    fiveFinger: "unmapped",
    rockOn: "unmapped",
    fist: "unmapped",
  });

  const actions: Action[] = [
    { internal: "unmapped", display: "Unmapped" },
    { internal: "action1", display: "Action 1" },
    { internal: "action2", display: "Action 2" },
    { internal: "action3", display: "Action 3" },
    { internal: "action4", display: "Action 4" },
    { internal: "action5", display: "Action 5" },
    { internal: "action6", display: "Action 6" },
    { internal: "action7", display: "Action 7" },
  ];

  const gestures: Gesture[] = [
    { internal: "oneFinger", display: "One Finger" },
    { internal: "twoFinger", display: "Two Fingers" },
    { internal: "threeFinger", display: "Three Fingers" },
    { internal: "fourFinger", display: "Four Fingers" },
    { internal: "fiveFinger", display: "Five Fingers" },
    { internal: "rockOn", display: "Rock On" },
    { internal: "fist", display: "Fist" },
  ];

  const handleMappingChange = (gesture: string, action: string) => {
    setGestureMappings((prevMappings) => ({
      ...prevMappings,
      [gesture]: action,
    }));
  };

  const navigate = useNavigate();
  const handleNavigate = () => {
    navigate("/");
  };

  const submitMappings = async () => {
    try {
      const response = await fetch("http://localhost:5000/gesture-mappings", {
        method: "POST",
        body: JSON.stringify(gestureMappings),
      });
      const data = await response.json();
      console.log("Gesture Mappings:", data);
    } catch (error) {
      console.error("Error submitting gesture mappings:", error);
    }
  };

  useEffect(() => {
    const fetchMappings = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:5000/gesture-mappings");
        const data = await response.json();
        setGestureMappings(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching gesture mappings:", error);
        setLoading(false);
      }
    };

    fetchMappings();
  }, []);

  const getAvailableActions = (currentGesture: string): Action[] => {
    const assignedActions = Object.values(gestureMappings).filter(action => action !== "unmapped" && action !== gestureMappings[currentGesture]);
    return actions.filter(action => !assignedActions.includes(action.internal));
  };

  return (
    <div>
      <h1>Gesture Mapping</h1>
      <div className="flex flex-col gap-4 w-full min-w-[300px]">
        {loading ? "Retrieving settings configuration..." : <>
          {gestures.map(({ internal: gestureInternal, display: gestureDisplay }) => (
            <div key={gestureInternal} className="flex flex-row justify-between items-center">
              <label>{gestureDisplay}</label>
              <select
                className="mt-2 mb-2 p-2 border-none text-white rounded"
                value={gestureMappings[gestureInternal]}
                onChange={(e) => handleMappingChange(gestureInternal, e.target.value)}
              >
                {getAvailableActions(gestureInternal).map(({ internal: actionInternal, display: actionDisplay }) => (
                  <option key={actionInternal} value={actionInternal}>
                    {actionDisplay}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </>}
      </div>
      <div className="flex flex-col justify-center">
        <button
          onClick={submitMappings}
          className="mt-4 p-2 border-none text-white rounded cursor-pointer bg-blue-500 hover:bg-blue-700"
        >
          Confirm Gesture Mappings
        </button>
        <button
          onClick={handleNavigate}
          className="mt-4 p-2 border-none text-white rounded cursor-pointer"
        >
          Go Back
        </button>
      </div>
    </div>
  );
};

export default GestureMap;