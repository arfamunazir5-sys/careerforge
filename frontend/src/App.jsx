import StateHeader from "./components/StateHeader";
import WeeklyPlanPage from "./pages/WeeklyPlanPage";

function App() {
  return (
    <div className="app-shell">
      <StateHeader />
      <main>
        <WeeklyPlanPage />
      </main>
    </div>
  );
}

export default App;