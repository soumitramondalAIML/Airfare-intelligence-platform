import { useState } from "react";

import {
  Braces,
  Check,
  ChevronDown,
  ChevronUp,
  Clipboard,
  Code2,
  Copy,
  Database,
  FileJson,
  HeartPulse,
  KeyRound,
  LockKeyhole,
  Route,
  Server,
  ShieldCheck,
  TestTube2,
} from "lucide-react";

import "./styles/ApiDocs.css";


const BASE_PATH = "/api/v1";


const endpoints = [
  {
    method: "GET",

    path: "/index/current",

    title: "Current Airfare Price Index",

    description:
      "Returns the latest available national APIx value, average fare and movement indicators.",

    parameters: [],

    response: `{
  "date": "2026-09-03",
  "index": 104.8,
  "daily_change_pct": 0.6,
  "weekly_change_pct": 1.9,
  "monthly_change_pct": 3.4,
  "average_fare": 6420,
  "updated_at": "2026-09-03T12:30:00Z"
}`,
  },


  {
    method: "GET",

    path: "/index/history",

    title: "APIx Historical Series",

    description:
      "Returns historical daily, weekly or monthly Airfare Price Index observations.",

    parameters: [
      {
        name: "frequency",
        type: "string",
        required: false,
        description:
          "daily, weekly or monthly",
      },

      {
        name: "from",
        type: "date",
        required: false,
        description:
          "Beginning of requested period",
      },

      {
        name: "to",
        type: "date",
        required: false,
        description:
          "End of requested period",
      },
    ],

    response: `{
  "frequency": "daily",
  "observations": [
    {
      "date": "2026-09-02",
      "index": 104.2
    },
    {
      "date": "2026-09-03",
      "index": 104.8
    }
  ]
}`,
  },


  {
    method: "GET",

    path: "/routes",

    title: "Representative Route Basket",

    description:
      "Returns monitored domestic city-pairs together with route-level metadata.",

    parameters: [],

    response: `{
  "routes": [
    {
      "origin": "DEL",
      "destination": "BOM",
      "route": "DEL-BOM"
    },
    {
      "origin": "DEL",
      "destination": "BLR",
      "route": "DEL-BLR"
    }
  ]
}`,
  },


  {
    method: "GET",

    path: "/routes/{origin}/{destination}",

    title: "Route Analytics",

    description:
      "Returns route-level fare statistics, price-index movement, fare history, booking-window information and source observations.",

    parameters: [
      {
        name: "origin",
        type: "string",
        required: true,
        description:
          "Three-letter origin airport code",
      },

      {
        name: "destination",
        type: "string",
        required: true,
        description:
          "Three-letter destination airport code",
      },

      {
        name: "window",
        type: "string",
        required: false,
        description:
          "T+1, T+7, T+15, T+30 or T+45",
      },
    ],

    response: `{
  "route": "DEL-BOM",
  "purchase_window": "T+7",
  "average_fare": 6480,
  "route_index": 106.1,
  "daily_change_pct": 0.8,
  "monthly_change_pct": 3.2,
  "history": [
    {
      "date": "2026-09-03",
      "fare": 6480
    }
  ],
  "lead_times": [
    {
      "window": "T+7",
      "fare": 6480
    }
  ]
}`,
  },


  {
    method: "GET",

    path: "/fares",

    title: "Cleaned Fare Observations",

    description:
      "Returns cleaned and normalised fare records with route, carrier, source and fare-component metadata.",

    parameters: [
      {
        name: "route",
        type: "string",
        required: false,
        description:
          "Example: DEL-BOM",
      },

      {
        name: "carrier",
        type: "string",
        required: false,
        description:
          "Filter observations by carrier",
      },

      {
        name: "window",
        type: "string",
        required: false,
        description:
          "Advance-purchase window",
      },

      {
        name: "source_type",
        type: "string",
        required: false,
        description:
          "Airline or OTA",
      },
    ],

    response: `{
  "observations": [
    {
      "id": "OBS-001",
      "origin": "DEL",
      "destination": "BOM",
      "carrier": "IndiGo",
      "source": "IndiGo",
      "source_type": "Airline",
      "window": "T+7",
      "fare_class": "Economy",
      "base_fare": 5100,
      "taxes": 720,
      "udf": 180,
      "convenience_fee": 350,
      "total_fare": 6350,
      "quality": "Clean"
    }
  ]
}`,
  },


  {
    method: "GET",

    path: "/quality/status",

    title: "Data Quality Status",

    description:
      "Returns collection coverage, source health and the latest data-quality indicators.",

    parameters: [],

    response: `{
  "coverage_pct": 96.4,
  "active_sources": 9,
  "observations_today": 2014,
  "flagged_records": 17,
  "sources": [
    {
      "source": "IndiGo",
      "status": "Healthy",
      "coverage": 98
    }
  ]
}`,
  },


  {
    method: "GET",

    path: "/backtest",

    title: "DGCA Back-test Results",

    description:
      "Returns prototype validation results comparing APIx-derived airfare measures with the configured DGCA reference dataset.",

    parameters: [],

    response: `{
  "summary": {
    "start_date": "2026-08-05",
    "end_date": "2026-09-03",
    "number_of_days": 30,
    "correlation": 0.94,
    "mape": 4.8,
    "route_coverage": 100,
    "observations": 1842
  },
  "comparison_trend": [],
  "error_trend": [],
  "route_comparison": []
}`,
  },


  {
    method: "GET",

    path: "/health",

    title: "API Health Check",

    description:
      "Returns the availability status of the backend API service.",

    parameters: [],

    response: `{
  "status": "ok",
  "service": "airfare-price-index-api"
}`,
  },
];


