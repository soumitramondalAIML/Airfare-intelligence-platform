import { NavLink } from "react-router-dom";
import {
  BarChart3,
  BookOpenText,
  Braces,
  ChartNoAxesCombined,
  Database,
  LayoutDashboard,
  PlaneTakeoff,
  Route,
  ShieldCheck,
} from "lucide-react";
import "./styles/Sidebar.css";

const navigation = [
  {
    label: "Dashboard",
    path: "/",
    icon: <LayoutDashboard size={19} />,
    end: true,
  },
  {
    label: "Route Analytics",
    path: "/routes",
    icon: <Route size={19} />,
  },
  {
    label: "Fare Explorer",
    path: "/fares",
    icon: <Database size={19} />,
  },
  {
    label: "Data Quality",
    path: "/quality",
    icon: <ShieldCheck size={19} />,
  },
  {
    label: "DGCA Back-test",
    path: "/backtest",
    icon: <ChartNoAxesCombined size={19} />,
  },
];

function Sidebar({ isOpen, onClose }) {
  return (
    <aside
     className={`premium-sidebar ${isOpen ? "sidebar-open" : ""}`}
    >
      <div className="premium-brand">
        <div className="premium-brand-logo">
          <PlaneTakeoff size={24} />
        </div>

        <div>
          <h1>APIx</h1>
          <span>India</span>
        </div>
      </div>

      <div className="sidebar-product">
        <BarChart3 size={15} />
        National Airfare Intelligence
      </div>

      <p className="premium-sidebar-label">ANALYTICS</p>

      <nav className="premium-sidebar-nav">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            onClick={onClose}
            className={({ isActive }) =>
              `premium-nav-item ${isActive ? "active" : ""}`
            }
          >
            {item.icon}
            <span>{item.label}</span>

            {item.label === "Data Quality" && (
              <span className="nav-status"></span>
            )}
          </NavLink>
        ))}
      </nav>

      <p className="premium-sidebar-label resource-label">
        RESOURCES
      </p>

      <nav className="premium-sidebar-nav">
        <NavLink
          to="/methodology"
          onClick={onClose}
          className={({ isActive }) =>
            `premium-nav-item ${isActive ? "active" : ""}`
          }
        >
          <BookOpenText size={19} />
          <span>Methodology</span>
        </NavLink>

        <NavLink
          to="/api"
          onClick={onClose}
          className={({ isActive }) =>
            `premium-nav-item ${isActive ? "active" : ""}`
          }
        >
          <Braces size={19} />
          <span>API Access</span>
        </NavLink>
      </nav>

      <div className="sidebar-bottom-card">
        <div className="sidebar-bottom-icon">
          <ShieldCheck size={18} />
        </div>

        <div>
          <strong>Secure Collection</strong>
          <span>Ethical scraping safeguards enabled</span>
        </div>
      </div>

      <div className="sidebar-version">
        APIx Prototype · SIH 2026
      </div>
    </aside>
  );
}

export default Sidebar;