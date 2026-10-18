import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import HomePage from "./pages/HomePage";
import HomePageV2 from "./pages/HomePageV2";
import DashboardPage from "./pages/DashboardPage";
import CommandCenterPage from "./pages/CommandCenterPage";
import ProfilePage from "./pages/ProfilePage";
import ProfilePageV2 from "./pages/ProfilePageV2";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const triggerRefresh = () => setRefreshKey((k) => k + 1);

  return (
    <BrowserRouter>
      <div className="app-shell">
        <NavBar />
        <main>
          <Routes>
            <Route path="/" element={<HomePageV2 refreshKey={refreshKey} onTaskUpdate={triggerRefresh} />} />
            <Route path="/profile" element={<ProfilePageV2 onProfileComplete={triggerRefresh} />} />
            <Route path="/dashboard" element={<CommandCenterPage refreshKey={refreshKey} />} />
            <Route path="/plan-classic" element={<HomePage refreshKey={refreshKey} onTaskUpdate={triggerRefresh} />} />
            <Route path="/profile-classic" element={<ProfilePage onProfileComplete={triggerRefresh} />} />
            <Route path="/dashboard-classic" element={<DashboardPage refreshKey={refreshKey} />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;