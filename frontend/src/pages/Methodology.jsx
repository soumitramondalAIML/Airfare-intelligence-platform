import {
  ArrowDown,
  BarChart3,
  CalendarRange,
  CheckCircle2,
  Database,
  FileCheck2,
  Plane,
  Scale,
  ShieldCheck,
  TableProperties,
} from "lucide-react";

import "./styles/Methodology.css";


/* =====================================================
   METHODOLOGY PIPELINE
===================================================== */

const methodologySteps = [
  {
    number: "01",

    title: "Source Collection",

    description:
      "Scheduled daily fare collection from supported airline and OTA portals, with safeguards for JavaScript-rendered pages, sessions, rate limits and compliant scraping.",

    icon: <Plane size={19} />,
  },

  {
    number: "02",

    title: "Structured Storage",

    description:
      "Raw observations are stored with origin, destination, carrier, source, purchase window, fare class, fare components and collection metadata.",

    icon: <Database size={19} />,
  },

  {
    number: "03",

    title: "Cleaning & Validation",

    description:
      "Duplicates, missing values, outliers, cancellations and sold-out observations are identified and handled before aggregation.",

    icon: <ShieldCheck size={19} />,
  },

  {
    number: "04",

    title: "Fare Normalisation",

    description:
      "Fare components are standardised while keeping base fare, taxes, user-development fee and convenience charges separately traceable.",

    icon: <TableProperties size={19} />,
  },

  {
    number: "05",

    title: "Route Aggregation",

    description:
      "Validated observations are aggregated across representative city-pairs and multiple advance-purchase windows.",

    icon: <BarChart3 size={19} />,
  },

  {
    number: "06",

    title: "APIx Construction",

    description:
      "Route-level measures are combined according to the routes and weights specified by the Problem Statement Department.",

    icon: <Scale size={19} />,
  },
];


/* =====================================================
   REPRESENTATIVE ROUTES

   These are representative city-pairs explicitly
   mentioned in the SIH problem statement. The final
   production basket may include additional sectors.
===================================================== */

const routeBasket = [
  {
    route: "DEL → BOM",
    cities: "Delhi – Mumbai",
  },

  {
    route: "DEL → BLR",
    cities: "Delhi – Bengaluru",
  },

  {
    route: "BOM → BLR",
    cities: "Mumbai – Bengaluru",
  },

  {
    route: "DEL → CCU",
    cities: "Delhi – Kolkata",
  },

  {
    route: "BLR → HYD",
    cities: "Bengaluru – Hyderabad",
  },

  {
    route: "MAA → DEL",
    cities: "Chennai – Delhi",
  },
];


/* =====================================================
   ADVANCE-PURCHASE WINDOWS
===================================================== */

const purchaseWindows = [
  {
    name: "T+1",
    days: "1 day before departure",
  },

  {
    name: "T+7",
    days: "7 days before departure",
  },

  {
    name: "T+15",
    days: "15 days before departure",
  },

  {
    name: "T+30",
    days: "30 days before departure",
  },

  {
    name: "T+45",
    days: "45 days before departure",
  },
];