function ApiDocs() {

  const [
    openEndpoint,
    setOpenEndpoint,
  ] = useState(null);

  const [
    copied,
    setCopied,
  ] = useState(false);


  /* =====================================================
     ENDPOINT TOGGLE
  ===================================================== */

  const toggleEndpoint = (
    index
  ) => {

    setOpenEndpoint(
      (current) =>
        current === index
          ? null
          : index
    );

  };


  /* =====================================================
     COPY BASE PATH
  ===================================================== */

  const copyBasePath = async () => {

    try {

      await navigator.clipboard.writeText(
        BASE_PATH
      );

      setCopied(true);


      setTimeout(() => {

        setCopied(false);

      }, 1500);

    } catch {

      setCopied(false);

    }

  };


  return (
    <div className="api-docs-page">

      {/* =====================================================
          PAGE HEADING
      ===================================================== */}

      <header className="api-page-heading">

        <div>

          <span>
            DEVELOPER INTERFACE
          </span>

          <h1>
            Data API
          </h1>

          <p>
            Programmatic access to APIx, route analytics,
            cleaned fare observations, validation results
            and data-quality information.
          </p>

        </div>


        <div className="api-spec-badge">
          API specification · Prototype
        </div>

      </header>


      {/* =====================================================
          API HERO
      ===================================================== */}

      <section className="api-hero">

        <div className="api-hero-copy">

          <Code2 size={27} />

          <span>
            APIx DATA SERVICE
          </span>

          <h2>
            Airfare intelligence, available programmatically.
          </h2>

          <p>
            The REST interface is designed to expose index
            values, route-level statistics, fare observations,
            validation outputs and quality metadata to
            authorised institutional consumers.
          </p>

        </div>


        <div className="api-base-url-card">

          <span>
            PROTOTYPE BASE PATH
          </span>


          <div className="api-base-url">

            <code>
              {BASE_PATH}
            </code>


            <button
              type="button"
              onClick={copyBasePath}
              title="Copy API base path"
            >

              {copied ? (
                <Check size={15} />
              ) : (
                <Copy size={15} />
              )}

            </button>

          </div>


          <p>
            The deployment host will be configured when the
            backend service is deployed.
          </p>

        </div>

      </section>


      {/* =====================================================
          API CHARACTERISTICS
      ===================================================== */}

      <section className="api-feature-grid">

        <article>

          <div className="api-feature-icon">
            <Server size={19} />
          </div>

          <div>

            <span>
              INTERFACE
            </span>

            <strong>
              REST / JSON
            </strong>

            <p>
              Standard HTTP-based data access
            </p>

          </div>

        </article>


        <article>

          <div className="api-feature-icon">
            <Database size={19} />
          </div>

          <div>

            <span>
              DATASETS
            </span>

            <strong>
              Index + Fares
            </strong>

            <p>
              National and route-level access
            </p>

          </div>

        </article>


        <article>

          <div className="api-feature-icon">
            <KeyRound size={19} />
          </div>

          <div>

            <span>
              ACCESS
            </span>

            <strong>
              API Key
            </strong>

            <p>
              Authentication planned for production
            </p>

          </div>

        </article>


        <article>

          <div className="api-feature-icon">
            <ShieldCheck size={19} />
          </div>

          <div>

            <span>
              FORMAT
            </span>

            <strong>
              Traceable
            </strong>

            <p>
              Source metadata preserved
            </p>

          </div>

        </article>

      </section>


      {/* =====================================================
          QUICK START
      ===================================================== */}

      <section className="api-panel api-quick-start">

        <div className="api-section-heading">

          <div>

            <span>
              QUICK START
            </span>

            <h2>
              Retrieve the latest APIx
            </h2>

          </div>


          <p>
            Example request for the most recent national
            airfare index.
          </p>

        </div>


        <div className="quick-start-grid">

          <div className="quick-start-label">

            <Braces size={19} />

            <div>

              <span>
                REQUEST
              </span>

              <strong>
                HTTP
              </strong>

            </div>

          </div>


          <pre className="api-code-block">
            <code>
{`GET ${BASE_PATH}/index/current HTTP/1.1
Accept: application/json
X-API-Key: YOUR_API_KEY`}
            </code>
          </pre>

        </div>

      </section>


      {/* =====================================================
          ENDPOINT REFERENCE
      ===================================================== */}

      <section className="api-panel">

        <div className="api-section-heading">

          <div>

            <span>
              ENDPOINT REFERENCE
            </span>

            <h2>
              Available resources
            </h2>

          </div>


          <p>
            Expand an endpoint to inspect parameters and
            example responses.
          </p>

        </div>


        <div className="api-endpoint-list">

          {endpoints.map(
            (endpoint, index) => {

              const isOpen =
                openEndpoint === index;


              return (
                <article
                  className={`api-endpoint-card ${
                    isOpen
                      ? "open"
                      : ""
                  }`}
                  key={endpoint.path}
                >

                  <button
                    type="button"
                    className="api-endpoint-header"
                    onClick={() =>
                      toggleEndpoint(
                        index
                      )
                    }
                  >

                    <span className="api-method get">
                      {endpoint.method}
                    </span>


                    <div className="api-endpoint-main">

                      <code>
                        {BASE_PATH}
                        {endpoint.path}
                      </code>

                      <strong>
                        {endpoint.title}
                      </strong>

                      <p>
                        {endpoint.description}
                      </p>

                    </div>


                    <span className="api-endpoint-chevron">

                      {isOpen ? (
                        <ChevronUp
                          size={17}
                        />
                      ) : (
                        <ChevronDown
                          size={17}
                        />
                      )}

                    </span>

                  </button>


                  {isOpen && (

                    <div className="api-endpoint-details">

                      {endpoint.parameters
                        .length > 0 && (

                        <div className="api-parameters">

                          <span>
                            PARAMETERS
                          </span>


                          <div className="api-parameter-table">

                            <div className="api-parameter-header">

                              <span>
                                Name
                              </span>

                              <span>
                                Type
                              </span>

                              <span>
                                Requirement
                              </span>

                              <span>
                                Description
                              </span>

                            </div>


                            {endpoint.parameters.map(
                              (parameter) => (

                                <div
                                  className="api-parameter-row"
                                  key={
                                    parameter.name
                                  }
                                >

                                  <code>
                                    {parameter.name}
                                  </code>

                                  <span>
                                    {parameter.type}
                                  </span>

                                  <span
                                    className={
                                      parameter.required
                                        ? "api-required"
                                        : "api-optional"
                                    }
                                  >

                                    {parameter.required
                                      ? "Required"
                                      : "Optional"}

                                  </span>

                                  <span>
                                    {parameter.description}
                                  </span>

                                </div>

                              )
                            )}

                          </div>

                        </div>

                      )}


                      <div className="api-example-block">

                        <span>
                          EXAMPLE RESPONSE
                        </span>

                        <pre className="api-code-block">

                          <code>
                            {endpoint.response}
                          </code>

                        </pre>

                      </div>

                    </div>

                  )}

                </article>
              );

            }
          )}

        </div>

      </section>


      {/* =====================================================
          AUTHENTICATION + RESPONSE FORMAT
      ===================================================== */}

      <div className="api-bottom-grid">

        <section className="api-panel">

          <div className="api-mini-heading">

            <span>
              AUTHENTICATION
            </span>

            <KeyRound size={20} />

          </div>


          <h2>
            Production authentication
          </h2>

          <p>
            Institutional access can be secured using API keys
            transmitted through request headers.
          </p>


          <div className="api-inline-code">

            <code>
              X-API-Key: YOUR_API_KEY
            </code>

          </div>

        </section>


        <section className="api-panel">

          <div className="api-mini-heading">

            <span>
              RESPONSE FORMAT
            </span>

            <FileJson size={20} />

          </div>


          <h2>
            Consistent JSON responses
          </h2>


          <div className="api-response-list">

            <span>
              <Check size={15} />
              Timestamped observations
            </span>

            <span>
              <Check size={15} />
              Route and carrier metadata
            </span>

            <span>
              <Check size={15} />
              Fare-component traceability
            </span>

            <span>
              <Check size={15} />
              Quality-status metadata
            </span>

          </div>

        </section>

      </div>


      {/* =====================================================
          INTERNAL SERVICE ENDPOINTS
      ===================================================== */}

      <section className="api-panel">

        <div className="api-section-heading">

          <div>

            <span>
              SERVICE SUPPORT
            </span>

            <h2>
              Validation and health resources
            </h2>

          </div>


          <p>
            The frontend contract also includes back-test
            and service-health endpoints.
          </p>

        </div>


        <div className="api-response-list">

          <span>
            <TestTube2 size={15} />
            /backtest · validation results
          </span>

          <span>
            <HeartPulse size={15} />
            /health · backend availability
          </span>

        </div>

      </section>


      {/* =====================================================
          ACCESS MODEL
      ===================================================== */}

      <section className="institutional-access-panel">

        <div>

          <span>
            ACCESS MODEL
          </span>

          <h2>
            Institutional data access without administrative
            privileges.
          </h2>

          <p>
            The public-facing data interface should expose
            approved read-only datasets. Data modification,
            scraper controls and administrative operations
            remain private backend capabilities.
          </p>

        </div>


        <div className="api-access-rules">

          <div>

            <LockKeyhole size={16} />

            Read-only institutional endpoints

          </div>


          <div>

            <KeyRound size={16} />

            API-key authentication

          </div>


          <div>

            <Route size={16} />

            Route and index data access

          </div>


          <div>

            <ShieldCheck size={16} />

            No administrative operations exposed

          </div>

        </div>

      </section>


      {/* =====================================================
          PROTOTYPE NOTE
      ===================================================== */}

      <div className="api-contract-note">

        <Clipboard size={16} />

        <p>

          <strong>
            Frontend API contract.
          </strong>{" "}

          The endpoints shown here define the intended
          interface between the React frontend and the
          backend service. They do not indicate that a
          production API is currently deployed.

        </p>

      </div>

    </div>
  );
}


export default ApiDocs;