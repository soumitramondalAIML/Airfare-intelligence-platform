import axios from "axios";

import {
  dashboardStats,
  systemInfo,
  trendData,
  leadTimeData,
  routeHeatmapData,
  sourceCoverage,
  routeAnalyticsData,
  fareObservations,
  dailyQualityTrend,
  qualityIssues,
  qualitySummary,
  sourceHealthData,
  backtestErrorTrend,
  backtestSummary,
  dgcaBacktestTrend,
  dgcaRouteComparison,
} from "../data/mockData";

/* =====================================================
   API CONFIGURATION
===================================================== */

const API_MODE =
  import.meta.env.VITE_API_MODE || "mock";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000/api/v1";


/* =====================================================
   AXIOS INSTANCE
===================================================== */

const apiClient = axios.create({
  baseURL: API_BASE_URL,

  timeout: 15000,

  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});


/* =====================================================
   RESPONSE INTERCEPTOR
===================================================== */

apiClient.interceptors.response.use(
  (response) => response,

  (error) => {
    console.error(
      "API request failed:",
      error?.response?.data || error.message
    );

    return Promise.reject(error);
  }
);


/* =====================================================
   SMALL MOCK DELAY

   Makes mock mode behave a little like a real API.
===================================================== */

const mockDelay = (milliseconds = 250) =>
  new Promise((resolve) =>
    setTimeout(resolve, milliseconds)
  );


/* =====================================================
   DASHBOARD DATA
===================================================== */

export async function getDashboardData() {

  /* -----------------------------
     MOCK MODE
  ----------------------------- */

  if (API_MODE === "mock") {

    await mockDelay();

    return {
      stats: dashboardStats,
      system: systemInfo,
      trend: trendData,
      leadTime: leadTimeData,
      heatmap: routeHeatmapData,
      sources: sourceCoverage,
    };
  }


  /* -----------------------------
     REAL API MODE
  ----------------------------- */

  const [
    currentIndexResponse,
    historyResponse,
    routesResponse,
    qualityResponse,
    leadTimeResponse,
    scraperHealthResponse,
  ] = await Promise.all([

    apiClient.get(
      "/index/current"
    ),

    apiClient.get(
      "/index/history",
      {
        params: {
          frequency: "daily",
        },
      }
    ),

    apiClient.get(
      "/routes"
    ),

    apiClient.get(
      "/quality/status"
    ),

    apiClient.get(
      "/routes/DEL/BOM"
    ),

    apiClient.get(
      "/scrapers/health"
    ),

  ]);


  const current =
    currentIndexResponse.data || {};

  const history =
    historyResponse.data || {};

  const routes =
    routesResponse.data || {};

  const quality =
    qualityResponse.data || {};

  const leadTimeRoute =
    leadTimeResponse.data || {};

  const scraperHealth =
    scraperHealthResponse.data || {};


  /* -----------------------------
     DASHBOARD STATS
  ----------------------------- */

  const stats = {

    currentIndex:
      current.index ??
      current.current_index ??
      0,

    dailyChange:
      current.dailyChange ??
      current.daily_change_pct ??
      0,

    weeklyChange:
      current.weeklyChange ??
      current.weekly_change_pct ??
      0,

    monthlyChange:
      current.monthlyChange ??
      current.monthly_change_pct ??
      0,

    averageFare:
      current.averageFare ??
      current.average_fare ??
      0,

    sourceCoverage:
      quality.coverage ??
      quality.coverage_pct ??
      quality.collection_health ??
      0,
  };


  /* -----------------------------
     SYSTEM INFORMATION
  ----------------------------- */

  const system = {

    observationsToday:
      quality.observationsToday ??
      quality.observations_today ??
      0,

    activeSources:
      scraperHealth.eligibleSources ??
      scraperHealth.eligible_sources ??
      0,

    lastUpdated:
      current.lastUpdated ??
      current.updated_at ??
      current.date ??
      "",
  };


  /* -----------------------------
     INDEX TREND
  ----------------------------- */

  const rawTrend =
    history.observations || [];

  const trend =
    rawTrend.map(
      (item) => ({

        date:
          item.date ?? "",

        index:
          item.index ??
          item.apix ??
          0,
      })
    );


  /* -----------------------------
     LEAD TIME
  ----------------------------- */

  const leadTime =
    (
      leadTimeRoute.lead_time_fares ||
      []
    ).map(
      (item) => ({

        window:
          `T+${item.advance_days}`,

        fare:
          item.average_fare ?? 0,
      })
    );


  /* -----------------------------
     ROUTE HEATMAP
  ----------------------------- */

  const rawRoutes =
    Array.isArray(routes)
      ? routes
      : routes.routes || [];


  const heatmap =
    rawRoutes
      .map((item) => {

        const origin =
          item.origin ??
          item.origin_code ??
          "";

        const destination =
          item.destination ??
          item.destination_code ??
          "";

        const routeCode =
          item.route ??
          (
            origin &&
            destination
              ? `${origin}-${destination}`
              : ""
          );

        const rawWindows =
          item.windows ??
          item.movements ??
          item.window_changes ??
          {};


        return {

          route:
            routeCode,

          cityPair:
            item.cityPair ??
            item.city_pair ??
            (
              origin &&
              destination
                ? `${origin} → ${destination}`
                : routeCode
            ),

          windows: {

            "T+45":
              rawWindows["T+45"] ??
              rawWindows.t45 ??
              null,

            "T+30":
              rawWindows["T+30"] ??
              rawWindows.t30 ??
              null,

            "T+15":
              rawWindows["T+15"] ??
              rawWindows.t15 ??
              null,

            "T+7":
              rawWindows["T+7"] ??
              rawWindows.t7 ??
              null,

            "T+1":
              rawWindows["T+1"] ??
              rawWindows.t1 ??
              null,
          },
        };

      })
      .filter(
        (item) =>
          item.route
      );


  /* -----------------------------
     LIVE SOURCE COVERAGE
  ----------------------------- */

  const sources =
    (scraperHealth.sources || [])
      .map(
        (source) =>
          source.source ??
          source.name ??
          ""
      )
      .filter(Boolean);


  return {
    stats,
    system,
    trend,
    leadTime,
    heatmap,
    sources,
  };
}


