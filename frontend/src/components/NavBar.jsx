import { NavLink } from "react-router-dom";
import { CalendarCheck, User, LayoutDashboard } from "lucide-react";

const linkClass = ({ isActive }) => (isActive ? "nav-link active" : "nav-link");

function NavBar() {
  return (
    <nav className="nav-bar">
      <span className="brand-mark">CareerForge</span>
      <div className="nav-links">
        <NavLink to="/" end className={linkClass}>
          <CalendarCheck size={16} aria-hidden="true" />
          <span>Weekly Plan</span>
        </NavLink>
        <NavLink to="/profile" className={linkClass}>
          <User size={16} aria-hidden="true" />
          <span>Profile</span>
        </NavLink>
        <NavLink to="/dashboard" className={linkClass}>
          <LayoutDashboard size={16} aria-hidden="true" />
          <span>Dashboard</span>
        </NavLink>
      </div>
    </nav>
  );
}

export default NavBar;