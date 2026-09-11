import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useSearchParams,
} from "react-router-dom";

import {
  ArrowRight,
  CalendarDays,
  Database,
  IndianRupee,
  MapPin,
  PlaneTakeoff,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getFares,
  getRouteAnalytics,
} from "../services/api";

import "./styles/RouteAnalytics.css";


const purchaseWindows = [
  "T+1",
  "T+7",
  "T+15",
  "T+30",
  "T+45",
];


const routeOptions = [
  {
    code: "DEL-BOM",
    label: "Delhi → Mumbai",
  },
  {
    code: "DEL-BLR",
    label: "Delhi → Bengaluru",
  },
  {
    code: "BOM-BLR",
    label: "Mumbai → Bengaluru",
  },
  {
    code: "DEL-CCU",
    label: "Delhi → Kolkata",
  },
  {
    code: "BLR-HYD",
    label: "Bengaluru → Hyderabad",
  },
  {
    code: "MAA-DEL",
    label: "Chennai → Delhi",
  },
];


function average(values) {

  if (!values.length) {
    return 0;
  }

  return (
    values.reduce(
      (sum, value) =>
        sum + Number(value || 0),
      0
    ) / values.length
  );

}


function RouteAnalytics() {

  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams();


  const queryOrigin =
    searchParams.get("origin") || "DEL";

  const queryDestination =
    searchParams.get("destination") || "BOM";

  const queryWindow =
    searchParams.get("window") || "T+7";

  const queryPeriod =
    searchParams.get("period") || "30";


  const [
    selectedRoute,
    setSelectedRoute,
  ] = useState(
    `${queryOrigin}-${queryDestination}`
  );


  const [
    selectedWindow,
    setSelectedWindow,
  ] = useState(
    purchaseWindows.includes(queryWindow)
      ? queryWindow
      : "T+7"
  );


  const [
    selectedPeriod,
    setSelectedPeriod,
  ] = useState(queryPeriod);


  const [
    data,
    setData,
  ] = useState(null);


  const [
    fares,
    setFares,
  ] = useState([]);


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState(null);


  /* =========================================
     LOAD REAL BACKEND DATA
  ========================================= */

  useEffect(() => {

    let active = true;


    async function loadRoute() {

      try {

        setLoading(true);
        setError(null);


        const [
          origin,
          destination,
        ] = selectedRoute.split("-");


        const [
          routeData,
          fareData,
        ] = await Promise.all([

          getRouteAnalytics(
            origin,
            destination,
            selectedWindow
          ),

          getFares({
            route: selectedRoute,
          }),

        ]);


        if (active) {

          setData(routeData);
          setFares(fareData);

        }

      } catch (err) {

        console.error(
          "Unable to load route analytics:",
          err
        );


        if (active) {

          setError(
            "Route analytics could not be loaded."
          );

        }

      } finally {

        if (active) {

          setLoading(false);

        }

      }

    }


    loadRoute();


    return () => {

      active = false;

    };

  }, [
    selectedRoute,
    selectedWindow,
  ]);


  /* =========================================
     NORMALISE ROUTE INFORMATION
  ========================================= */

  const [
    originCode,
    destinationCode,
  ] = selectedRoute.split("-");


  const originInfo =
    typeof data?.origin === "object"
      ? data.origin
      : {
          code:
            data?.origin ||
            originCode,

          city:
            data?.origin ||
            originCode,

          airport: "",
        };


  const destinationInfo =
    typeof data?.destination === "object"
      ? data.destination
      : {
          code:
            data?.destination ||
            destinationCode,

          city:
            data?.destination ||
            destinationCode,

          airport: "",
        };


  /* =========================================
     LEAD-TIME DATA
  ========================================= */

  const leadTimes = useMemo(() => {

    return (
      data?.leadTimes || []
    ).map((item) => ({

      window:
        item.window ??
        (
          item.advance_days !== undefined
            ? `T+${item.advance_days}`
            : ""
        ),

      fare:
        Number(
          item.fare ??
          item.average_fare ??
          0
        ),

    }));

  }, [data]);


  /* =========================================
     SELECTED WINDOW OBSERVATIONS
  ========================================= */

  const selectedWindowFares =
    useMemo(() => {

      return fares.filter(
        (fare) =>
          fare.window === selectedWindow
      );

    }, [
      fares,
      selectedWindow,
    ]);


  /* =========================================
     FARE HISTORY
  ========================================= */

  const fareHistory =
    useMemo(() => {

      const groups = {};


      selectedWindowFares.forEach(
        (fare) => {

          const date =
            String(
              fare.collectedAt || ""
            ).split("T")[0];


          if (!date) {
            return;
          }


          if (!groups[date]) {
            groups[date] = [];
          }


          const totalFare =
            Number(
              fare.totalFare
            );


          if (
            Number.isFinite(totalFare) &&
            totalFare > 0
          ) {

            groups[date].push(
              totalFare
            );

          }

        }
      );


      const history =
        Object.entries(groups)
          .map(
            ([date, values]) => ({

              date,

              fare: Math.round(
                average(values)
              ),

            })
          )
          .sort(
            (a, b) =>
              a.date.localeCompare(
                b.date
              )
          );


      const period =
        Number(selectedPeriod);


      return history.slice(
        -period
      );

    }, [
      selectedWindowFares,
      selectedPeriod,
    ]);


  /* =========================================
     SELECTED FARE
  ========================================= */

  const selectedFare =
    useMemo(() => {

      const fromLeadTime =
        leadTimes.find(
          (item) =>
            item.window ===
            selectedWindow
        )?.fare;


      if (
        Number.isFinite(
          Number(fromLeadTime)
        ) &&
        Number(fromLeadTime) > 0
      ) {

        return Number(fromLeadTime);

      }


      const validTotals =
        selectedWindowFares
          .map(
            (fare) =>
              Number(fare.totalFare)
          )
          .filter(
            (value) =>
              Number.isFinite(value) &&
              value > 0
          );


      return average(validTotals);

    }, [
      leadTimes,
      selectedWindow,
      selectedWindowFares,
    ]);


  /* =========================================
     FARE COMPOSITION
  ========================================= */

  const fareBreakdown =
    useMemo(() => {

      if (
        selectedWindowFares.length === 0
      ) {

        return {

          baseFare: null,
          taxes: null,
          udf: null,
          convenienceFee: null,

        };

      }


      const latestDate =
        [...selectedWindowFares]
          .map(
            (fare) =>
              String(
                fare.collectedAt || ""
              ).split("T")[0]
          )
          .sort()
          .at(-1);


      const latestFares =
        selectedWindowFares.filter(
          (fare) =>
            String(
              fare.collectedAt || ""
            ).split("T")[0] ===
            latestDate
        );


      const getAverageIfAvailable = (
        values
      ) => {

        const validValues =
          values
            .map(
              (value) =>
                Number(value)
            )
            .filter(
              (value) =>
                Number.isFinite(value) &&
                value > 0
            );


        if (
          validValues.length === 0
        ) {

          return null;

        }


        return average(validValues);

      };


      return {

        baseFare:
          getAverageIfAvailable(
            latestFares.map(
              (fare) =>
                fare.baseFare
            )
          ),

        taxes:
          getAverageIfAvailable(
            latestFares.map(
              (fare) =>
                fare.taxes
            )
          ),

        udf:
          getAverageIfAvailable(
            latestFares.map(
              (fare) =>
                fare.udf
            )
          ),

        convenienceFee:
          getAverageIfAvailable(
            latestFares.map(
              (fare) =>
                fare.convenienceFee
            )
          ),

      };

    }, [
      selectedWindowFares,
    ]);


  /* =========================================
     TOTAL OBSERVED FARE
  ========================================= */

  const totalFare =
    useMemo(() => {

      if (
        selectedWindowFares.length === 0
      ) {

        return 0;

      }


      const latestDate =
        [...selectedWindowFares]
          .map(
            (fare) =>
              String(
                fare.collectedAt || ""
              ).split("T")[0]
          )
          .sort()
          .at(-1);


      const latestFares =
        selectedWindowFares.filter(
          (fare) =>
            String(
              fare.collectedAt || ""
            ).split("T")[0] ===
            latestDate
        );


      const validTotals =
        latestFares
          .map(
            (fare) =>
              Number(fare.totalFare)
          )
          .filter(
            (value) =>
              Number.isFinite(value) &&
              value > 0
          );


      if (
        validTotals.length === 0
      ) {

        return 0;

      }


      return average(validTotals);

    }, [
      selectedWindowFares,
    ]);


  /* =========================================
     ROUTE INDEX
  ========================================= */

  const indexHistory =
    data?.history || [];


  const currentIndex =
    Number(
      data?.currentIndex ??
      indexHistory.at(-1)?.index ??
      0
    );


  const monthlyChange =
    useMemo(() => {

      if (
        indexHistory.length < 2
      ) {

        return 0;

      }


      const last =
        Number(
          indexHistory.at(-1)?.index ||
          0
        );


      const reference =
        Number(
          indexHistory[
            Math.max(
              0,
              indexHistory.length - 30
            )
          ]?.index || 0
        );


      if (!reference) {

        return 0;

      }


      return Number(
        (
          (
            (
              last -
              reference
            ) /
            reference
          ) *
          100
        ).toFixed(2)
      );

    }, [
      indexHistory,
    ]);


  /* =========================================
     SOURCE / CARRIER COMPARISON
  ========================================= */

  const carrierComparison =
    useMemo(() => {

      if (
        selectedWindowFares.length === 0
      ) {

        return [];

      }


      /* -----------------------------------------
         Find latest collection date
      ----------------------------------------- */

      const latestDate =
        [...selectedWindowFares]
          .map(
            (fare) =>
              String(
                fare.collectedAt || ""
              ).split("T")[0]
          )
          .sort()
          .at(-1);


      /* -----------------------------------------
         Keep latest observations
      ----------------------------------------- */

      const latestFares =
        selectedWindowFares.filter(
          (fare) =>
            String(
              fare.collectedAt || ""
            ).split("T")[0] ===
            latestDate
        );


      /* -----------------------------------------
         Calculate movement
      ----------------------------------------- */

      return latestFares.map(
        (fare) => {

          const currentFare =
            Number(
              fare.totalFare || 0
            );


          /*
            Find the most recent previous
            comparable observation.

            Comparison remains within:

            - same carrier
            - same source
            - same route
            - same T+ window
            - same fare series
          */

          const previousFares =
            selectedWindowFares
              .filter(
                (previous) => {

                  const previousDate =
                    String(
                      previous.collectedAt || ""
                    ).split("T")[0];


                  return (

                    previous !== fare &&

                    previousDate !==
                      latestDate &&

                    (
                      previous.carrier ||
                      ""
                    ) === (
                      fare.carrier ||
                      ""
                    ) &&

                    (
                      previous.source ||
                      ""
                    ) === (
                      fare.source ||
                      ""
                    ) &&

                    Number(
                      previous.totalFare || 0
                    ) > 0

                  );

                }
              )
              .sort(
                (a, b) =>
                  new Date(
                    b.collectedAt || 0
                  ) -
                  new Date(
                    a.collectedAt || 0
                  )
              );


          const previousFare =
            Number(
              previousFares[0]?.totalFare ||
              0
            );


          /*
            Movement formula:

            ((Current - Previous) / Previous)
            × 100
          */

          let change = null;


          if (
            currentFare > 0 &&
            previousFare > 0
          ) {

            change =
              (
                (
                  currentFare -
                  previousFare
                ) /
                previousFare
              ) *
              100;

          }


          return {

            carrier:
              fare.carrier ||
              "Unknown",

            source:
              fare.sourceType
                ?.toUpperCase() ===
              "OTA"
                ? "OTA"
                : (
                    fare.sourceType ||
                    "Source"
                  ),

            sourceName:
              fare.source ||
              "",

            fare:
              currentFare,

            change,

          };

        }
      );

    }, [
      selectedWindowFares,
    ]);


  /* =========================================
     URL STATE
  ========================================= */

  function updateUrl(
    route,
    window,
    period
  ) {

    const [
      origin,
      destination,
    ] = route.split("-");


    setSearchParams({

      origin,
      destination,
      window,
      period,

    });

  }


  function handleRouteChange(
    event
  ) {

    const value =
      event.target.value;


    setSelectedRoute(value);


    updateUrl(
      value,
      selectedWindow,
      selectedPeriod
    );

  }


  function handleWindowChange(
    window
  ) {

    setSelectedWindow(
      window
    );


    updateUrl(
      selectedRoute,
      window,
      selectedPeriod
    );

  }


  function handlePeriodChange(
    event
  ) {

    const value =
      event.target.value;


    setSelectedPeriod(
      value
    );


    updateUrl(
      selectedRoute,
      selectedWindow,
      value
    );

  }


  /* =========================================
     LOADING
  ========================================= */

  if (loading) {

    return (

      <div className="route-analytics-page">

        <div className="route-data-status">

          Loading route analytics...

        </div>

      </div>

    );

  }


  /* =========================================
     ERROR
  ========================================= */

  if (
    error ||
    !data
  ) {

    return (

      <div className="route-analytics-page">

        <div className="route-data-status">

          {
            error ||
            "No route data available."
          }

        </div>

      </div>

    );

  }


  /* =========================================
     PAGE
  ========================================= */

  return (

    <div className="route-analytics-page">


      {/* PAGE HEADER */}

      <div className="route-page-heading">

        <div>

          <span className="route-page-eyebrow">

            SECTOR ANALYSIS

          </span>


          <h1>

            Route Analytics

          </h1>


          <p>

            Examine route-level airfare behaviour
            across advance-purchase windows and
            collection sources.

          </p>

        </div>


        <div className="route-data-status">

          <span></span>

          Latest collection available

        </div>

      </div>


      {/* ROUTE SELECTOR */}

      <section className="route-selector-panel">

        <div className="selector-route">


          <div className="airport-block">

            <span>
              ORIGIN
            </span>


            <strong>
              {originInfo.code}
            </strong>


            <p>
              {originInfo.city}
            </p>


            <small>
              {originInfo.airport}
            </small>

          </div>


          <div className="route-airline-line">

            <div className="route-line"></div>


            <div className="route-plane">

              <PlaneTakeoff size={19} />

            </div>

          </div>


          <div className="airport-block destination-block">

            <span>
              DESTINATION
            </span>


            <strong>
              {destinationInfo.code}
            </strong>


            <p>
              {destinationInfo.city}
            </p>


            <small>
              {destinationInfo.airport}
            </small>

          </div>

        </div>


        <div className="route-selector-controls">


          <label>

            <span>
              ROUTE
            </span>


            <select
              value={selectedRoute}
              onChange={
                handleRouteChange
              }
            >

              {routeOptions.map(
                (route) => (

                  <option
                    key={route.code}
                    value={route.code}
                  >

                    {route.label}

                  </option>

                )
              )}

            </select>

          </label>


          <label>

            <span>
              REFERENCE PERIOD
            </span>


            <select
              value={selectedPeriod}
              onChange={
                handlePeriodChange
              }
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

          </label>


          <div className="route-observation-count">

            <Database size={16} />


            <div>

              <span>
                OBSERVATIONS
              </span>


              <strong>
                {fares.length}
              </strong>

            </div>

          </div>

        </div>

      </section>


      {/* PURCHASE WINDOW */}

      <section className="purchase-window-bar">

        <div>

          <span className="purchase-label">

            ADVANCE-PURCHASE WINDOW

          </span>


          <p>

            Choose how many days before departure
            the airfare was observed.

          </p>

        </div>


        <div className="window-options">

          {purchaseWindows.map(
            (window) => (

              <button
                type="button"
                key={window}
                className={
                  selectedWindow === window
                    ? "window-option active"
                    : "window-option"
                }
                onClick={() =>
                  handleWindowChange(
                    window
                  )
                }
              >

                <strong>
                  {window}
                </strong>


                <span>

                  {
                    window === "T+1"
                      ? "1 day"
                      : `${window.replace(
                          "T+",
                          ""
                        )} days`
                  }

                </span>

              </button>

            )
          )}

        </div>

      </section>


      {/* SUMMARY */}

      <div className="route-summary-grid">


        <article>

          <span>
            Observed Fare
          </span>


          <strong>

            ₹
            {Math.round(
              selectedFare
            ).toLocaleString(
              "en-IN"
            )}

          </strong>


          <small>
            Selected {selectedWindow} window
          </small>

        </article>


        <article>

          <span>
            Route APIx
          </span>


          <strong>
            {currentIndex.toFixed(2)}
          </strong>


          <small>
            Route price index
          </small>

        </article>


        <article>

          <span>
            Daily Movement
          </span>


          <strong
            className={
              Number(data.change) >= 0
                ? "route-positive"
                : "route-negative"
            }
          >

            {
              Number(data.change) >= 0
                ? (
                  <TrendingUp size={18} />
                )
                : (
                  <TrendingDown size={18} />
                )
            }


            {
              Number(data.change) >= 0
                ? "+"
                : ""
            }


            {Number(
              data.change || 0
            ).toFixed(2)}

            %

          </strong>


          <small>
            vs previous collection
          </small>

        </article>


        <article>

          <span>
            30-Day Movement
          </span>


          <strong
            className={
              monthlyChange >= 0
                ? "route-positive"
                : "route-negative"
            }
          >

            {
              monthlyChange >= 0
                ? "+"
                : ""
            }

            {monthlyChange}%

          </strong>


          <small>
            monthly movement
          </small>

        </article>

      </div>


      {/* MAIN CHART */}

      <section className="route-chart-panel">

        <div className="route-section-heading">

          <div>

            <span>
              PRICE HISTORY
            </span>


            <h2>

              Fare movement ·{" "}
              {originInfo.code} →{" "}
              {destinationInfo.code}

            </h2>


            <p>

              Historical average fare for the
              selected booking window.

            </p>

          </div>


          <div className="chart-route-label">

            <MapPin size={14} />


            {originInfo.city}


            <ArrowRight size={13} />


            {destinationInfo.city}

          </div>

        </div>


        <div className="route-history-chart">

          <ResponsiveContainer
            width="100%"
            height="100%"
          >

            <AreaChart
              data={fareHistory}
            >

              <defs>

                <linearGradient
                  id="routeFareGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >

                  <stop
                    offset="0%"
                    stopColor="#C86A32"
                    stopOpacity={0.22}
                  />


                  <stop
                    offset="100%"
                    stopColor="#C86A32"
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
                  fontSize: 10,
                  fill: "#878178",
                }}
              />


              <YAxis
                axisLine={false}
                tickLine={false}
                width={50}
                tick={{
                  fontSize: 10,
                  fill: "#878178",
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
              />


              <Area
                type="monotone"
                dataKey="fare"
                stroke="#C86A32"
                strokeWidth={2.5}
                fill="url(#routeFareGradient)"
              />

            </AreaChart>

          </ResponsiveContainer>

        </div>

      </section>


      {/* LOWER ANALYSIS */}

      <div className="route-analysis-grid">


        {/* LEAD TIME */}

        <section className="route-subpanel">

          <div className="route-section-heading">

            <div>

              <span>
                LEAD-TIME ELASTICITY
              </span>


              <h2>
                Fare by booking window
              </h2>


              <p>
                Average fare as departure approaches.
              </p>

            </div>


            <CalendarDays size={19} />

          </div>


          <div className="route-bar-chart">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <BarChart
                data={[
                  ...leadTimes,
                ].reverse()}
              >

                <CartesianGrid
                  vertical={false}
                  stroke="#eee8df"
                  strokeDasharray="3 3"
                />


                <XAxis
                  dataKey="window"
                  axisLine={false}
                  tickLine={false}
                />


                <YAxis
                  axisLine={false}
                  tickLine={false}
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

                    "Fare",

                  ]}
                />


                <Bar
                  dataKey="fare"
                  fill="#566B57"
                  radius={[
                    5,
                    5,
                    0,
                    0,
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

        </section>


        {/* FARE COMPOSITION */}

        <section className="route-subpanel">


          <div className="route-section-heading">

            <div>

              <span>
                FARE STRUCTURE
              </span>


              <h2>
                Fare composition
              </h2>


              <p>
                Components contributing to the
                observed total.
              </p>

            </div>


            <IndianRupee size={19} />

          </div>


          <div className="fare-total">

            <span>
              TOTAL FARE
            </span>


            <strong>

              ₹
              {Math.round(
                totalFare
              ).toLocaleString(
                "en-IN"
              )}

            </strong>

          </div>


          <div className="fare-component-list">


            <div>

              <span>
                Base fare
              </span>


              <strong>

                {
                  fareBreakdown.baseFare === null
                    ? "N/A"
                    : `₹${Math.round(
                        fareBreakdown.baseFare
                      ).toLocaleString(
                        "en-IN"
                      )}`
                }

              </strong>

            </div>


            <div>

              <span>
                Taxes
              </span>


              <strong>

                {
                  fareBreakdown.taxes === null
                    ? "N/A"
                    : `₹${Math.round(
                        fareBreakdown.taxes
                      ).toLocaleString(
                        "en-IN"
                      )}`
                }

              </strong>

            </div>


            <div>

              <span>
                User Development Fee
              </span>


              <strong>

                {
                  fareBreakdown.udf === null
                    ? "N/A"
                    : `₹${Math.round(
                        fareBreakdown.udf
                      ).toLocaleString(
                        "en-IN"
                      )}`
                }

              </strong>

            </div>


            <div>

              <span>
                Convenience charge
              </span>


              <strong>

                {
                  fareBreakdown.convenienceFee === null
                    ? "N/A"
                    : `₹${Math.round(
                        fareBreakdown.convenienceFee
                      ).toLocaleString(
                        "en-IN"
                      )}`
                }

              </strong>

            </div>


          </div>


        </section>

      </div>


      {/* SOURCE COMPARISON */}

      <section className="carrier-panel">


        <div className="route-section-heading">

          <div>

            <span>
              SOURCE COMPARISON
            </span>


            <h2>
              Carrier & portal comparison
            </h2>


            <p>
              Compare observed fares collected
              from airline and OTA sources.
            </p>

          </div>

        </div>


        <div className="carrier-table">


          <div className="carrier-table-header">

            <span>
              Carrier / Source
            </span>


            <span>
              Type
            </span>


            <span>
              Observed Fare
            </span>


            <span>
              Movement
            </span>

          </div>


          {carrierComparison.map(
            (carrier, index) => (

              <div
                className="carrier-row"
                key={
                  `${carrier.carrier}-${carrier.sourceName}-${index}`
                }
              >


                <div className="carrier-name">


                  <div>

                    {
                      carrier.carrier
                        .charAt(0)
                    }

                  </div>


                  <strong>

                    {carrier.carrier}

                  </strong>


                </div>


                <div>


                  <span
                    className={
                      carrier.source ===
                      "OTA"
                        ? "source-type ota"
                        : "source-type"
                    }
                  >

                    {carrier.source}

                  </span>


                </div>


                <strong>

                  ₹
                  {Math.round(
                    carrier.fare
                  ).toLocaleString(
                    "en-IN"
                  )}

                </strong>


                <strong
                  className={
                    carrier.change === null
                      ? "route-neutral"
                      : carrier.change > 0
                      ? "route-negative"
                      : carrier.change < 0
                      ? "route-positive"
                      : "route-neutral"
                  }
                >

                  {
                    carrier.change === null
                      ? "N/A"
                      : `${
                          carrier.change > 0
                            ? "+"
                            : ""
                        }${
                          carrier.change.toFixed(
                            2
                          )
                        }%`
                  }

                </strong>


              </div>

            )
          )}


        </div>

      </section>


      <div className="mock-data-note">

        Live backend integration · Historical demo
        observations are synthetic prototype data.

      </div>


    </div>

  );

}


export default RouteAnalytics;