/* =====================================================
   CURRENT INDEX
===================================================== */

export async function getCurrentIndex() {

  if (API_MODE === "mock") {

    await mockDelay();

    return {
      index:
        dashboardStats.currentIndex,

      daily_change_pct:
        dashboardStats.dailyChange,

      weekly_change_pct:
        dashboardStats.weeklyChange,

      monthly_change_pct:
        dashboardStats.monthlyChange,

      average_fare:
        dashboardStats.averageFare,
    };
  }


  const response =
    await apiClient.get(
      "/index/current"
    );


  return response.data;
}


/* =====================================================
   INDEX HISTORY
===================================================== */

export async function getIndexHistory(
  frequency = "daily"
) {

  if (API_MODE === "mock") {

    await mockDelay();

    return trendData;
  }


  const response =
    await apiClient.get(
      "/index/history",
      {
        params: {
          frequency,
        },
      }
    );


  return (
    response.data?.observations || []
  );
}


/* =====================================================
   ROUTE LIST
===================================================== */

export async function getRoutes() {

  if (API_MODE === "mock") {

    await mockDelay();

    return routeHeatmapData;
  }


  const response =
    await apiClient.get(
      "/routes"
    );


  return (
    Array.isArray(response.data)
      ? response.data
      : response.data?.routes || []
  );
}


/* =====================================================
   ROUTE ANALYTICS
===================================================== */

export async function getRouteAnalytics(
  origin,
  destination,
  window = "T+7"
) {

  const route =
    `${origin}-${destination}`;


  /* -----------------------------
     MOCK MODE
  ----------------------------- */

  if (API_MODE === "mock") {

    await mockDelay();

    const routeData =
      routeAnalyticsData[route];


    if (!routeData) {

      throw new Error(
        `No route analytics found for ${route}`
      );
    }


    return {
      ...routeData,
      purchaseWindow: window,
    };
  }


  /* -----------------------------
     REAL API MODE
  ----------------------------- */

  const response =
    await apiClient.get(
      `/routes/${origin}/${destination}`,
      {
        params: {
          window,
        },
      }
    );


  const data =
    response.data;


  return {

    origin:
      (
        typeof data.origin === "object" &&
        data.origin !== null
      )
        ? data.origin
        : {
            code:
              data.origin ||
              origin,

            city:
              data.origin_city ||
              data.origin ||
              origin,

            airport:
              data.origin_airport ||
              "",
          },


    destination:
      (
        typeof data.destination === "object" &&
        data.destination !== null
      )
        ? data.destination
        : {
            code:
              data.destination ||
              destination,

            city:
              data.destination_city ||
              data.destination ||
              destination,

            airport:
              data.destination_airport ||
              "",
          },


    currentIndex:
      data.current_index ??
      data.route_index ??
      data.index_value ??
      0,


    change:
      data.daily_change_pct ??
      data.change ??
      0,


    monthlyChange:
      data.monthly_change_pct ??
      data.monthly_change ??
      0,


    history:
      data.history || [],


    leadTimes:
      data.lead_times ||
      data.leadTimes ||
      data.lead_time_fares ||
      [],


    fareBreakdown: {

      baseFare:
        data.fare_breakdown?.base_fare ??
        data.fareBreakdown?.baseFare ??
        0,

      taxes:
        data.fare_breakdown?.taxes ??
        data.fareBreakdown?.taxes ??
        0,

      udf:
        data.fare_breakdown?.udf ??
        data.fareBreakdown?.udf ??
        0,

      convenienceFee:
        data.fare_breakdown?.convenience_fee ??
        data.fareBreakdown?.convenienceFee ??
        0,
    },


    carriers:
      (
        data.carriers ||
        []
      ).map(
        (carrier) => ({

          carrier:
            carrier.carrier,

          source:
            carrier.source,

          fare:
            carrier.fare,

          change:
            carrier.change ??
            carrier.change_pct ??
            0,
        })
      ),


    purchaseWindow:
      data.purchase_window ||
      window,
  };
}


