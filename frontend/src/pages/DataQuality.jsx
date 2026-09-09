import {
  useEffect,
  useState,
} from "react";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Database,
  RefreshCw,
  ShieldCheck,
  Trash2,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getQualityData,
} from "../services/api";

import "./styles/DataQuality.css";


function DataQuality() {

  /* =====================================================
     STATE
  ===================================================== */

  const [
    qualityData,
    setQualityData,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState(null);


  /* =====================================================
     LOAD QUALITY DATA
  ===================================================== */

  const loadQualityData = async (
    isRefresh = false
  ) => {

    try {

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError(null);

      const data =
        await getQualityData();

      setQualityData(data);

    } catch (err) {

      console.error(
        "Unable to load data quality:",
        err
      );

      setError(
        "Data quality information could not be loaded."
      );

    } finally {

      setLoading(false);
      setRefreshing(false);

    }

  };


  /* =====================================================
     INITIAL LOAD
  ===================================================== */

  useEffect(() => {

    let active = true;


    async function fetchQualityData() {

      try {

        setLoading(true);
        setError(null);

        const data =
          await getQualityData();


        if (active) {

          setQualityData(data);

        }

      } catch (err) {

        console.error(
          "Unable to load data quality:",
          err
        );


        if (active) {

          setError(
            "Data quality information could not be loaded."
          );

        }

      } finally {

        if (active) {

          setLoading(false);

        }

      }

    }


    fetchQualityData();


    return () => {

      active = false;

    };

  }, []);


  /* =====================================================
     LOADING
  ===================================================== */

  if (loading) {

    return (
      <div className="quality-state-screen">

        <div className="quality-loader"></div>

        <strong>
          Loading data quality
        </strong>

        <span>
          Checking collection health and validation data...
        </span>

      </div>
    );

  }


  /* =====================================================
     ERROR
  ===================================================== */

  if (
    error ||
    !qualityData
  ) {

    return (
      <div className="quality-state-screen quality-error-state">

        <Activity size={28} />

        <strong>
          Unable to load Data Quality
        </strong>

        <span>
          {error ||
            "No data quality information is currently available."}
        </span>

        <button
          type="button"
          onClick={() =>
            loadQualityData()
          }
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
    summary: qualitySummary,
    sources: sourceHealthData,
    trend: dailyQualityTrend,
    issues: qualityIssues,
  } = qualityData;


  return (
    <div className="quality-page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="quality-page-heading">

        <div>

          <span>
            DATA GOVERNANCE
          </span>

          <h1>
            Data Quality
          </h1>

          <p>
            Monitor collection reliability, cleaning operations
            and observation-level quality issues.
          </p>

        </div>


        <div className="quality-live-status">

          <span></span>

          Quality pipeline active

        </div>

      </div>


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <div className="quality-summary-grid">

        <article>

          <ShieldCheck />

          <div>

            <span>
              COLLECTION HEALTH
            </span>

            <strong>
              {qualitySummary.collectionHealth}%
            </strong>

            <small>
              Across monitored sources
            </small>

          </div>

        </article>


        <article>

          <CheckCircle2 />

          <div>

            <span>
              VALID OBSERVATIONS
            </span>

            <strong>
              {Number(
                qualitySummary.validObservations || 0
              ).toLocaleString("en-IN")}
            </strong>

            <small>
              Passed quality checks
            </small>

          </div>

        </article>


        <article>

          <AlertTriangle />

          <div>

            <span>
              FLAGGED RECORDS
            </span>

            <strong>
              {qualitySummary.flaggedRecords}
            </strong>

            <small>
              Require review or exclusion
            </small>

          </div>

        </article>


        <article>

          <Database />

          <div>

            <span>
              MISSING QUOTES
            </span>

            <strong>
              {qualitySummary.missingQuotes}
            </strong>

            <small>
              Current collection cycle
            </small>

          </div>

        </article>

      </div>


      {/* =====================================================
          CLEANING PIPELINE
      ===================================================== */}

      <section className="quality-panel cleaning-pipeline-panel">

        <div className="quality-section-heading">

          <div>

            <span>
              PROCESSING PIPELINE
            </span>

            <h2>
              Observation cleaning workflow
            </h2>

            <p>
              Each collected quote passes through validation
              before contributing to APIx.
            </p>

          </div>

        </div>


        <div className="cleaning-pipeline">

          <div className="pipeline-step completed">

            <span>
              01
            </span>

            <strong>
              Raw Collection
            </strong>

            <small>
              2,014 quotes
            </small>

          </div>


          <div className="pipeline-arrow">
            →
          </div>


          <div className="pipeline-step completed">

            <span>
              02
            </span>

            <strong>
              Deduplicate
            </strong>

            <small>
              {qualitySummary.duplicateRecords}
              {" "}removed
            </small>

          </div>


          <div className="pipeline-arrow">
            →
          </div>


          <div className="pipeline-step completed">

            <span>
              03
            </span>

            <strong>
              Missing Values
            </strong>

            <small>
              {qualitySummary.missingQuotes}
              {" "}handled
            </small>

          </div>


          <div className="pipeline-arrow">
            →
          </div>


          <div className="pipeline-step completed">

            <span>
              04
            </span>

            <strong>
              Outlier Detection
            </strong>

            <small>
              {qualitySummary.outliersRemoved}
              {" "}flagged
            </small>

          </div>


          <div className="pipeline-arrow">
            →
          </div>


          <div className="pipeline-step final">

            <span>
              05
            </span>

            <strong>
              Normalised
            </strong>

            <small>
              {Number(
                qualitySummary.validObservations || 0
              ).toLocaleString("en-IN")}
              {" "}valid
            </small>

          </div>

        </div>

      </section>


      {/* =====================================================
          MAIN GRID
      ===================================================== */}

      <div className="quality-main-grid">

        {/* =====================================================
            SOURCE HEALTH
        ===================================================== */}

        <section className="quality-panel">

          <div className="quality-section-heading">

            <div>

              <span>
                COLLECTION SOURCES
              </span>

              <h2>
                Source health
              </h2>

              <p>
                Current availability and coverage of monitored portals.
              </p>

            </div>


            <button
              type="button"
              className="quality-refresh-button"
              onClick={() =>
                loadQualityData(true)
              }
              disabled={refreshing}
            >

              <RefreshCw
                size={14}
                className={
                  refreshing
                    ? "refresh-spinning"
                    : ""
                }
              />

              {refreshing
                ? "Checking..."
                : "Check sources"}

            </button>

          </div>


          <div className="source-health-table">

            <div className="source-health-header">

              <span>
                Source
              </span>

              <span>
                Status
              </span>

              <span>
                Coverage
              </span>

              <span>
                Records
              </span>

              <span>
                Updated
              </span>

            </div>


            {(sourceHealthData || []).map(
              (source) => (

                <div
                  className="source-health-row"
                  key={source.source}
                >

                  <div>

                    <strong>
                      {source.source}
                    </strong>

                    <span>
                      {source.type}
                    </span>

                  </div>


                  <span
                    className={`source-health-status ${
                      source.status.toLowerCase()
                    }`}
                  >

                    <i></i>

                    {source.status}

                  </span>


                  <strong>
                    {source.coverage}%
                  </strong>


                  <span>
                    {Number(
                      source.records || 0
                    ).toLocaleString(
                      "en-IN"
                    )}
                  </span>


                  <span className="source-updated">

                    <Clock3 size={12} />

                    {source.lastUpdate}

                  </span>

                </div>

              )
            )}

          </div>

        </section>


        {/* =====================================================
            QUALITY TREND
        ===================================================== */}

        <section className="quality-panel">

          <div className="quality-section-heading">

            <div>

              <span>
                7-DAY QUALITY
              </span>

              <h2>
                Collection coverage
              </h2>

              <p>
                Percentage of expected fare observations
                successfully collected.
              </p>

            </div>

          </div>


          <div className="quality-chart">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <AreaChart
                data={
                  dailyQualityTrend || []
                }
              >

                <defs>

                  <linearGradient
                    id="qualityGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >

                    <stop
                      offset="0%"
                      stopColor="#566B57"
                      stopOpacity={0.22}
                    />

                    <stop
                      offset="100%"
                      stopColor="#566B57"
                      stopOpacity={0}
                    />

                  </linearGradient>

                </defs>


                <CartesianGrid
                  vertical={false}
                  stroke="#eee8df"
                  strokeDasharray="3 3"
                />


                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: "#817c73",
                    fontSize: 9,
                  }}
                />


                <YAxis
                  domain={[90, 100]}
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: "#817c73",
                    fontSize: 9,
                  }}
                  tickFormatter={(
                    value
                  ) =>
                    `${value}%`
                  }
                />


                <Tooltip
                  formatter={(
                    value
                  ) => [
                    `${value}%`,
                    "Coverage",
                  ]}
                />


                <Area
                  type="monotone"
                  dataKey="coverage"
                  stroke="#566B57"
                  strokeWidth={2.5}
                  fill="url(#qualityGradient)"
                />

              </AreaChart>

            </ResponsiveContainer>

          </div>


          <div className="quality-chart-note">

            <ShieldCheck size={15} />

            <div>

              <strong>
                {qualitySummary.collectionHealth}%
                {" "}collection coverage
              </strong>

              <span>
                Above the current prototype monitoring threshold.
              </span>

            </div>

          </div>

        </section>

      </div>


      {/* =====================================================
          QUALITY ISSUES
      ===================================================== */}

      <section className="quality-panel quality-issues-panel">

        <div className="quality-section-heading">

          <div>

            <span>
              QUALITY EVENTS
            </span>

            <h2>
              Recent data issues
            </h2>

            <p>
              Observations requiring correction,
              exclusion or review.
            </p>

          </div>

        </div>


        <div className="quality-issue-table">

          <div className="quality-issue-header">

            <span>ID</span>
            <span>Issue</span>
            <span>Source</span>
            <span>Route</span>
            <span>Window</span>
            <span>Severity</span>
            <span>Action</span>

          </div>


          {(qualityIssues || []).map(
            (issue) => (

              <div
                className="quality-issue-row"
                key={issue.id}
              >

                <strong>
                  {issue.id}
                </strong>

                <span>
                  {issue.type}
                </span>

                <span>
                  {issue.source}
                </span>

                <strong>
                  {issue.route}
                </strong>

                <span>
                  {issue.window}
                </span>

                <span
                  className={`issue-severity ${
                    issue.severity.toLowerCase()
                  }`}
                >
                  {issue.severity}
                </span>


                <span className="issue-action">

                  {issue.action ===
                    "Removed" && (

                    <Trash2
                      size={12}
                    />

                  )}

                  {issue.action}

                </span>

              </div>

            )
          )}

        </div>

      </section>


      {/* =====================================================
          MOCK NOTICE
      ===================================================== */}

      <div className="mock-data-note">

        Prototype Data Quality dashboard · Values shown are
        mock frontend data.

      </div>

    </div>
  );
}


export default DataQuality;