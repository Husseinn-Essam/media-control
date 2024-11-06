import { useState } from "react";
import UpdateElectron from "@/components/update";
import logoVite from "./assets/logo-vite.svg";
import logoElectron from "./assets/logo-electron.svg";
import "./App.css";

function App() {
  return (
    <div className="App">
      <div className="flex justify-center items-center ">
        <div className="relative flex flex-col items-center">
          <div className="text-6xl animate-bounce">🖕</div>

          <div className="absolute top-0 -translate-y-20">
            <div className="relative flex space-x-4">
              <div className="text-2xl text-blue-500 animate-note1">🎶</div>

              <div className="text-3xl text-purple-500 animate-note2">🎵</div>

              <div className="text-4xl text-green-500 animate-note3">🎶</div>
            </div>
          </div>
        </div>
      </div>
      <h1 className="">Media Control</h1>

      <UpdateElectron />
    </div>
  );
}

export default App;
