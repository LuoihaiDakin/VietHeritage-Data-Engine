import { useEffect, useState } from "react";
import AssetCard from "./components/AssetCard";
import AssetModal from "./components/AssetModal";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Search
  const [searchTerm, setSearchTerm] = useState("");

  // Category filter
  const [categoryFilter, setCategoryFilter] = useState("all");

  // Quality filter
  const [qualityFilter, setQualityFilter] = useState("all");

  useEffect(() => {
    fetch(`${API_URL}/assets`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        return response.json();
      })
      .then((data) => {
        console.log("API response:", data);

        setAssets(data.results || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load assets:", err);

        setError(err.message);
        setLoading(false);
      });
  }, []);

  /*
   * Get unique categories
   *
   * Example:
   * dong_ho
   * hang_trong
   * ...
   */
  const categories = [
    ...new Set(
      assets
        .map((asset) => asset.category)
        .filter(Boolean)
    ),
  ];

  /*
   * Filter assets
   */
  const filteredAssets = assets.filter((asset) => {
    /*
     * SEARCH
     *
     * Search through:
     * - filename
     * - category
     * - period
     * - dynasty
     * - motif
     * - region
     */
    const search = searchTerm.toLowerCase().trim();

    const matchesSearch =
      search === "" ||
      [
        asset.filename,
        asset.category,
        asset.period,
        asset.dynasty,
        asset.motif,
        asset.region,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value)
            .toLowerCase()
            .includes(search)
        );

    /*
     * CATEGORY
     */
    const matchesCategory =
      categoryFilter === "all" ||
      asset.category === categoryFilter;

    /*
     * QUALITY
     */
    const matchesQuality =
      qualityFilter === "all" ||
      asset.quality?.quality?.toLowerCase() ===
        qualityFilter.toLowerCase();

    return (
      matchesSearch &&
      matchesCategory &&
      matchesQuality
    );
  });

  /*
   * Clear all filters
   */
  const clearFilters = () => {
    setSearchTerm("");
    setCategoryFilter("all");
    setQualityFilter("all");
  };

  return (
    <div className="dashboard">

      {/* HEADER */}
      <header className="dashboard-header">
        <div>
          <h1>VietHeritage Data Engine</h1>

          <p>
            Digital heritage restoration and cultural
            asset management
          </p>
        </div>
      </header>


      {/* MAIN */}
      <main className="dashboard-content">

        {/* SECTION HEADER */}
        <div className="section-header">

          <div>
            <h2>Heritage Assets</h2>

            <p>
              Browse and inspect Vietnamese cultural
              heritage assets.
            </p>
          </div>

          <div className="asset-count">
            {filteredAssets.length} / {assets.length} assets
          </div>

        </div>


        {/* SEARCH + FILTERS */}
        <div className="filters">

          {/* SEARCH */}
          <div className="search-box">

            <input
              type="text"
              placeholder="Search heritage assets..."
              value={searchTerm}
              onChange={(event) =>
                setSearchTerm(event.target.value)
              }
            />

          </div>


          {/* CATEGORY */}
          <div className="filter-group">

            <label>
              Category
            </label>

            <select
              value={categoryFilter}
              onChange={(event) =>
                setCategoryFilter(event.target.value)
              }
            >
              <option value="all">
                All categories
              </option>

              {categories.map((category) => (
                <option
                  key={category}
                  value={category}
                >
                  {category}
                </option>
              ))}
            </select>

          </div>


          {/* QUALITY */}
          <div className="filter-group">

            <label>
              Quality
            </label>

            <select
              value={qualityFilter}
              onChange={(event) =>
                setQualityFilter(event.target.value)
              }
            >
              <option value="all">
                All quality
              </option>

              <option value="good">
                Good
              </option>

              <option value="acceptable">
                Acceptable
              </option>

              <option value="poor">
                Poor
              </option>

            </select>

          </div>


          {/* CLEAR */}
          <button
            className="clear-filters"
            onClick={clearFilters}
          >
            Clear
          </button>

        </div>


        {/* LOADING */}
        {loading && (
          <div className="status">
            Loading assets...
          </div>
        )}


        {/* ERROR */}
        {error && (
          <div className="status error">
            Failed to load assets: {error}
          </div>
        )}


        {/* NO ASSETS */}
        {!loading &&
          !error &&
          assets.length === 0 && (
            <div className="status">
              No heritage assets found.
            </div>
          )}


        {/* NO SEARCH RESULT */}
        {!loading &&
          !error &&
          assets.length > 0 &&
          filteredAssets.length === 0 && (
            <div className="status">

              <h3>
                No matching assets
              </h3>

              <p>
                Try changing your search or filters.
              </p>

              <button
                className="clear-filters"
                onClick={clearFilters}
              >
                Clear filters
              </button>

            </div>
          )}


        {/* ASSET GRID */}
        {!loading &&
          !error &&
          filteredAssets.length > 0 && (

            <div className="asset-grid">

              {filteredAssets.map((asset) => (

                <div
                  key={asset.id}
                  onClick={() =>
                    setSelectedAsset(asset)
                  }
                >
                  <AssetCard
                    asset={asset}
                  />
                </div>

              ))}

            </div>

          )}

      </main>


      {/* MODAL */}
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