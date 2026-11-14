
import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
} from "react-router-dom";

import Overview from "./pages/Overview";
import ModelComparison from "./pages/ModelComparison";
import Forecasting from "./pages/Forecasting";
import SeasonalAnalysis from "./pages/SeasonalAnalysis";
import EconomicAnalysis from "./pages/EconomicAnalysis";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">

        {/* SIDEBAR */}
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-icon">₱</div>

            <div>
              <h2>RemitTrendPH</h2>
              <span>Remittance Intelligence</span>
            </div>
          </div>

          <div className="nav-label">MAIN MENU</div>

          <nav className="navigation">

            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              ▦ &nbsp; Overview
            </NavLink>

            <NavLink
              to="/forecasting"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              ↗ &nbsp; Forecasting
            </NavLink>

            <NavLink
              to="/models"
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              ▤ &nbsp; Model Comparison
            </NavLink>

<NavLink
  to="/seasonal-analysis"
  className={({ isActive }) =>
    isActive ? "nav-link active" : "nav-link"
  }
>
  Seasonal & Trend Analysis
</NavLink>

<NavLink
  to="/economic-analysis"
  className={({ isActive }) =>
    isActive ? "nav-link active" : "nav-link"
  }
>
  Economic Analysis
</NavLink>

          </nav>

          <div className="sidebar-bottom">
            <div className="status-dot"></div>
            Data through June 2026
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route
              path="/models"
              element={<ModelComparison />}
            />
            <Route
              path="/forecasting"
              element={<Forecasting />}
            />
<Route
  path="/seasonal-analysis"
  element={<SeasonalAnalysis />}
/>

<Route
  path="/economic-analysis"
  element={<EconomicAnalysis />}
/>
          </Routes>
        </main>

      </div>
    </BrowserRouter>
  );
}

export default App;
