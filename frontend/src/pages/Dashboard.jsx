import {
  useEffect,
  useState,
} from "react";

import {
  Activity,
  ArrowRight,
  CalendarDays,
  ChevronDown,
  Database,
  IndianRupee,
  MapPin,
  Plane,
  Search,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import StatCard from "../components/StatCard";
import RouteHeatmap from "../components/RouteHeatmap";
import {
  useNavigate,
} from "react-router-dom";

import {
  getDashboardData,
} from "../services/api";

import "./styles/Dashboard.css";


function Dashboard() {

  /* =====================================================
     STATE
  ===================================================== */

  const navigate = useNavigate();

  const [selectedWindow, setSelectedWindow] =
  useState("T+7");

  const [selectedPeriod, setSelectedPeriod] =
  useState("30");

  const [dashboardData, setDashboardData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState(null);


  /* =====================================================
     LOAD DASHBOARD DATA
  ===================================================== */

  const loadDashboard = async () => {

    try {

      setLoading(true);
      setError(null);

      const data =
        await getDashboardData();

      setDashboardData(data);

    } catch (err) {

      console.error(
        "Unable to load dashboard:",
        err
      );

      setError(
        "Dashboard data could not be loaded."
      );

    } finally {

      setLoading(false);

    }

  };


  /* =====================================================
     INITIAL FETCH
  ===================================================== */

  useEffect(() => {

    let active = true;


    async function fetchDashboard() {

      try {

        setLoading(true);
        setError(null);

        const data =
          await getDashboardData();


        if (active) {
          setDashboardData(data);
        }

      } catch (err) {

        console.error(
          "Unable to load dashboard:",
          err
        );


        if (active) {

          setError(
            "Dashboard data could not be loaded."
          );

        }

      } finally {

        if (active) {
          setLoading(false);
        }

      }

    }


    fetchDashboard();


    return () => {
      active = false;
    };

  }, []);


  /* =====================================================
     LOADING STATE
  ===================================================== */

  if (loading) {

    return (
      <div className="dashboard-state-screen">

        <div className="dashboard-loader"></div>

        <strong>
          Loading airfare intelligence
        </strong>

        <span>
          Preparing the latest dashboard data...
        </span>

      </div>
    );

  }


  /* =====================================================
     ERROR STATE
  ===================================================== */

  if (error || !dashboardData) {

    return (
      <div className="dashboard-state-screen dashboard-error-state">

        <Activity size={28} />

        <strong>
          Unable to load dashboard
        </strong>

        <span>
          {error ||
            "No dashboard data is currently available."}
        </span>

        <button
          type="button"
          onClick={loadDashboard}
        >
          Try Again
        </button>

      </div>
    );

  }


  /* =====================================================
     DATA
  ===================================================== */

  const {
    stats: dashboardStats,
    system: systemInfo,
    trend: trendData,
    leadTime: leadTimeData,
    heatmap: routeHeatmapData,
    sources: sourceCoverage,
  } = dashboardData;


  return (
    <div className="premium-dashboard">

      {/* =====================================================
          HERO
      ===================================================== */}

      <section className="aviation-hero">

        <div className="hero-glow hero-glow-one"></div>
        <div className="hero-glow hero-glow-two"></div>


        <div className="hero-flight-path">

          <div className="flight-path-line"></div>

          <Plane size={27} />

        </div>


        <div className="hero-content">

          <div className="hero-badge">
            Domestic Airfare Monitor · India
          </div>


          <h1>
            Track the movement of
            <span>
              {" "}airfares across India.
            </span>
          </h1>


          <p>
            A high-frequency view of domestic airfare
            movements across routes, carriers and
            advance-purchase windows.
          </p>


          <div className="hero-meta">

            <span>

              <span className="live-dot"></span>

              Live monitoring

            </span>


            <span>

              <Database size={14} />

              {Number(
                systemInfo.observationsToday || 0
              ).toLocaleString("en-IN")}

              {" "}observations today

            </span>


            <span>

              <ShieldCheck size={14} />

              {systemInfo.activeSources || 0}

              {" "}active sources

            </span>

          </div>

        </div>


        {/* =====================================================
            ROUTE ANALYSER
        ===================================================== */}

        <div className="route-search-card">

          <div className="route-search-heading">

            <div>

              <strong>
                Explore airfare intelligence
              </strong>

              <span>
                Analyse any monitored domestic route
              </span>

            </div>


            <div className="analytics-tag">
              ANALYTICS
            </div>

          </div>


          <div className="route-search-grid">

            {/* ORIGIN */}

            <button
              type="button"
              className="search-field location-field origin-field"
            >

              <div className="search-field-icon">

                <Plane size={17} />

              </div>


              <div>

                <span>
                  FROM
                </span>

                <strong>
                  Delhi
                </strong>

                <small>
                  DEL · Indira Gandhi International
                </small>

              </div>

            </button>


            {/* SWAP */}

            <div className="route-swap">

              <ArrowRight size={18} />

            </div>


            {/* DESTINATION */}

            <button
              type="button"
              className="search-field location-field destination-field"
            >

              <div className="search-field-icon destination">

                <MapPin size={17} />

              </div>


              <div>

                <span>
                  TO
                </span>

                <strong>
                  Mumbai
                </strong>

                <small>
                  BOM · Chhatrapati Shivaji Maharaj
                </small>

              </div>

            </button>


            {/* WINDOW */}

            {/* WINDOW */}

            <label className="search-field compact-field window-field">

              <div className="search-field-icon">
                <CalendarDays size={17} />
              </div>

              <div>
                <span>WINDOW</span>

                <select
                 value={selectedWindow}
                 onChange={(event) =>
                   setSelectedWindow(event.target.value)
                 }
                 className="dashboard-route-select"
               >         
                 <option value="T+1">T+1 Days</option>
                 <option value="T+7">T+7 Days</option>
                 <option value="T+15">T+15 Days</option>
                 <option value="T+30">T+30 Days</option>
                 <option value="T+45">T+45 Days</option>
               </select>
             </div>

           </label>


            {/* PERIOD */}

<label className="search-field compact-field period-field">

  <div>
    <span>PERIOD</span>

    <select
      value={selectedPeriod}
      onChange={(event) =>
        setSelectedPeriod(event.target.value)
      }
      className="dashboard-route-select"
    >
      <option value="7">
        Last 7 days
      </option>

      <option value="30">
        Last 30 days
      </option>

      <option value="90">
        Last 3 months
      </option>
    </select>
  </div>

</label>

            {/* ANALYSE */}

            <button
              type="button"
              className="analyse-button"
              onClick={() =>
                navigate(
                  `/routes?origin=DEL&destination=BOM&window=${encodeURIComponent(
                    selectedWindow
                  )}&period=${selectedPeriod}`
                )
              }
             >

              <Search size={18} />

              Analyse Route

            </button>

          </div>

        </div>

      </section>


      {/* =====================================================
          EXECUTIVE OVERVIEW
      ===================================================== */}

      <div className="premium-page-heading">

        <div>

          <span>
            EXECUTIVE OVERVIEW
          </span>

          <h2>
            National Airfare Pulse
          </h2>

          <p>
            Latest movement in India's monitored
            domestic airfare basket.
          </p>

        </div>


        <div className="updated-chip">

          Updated{" "}

          {systemInfo.lastUpdated ||
            "recently"}

        </div>

      </div>


      {/* =====================================================
          KPI CARDS
      ===================================================== */}

      <div className="premium-stats-grid">

        <StatCard
          title="National APIx"
          value={
            dashboardStats.currentIndex
          }
          change={`+${
            dashboardStats.dailyChange
          }%`}
          changeType="positive"
          subtitle="from previous day"
          detail="Base index = 100"
          accent="index"
          icon={
            <Activity size={19} />
          }
        />


        <StatCard
          title="Average Domestic Fare"
          value={`₹${Number(
            dashboardStats.averageFare || 0
          ).toLocaleString("en-IN")}`}
          change="+3.8%"
          changeType="positive"
          subtitle="over 30 days"
          detail="Across monitored city-pairs"
          accent="fare"
          icon={
            <IndianRupee size={19} />
          }
        />


        <StatCard
          title="30-Day Movement"
          value={`+${
            dashboardStats.monthlyChange
          }%`}
          change={`+${
            dashboardStats.weeklyChange
          }%`}
          changeType="positive"
          subtitle="over 7 days"
          detail="Weighted airfare basket"
          accent="movement"
          icon={
            <TrendingUp size={19} />
          }
        />


        <StatCard
          title="Collection Coverage"
          value={`${
            dashboardStats.sourceCoverage
          }%`}
          change="Healthy"
          changeType="positive"
          subtitle="today"
          detail={`${
            systemInfo.activeSources
          } monitored sources`}
          accent="coverage"
          icon={
            <Database size={19} />
          }
        />

      </div>


      {/* =====================================================
          PRIMARY ANALYTICS
      ===================================================== */}

      <div className="analytics-row">

        {/* APIx TREND */}

        <section className="premium-panel trend-panel">

          <div className="premium-panel-header">

            <div>

              <span className="panel-eyebrow">
                PRICE INDEX
              </span>

              <h3>
                Airfare Price Index Trend
              </h3>

              <p>
                Daily movement in the national
                airfare basket
              </p>

            </div>


            <select defaultValue="30">

              <option value="7">
                7 Days
              </option>

              <option value="30">
                30 Days
              </option>

              <option value="90">
                3 Months
              </option>

            </select>

          </div>


          <div className="trend-summary">

            <div>

              <span>
                CURRENT INDEX
              </span>

              <strong>
                {dashboardStats.currentIndex}
              </strong>

            </div>


            <div>

              <span>
                MONTHLY CHANGE
              </span>

              <strong className="positive-text">
                +
                {dashboardStats.monthlyChange}
                %
              </strong>

            </div>


            <div>

              <span>
                AVERAGE FARE
              </span>

              <strong>
                ₹
                {Number(
                  dashboardStats.averageFare || 0
                ).toLocaleString("en-IN")}
              </strong>

            </div>

          </div>


          <div className="main-chart">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <AreaChart
                data={trendData || []}
              >

                <defs>

                  <linearGradient
                    id="indexGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >

                    <stop
                      offset="0%"
                      stopColor="#C86A32"
                      stopOpacity={0.25}
                    />

                    <stop
                      offset="100%"
                      stopColor="#C86A32"
                      stopOpacity={0}
                    />

                  </linearGradient>

                </defs>


                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#eee8df"
                />


                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: "#817c73",
                    fontSize: 10,
                  }}
                />


                <YAxis
                  domain={[98, 110]}
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: "#817c73",
                    fontSize: 10,
                  }}
                />


                <Tooltip
                  contentStyle={{
                    borderRadius: "7px",
                    border:
                      "1px solid #ded7cc",
                    background:
                      "#fffdf8",
                    boxShadow:
                      "0 10px 25px rgba(30,29,25,.08)",
                  }}
                />


                <Area
                  type="monotone"
                  dataKey="index"
                  stroke="#C86A32"
                  strokeWidth={2.6}
                  fill="url(#indexGradient)"
                />

              </AreaChart>

            </ResponsiveContainer>

          </div>

        </section>


        {/* ROUTE HEATMAP */}

        <RouteHeatmap
          data={routeHeatmapData}
        />

      </div>


      {/* =====================================================
          LOWER ANALYTICS
      ===================================================== */}

      <div className="lower-analytics-grid">

        {/* LEAD TIME */}

        <section className="premium-panel lead-panel">

          <div className="premium-panel-header">

            <div>

              <span className="panel-eyebrow">
                BOOKING BEHAVIOUR
              </span>

              <h3>
                Advance Purchase Intelligence
              </h3>

              <p>
                How fares change as departure
                approaches
              </p>

            </div>


            <div className="route-pill">
              DEL → BOM
            </div>

          </div>


          <div className="lead-chart">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <LineChart
                data={leadTimeData || []}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#eee8df"
                />


                <XAxis
                  dataKey="window"
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: "#817c73",
                    fontSize: 10,
                  }}
                />


                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: "#817c73",
                    fontSize: 10,
                  }}
                  tickFormatter={(value) =>
                    `₹${Math.round(
                      value / 1000
                    )}k`
                  }
                />


                <Tooltip
                  formatter={(value) => [
                    `₹${Number(
                      value
                    ).toLocaleString(
                      "en-IN"
                    )}`,
                    "Average Fare",
                  ]}
                  contentStyle={{
                    borderRadius: "7px",
                    border:
                      "1px solid #ded7cc",
                    background:
                      "#fffdf8",
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="fare"
                  stroke="#566B57"
                  strokeWidth={2.6}
                  dot={{
                    r: 4,
                    fill: "#fffdf8",
                    strokeWidth: 2.5,
                    stroke: "#566B57",
                  }}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>


          <div className="lead-insight">

            <div className="lead-insight-icon">

              <TrendingUp size={17} />

            </div>


            <div>

              <strong>
                Pricing observation
              </strong>

              <span>
                Current sample indicates
                substantially higher fares close
                to departure.
              </span>

            </div>

          </div>

        </section>


        {/* SOURCE COVERAGE */}

        <section className="premium-panel source-panel">

          <div className="premium-panel-header">

            <div>

              <span className="panel-eyebrow">
                COLLECTION NETWORK
              </span>

              <h3>
                Source Coverage
              </h3>

              <p>
                Airlines and OTA portals monitored
              </p>

            </div>


            <div className="health-badge">

              <span></span>

              Healthy

            </div>

          </div>


          <div className="coverage-ring-wrap">

            <div className="coverage-ring">

              <div>

                <strong>
                  {
                    dashboardStats
                      .sourceCoverage
                  }
                  %
                </strong>

                <span>
                  coverage
                </span>

              </div>

            </div>

          </div>


          <div className="source-chips">

            {(sourceCoverage || []).map(
              (source) => (

                <span key={source}>

                  <span className="source-status-dot"></span>

                  {source}

                </span>

              )
            )}

          </div>

        </section>

      </div>


      {/* =====================================================
          MOCK NOTICE
      ===================================================== */}

      <div className="mock-data-note">

        Prototype dashboard · Values currently
        shown are mock data for frontend
        development.

      </div>

    </div>
  );
}


export default Dashboard;