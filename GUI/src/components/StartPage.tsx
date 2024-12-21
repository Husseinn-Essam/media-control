import { useNavigate } from "react-router-dom";

export const StartPage = () => {
  const navigate = useNavigate();
  
  const handleNavigate = (path: string) => {
    navigate(path); 
  };
  
  const fetchGesture = async () => {
    try {
      const response = await fetch(
        "http://localhost:5000/recognize_gesture",
        {
          method: "POST",
        }
      );
      
    } catch (error) {
    
    }
  };

  return (
    <div>
      <div className="flex justify-center items-center mx-auto">
        <div className="relative flex flex-col items-center">
          <div className="text-6xl animate-bounce">👋</div>
          <div className="absolute top-0 -translate-y-20">
            <div className="relative flex space-x-4">
              <div className="text-2xl text-blue-500 animate-note1">🎶</div>
              <div className="text-3xl text-purple-500 animate-note2">🎵</div>
              <div className="text-4xl text-green-500 animate-note3">🎶</div>
            </div>
          </div>
        </div>
      </div>
      <h1 className="text-6xl mb-8">Media Control</h1>
      <div className="flex flex-col justify-center gap-4">
      <button
        onClick={fetchGesture}
        className="w-50 text-xl px-6 py-3 text-white font-semibold rounded-lg border-none  
                                                transition duration-300 bg-violet-600 hover:bg-slate-900 hover:cursor-pointer"
      >
        Start Feed 📹
      </button>
      <button
        onClick={() => handleNavigate("/gesture-mappings")}
        className="w-50 text-xl px-6 py-3 text-white font-semibold rounded-lg border-none  
                                                transition duration-300 bg-violet-600 hover:bg-slate-900 hover:cursor-pointer"
      >
        Gesture Mapping 🖐
      </button>
      <button
        onClick={() => handleNavigate("/settings")}
        className="w-50 text-xl px-6 py-3 text-white font-semibold rounded-lg border-none  
                                                transition duration-300 bg-violet-600 hover:bg-slate-900 hover:cursor-pointer"
      >
        Settings ⚙️
      </button>
      </div>
    </div>
  );
};
