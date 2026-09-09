import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  Bell,
  Menu,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

import {
  getScraperHealth,
} from "../services/api";

import "./styles/Header.css";


function Header({
  onMenuClick,
}) {

  const [
    health,
    setHealth,
  ] = useState(null);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);


  const loadHealth =
    useCallback(
      async () => {

        try {

          setRefreshing(true);

          const result =
            await getScraperHealth();

          setHealth(
            result
          );

        } catch (error) {

          console.error(
            "Unable to load scraper health:",
            error
          );

          setHealth(
            {
              overallStatus:
                "unavailable",

              dataMode:
                "unknown",

              sources: [],
            }
          );

        } finally {

          setRefreshing(false);

        }

      },
      []
    );


  useEffect(
    () => {

      loadHealth();

    },
    [
      loadHealth,
    ]
  );


  const sources =
    health?.sources || [];


  const primarySource =
    sources[0] || null;


  let dataLabel =
    "Checking data";


  if (
    health?.dataMode === "real"
  ) {

    if (
      sources.length === 1
      && primarySource?.source
    ) {

      dataLabel =
        `Real Data · ${primarySource.source}`;

    } else if (
      sources.length > 1
    ) {

      dataLabel =
        `Real Data · ${sources.length} sources`;

    } else {

      dataLabel =
        "Real Data";

    }

  } else if (
    health?.dataMode === "mock"
  ) {

    dataLabel =
      "Mock Data";

  }


  let healthLabel =
    "Checking collection";


  switch (
    health?.overallStatus
  ) {

    case "healthy":

      healthLabel =
        "Collection healthy";

      break;


    case "degraded":

      healthLabel =
        "Collection degraded";

      break;


    case "failed":

      healthLabel =
        "Collection failed";

      break;


    case "unavailable":

      healthLabel =
        "Collection unavailable";

      break;


    case "unknown":

      healthLabel =
        "Collection unknown";

      break;


    default:

      break;
  }


  const healthTooltip =
    primarySource
      ? (
          `${primarySource.source}: ` +
          `${primarySource.storedObservations}/` +
          `${primarySource.expectedObservations} ` +
          `observations · ` +
          `${primarySource.coveragePct}% coverage`
        )
      : (
          "Collection status"
        );


  return (

    <header className="premium-header">

      <div className="header-left">

        <button
          className="mobile-menu-button"
          onClick={onMenuClick}
          aria-label="Open navigation"
        >
          <Menu size={20} />
        </button>


        <div className="gov-badge">

          भारत सरकार

        </div>


        <div>

          <p>
            Ministry of Statistics & Programme
            Implementation
          </p>

          <strong>
            Airfare Intelligence Platform
          </strong>

        </div>

      </div>


      <div className="header-right">

        <div
          className="live-data-chip"
          title={
            primarySource
              ? (
                  `Latest collection: ${
                    primarySource.latestCollectionDate ||
                    "N/A"
                  }`
                )
              : "Data source status"
          }
        >

          <span className="pulse-dot"></span>

          {dataLabel}

        </div>


        <div
          className="header-health"
          title={healthTooltip}
        >

          <ShieldCheck size={16} />

          <span>
            {healthLabel}
          </span>

        </div>


        <button
          className="header-icon-button"
          aria-label="Notifications"
          type="button"
        >

          <Bell size={18} />

        </button>


        <button
          className="premium-refresh"
          type="button"
          onClick={loadHealth}
          disabled={refreshing}
        >

          <RefreshCw size={16} />

          {refreshing
            ? "Refreshing"
            : "Refresh"}

        </button>

      </div>

    </header>
  );
}


export default Header;