/* =====================================================
   FARE OBSERVATIONS
===================================================== */

export async function getFares(
  filters = {}
) {

  /* -----------------------------
     MOCK MODE
  ----------------------------- */

  if (API_MODE === "mock") {

    await mockDelay();

    return fareObservations;
  }


  /* -----------------------------
     REAL API MODE
  ----------------------------- */

  const response =
    await apiClient.get(
      "/fares",
      {
        params: filters,
      }
    );


  const observations =
    response.data?.observations || [];


  return observations.map(
    (fare) => {

      const routeParts =
        fare.route?.split("-") || [];


      return {

        id:
          fare.id ??
          fare.observation_id ??
          "",


        collectedAt:
          fare.collectedAt ??
          fare.collected_at ??
          "",


        origin:
          fare.origin ??
          routeParts[0] ??
          "",


        destination:
          fare.destination ??
          routeParts[1] ??
          "",


        carrier:
          fare.carrier ??
          "",


        source:
          fare.source ??
          "",


        sourceType:
          fare.sourceType ??
          fare.source_type ??
          "",


        window:
          fare.window ??
          fare.purchase_window ??
          "",


        fareClass:
          fare.fareClass ??
          fare.fare_class ??
          "",


        baseFare:
          fare.baseFare ??
          fare.base_fare ??
          null,


        taxes:
          fare.taxes ??
          0,


        udf:
          fare.udf ??
          0,


        convenienceFee:
          fare.convenienceFee ??
          fare.convenience_fee ??
          0,


        totalFare:
          fare.totalFare ??
          fare.total_fare ??
          0,


        quality:
          fare.quality ??
          fare.quality_status ??
          "Clean",


        sourceUrl:
          fare.sourceUrl ??
          fare.source_url ??
          "",
      };
    }
  );
}


/* =====================================================
   DATA QUALITY
===================================================== */

