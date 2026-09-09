import {
  useEffect,
  useState,
} from "react";

import {
  Activity,
  CalendarDays,
  CheckCircle2,
  Database,
  Info,
  Target,
  TrendingUp,
} from "lucide-react";

import {
  getBacktestData,
} from "../services/api";

import "./styles/Backtest.css";


function formatCurrency(
  value
) {

  if (
    value === null ||
    value === undefined
  ) {
    return "N/A";
  }

  return `₹${Number(
    value
  ).toLocaleString(
    "en-IN"
  )}`;
}


function Backtest() {

  const [
    backtestData,
    setBacktestData,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState(null);


  const loadBacktestData =
    async () => {

      try {

        setLoading(true);
        setError(null);

        const data =
          await getBacktestData();

        setBacktestData(
          data
        );

      } catch (err) {

        console.error(
          "Unable to load back-test data:",
          err
        );

        setError(
          "Validation data could not be loaded."
        );

      } finally {

        setLoading(false);

      }

    };


  useEffect(() => {

    let active = true;


    async function load() {

      try {

        setLoading(true);
        setError(null);

        const data =
          await getBacktestData();


        if (active) {

          setBacktestData(
            data
          );

        }

      } catch (err) {

        console.error(
          "Unable to load back-test data:",
          err
        );


        if (active) {

          setError(
            "Validation data could not be loaded."
          );

        }

      } finally {

        if (active) {

          setLoading(false);

        }

      }

    }


    load();


    return () => {

      active = false;

    };

  }, []);


  if (loading) {

    return (
      <div className="backtest-state-screen">

        <div className="backtest-loader"></div>

        <strong>
          Loading validation data
        </strong>

        <span>
          Checking real fare observations
          and official reference coverage...
        </span>

      </div>
    );

  }


  if (
    error ||
    !backtestData
  ) {

    return (
      <div
        className="
          backtest-state-screen
          backtest-error-state
        "
      >

        <Activity size={28} />

        <strong>
          Unable to load validation data
        </strong>

        <span>
          {error ||
            "No validation data is currently available."}
        </span>

        <button
          type="button"
          onClick={
            loadBacktestData
          }
        >
          Try Again
        </button>

      </div>
    );

  }


  const {
    summary,
    routeComparison,
    statisticalErrorComparable,
    dgcaStatus,
    dgcaNote,
    dataNote,
  } = backtestData;


  const correlationText =
    summary.correlation === null
      ? "N/A"
      : summary.correlation;


  const mapeText =
    summary.mape === null
      ? "N/A"
      : `${summary.mape}%`;


  return (
    <div className="backtest-page">

      {/* PAGE HEADER */}

      <div className="backtest-page-heading">

        <div>

          <span>
            MODEL VALIDATION
          </span>

          <h1>
            Reference Validation & DGCA Back-test
          </h1>

          <p>
            Validate real airfare observations
            against official reference data while
            keeping the DGCA statistical back-test
            separate until comparable DGCA fare
            observations are available.
          </p>

        </div>


        <div className="backtest-validation-badge">

          <CheckCircle2 size={15} />

          Official reference loaded

        </div>

      </div>


      {/* COLLECTION PERIOD */}

      <section className="backtest-period-panel">

        <div className="backtest-period-icon">

          <CalendarDays size={21} />

        </div>


        <div className="backtest-period-main">

          <span>
            REAL COLLECTION PERIOD
          </span>


          <div>

            <strong>
              {summary.startDate ||
                "N/A"}
            </strong>


            <div className="period-line">

              <span></span>

            </div>


            <strong>
              {summary.endDate ||
                "N/A"}
            </strong>

          </div>

        </div>


        <div className="backtest-days">

          <strong>
            {summary.numberOfDays}
          </strong>

          <span>
            DAY
            {summary.numberOfDays === 1
              ? ""
              : "S"}
          </span>

        </div>

      </section>


      {/* KPI SUMMARY */}

      <div className="backtest-summary-grid">

        <article>

          <Target size={19} />

          <div>

            <span>
              REFERENCE COVERAGE
            </span>

            <strong>
              {summary.routeCoverage}%
            </strong>

            <small>
              Project routes with an
              official reference
            </small>

          </div>

        </article>


        <article>

          <Database size={19} />

          <div>

            <span>
              MATCHED OBSERVATIONS
            </span>

            <strong>
              {Number(
                summary.matchedObservations ||
                0
              ).toLocaleString(
                "en-IN"
              )}
              /
              {Number(
                summary.observations ||
                0
              ).toLocaleString(
                "en-IN"
              )}
            </strong>

            <small>
              Real observations linked
              to reference data
            </small>

          </div>

        </article>


        <article>

          <TrendingUp size={19} />

          <div>

            <span>
              ROUTES REFERENCED
            </span>

            <strong>
              {summary.routesWithReference}
              /
              {summary.routesEvaluated}
            </strong>

            <small>
              Representative routes
              covered
            </small>

          </div>

        </article>


        <article>

          <Activity size={19} />

          <div>

            <span>
              DGCA BACK-TEST
            </span>

            <strong>
              {dgcaStatus ===
              "reference_data_pending"
                ? "Pending"
                : "Available"}
            </strong>

            <small>
              Comparable DGCA average-fare
              series
            </small>

          </div>

        </article>

      </div>


      {/* OFFICIAL REFERENCE VALIDATION */}

      <section className="backtest-panel">

        <div className="backtest-section-heading">

          <div>

            <span>
              REAL REFERENCE VALIDATION
            </span>

            <h2>
              Official Air India tariff coverage
            </h2>

            <p>
              Real Air India fare-calendar
              observations are matched to the
              official published Economy tariff
              reference for each representative
              route.
            </p>

          </div>


          <div className="comparison-legend-note">
            {summary.routeCoverage}%
            {" "}route coverage
          </div>

        </div>


        <div className="backtest-chart-explanation">

          <CheckCircle2 size={15} />

          <p>
            {summary.matchedObservations}
            {" "}of{" "}
            {summary.observations}
            {" "}real fare observations have a
            valid official route reference.
          </p>

        </div>

      </section>


      {/* STATISTICAL VALIDATION + DGCA */}

      <div className="backtest-analysis-grid">

        <section className="backtest-panel">

          <div className="backtest-section-heading">

            <div>

              <span>
                STATISTICAL COMPARABILITY
              </span>

              <h2>
                MAPE and correlation
              </h2>

              <p>
                Statistical error is calculated
                only when observed and reference
                values represent comparable fare
                quantities.
              </p>

            </div>

          </div>


          <div className="validation-score">

            <div className="validation-score-ring">

              <div>

                <strong>
                  {statisticalErrorComparable
                    ? "Yes"
                    : "N/A"}
                </strong>

              </div>

            </div>


            <strong>
              Direct statistical comparison
              is not applicable
            </strong>

            <p>
              The scraped observations are total
              fares, while the official Air India
              tariff contains base-fare ranges.
              Reporting a percentage error between
              them would be misleading.
            </p>

          </div>


          <div className="validation-checks">

            <div>

              <Info size={14} />

              <span>
                Correlation: {correlationText}
              </span>

            </div>


            <div>

              <Info size={14} />

              <span>
                MAPE: {mapeText}
              </span>

            </div>

          </div>

        </section>


        <section
          className="
            backtest-panel
            validation-panel
          "
        >

          <div className="backtest-section-heading">

            <div>

              <span>
                DGCA STATISTICAL BACK-TEST
              </span>

              <h2>
                Reference series pending
              </h2>

            </div>

          </div>


          <div className="validation-score">

            <div className="validation-score-ring">

              <div>

                <strong>
                  N/A
                </strong>

              </div>

            </div>


            <strong>
              No fabricated DGCA metrics
            </strong>

            <p>
              {dgcaNote ||
                "A comparable DGCA average-fare series has not yet been imported."}
            </p>

          </div>


          <div className="validation-checks">

            <div>

              <CheckCircle2 size={14} />

              <span>
                Real Air India observations loaded
              </span>

            </div>


            <div>

              <CheckCircle2 size={14} />

              <span>
                Official tariff references loaded
              </span>

            </div>


            <div>

              <Info size={14} />

              <span>
                DGCA average-fare series pending
              </span>

            </div>

          </div>

        </section>

      </div>


      {/* ROUTE VALIDATION */}

      <section className="backtest-panel">

        <div className="backtest-section-heading">

          <div>

            <span>
              ROUTE REFERENCE COVERAGE
            </span>

            <h2>
              Route-level real-data validation
            </h2>

            <p>
              Observed total fares are shown next
              to the official published base-fare
              envelope for provenance and
              plausibility reference only.
            </p>

          </div>

        </div>


        <div className="backtest-route-table">

          <div className="backtest-route-header">

            <span>
              Route
            </span>

            <span>
              Avg Total Fare
            </span>

            <span>
              Official Base-Fare Range
            </span>

            <span>
              Observations
            </span>

            <span>
              Reference
            </span>

          </div>


          {(routeComparison || []).map(
            (route) => (

              <div
                className="backtest-route-row"
                key={route.route}
              >

                <strong>
                  {route.route}
                </strong>


                <span>
                  {formatCurrency(
                    route.observedAverage
                  )}
                </span>


                <span>
                  {formatCurrency(
                    route.referenceMinimum
                  )}
                  {" – "}
                  {formatCurrency(
                    route.referenceMaximum
                  )}
                </span>


                <strong>
                  {route.observations}
                </strong>


                <span
                  className={`backtest-assessment ${
                    route.referenceAvailable
                      ? "good"
                      : "review"
                  }`}
                >
                  {route.referenceAvailable
                    ? "Available"
                    : "Missing"}
                </span>

              </div>

            )
          )}

        </div>

      </section>


      {/* DATA NOTE */}

      <div className="backtest-warning">

        <Info size={15} />

        <div>

          <strong>
            Validation methodology
          </strong>

          <p>
            {dataNote}
            {" "}
            Official tariff coverage is real
            reference validation, but it is not
            presented as a DGCA statistical
            back-test. MAPE and correlation remain
            N/A until directly comparable reference
            observations are available.
          </p>

        </div>

      </div>

    </div>
  );
}


export default Backtest;