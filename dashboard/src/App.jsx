import { useEffect, useMemo, useState } from "react";
import "./App.css";

import AssetCard from "./components/AssetCard";
import AssetModal from "./components/AssetModal";

const API_BASE = "http://127.0.0.1:8000";


function App() {

  const [assets, setAssets] = useState([]);

  const [selectedAsset, setSelectedAsset] =
    useState(null);


  // =========================
  // FILTER STATE
  // =========================

  const [search, setSearch] =
    useState("");

  const [category, setCategory] =
    useState("");

  const [dynasty, setDynasty] =
    useState("");

  const [period, setPeriod] =
    useState("");

  const [motif, setMotif] =
    useState("");

  const [region, setRegion] =
    useState("");

  const [quality, setQuality] =
    useState("");

  const [processingFilter, setProcessingFilter] =
    useState("");


  // =========================
  // UI STATE
  // =========================

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  // =========================
  // LOAD ASSETS
  // =========================

  async function loadAssets() {

    try {

      setLoading(true);
      setError("");


      const response = await fetch(
        `${API_BASE}/assets?limit=100&offset=0`
      );


      if (!response.ok) {

        throw new Error(
          `API error: ${response.status}`
        );

      }


      const data =
        await response.json();


      console.log(
        "API DATA:",
        data
      );


      setAssets(
        data.results || []
      );


    } catch (err) {

      console.error(err);

      setError(
        "Cannot load assets from API."
      );


    } finally {

      setLoading(false);

    }

  }


  // =========================
  // INITIAL LOAD
  // =========================

  useEffect(() => {

    loadAssets();

  }, []);


  // =========================
  // UNIQUE FILTER VALUES
  // =========================

  const categories = useMemo(() => {

    return [
      ...new Set(
        assets
          .map(
            (asset) =>
              asset.category
          )
          .filter(Boolean)
      ),
    ].sort();

  }, [assets]);


  const dynasties = useMemo(() => {

    return [
      ...new Set(
        assets
          .map(
            (asset) =>
              asset.dynasty
          )
          .filter(Boolean)
      ),
    ].sort();

  }, [assets]);


  const periods = useMemo(() => {

    return [
      ...new Set(
        assets
          .map(
            (asset) =>
              asset.period
          )
          .filter(Boolean)
      ),
    ].sort();

  }, [assets]);


  const motifs = useMemo(() => {

    return [
      ...new Set(
        assets
          .map(
            (asset) =>
              asset.motif
          )
          .filter(Boolean)
      ),
    ].sort();

  }, [assets]);


  const regions = useMemo(() => {

    return [
      ...new Set(
        assets
          .map(
            (asset) =>
              asset.region
          )
          .filter(Boolean)
      ),
    ].sort();

  }, [assets]);


  // =========================
  // STATISTICS
  // =========================

  const statistics = useMemo(() => {

    const total =
      assets.length;


    const preprocessed =
      assets.filter(
        (asset) =>
          asset.processing?.preprocessed === true
      ).length;


    const restored =
      assets.filter(
        (asset) =>
          asset.processing?.restored === true
      ).length;


    const normalized =
      assets.filter(
        (asset) =>
          asset.processing?.normalized === true
      ).length;


    const segmented =
      assets.filter(
        (asset) =>
          asset.processing?.segmented === true
      ).length;


    const vectorized =
      assets.filter(
        (asset) =>
          asset.processing?.vectorized === true
      ).length;


    const good =
      assets.filter(
        (asset) =>
          asset.quality?.quality === "GOOD"
      ).length;


    const acceptable =
      assets.filter(
        (asset) =>
          asset.quality?.quality === "ACCEPTABLE"
      ).length;


    const poor =
      assets.filter(
        (asset) =>
          asset.quality?.quality === "POOR"
      ).length;


    const qualityScores =
      assets
        .map(
          (asset) =>
            asset.quality?.overall_score
        )
        .filter(
          (score) =>
            typeof score === "number"
        );


    const averageQuality =
      qualityScores.length > 0
        ? qualityScores.reduce(
            (sum, score) =>
              sum + score,
            0
          ) / qualityScores.length
        : null;


    return {

      total,

      preprocessed,

      restored,

      normalized,

      segmented,

      vectorized,

      processed:
        restored,

      good,

      acceptable,

      poor,

      averageQuality

    };

  }, [assets]);


  // =========================
  // QUALITY PERCENTAGES
  // =========================

  const qualityPercentages =
    useMemo(() => {

      const total =
        statistics.total || 1;


      return {

        good:
          (statistics.good / total) * 100,

        acceptable:
          (statistics.acceptable / total) * 100,

        poor:
          (statistics.poor / total) * 100

      };

    }, [statistics]);


  // =========================
  // PROCESSING PERCENTAGES
  // =========================

  const processingPercentages =
    useMemo(() => {

      const total =
        statistics.total || 1;


      return {

        preprocessed:
          (statistics.preprocessed / total) * 100,

        restored:
          (statistics.restored / total) * 100,

        normalized:
          (statistics.normalized / total) * 100,

        segmented:
          (statistics.segmented / total) * 100,

        vectorized:
          (statistics.vectorized / total) * 100

      };

    }, [statistics]);


  // =========================
  // FILTER
  // =========================

  const filteredAssets = useMemo(() => {

    return assets.filter((asset) => {

      const searchText =
        search
          .toLowerCase()
          .trim();


      // =========================
      // SEARCH
      // =========================

      const searchableFields = [

        asset.filename,

        asset.id,

        asset.category,

        asset.dynasty,

        asset.period,

        asset.motif,

        asset.region,

        asset.source

      ];


      const matchesSearch =
        !searchText ||

        searchableFields.some(
          (value) =>
            String(value || "")
              .toLowerCase()
              .includes(searchText)
        );


      // =========================
      // CATEGORY
      // =========================

      const matchesCategory =
        !category ||
        asset.category === category;


      // =========================
      // DYNASTY
      // =========================

      const matchesDynasty =
        !dynasty ||
        asset.dynasty === dynasty;


      // =========================
      // PERIOD
      // =========================

      const matchesPeriod =
        !period ||
        asset.period === period;


      // =========================
      // MOTIF
      // =========================

      const matchesMotif =
        !motif ||
        asset.motif === motif;


      // =========================
      // REGION
      // =========================

      const matchesRegion =
        !region ||
        asset.region === region;


      // =========================
      // QUALITY
      // =========================

      const matchesQuality =
        !quality ||
        asset.quality?.quality === quality;


      // =========================
      // PROCESSING
      // =========================

      let matchesProcessing = true;


      if (processingFilter) {

        const processing =
          asset.processing || {};


        matchesProcessing =
          processing[
            processingFilter
          ] === true;

      }


      return (

        matchesSearch &&

        matchesCategory &&

        matchesDynasty &&

        matchesPeriod &&

        matchesMotif &&

        matchesRegion &&

        matchesQuality &&

        matchesProcessing

      );

    });

  }, [
    assets,
    search,
    category,
    dynasty,
    period,
    motif,
    region,
    quality,
    processingFilter
  ]);


  // =========================
  // RESET FILTER
  // =========================

  function clearFilters() {

    setSearch("");

    setCategory("");

    setDynasty("");

    setPeriod("");

    setMotif("");

    setRegion("");

    setQuality("");

    setProcessingFilter("");

  }


  // =========================
  // PROCESS COMPLETE
  // =========================

  async function handleAssetProcessed(
    processedAsset
  ) {

    console.log(
      "Asset processed:",
      processedAsset
    );


    await loadAssets();

  }


  // =========================
  // ACTIVE FILTERS
  // =========================

  const hasActiveFilters =
    Boolean(

      search ||

      category ||

      dynasty ||

      period ||

      motif ||

      region ||

      quality ||

      processingFilter

    );


  // =========================
  // PROCESSING DATA
  // =========================

  const processingRows = [

    {
      label: "Preprocessed",
      value: statistics.preprocessed,
      percentage:
        processingPercentages.preprocessed
    },

    {
      label: "Restored",
      value: statistics.restored,
      percentage:
        processingPercentages.restored
    },

    {
      label: "Normalized",
      value: statistics.normalized,
      percentage:
        processingPercentages.normalized
    },

    {
      label: "Segmented",
      value: statistics.segmented,
      percentage:
        processingPercentages.segmented
    },

    {
      label: "Vectorized",
      value: statistics.vectorized,
      percentage:
        processingPercentages.vectorized
    }

  ];


  // =========================
  // QUALITY DATA
  // =========================

  const qualityRows = [

    {
      label: "Good",
      value: statistics.good,
      percentage:
        qualityPercentages.good,
      className: "good"
    },

    {
      label: "Acceptable",
      value: statistics.acceptable,
      percentage:
        qualityPercentages.acceptable,
      className: "acceptable"
    },

    {
      label: "Poor",
      value: statistics.poor,
      percentage:
        qualityPercentages.poor,
      className: "poor"
    }

  ];


  return (

    <div className="app">


      {/* ================= HEADER ================= */}

      <header className="header">

        <div>

          <h1>
            VietHeritage Data Engine
          </h1>

          <p>
            Heritage Asset Management &
            Data Quality Dashboard
          </p>

        </div>

      </header>


      {/* ================= MAIN ================= */}

      <main className="container">


        {/* ================= TOP STATS ================= */}

        <section className="stats-grid">


          <div className="stat-card">

            <span className="stat-label">
              Total Assets
            </span>

            <strong className="stat-value">
              {statistics.total}
            </strong>

            <span className="stat-description">
              Heritage records
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Processed
            </span>

            <strong className="stat-value">
              {statistics.processed}
            </strong>

            <span className="stat-description">
              Restored assets
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Vectorized
            </span>

            <strong className="stat-value">
              {statistics.vectorized}
            </strong>

            <span className="stat-description">
              SVG patterns
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Average Quality
            </span>

            <strong className="stat-value">

              {statistics.averageQuality !== null
                ? statistics.averageQuality.toFixed(1)
                : "—"}

            </strong>

            <span className="stat-description">
              Source quality score
            </span>

          </div>


        </section>


        {/* ================= ANALYTICS ================= */}

        <section className="analytics-grid">


          {/* ================= QUALITY ================= */}

          <div className="analytics-card">

            <div className="analytics-header">

              <div>

                <h2>
                  Quality Distribution
                </h2>

                <p>
                  Heritage source quality
                </p>

              </div>

            </div>


            <div className="quality-bars">

              {qualityRows.map(
                (row) => (

                  <div
                    className="quality-row"
                    key={row.label}
                  >

                    <div className="quality-row-top">

                      <span>
                        {row.label}
                      </span>

                      <strong>
                        {row.value}
                      </strong>

                    </div>


                    <div className="quality-track">

                      <div
                        className={
                          `quality-fill ${row.className}`
                        }
                        style={{
                          width:
                            `${Math.max(
                              row.percentage,
                              row.value > 0
                                ? 3
                                : 0
                            )}%`
                        }}
                      />

                    </div>


                    <span className="quality-percent">

                      {row.percentage.toFixed(1)}
                      %

                    </span>

                  </div>

                )
              )}

            </div>

          </div>


          {/* ================= PROCESSING ================= */}

          <div className="analytics-card">

            <div className="analytics-header">

              <div>

                <h2>
                  Processing Pipeline
                </h2>

                <p>
                  Asset processing progress
                </p>

              </div>

            </div>


            <div className="processing-bars">

              {processingRows.map(
                (row) => (

                  <div
                    className="processing-row"
                    key={row.label}
                  >

                    <div className="processing-row-top">

                      <span>
                        {row.label}
                      </span>

                      <strong>
                        {row.value}
                      </strong>

                    </div>


                    <div className="processing-track">

                      <div
                        className="processing-fill"
                        style={{
                          width:
                            `${Math.max(
                              row.percentage,
                              row.value > 0
                                ? 3
                                : 0
                            )}%`
                        }}
                      />

                    </div>


                    <span className="processing-percent">

                      {row.percentage.toFixed(1)}
                      %

                    </span>

                  </div>

                )
              )}

            </div>

          </div>


        </section>


        {/* ================= FILTERS ================= */}

        <section className="filters">


          {/* ================= SEARCH ================= */}

          <div className="filter-group filter-search">

            <label>
              Search
            </label>

            <input
              type="text"
              placeholder="Search filename, ID, motif, region..."
              value={search}
              onChange={(e) =>
                setSearch(
                  e.target.value
                )
              }
            />

          </div>


          {/* ================= CATEGORY ================= */}

          <div className="filter-group">

            <label>
              Category
            </label>

            <select
              value={category}
              onChange={(e) =>
                setCategory(
                  e.target.value
                )
              }
            >

              <option value="">
                All categories
              </option>


              {categories.map(
                (item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                )
              )}

            </select>

          </div>


          {/* ================= DYNASTY ================= */}

          <div className="filter-group">

            <label>
              Dynasty
            </label>

            <select
              value={dynasty}
              onChange={(e) =>
                setDynasty(
                  e.target.value
                )
              }
            >

              <option value="">
                All dynasties
              </option>


              {dynasties.map(
                (item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                )
              )}

            </select>

          </div>


          {/* ================= PERIOD ================= */}

          <div className="filter-group">

            <label>
              Period
            </label>

            <select
              value={period}
              onChange={(e) =>
                setPeriod(
                  e.target.value
                )
              }
            >

              <option value="">
                All periods
              </option>


              {periods.map(
                (item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                )
              )}

            </select>

          </div>


          {/* ================= MOTIF ================= */}

          <div className="filter-group">

            <label>
              Motif
            </label>

            <select
              value={motif}
              onChange={(e) =>
                setMotif(
                  e.target.value
                )
              }
            >

              <option value="">
                All motifs
              </option>


              {motifs.map(
                (item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                )
              )}

            </select>

          </div>


          {/* ================= REGION ================= */}

          <div className="filter-group">

            <label>
              Region
            </label>

            <select
              value={region}
              onChange={(e) =>
                setRegion(
                  e.target.value
                )
              }
            >

              <option value="">
                All regions
              </option>


              {regions.map(
                (item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                )
              )}

            </select>

          </div>


          {/* ================= QUALITY ================= */}

          <div className="filter-group">

            <label>
              Quality
            </label>

            <select
              value={quality}
              onChange={(e) =>
                setQuality(
                  e.target.value
                )
              }
            >

              <option value="">
                All quality
              </option>

              <option value="GOOD">
                Good
              </option>

              <option value="ACCEPTABLE">
                Acceptable
              </option>

              <option value="POOR">
                Poor
              </option>

            </select>

          </div>


          {/* ================= PROCESSING ================= */}

          <div className="filter-group">

            <label>
              Processing
            </label>

            <select
              value={processingFilter}
              onChange={(e) =>
                setProcessingFilter(
                  e.target.value
                )
              }
            >

              <option value="">
                All processing
              </option>

              <option value="preprocessed">
                Preprocessed
              </option>

              <option value="restored">
                Restored
              </option>

              <option value="normalized">
                Normalized
              </option>

              <option value="segmented">
                Segmented
              </option>

              <option value="vectorized">
                Vectorized
              </option>

            </select>

          </div>


          {/* ================= CLEAR ================= */}

          <button
            className="clear-button"
            onClick={clearFilters}
          >
            Clear
          </button>


        </section>


        {/* ================= RESULTS ================= */}

        <section className="results-info">

          <div>

            Showing{" "}

            <strong>
              {filteredAssets.length}
            </strong>{" "}

            of{" "}

            <strong>
              {assets.length}
            </strong>{" "}

            assets

          </div>


          {hasActiveFilters && (

            <div className="active-filters">

              Filters active

            </div>

          )}

        </section>


        {/* ================= CONTENT ================= */}

        {loading && (

          <div className="message">
            Loading assets...
          </div>

        )}


        {error && (

          <div className="message error">
            {error}
          </div>

        )}


        {!loading &&
          !error &&
          filteredAssets.length === 0 && (

            <div className="message">
              No assets found.
            </div>

          )}


        {!loading &&
          !error &&
          filteredAssets.length > 0 && (

            <section className="asset-grid">

              {filteredAssets.map(
                (asset) => (

                  <AssetCard
                    key={asset.id}
                    asset={asset}
                    onClick={() =>
                      setSelectedAsset(
                        asset
                      )
                    }
                  />

                )
              )}

            </section>

          )}

      </main>


      {/* ================= MODAL ================= */}

      {selectedAsset && (

        <AssetModal
          asset={selectedAsset}

          onClose={() =>
            setSelectedAsset(null)
          }

          onProcessed={
            handleAssetProcessed
          }

        />

      )}


    </div>

  );

}


export default App;