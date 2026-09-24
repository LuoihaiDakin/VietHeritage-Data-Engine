function AssetCard({ asset, onClick }) {
  const quality = asset.quality?.quality || "UNKNOWN";

  const score =
    asset.quality?.overall_score ?? "-";

  const category =
    asset.category || "Unknown";

  const imagePath =
    asset.original?.path ||
    asset.path;

  const imageUrl = imagePath
    ? `http://127.0.0.1:8000/${imagePath.replace(/^\/+/, "")}`
    : null;

  return (
    <div
      className="asset-card"
      onClick={onClick}
    >
      <div className="asset-image-container">

        {imageUrl ? (
          <img
            src={imageUrl}
            alt={asset.filename}
            className="asset-image"
          />
        ) : (
          <div className="image-placeholder">
            No image
          </div>
        )}

      </div>

      <div className="asset-content">

        <h3>
          {asset.filename}
        </h3>

        <p className="asset-category">
          {category}
        </p>

        <div className="asset-meta">

          <span
            className={`quality-badge ${quality.toLowerCase()}`}
          >
            {quality}
          </span>

          <span className="score">
            Score: {score}
          </span>

        </div>

      </div>
    </div>
  );
}

export default AssetCard;