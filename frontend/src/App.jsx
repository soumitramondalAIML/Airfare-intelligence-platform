import { Routes, Route } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import RouteAnalytics from "./pages/RouteAnalytics";
import FareExplorer from "./pages/FareExplorer";
import DataQuality from "./pages/DataQuality";
import Backtest from "./pages/Backtest";
import Methodology from "./pages/Methodology";
import ApiDocs from "./pages/ApiDocs";

function PlaceholderPage({ title, description }) {
  return (
    <div className="placeholder-page">
      <h2>{title}</h2>
      <p>{description}</p>
      <div className="placeholder-box">
        This module will be implemented in the next development phase.
      </div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardLayout />}>
        <Route index element={<Dashboard />} />

        <Route
         path="routes"
         element={<RouteAnalytics />}
        />

        <Route
          path="fares"
          element={<FareExplorer />}
        />

       <Route
          path="quality"
          element={<DataQuality />}
        />

        <Route
          path="backtest"
          element={<Backtest />}
        />

        <Route
          path="methodology"
          element={<Methodology />}
        />

        <Route
          path="api"
          element={<ApiDocs />}
        />
      </Route>
    </Routes>
  );
}

export default App;