export async function getQualityData() {

  /* -----------------------------
     MOCK MODE
  ----------------------------- */

  if (API_MODE === "mock") {

    await mockDelay();

    return {
      summary: qualitySummary,
      sources: sourceHealthData,
      trend: dailyQualityTrend,
      issues: qualityIssues,
    };
  }


  /* -----------------------------
     REAL API MODE
  ----------------------------- */

  /*
    We call BOTH endpoints.

    /quality/status
      -> quality summary, trend and issues

    /scrapers/health
      -> live source health and collection status
  */

  const [
    qualityResponse,
    scraperHealthResponse,
  ] = await Promise.all([

    apiClient.get(
      "/quality/status"
    ),

    apiClient.get(
      "/scrapers/health"
    ),

  ]);


  const data =
    qualityResponse.data || {};

  const scraperHealth =
    scraperHealthResponse.data || {};


  /* =====================================================
     SUMMARY NORMALISATION
  ===================================================== */

  const summarySource =
    data.summary || data;


  const summary = {

    collectionHealth:
      summarySource.collectionHealth ??
      summarySource.collection_health ??
      summarySource.coverage_pct ??
      0,


    validObservations:
      summarySource.validObservations ??
      summarySource.valid_observations ??
      0,


    flaggedRecords:
      summarySource.flaggedRecords ??
      summarySource.flagged_records ??
      0,


    missingQuotes:
      summarySource.missingQuotes ??
      summarySource.missing_quotes ??
      0,


    duplicateRecords:
      summarySource.duplicateRecords ??
      summarySource.duplicate_records ??
      0,


    outliersRemoved:
      summarySource.outliersRemoved ??
      summarySource.outliers_removed ??
      0,
  };


  /* =====================================================
     SOURCE HEALTH NORMALISATION
  ===================================================== */

  const rawSources =
    scraperHealth.sources || [];


  const sources =
    rawSources.map(
      (source) => ({

        source:
          source.source ??
          source.name ??
          "",


        type:
          source.sourceType ??
          source.source_type ??
          source.type ??
          "",


        status:
          source.status ??
          "Unknown",


        coverage:
          source.coveragePct ??
          source.coverage_pct ??
          source.coverage ??
          0,


        records:
          source.storedObservations ??
          source.stored_observations ??
          source.recordCount ??
          source.record_count ??
          0,


        lastUpdate:
          source.lastObservationAt ??
          source.last_observation_at ??
          source.updated_at ??
          "",
      })
    );


  /* =====================================================
     QUALITY TREND NORMALISATION
  ===================================================== */

  const rawTrend =
    data.trend ||
    data.daily_quality_trend ||
    [];


  const trend =
    rawTrend.map(
      (item) => ({

        date:
          item.date ??
          item.day ??
          "",


        coverage:
          item.coverage ??
          item.coverage_pct ??
          item.coveragePct ??
          0,


        records:
          item.records ??
          item.record_count ??
          item.recordCount ??
          0,
      })
    );


  /* =====================================================
     QUALITY ISSUES NORMALISATION
  ===================================================== */

  const rawIssues =
    data.issues ||
    data.quality_issues ||
    [];


  const issues =
    rawIssues.map(
      (issue) => ({

        id:
          issue.id ??
          issue.issue_id ??
          "",


        type:
          issue.type ??
          issue.issue_type ??
          "Quality",


        source:
          issue.source ??
          "",


        route:
          issue.route ??
          "",


        window:
          issue.window ??
          issue.purchase_window ??
          "",


        severity:
          issue.severity ??
          "Low",


        action:
          issue.action ??
          issue.resolution ??
          "",


        message:
          issue.message ??
          issue.description ??
          "",


        count:
          issue.count ??
          0,
      })
    );


  return {
    summary,
    sources,
    trend,
    issues,
  };
}


/* =====================================================
   DATA QUALITY STATUS
===================================================== */

export async function getQualityStatus() {

  if (API_MODE === "mock") {

    await mockDelay();

    return {
      coverage:
        dashboardStats.sourceCoverage,

      activeSources:
        systemInfo.activeSources,

      observationsToday:
        systemInfo.observationsToday,

      sources:
        sourceCoverage,
    };
  }


  const response =
    await apiClient.get(
      "/quality/status"
    );


  return response.data;
}


/* =====================================================
   SCRAPER / SOURCE HEALTH
===================================================== */

export async function getScraperHealth() {

  if (API_MODE === "mock") {

    return {
      overallStatus: "mock",
      dataMode: "mock",
      syntheticIncluded: true,
      eligibleSources: 0,
      expectedObservationsPerCollection: 0,
      sources: [],
    };
  }


  const response =
    await apiClient.get(
      "/scrapers/health"
    );


  const data =
    response.data || {};


  const sources =
    (
      data.sources || []
    ).map(
      (source) => ({

        source:
          source.source ??
          source.name ??
          "",


        sourceCode:
          source.sourceCode ??
          source.source_code ??
          "",


        sourceType:
          source.sourceType ??
          source.source_type ??
          "",


        status:
          source.status ??
          "unknown",


        latestRunStatus:
          source.latestRunStatus ??
          source.latest_run_status ??
          "unknown",


        latestRunStartedAt:
          source.latestRunStartedAt ??
          source.latest_run_started_at ??
          null,


        latestRunFinishedAt:
          source.latestRunFinishedAt ??
          source.latest_run_finished_at ??
          null,


        lastSuccessfulRun:
          source.lastSuccessfulRun ??
          source.last_successful_run ??
          null,


        lastObservationAt:
          source.lastObservationAt ??
          source.last_observation_at ??
          null,


        latestCollectionDate:
          source.latestCollectionDate ??
          source.latest_collection_date ??
          null,


        storedObservations:
          source.storedObservations ??
          source.stored_observations ??
          0,


        expectedObservations:
          source.expectedObservations ??
          source.expected_observations ??
          0,


        coveragePct:
          source.coveragePct ??
          source.coverage_pct ??
          0,


        dataAgeHours:
          source.dataAgeHours ??
          source.data_age_hours ??
          null,


        errorMessage:
          source.errorMessage ??
          source.error_message ??
          null,
      })
    );


  return {

    overallStatus:
      data.overallStatus ??
      data.overall_status ??
      "unknown",


    dataMode:
      data.dataMode ??
      data.data_mode ??
      "unknown",


    syntheticIncluded:
      data.syntheticIncluded ??
      data.synthetic_included ??
      false,


    eligibleSources:
      data.eligibleSources ??
      data.eligible_sources ??
      sources.length,


    expectedObservationsPerCollection:
      data.expectedObservationsPerCollection ??
      data.expected_observations_per_collection ??
      0,


    sources,
  };
}


