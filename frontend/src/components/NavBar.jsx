import { NavLink } from "react-router-dom";

function NavBar() {
  return (
    <nav className="nav-bar">
      <span className="brand-mark">CareerForge</span>
      <div className="nav-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
          Weekly Plan
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
          Dashboard
        </NavLink>
      </div>
    </nav>
  );
}

export default NavBar;