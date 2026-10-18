import StateHeader from "../components/StateHeader";
import WeeklyPlanPageV2 from "./WeeklyPlanPageV2";

function HomePageV2({ refreshKey, onTaskUpdate }) {
  return (
    <>
      <StateHeader refreshKey={refreshKey} />
      <WeeklyPlanPageV2 onTaskUpdate={onTaskUpdate} />
    </>
  );
}

export default HomePageV2;