/* =====================================================
   API HEALTH
===================================================== */

export async function checkApiHealth() {

  if (API_MODE === "mock") {

    return {
      status: "mock",
      available: true,
    };
  }


  try {

    const response =
      await apiClient.get(
        "/health"
      );


    return {

      status:
        response.data?.status ??
        "online",

      available: true,
    };

  } catch (error) {

    console.error(
      "API health check failed:",
      error
    );


    return {
      status: "offline",
      available: false,
    };
  }
}


/* =====================================================
   DGCA BACK-TEST DATA
===================================================== */

export async function getBacktestData() {

  /* -----------------------------
     MOCK MODE
  ----------------------------- */

  if (API_MODE === "mock") {

    await mockDelay();

    return {

      status: "mock",

      dataNote:
        "Mock validation mode.",

      statisticalErrorComparable:
        true,

      dgcaStatus:
        "mock",

      summary:
        backtestSummary,

      comparisonTrend:
        dgcaBacktestTrend,

      errorTrend:
        backtestErrorTrend,

      routeComparison:
        dgcaRouteComparison,
    };
  }


  /* -----------------------------
     REAL API MODE
  ----------------------------- */

  const response =
    await apiClient.get(
      "/backtest"
    );


  const data =
    response.data || {};


  const rawSummary =
    data.summary || {};


  const summary = {

    startDate:
      rawSummary.startDate ??
      rawSummary.start_date ??
      "",


    endDate:
      rawSummary.endDate ??
      rawSummary.end_date ??
      "",


    numberOfDays:
      rawSummary.numberOfDays ??
      rawSummary.number_of_days ??
      0,


    correlation:
      rawSummary.correlation ??
      null,


    mape:
      rawSummary.mape ??
      null,


    routeCoverage:
      rawSummary.routeCoverage ??
      rawSummary.route_coverage ??
      0,


    observationCoverage:
      rawSummary.observationCoverage ??
      rawSummary.observation_coverage ??
      0,


    observations:
      rawSummary.observations ??
      0,


    matchedObservations:
      rawSummary.matchedObservations ??
      rawSummary.matched_observations ??
      0,


    routesEvaluated:
      rawSummary.routesEvaluated ??
      rawSummary.routes_evaluated ??
      0,


    routesWithReference:
      rawSummary.routesWithReference ??
      rawSummary.routes_with_reference ??
      0,
  };


  const rawRoutes =
    data.routeComparison ||
    data.route_comparison ||
    [];


  const routeComparison =
    rawRoutes.map(
      (item) => ({

        route:
          item.route ??
          "",


        observedAverage:
          item.observedAverage ??
          item.observed_average_total_fare ??
          null,


        observedMinimum:
          item.observedMinimum ??
          item.observed_minimum_total_fare ??
          null,


        observedMaximum:
          item.observedMaximum ??
          item.observed_maximum_total_fare ??
          null,


        referenceMinimum:
          item.referenceMinimum ??
          item.reference_minimum_base_fare ??
          null,


        referenceMaximum:
          item.referenceMaximum ??
          item.reference_maximum_base_fare ??
          null,


        observations:
          item.observations ??
          0,


        referenceAvailable:
          item.referenceAvailable ??
          item.reference_available ??
          false,


        status:
          item.status ??
          "Reference missing",
      })
    );


  return {

    status:
      data.status ??
      "",


    dataNote:
      data.dataNote ??
      data.data_note ??
      "",


    validationType:
      data.validationType ??
      data.validation_type ??
      "",


    statisticalErrorComparable:
      data.statisticalErrorComparable ??
      data.statistical_error_comparable ??
      false,


    dgcaStatus:
      data.dgca?.status ??
      "reference_data_pending",


    dgcaNote:
      data.dgca?.dataNote ??
      data.dgca?.data_note ??
      "",


    referenceValidation:
      data.referenceValidation ??
      data.reference_validation ??
      {},


    summary,


    comparisonTrend:
      data.comparisonTrend ??
      data.comparison_trend ??
      [],


    errorTrend:
      data.errorTrend ??
      data.error_trend ??
      [],


    routeComparison,
  };
}


/* =====================================================
   EXPORTS
===================================================== */

export {
  apiClient,
  API_MODE,
  API_BASE_URL,
};