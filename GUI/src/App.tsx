import { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import "./App.css";
import { StartPage } from "./components/StartPage";
import VideoFeed from "./components/Videofeed";
import GestureMap from "./components/GestureMap";
import Settings from "./components/Settings";

function App() {
  return (
    <div className="App">
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<StartPage />} />
            <Route path="/video-feed" element={<VideoFeed />} />
            <Route path="/gesture-mappings" element={<GestureMap />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
}

export default App;
