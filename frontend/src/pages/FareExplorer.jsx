import {
  useEffect,
  useState,
} from "react";

import {
  Activity,
  Database,
  Download,
  ExternalLink,
  Filter,
  IndianRupee,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";

import {
  getFares,
} from "../services/api";

import "./styles/FareExplorer.css";


function FareExplorer() {

  /* =====================================================
     DATA STATE
  ===================================================== */

  const [
    fareObservations,
    setFareObservations,
  ] = useState([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState(null);


  /* =====================================================
     FILTER STATE
  ===================================================== */

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    route,
    setRoute,
  ] = useState("All");

  const [
    sourceType,
    setSourceType,
  ] = useState("All");

  const [
    windowFilter,
    setWindowFilter,
  ] = useState("All");

  const [
    selectedFare,
    setSelectedFare,
  ] = useState(null);


  /* =====================================================
     LOAD FARES
  ===================================================== */

  const loadFares = async () => {

    try {

      setLoading(true);
      setError(null);

      const data =
        await getFares();

      setFareObservations(
        Array.isArray(data)
          ? data
          : []
      );

    } catch (err) {

      console.error(
        "Unable to load fare observations:",
        err
      );

      setError(
        "Fare observations could not be loaded."
      );

    } finally {

      setLoading(false);

    }

  };


  /* =====================================================
     INITIAL LOAD
  ===================================================== */

  useEffect(() => {

    let active = true;


    async function fetchFares() {

      try {

        setLoading(true);
        setError(null);

        const data =
          await getFares();


        if (active) {

          setFareObservations(
            Array.isArray(data)
              ? data
              : []
          );

        }

      } catch (err) {

        console.error(
          "Unable to load fare observations:",
          err
        );


        if (active) {

          setError(
            "Fare observations could not be loaded."
          );

        }

      } finally {

        if (active) {
          setLoading(false);
        }

      }

    }


    fetchFares();


    return () => {

      active = false;

    };

  }, []);


  /* =====================================================
     FILTERED DATA

     No useMemo is needed here.
     The mock dataset is small and this avoids
     unnecessary hook-order issues.
  ===================================================== */

  const filteredFares =
    fareObservations.filter(
      (fare) => {

        const routeCode =
          `${fare.origin}-${fare.destination}`;


        const searchValue =
          search.toLowerCase();


        const matchesSearch =
          fare.carrier
            .toLowerCase()
            .includes(searchValue) ||

          fare.source
            .toLowerCase()
            .includes(searchValue) ||

          fare.id
            .toLowerCase()
            .includes(searchValue);


        const matchesRoute =
          route === "All" ||
          route === routeCode;


        const matchesSource =
          sourceType === "All" ||
          String(
            fare.sourceType || ""
          ).toLowerCase() ===
            String(
              sourceType
            ).toLowerCase();


        const matchesWindow =
          windowFilter === "All" ||
          fare.window ===
            windowFilter;


        return (
          matchesSearch &&
          matchesRoute &&
          matchesSource &&
          matchesWindow
        );

      }
    );


  /* =====================================================
     AVERAGE FARE
  ===================================================== */

  const averageFare =
    filteredFares.length > 0
      ? Math.round(
          filteredFares.reduce(
            (
              sum,
              fare
            ) =>
              sum +
              fare.totalFare,
            0
          ) /
            filteredFares.length
        )
      : 0;


  /* =====================================================
     CSV EXPORT
  ===================================================== */

  function exportCSV() {

    const headers = [
      "Observation ID",
      "Collected At",
      "Origin",
      "Destination",
      "Carrier",
      "Source",
      "Source Type",
      "Window",
      "Fare Class",
      "Base Fare",
      "Taxes",
      "UDF",
      "Convenience Fee",
      "Total Fare",
      "Quality",
    ];


    const rows =
      filteredFares.map(
        (fare) => [
          fare.id,
          fare.collectedAt,
          fare.origin,
          fare.destination,
          fare.carrier,
          fare.source,
          fare.sourceType,
          fare.window,
          fare.fareClass,
          fare.baseFare,
          fare.taxes,
          fare.udf,
          fare.convenienceFee,
          fare.totalFare,
          fare.quality,
        ]
      );


    const csv =
      [
        headers,
        ...rows,
      ]
        .map((row) =>
          row
            .map(
              (value) =>
                `"${String(
                  value
                ).replaceAll(
                  '"',
                  '""'
                )}"`
            )
            .join(",")
        )
        .join("\n");


    const blob =
      new Blob(
        [csv],
        {
          type:
            "text/csv;charset=utf-8;",
        }
      );


    const url =
      URL.createObjectURL(
        blob
      );


    const link =
      document.createElement(
        "a"
      );

    link.href = url;

    link.download =
      "airfare-observations.csv";


    document.body.appendChild(
      link
    );

    link.click();

    document.body.removeChild(
      link
    );


    URL.revokeObjectURL(
      url
    );

  }


  /* =====================================================
     LOADING STATE
  ===================================================== */

  if (loading) {

    return (
      <div className="fare-state-screen">

        <div className="fare-loader"></div>

        <strong>
          Loading fare observations
        </strong>

        <span>
          Preparing the cleaned airfare dataset...
        </span>

      </div>
    );

  }


  /* =====================================================
     ERROR STATE
  ===================================================== */

  if (error) {

    return (
      <div className="fare-state-screen fare-error-state">

        <Activity size={28} />

        <strong>
          Unable to load Fare Explorer
        </strong>

        <span>
          {error}
        </span>

        <button
          type="button"
          onClick={loadFares}
        >
          Try Again
        </button>

      </div>
    );

  }


  return (
    <div className="fare-explorer-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="fare-page-heading">

        <div>

          <span>
            OBSERVATION DATABASE
          </span>

          <h1>
            Fare Explorer
          </h1>

          <p>
            Inspect cleaned and normalised airfare
            observations used for index construction.
          </p>

        </div>


        <button
          type="button"
          className="fare-export-button"
          onClick={exportCSV}
        >

          <Download size={16} />

          Export CSV

        </button>

      </div>


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <section className="fare-summary-strip">

        <div>

          <Database size={18} />

          <div>

            <span>
              VISIBLE OBSERVATIONS
            </span>

            <strong>
              {filteredFares.length}
            </strong>

          </div>

        </div>


        <div>

          <IndianRupee size={18} />

          <div>

            <span>
              AVERAGE TOTAL FARE
            </span>

            <strong>
              ₹
              {averageFare.toLocaleString(
                "en-IN"
              )}
            </strong>

          </div>

        </div>


        <div>

          <SlidersHorizontal
            size={18}
          />

          <div>

            <span>
              COLLECTION STATUS
            </span>

            <strong>
              Normalised
            </strong>

          </div>

        </div>

      </section>


      {/* =====================================================
          FILTERS
      ===================================================== */}

      <section className="fare-filter-panel">

        <div className="fare-search">

          <Search size={16} />

          <input
            type="text"
            placeholder="Search carrier, source or observation ID..."
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
          />

        </div>


        <div className="fare-filter">

          <Filter size={14} />

          <select
            value={route}
            onChange={(event) =>
              setRoute(
                event.target.value
              )
            }
          >

            <option value="All">
              All routes
            </option>

            <option value="DEL-BOM">
              DEL → BOM
            </option>

            <option value="DEL-BLR">
              DEL → BLR
            </option>

            <option value="BOM-BLR">
              BOM → BLR
            </option>

            <option value="DEL-CCU">
              DEL → CCU
            </option>

            <option value="BLR-HYD">
              BLR → HYD
            </option>

            <option value="MAA-DEL">
              MAA → DEL
            </option>

          </select>

        </div>


        <div className="fare-filter">

          <select
            value={windowFilter}
            onChange={(event) =>
              setWindowFilter(
                event.target.value
              )
            }
          >

            <option value="All">
              All purchase windows
            </option>

            <option value="T+1">
              T+1
            </option>

            <option value="T+7">
              T+7
            </option>

            <option value="T+15">
              T+15
            </option>

            <option value="T+30">
              T+30
            </option>

            <option value="T+45">
              T+45
            </option>

          </select>

        </div>


        <div className="fare-filter">

          <select
            value={sourceType}
            onChange={(event) =>
              setSourceType(
                event.target.value
              )
            }
          >

            <option value="All">
              All sources
            </option>

            <option value="airline">
              Airlines
            </option>

            <option value="ota">
              OTAs
            </option>

            <option value="synthetic">
              Synthetic Demo
            </option>

          </select>

        </div>

      </section>


      {/* =====================================================
          TABLE
      ===================================================== */}

      <section className="fare-table-panel">

        <div className="fare-table-heading">

          <div>

            <span>
              CLEANED DATASET
            </span>

            <h2>
              Fare observations
            </h2>

          </div>


          <span>
            {filteredFares.length}
            {" "}records shown
          </span>

        </div>


        <div className="fare-table-scroll">

          <div className="fare-table-header">

            <span>
              Collected
            </span>

            <span>
              Route
            </span>

            <span>
              Carrier
            </span>

            <span>
              Source
            </span>

            <span>
              Window
            </span>

            <span>
              Base Fare
            </span>

            <span>
              Total Fare
            </span>

            <span>
              Quality
            </span>

          </div>


          {filteredFares.map(
            (fare) => (

              <button
                type="button"
                className="fare-table-row"
                key={fare.id}
                onClick={() =>
                  setSelectedFare(
                    fare
                  )
                }
              >

                <div>

                  <strong>
                    {fare.collectedAt
                      .split(",")[0]}
                  </strong>

                  <span>
                    {fare.collectedAt
                      .split(",")[1]}
                  </span>

                </div>


                <div className="fare-route-cell">

                  <strong>
                    {fare.origin}
                  </strong>

                  <span>
                    →
                  </span>

                  <strong>
                    {fare.destination}
                  </strong>

                </div>


                <div>

                  <strong>
                    {fare.carrier}
                  </strong>

                  <span>
                    {fare.fareClass}
                  </span>

                </div>


                <div>

                  <strong>
                    {fare.source}
                  </strong>

                  <span
                    className={
                      String(
                        fare.sourceType || ""
                      ).toLowerCase() === "ota"
                        ? "fare-source ota"
                        : "fare-source"
                    }
                  >
                    {fare.sourceType}
                  </span>

                </div>


                <div>

                  <span className="fare-window">
                    {fare.window}
                  </span>

                </div>


                <strong>
                  ₹
                  {Number(
                    fare.baseFare
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>


                <strong className="fare-total-value">
                  ₹
                  {Number(
                    fare.totalFare
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>


                <span
                  className={
                    fare.quality ===
                    "Clean"
                      ? "quality-pill clean"
                      : "quality-pill review"
                  }
                >

                  <span></span>

                  {fare.quality}

                </span>

              </button>

            )
          )}


          {filteredFares.length ===
            0 && (

            <div className="fare-empty">

              No observations match the
              selected filters.

            </div>

          )}

        </div>

      </section>


      {/* =====================================================
          MOCK NOTICE
      ===================================================== */}

      <div className="mock-data-note">

        Prototype Fare Explorer · Records currently
        shown are mock frontend data.

      </div>


      {/* =====================================================
          DETAIL DRAWER
      ===================================================== */}

      {selectedFare && (
        <>

          <div
            className="fare-drawer-overlay"
            onClick={() =>
              setSelectedFare(null)
            }
          />


          <aside className="fare-detail-drawer">

            <div className="fare-drawer-header">

              <div>

                <span>
                  FARE OBSERVATION
                </span>

                <h2>
                  {selectedFare.id}
                </h2>

              </div>


              <button
                type="button"
                onClick={() =>
                  setSelectedFare(null)
                }
                aria-label="Close fare details"
              >

                <X size={19} />

              </button>

            </div>


            <div className="drawer-route">

              <div>

                <span>
                  FROM
                </span>

                <strong>
                  {selectedFare.origin}
                </strong>

              </div>


              <span>
                →
              </span>


              <div>

                <span>
                  TO
                </span>

                <strong>
                  {selectedFare.destination}
                </strong>

              </div>

            </div>


            <div className="drawer-section">

              <span className="drawer-label">
                COLLECTION DETAILS
              </span>


              <div className="drawer-detail-row">

                <span>
                  Collected
                </span>

                <strong>
                  {selectedFare.collectedAt}
                </strong>

              </div>


              <div className="drawer-detail-row">

                <span>
                  Carrier
                </span>

                <strong>
                  {selectedFare.carrier}
                </strong>

              </div>


              <div className="drawer-detail-row">

                <span>
                  Source
                </span>

                <strong>
                  {selectedFare.source}
                </strong>

              </div>


              <div className="drawer-detail-row">

                <span>
                  Purchase window
                </span>

                <strong>
                  {selectedFare.window}
                </strong>

              </div>


              <div className="drawer-detail-row">

                <span>
                  Fare class
                </span>

                <strong>
                  {selectedFare.fareClass}
                </strong>

              </div>

            </div>


            <div className="drawer-section">

              <span className="drawer-label">
                FARE COMPOSITION
              </span>


              <div className="drawer-fare-row">

                <span>
                  Base fare
                </span>

                <strong>
                  ₹
                  {Number(
                    selectedFare.baseFare
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>


              <div className="drawer-fare-row">

                <span>
                  Taxes
                </span>

                <strong>
                  ₹
                  {Number(
                    selectedFare.taxes
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>


              <div className="drawer-fare-row">

                <span>
                  User Development Fee
                </span>

                <strong>
                  ₹
                  {Number(
                    selectedFare.udf
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>


              <div className="drawer-fare-row">

                <span>
                  Convenience charge
                </span>

                <strong>
                  ₹
                  {Number(
                    selectedFare
                      .convenienceFee
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>


              <div className="drawer-total">

                <span>
                  Total Fare
                </span>

                <strong>
                  ₹
                  {Number(
                    selectedFare.totalFare
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>

            </div>


            <div className="drawer-section">

              <span className="drawer-label">
                DATA QUALITY
              </span>


              <div className="drawer-quality-box">

                <div>

                  <span></span>

                  {selectedFare.quality}

                </div>

                <p>
                  Observation passed normalisation
                  and validation checks.
                </p>

              </div>

            </div>


            {selectedFare.sourceUrl && (

              <a
                href={
                  selectedFare.sourceUrl
                }
                target="_blank"
                rel="noreferrer"
                className="source-link-button"
              >

                View source portal

                <ExternalLink
                  size={14}
                />

              </a>

            )}

          </aside>

        </>
      )}

    </div>
  );
}


export default FareExplorer;