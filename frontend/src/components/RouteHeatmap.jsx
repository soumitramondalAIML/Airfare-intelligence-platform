import {
  ArrowRight,
  Info,
} from "lucide-react";

import {
  useNavigate,
} from "react-router-dom";

import "./styles/RouteHeatmap.css";


const windows = [
  "T+45",
  "T+30",
  "T+15",
  "T+7",
  "T+1",
];


function getHeatClass(value) {

  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "heat-neutral";
  }

  const numericValue =
    Number(value);

  if (numericValue >= 10)
    return "heat-very-high";

  if (numericValue >= 5)
    return "heat-high";

  if (numericValue >= 1)
    return "heat-medium";

  if (numericValue > -1)
    return "heat-neutral";

  if (numericValue > -4)
    return "heat-low";

  return "heat-very-low";
}


function RouteHeatmap({
  data = [],
}) {

  const navigate =
    useNavigate();


  return (
    <section className="premium-panel heatmap-panel">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="premium-panel-header">

        <div>

          <span className="panel-eyebrow">
            SECTOR MOVEMENT
          </span>

          <h3>
            Route Fare Heatmap
          </h3>

          <p>
            Fare movement by route and
            advance-purchase window
          </p>

        </div>


        <button
          type="button"
          className="view-all-button"
          onClick={() =>
            navigate("/routes")
          }
        >

          All routes

          <ArrowRight size={14} />

        </button>

      </div>


      {/* =====================================================
          HEATMAP
      ===================================================== */}

      <div className="heatmap-table">

        <div className="heatmap-header-row">

          <div className="heatmap-route-header">
            ROUTE
          </div>


          {windows.map(
            (window) => (

              <div
                key={window}
                className="heatmap-window-header"
              >
                {window}
              </div>

            )
          )}

        </div>


        {(data || []).map(
          (item) => (

            <div
              className="heatmap-row"
              key={item.route}
            >

              <div className="heatmap-route">

                <strong>
                  {item.route}
                </strong>

                <span>
                  {item.cityPair}
                </span>

              </div>


              {windows.map(
                (window) => {

                  const rawValue =
                    item.windows?.[
                      window
                    ];

                  const hasValue =
                    rawValue !== null &&
                    rawValue !== undefined &&
                    !Number.isNaN(
                      Number(rawValue)
                    );

                  const value =
                    hasValue
                      ? Number(rawValue)
                      : null;


                  return (
                    <div
                      className={`heat-cell ${
                        getHeatClass(
                          value
                        )
                      }`}
                      key={window}
                      title={
                        hasValue
                          ? `${item.route} ${window}: ${
                              value > 0
                                ? "+"
                                : ""
                            }${value}%`
                          : `${item.route} ${window}: No data`
                      }
                    >

                      {hasValue ? (
                        <>
                          {value > 0
                            ? "+"
                            : ""}

                          {value.toFixed(
                            1
                          )}
                        </>
                      ) : (
                        "—"
                      )}

                    </div>
                  );

                }
              )}

            </div>

          )
        )}


        {(!data ||
          data.length === 0) && (

          <div className="heatmap-empty-state">

            Route movement data is not
            currently available.

          </div>

        )}

      </div>


      {/* =====================================================
          LEGEND
      ===================================================== */}

      <div className="heatmap-footer">

        <div className="heatmap-scale">

          <span>
            Lower fares
          </span>

          <div className="scale-box scale-lowest"></div>

          <div className="scale-box scale-low"></div>

          <div className="scale-box scale-neutral"></div>

          <div className="scale-box scale-high"></div>

          <div className="scale-box scale-highest"></div>

          <span>
            Higher fares
          </span>

        </div>


        <div className="heatmap-note">

          <Info size={12} />

          Change relative to route reference fare

        </div>

      </div>

    </section>
  );
}


export default RouteHeatmap;