const AGENT_COLORS = {
  skill_building: "#2F6F5E",
  networking: "#3B6EA5",
  portfolio: "#C97A2B",
  interview_prep: "#7A5C8E",
};

const AGENT_LABELS = {
  skill_building: "Skill Building",
  networking: "Networking",
  portfolio: "Portfolio",
  interview_prep: "Interview Prep",
};

function AllocationBar({ tasks }) {
  const hoursByAgent = {};
  tasks.forEach((task) => {
    hoursByAgent[task.agent] = (hoursByAgent[task.agent] || 0) + task.hours;
  });

  const totalHours = Object.values(hoursByAgent).reduce((sum, h) => sum + h, 0);
  if (totalHours === 0) return null;

  return (
    <div className="allocation-bar-wrap">
      <div className="allocation-bar">
        {Object.entries(hoursByAgent).map(([agent, hours]) => (
          <div
            key={agent}
            className="allocation-segment"
            style={{ width: `${(hours / totalHours) * 100}%`, background: AGENT_COLORS[agent] || "#999" }}
          >
            {hours}h
          </div>
        ))}
      </div>
      <div className="allocation-legend">
        {Object.keys(hoursByAgent).map((agent) => (
          <span key={agent}>
            <span className="legend-dot" style={{ background: AGENT_COLORS[agent] || "#999" }} />
            {AGENT_LABELS[agent] || agent}
          </span>
        ))}
      </div>
    </div>
  );
}

export default AllocationBar;