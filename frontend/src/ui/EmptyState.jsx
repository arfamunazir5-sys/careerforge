import "../theme.css";
import "./States.css";
import Card from "./Card";

export default function EmptyState({ title, message, action }) {
  return (
    <Card>
      <div className="st-center">
        <div className="st-icon" aria-hidden="true">&middot;</div>
        <h3 className="st-title">{title}</h3>
        {message && <p className="st-message">{message}</p>}
        {action}
      </div>
    </Card>
  );
}