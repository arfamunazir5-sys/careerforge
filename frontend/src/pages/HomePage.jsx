import StateHeader from "../components/StateHeader";
import WeeklyPlanPage from "./WeeklyPlanPage";

function HomePage({ refreshKey, onTaskUpdate }) {
  return (
    <>
      <StateHeader refreshKey={refreshKey} />
      <WeeklyPlanPage onTaskUpdate={onTaskUpdate} />
    </>
  );
}

export default HomePage;