function Methodology() {

  return (
    <div className="methodology-page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="methodology-heading">

        <div>

          <span>
            METHODOLOGY & GOVERNANCE
          </span>

          <h1>
            How APIx is constructed
          </h1>

          <p>
            From high-frequency airfare collection to a
            consistent and traceable Airfare Price Index.
          </p>

        </div>


        <div className="methodology-version">

          <FileCheck2 size={15} />

          <div>

            <span>
              METHODOLOGY
            </span>

            <strong>
              Prototype v1.0
            </strong>

          </div>

        </div>

      </div>


      {/* =====================================================
          INTRODUCTION
      ===================================================== */}

      <section className="methodology-intro">

        <div>

          <span className="methodology-eyebrow">
            OBJECTIVE
          </span>

          <h2>
            Measuring the airfare consumers actually face
          </h2>

          <p>
            APIx is designed to convert high-frequency
            airfare observations collected from airline
            websites and Online Travel Aggregator portals
            into a structured price-monitoring series for
            domestic air travel.
          </p>

          <p>
            Route, carrier, advance-purchase window,
            fare-class, source and fare-component
            information are preserved through the
            processing pipeline so that aggregated results
            remain traceable to their underlying
            observations.
          </p>

        </div>


        <div className="methodology-principles">

          <div>

            <CheckCircle2 size={16} />

            <div>

              <strong>
                Representative
              </strong>

              <span>
                City-pairs are selected using DGCA
                passenger-traffic considerations.
              </span>

            </div>

          </div>


          <div>

            <CheckCircle2 size={16} />

            <div>

              <strong>
                High-frequency
              </strong>

              <span>
                Designed for scheduled daily airfare
                collection.
              </span>

            </div>

          </div>


          <div>

            <CheckCircle2 size={16} />

            <div>

              <strong>
                Traceable
              </strong>

              <span>
                Index outputs remain linked to cleaned
                underlying fare observations.
              </span>

            </div>

          </div>


          <div>

            <CheckCircle2 size={16} />

            <div>

              <strong>
                Reproducible
              </strong>

              <span>
                Cleaning, normalisation and aggregation
                rules are applied consistently.
              </span>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          PROCESS PIPELINE
      ===================================================== */}

      <section className="methodology-panel">

        <div className="methodology-section-heading">

          <span>
            END-TO-END PROCESS
          </span>

          <h2>
            From collection to index publication
          </h2>

          <p>
            Six processing stages separate raw web
            observations from the published airfare
            indicator.
          </p>

        </div>


        <div className="methodology-flow">

          {methodologySteps.map(
            (step, index) => (

              <div
                className="methodology-flow-wrapper"
                key={step.number}
              >

                <article className="methodology-step">

                  <div className="methodology-step-number">
                    {step.number}
                  </div>

                  <div className="methodology-step-icon">
                    {step.icon}
                  </div>

                  <h3>
                    {step.title}
                  </h3>

                  <p>
                    {step.description}
                  </p>

                </article>


                {index !==
                  methodologySteps.length - 1 && (

                  <div className="methodology-flow-arrow">

                    <ArrowDown size={17} />

                  </div>

                )}

              </div>

            )
          )}

        </div>

      </section>


      {/* =====================================================
          ROUTE BASKET + PURCHASE WINDOWS
      ===================================================== */}

      <div className="methodology-two-column">

        {/* ROUTES */}

        <section className="methodology-panel">

          <div className="methodology-section-heading">

            <span>
              REPRESENTATIVE BASKET
            </span>

            <h2>
              Prototype city-pairs
            </h2>

            <p>
              Representative domestic sectors identified
              in the problem statement form the initial
              prototype monitoring basket.
            </p>

          </div>


          <div className="methodology-route-list">

            {routeBasket.map(
              (route, index) => (

                <div
                  className="methodology-route-row"
                  key={route.route}
                >

                  <span>
                    {String(
                      index + 1
                    ).padStart(
                      2,
                      "0"
                    )}
                  </span>


                  <div>

                    <strong>
                      {route.route}
                    </strong>

                    <small>
                      {route.cities}
                    </small>

                  </div>


                  <div className="route-weight-status">
                    PSD-defined
                  </div>

                </div>

              )
            )}

          </div>


          <div className="methodology-source-note">

            These city-pairs are representative examples
            identified in the problem statement. The
            production route basket should follow DGCA
            passenger-traffic data together with the
            routes and weights specified by the Problem
            Statement Department.

          </div>

        </section>


        {/* PURCHASE WINDOWS */}

        <section className="methodology-panel">

          <div className="methodology-section-heading">

            <span>
              BOOKING HORIZON
            </span>

            <h2>
              Advance-purchase windows
            </h2>

            <p>
              Dynamic airfare pricing is sampled at
              multiple booking horizons before departure.
            </p>

          </div>


          <div className="purchase-methodology">

            {purchaseWindows.map(
              (window) => (

                <div
                  className="purchase-methodology-row"
                  key={window.name}
                >

                  <strong>
                    {window.name}
                  </strong>

                  <div className="purchase-window-line">
                    <span></span>
                  </div>

                  <span>
                    {window.days}
                  </span>

                </div>

              )
            )}

          </div>


          <div className="purchase-explanation">

            <CalendarRange size={18} />

            <p>
              Recording multiple advance-purchase
              horizons captures how fares change as the
              departure date approaches.
            </p>

          </div>

        </section>

      </div>


      {/* =====================================================
          DATA CLEANING
      ===================================================== */}

      <section className="methodology-panel">

        <div className="methodology-section-heading">

          <span>
            DATA PREPARATION
          </span>

          <h2>
            Cleaning and normalisation
          </h2>

          <p>
            Raw scraped observations do not directly enter
            index construction.
          </p>

        </div>


        <div className="methodology-cleaning-grid">

          <article>

            <span>
              01
            </span>

            <strong>
              Duplicate removal
            </strong>

            <p>
              Repeated observations are identified and
              removed before aggregation.
            </p>

          </article>


          <article>

            <span>
              02
            </span>

            <strong>
              Missing observations
            </strong>

            <p>
              Missing fare quotes are identified and
              handled through the data-quality pipeline.
            </p>

          </article>


          <article>

            <span>
              03
            </span>

            <strong>
              Outlier treatment
            </strong>

            <p>
              Unusual fare observations are detected so
              that extreme values do not silently distort
              the resulting series.
            </p>

          </article>


          <article>

            <span>
              04
            </span>

            <strong>
              Availability status
            </strong>

            <p>
              Cancellations and sold-out flights are
              distinguished from ordinary missing quotes.
            </p>

          </article>


          <article>

            <span>
              05
            </span>

            <strong>
              Fare decomposition
            </strong>

            <p>
              Base fare, taxes, user-development fee and
              convenience charges remain separately
              identifiable.
            </p>

          </article>


          <article>

            <span>
              06
            </span>

            <strong>
              Metadata preservation
            </strong>

            <p>
              Origin, destination, carrier, source,
              purchase window, fare class and collection
              metadata remain attached to cleaned records.
            </p>

          </article>

        </div>

      </section>


      {/* =====================================================
          INDEX CONSTRUCTION
      ===================================================== */}

      <section className="methodology-panel index-methodology-panel">

        <div className="methodology-section-heading">

          <span>
            INDEX CONSTRUCTION
          </span>

          <h2>
            Aggregation framework
          </h2>

          <p>
            Cleaned route-level observations support daily,
            weekly and monthly APIx outputs.
          </p>

        </div>


        <div className="index-methodology-content">

          <div className="index-concept-flow">

            <div>

              <span>
                1
              </span>

              <strong>
                Clean fares
              </strong>

            </div>


            <span>
              →
            </span>


            <div>

              <span>
                2
              </span>

              <strong>
                Route measures
              </strong>

            </div>


            <span>
              →
            </span>


            <div>

              <span>
                3
              </span>

              <strong>
                PSD route weights
              </strong>

            </div>


            <span>
              →
            </span>


            <div>

              <span>
                4
              </span>

              <strong>
                APIx
              </strong>

            </div>

          </div>


          <div className="methodology-formula-box">

            <div>

              <Scale size={21} />

              <div>

                <span>
                  WEIGHTING SPECIFICATION
                </span>

                <h3>
                  PSD-provided routes and weights
                </h3>

                <p>
                  The problem statement specifies an
                  index-construction module based on
                  PSD-given routes and weights. The
                  frontend therefore does not invent an
                  official weighting formula or numerical
                  route weights. The production
                  implementation should apply the
                  specification provided for those routes
                  and weights.
                </p>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          PUBLICATION FREQUENCIES
      ===================================================== */}

      <section className="methodology-frequency">

        <div>

          <span>
            PUBLICATION FREQUENCY
          </span>

          <h2>
            One collection system,
            three index frequencies.
          </h2>

        </div>


        <div className="frequency-options">

          <article>

            <strong>
              Daily
            </strong>

            <span>
              High-frequency airfare movement
            </span>

          </article>


          <article>

            <strong>
              Weekly
            </strong>

            <span>
              Short-term pricing trend
            </span>

          </article>


          <article>

            <strong>
              Monthly
            </strong>

            <span>
              CPI-oriented analytical view
            </span>

          </article>

        </div>

      </section>


      {/* =====================================================
          METHODOLOGY NOTE
      ===================================================== */}

      <div className="methodology-footer-note">

        This prototype methodology follows the current SIH
        problem-statement requirements. The completed
        solution should also demonstrate at least 30 days
        of back-tested results against publicly available
        DGCA monthly average-fare data. Final
        index-construction behaviour must follow the
        PSD-specified routes and weights.

      </div>

    </div>
  );
}


export default Methodology;