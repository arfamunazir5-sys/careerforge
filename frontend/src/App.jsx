import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const triggerRefresh = () => setRefreshKey((k) => k + 1);

  return (
    <BrowserRouter>
      <div className="app-shell">
        <NavBar />
        <main>
          <Routes>
            <Route path="/" element={<HomePage refreshKey={refreshKey} onTaskUpdate={triggerRefresh} />} />
            <Route path="/dashboard" element={<DashboardPage refreshKey={refreshKey} />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;