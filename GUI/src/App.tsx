import { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import "./App.css";
import { StartPage } from "./components/StartPage";
import VideoFeed from "./components/Videofeed";

function App() {
  return (
    <div className="App">
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<StartPage />} />
            <Route path="/video-feed" element={<VideoFeed />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
}

export default App;
