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

interface Direction {
  internal: string;
  display: string;
}

interface Motion {
  internal: string;
  display: string;
}

const GestureMap = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [gestureMappings, setGestureMappings] = useState<GestureMappings>({
    oneFinger: "unmapped",
    twoFinger: "unmapped",
    threeFinger: "unmapped",
    fourFinger: "unmapped",
    fiveFinger: "unmapped",
    rockOn: "unmapped",
    fist: "unmapped",
  });

  const [directionMappings, setDirectionMappings] = useState<GestureMappings>({
    oneFingerUp: "unmapped",
    oneFingerDown: "unmapped",
    oneFingerLeft: "unmapped",
    oneFingerRight: "unmapped",
  });

  const [motionMappings, setMotionMappings] = useState<GestureMappings>({
    moveHandUp: "unmapped",
    moveHandDown: "unmapped",
    moveHandLeft: "unmapped",
    moveHandRight: "unmapped",
  });

  const actions: Action[] = [
    { internal: "unmapped", display: "Unmapped" },
    { internal: "mute", display: "Mute" },
    { internal: "volume_up", display: "Volume Up" },
    { internal: "volume_down", display: "Volume Down" },
    { internal: "play_pause", display: "Play/Pause" },
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

  const directions: Direction[] = [
    { internal: "oneFingerUp", display: "One Finger Up" },
    { internal: "oneFingerDown", display: "One Finger Down" },
    { internal: "oneFingerLeft", display: "One Finger Left" },
    { internal: "oneFingerRight", display: "One Finger Right" },
  ];

  const motions: Motion[] = [
    { internal: "moveHandUp", display: "Move Hand Up" },
    { internal: "moveHandDown", display: "Move Hand Down" },
    { internal: "moveHandLeft", display: "Move Hand Left" },
    { internal: "moveHandRight", display: "Move Hand Right" },
  ];

  const handleMappingChange = (mappingType: string, key: string, action: string) => {
    if (mappingType === "gesture") {
      setGestureMappings((prevMappings) => ({
        ...prevMappings,
        [key]: action,
      }));
    } else if (mappingType === "direction") {
      setDirectionMappings((prevMappings) => ({
        ...prevMappings,
        [key]: action,
      }));
    } else if (mappingType === "motion") {
      setMotionMappings((prevMappings) => ({
        ...prevMappings,
        [key]: action,
      }));
    }
  };

  const navigate = useNavigate();
  const handleNavigate = () => {
    navigate("/");
  };

  const submitMappings = async () => {
    try {
      const response = await fetch("http://localhost:5000/update-gesture-mappings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // Set the Content-Type header
        },
        body: JSON.stringify({
          gestureMappings,
          directionMappings,
          motionMappings,
        }),
      });
      const data = await response.json();
      console.log("Mappings:", data);
    } catch (error) {
      console.error("Error submitting mappings:", error);
    }
  };

  useEffect(() => {
    const fetchMappings = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:5000/gesture-mappings");
        const data = await response.json();
        setGestureMappings(data.gestureMappings);
        setDirectionMappings(data.directionMappings);
        setMotionMappings(data.motionMappings);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching mappings:", error);
        setLoading(false);
      }
    };

    fetchMappings();
  }, []);

  const getAvailableActions = (currentKey: string): Action[] => {
    let assignedActions: string[] = [];
    if (gestureMappings[currentKey] !== undefined) {
      assignedActions = Object.values(gestureMappings).filter(action => action !== "unmapped" && action !== gestureMappings[currentKey]);
    } else if (directionMappings[currentKey] !== undefined) {
      assignedActions = Object.values(directionMappings).filter(action => action !== "unmapped" && action !== directionMappings[currentKey]);
    } else if (motionMappings[currentKey] !== undefined) {
      assignedActions = Object.values(motionMappings).filter(action => action !== "unmapped" && action !== motionMappings[currentKey]);
    }
    return actions.filter(action => !assignedActions.includes(action.internal));
  };

  return (
    <div>
      <h1>Gesture Mapping</h1>
      <div className="flex flex-row gap-12 w-full">
        <div className="flex flex-col gap-4 w-1/3 min-w-[250px]">
          <h2>Gestures</h2>
          {gestures.map(({ internal: gestureInternal, display: gestureDisplay }) => (
        <div key={gestureInternal} className="flex flex-row justify-between items-center">
          <label>{gestureDisplay}</label>
          <select
            className="mt-2 mb-2 p-2 border-none text-white rounded"
            value={gestureMappings[gestureInternal]}
            onChange={(e) => handleMappingChange("gesture", gestureInternal, e.target.value)}
          >
            {getAvailableActions(gestureInternal).map(({ internal: actionInternal, display: actionDisplay }) => (
          <option key={actionInternal} value={actionInternal}>
            {actionDisplay}
          </option>
            ))}
          </select>
        </div>
          ))}
        </div>
        <div className="flex flex-col gap-4 w-1/3 min-w-[250px]">
          <h2>Directions</h2>
          {directions.map(({ internal: directionInternal, display: directionDisplay }) => (
        <div key={directionInternal} className="flex flex-row justify-between items-center">
          <label>{directionDisplay}</label>
          <select
            className="mt-2 mb-2 p-2 border-none text-white rounded"
            value={directionMappings[directionInternal]}
            onChange={(e) => handleMappingChange("direction", directionInternal, e.target.value)}
          >
            {getAvailableActions(directionInternal).map(({ internal: actionInternal, display: actionDisplay }) => (
          <option key={actionInternal} value={actionInternal}>
            {actionDisplay}
          </option>
            ))}
          </select>
        </div>
          ))}
        </div>
        <div className="flex flex-col gap-4 w-1/3 min-w-[250px]">
          <h2>Motions</h2>
          {motions.map(({ internal: motionInternal, display: motionDisplay }) => (
        <div key={motionInternal} className="flex flex-row justify-between items-center">
          <label>{motionDisplay}</label>
          <select
            className="mt-2 mb-2 p-2 border-none text-white rounded"
            value={motionMappings[motionInternal]}
            onChange={(e) => handleMappingChange("motion", motionInternal, e.target.value)}
          >
            {getAvailableActions(motionInternal).map(({ internal: actionInternal, display: actionDisplay }) => (
          <option key={actionInternal} value={actionInternal}>
            {actionDisplay}
          </option>
            ))}
          </select>
        </div>
          ))}
        </div>
      </div>
      <div className="flex flex-col justify-center">
        <button
          onClick={submitMappings}
          className="mt-4 p-2 border-none text-white rounded cursor-pointer text-xl px-6 py-3 font-semibold transition duration-300 bg-violet-600 hover:bg-slate-900"
        >
          Confirm Gesture Mappings
        </button>
        <button
          onClick={handleNavigate}
          className="mt-4 p-2 border-none text-white rounded cursor-pointer text-xl px-6 py-3 font-semibold"
        >
          Go Back
        </button>
      </div>
    </div>
  );
};

export default GestureMap;