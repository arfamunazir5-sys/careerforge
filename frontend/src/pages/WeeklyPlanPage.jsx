import { useState, useEffect } from "react";
import { api } from "../api/client";
import TaskCard from "../components/TaskCard";
import AllocationBar from "../components/AllocationBar";

function WeeklyPlanPage() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getPlan();
      setPlan(data);
    } catch (err) {
      setPlan(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlan();
  }, []);

  const handleGeneratePlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.generatePlan();
      setPlan(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskAction = async (taskId, action) => {
    try {
      if (action === "done") {
        await api.completeTask(taskId);
      } else {
        await api.ignoreTask(taskId);
      }
      await loadPlan();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <p className="status-text">Loading this week's plan...</p>;

  return (
    <section className="plan-page">
      <div className="plan-page-header">
        <h2>This Week's Plan</h2>
        <button className="btn-primary" onClick={handleGeneratePlan}>
          Generate New Plan
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      {!plan && !error && (
        <p className="status-text">No plan yet — click "Generate New Plan" to get started.</p>
      )}

      {plan && (
        <>
          <AllocationBar tasks={plan.tasks} />
          <div className="task-list">
            {plan.tasks.map((task) => (
              <TaskCard key={task.id} task={task} onAction={handleTaskAction} />
            ))}
          </div>
        </>
      )}
    </section>
  );
}

export default WeeklyPlanPage;