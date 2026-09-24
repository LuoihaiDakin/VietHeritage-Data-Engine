import { useEffect, useMemo, useState } from "react";
import "./App.css";

import AssetCard from "./components/AssetCard";
import AssetModal from "./components/AssetModal";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [quality, setQuality] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // =========================
  // LOAD ASSETS
  // =========================
  useEffect(() => {
    async function loadAssets() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE}/assets?limit=100&offset=0`
        );

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        console.log("API DATA:", data);

        setAssets(data.results || []);
      } catch (err) {
        console.error(err);
        setError("Cannot load assets from API.");
      } finally {
        setLoading(false);
      }
    }

    loadAssets();
  }, []);

  // =========================
  // CATEGORIES
  // =========================
  const categories = useMemo(() => {
    const uniqueCategories = [
      ...new Set(
        assets
          .map((asset) => asset.category)
          .filter(Boolean)
      ),
    ];

    return uniqueCategories.sort();
  }, [assets]);

  // =========================
  // STATISTICS
  // =========================
  const statistics = useMemo(() => {
    return {
      total: assets.length,

      good: assets.filter(
        (asset) => asset.quality?.quality === "GOOD"
      ).length,

      acceptable: assets.filter(
        (asset) => asset.quality?.quality === "ACCEPTABLE"
      ).length,

      poor: assets.filter(
        (asset) => asset.quality?.quality === "POOR"
      ).length,
    };
  }, [assets]);

  // =========================
  // FILTER
  // =========================
  const filteredAssets = useMemo(() => {
    return assets.filter((asset) => {
      const searchText = search.toLowerCase().trim();

      const matchesSearch =
        !searchText ||
        asset.filename?.toLowerCase().includes(searchText) ||
        asset.id?.toLowerCase().includes(searchText) ||
        asset.category?.toLowerCase().includes(searchText);

      const matchesCategory =
        !category ||
        asset.category === category;

      const matchesQuality =
        !quality ||
        asset.quality?.quality === quality;

      return (
        matchesSearch &&
        matchesCategory &&
        matchesQuality
      );
    });
  }, [assets, search, category, quality]);

  // =========================
  // RESET FILTER
  // =========================
  function clearFilters() {
    setSearch("");
    setCategory("");
    setQuality("");
  }

  return (
    <div className="app">
      {/* ================= HEADER ================= */}
      <header className="header">
        <div>
          <h1>VietHeritage Data Engine</h1>
          <p>
            Heritage Asset Management & Data Quality Dashboard
          </p>
        </div>
      </header>

      {/* ================= MAIN ================= */}
      <main className="container">

        {/* ================= STATS ================= */}
        <section className="stats-grid">

          <div className="stat-card">
            <span className="stat-label">
              Total Assets
            </span>

            <strong className="stat-value">
              {statistics.total}
            </strong>
          </div>

          <div className="stat-card">
            <span className="stat-label">
              Good
            </span>

            <strong className="stat-value">
              {statistics.good}
            </strong>
          </div>

          <div className="stat-card">
            <span className="stat-label">
              Acceptable
            </span>

            <strong className="stat-value">
              {statistics.acceptable}
            </strong>
          </div>

          <div className="stat-card">
            <span className="stat-label">
              Poor
            </span>

            <strong className="stat-value">
              {statistics.poor}
            </strong>
          </div>

        </section>

        {/* ================= FILTERS ================= */}
        <section className="filters">

          <div className="filter-group">
            <label>
              Search
            </label>

            <input
              type="text"
              placeholder="Search filename or ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>
              Category
            </label>

            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">
                All categories
              </option>

              {categories.map((item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>
              Quality
            </label>

            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
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

          <button
            className="clear-button"
            onClick={clearFilters}
          >
            Clear
          </button>

        </section>

        {/* ================= RESULTS INFO ================= */}
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

          {(search || category || quality) && (
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
              {filteredAssets.map((asset) => (
                <AssetCard
                  key={asset.id}
                  asset={asset}
                  onClick={() =>
                    setSelectedAsset(asset)
                  }
                />
              ))}
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
        />
      )}
    </div>
  );
}

export default App;