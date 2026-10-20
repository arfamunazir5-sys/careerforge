import { useState } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import NavBar from "./components/NavBar";
import HomePage from "./pages/HomePage";
import HomePageV2 from "./pages/HomePageV2";
import DashboardPage from "./pages/DashboardPage";
import CommandCenterPage from "./pages/CommandCenterPage";
import ProfilePage from "./pages/ProfilePage";
import ProfilePageV2 from "./pages/ProfilePageV2";
import WakeUpBanner from "./ui/WakeUpBanner";
import ErrorBoundary from "./ui/ErrorBoundary";
import EmptyState from "./ui/EmptyState";

function Crash() {
  throw new Error("Test crash (dev only)");
}

function RoutedPages({ refreshKey, triggerRefresh }) {
  const location = useLocation();
  return (
    <ErrorBoundary key={location.pathname}>
      <Routes>
        <Route path="/" element={<HomePageV2 refreshKey={refreshKey} onTaskUpdate={triggerRefresh} />} />
        <Route path="/profile" element={<ProfilePageV2 onProfileComplete={triggerRefresh} />} />
        <Route path="/dashboard" element={<CommandCenterPage refreshKey={refreshKey} />} />
        <Route path="/plan-classic" element={<HomePage refreshKey={refreshKey} onTaskUpdate={triggerRefresh} />} />
        <Route path="/profile-classic" element={<ProfilePage onProfileComplete={triggerRefresh} />} />
        <Route path="/dashboard-classic" element={<DashboardPage refreshKey={refreshKey} />} />
        {import.meta.env.DEV && <Route path="/__crash" element={<Crash />} />}
        <Route
          path="*"
          element={
            <div className="cf-page">
              <EmptyState
                title="Page not found"
                message="That page does not exist."
                action={<Link className="btn-secondary" to="/">Back to Weekly Plan</Link>}
              />
            </div>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
}

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const triggerRefresh = () => setRefreshKey((k) => k + 1);

  return (
    <BrowserRouter>
      <div className="app-shell">
        <WakeUpBanner />
        <NavBar />
        <main>
          <RoutedPages refreshKey={refreshKey} triggerRefresh={triggerRefresh} />
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;