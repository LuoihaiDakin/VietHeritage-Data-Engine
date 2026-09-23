const API_URL = "http://127.0.0.1:8000";

function AssetCard({ asset }) {
  const imagePath = asset.path
    ? `${API_URL}/${asset.path}`
    : null;

  return (
    <div className="asset-card">
      {imagePath ? (
        <img
          src={imagePath}
          alt={asset.filename || "Heritage asset"}
          className="asset-card-image"
          onError={(event) => {
            console.error("Image failed:", event.target.src);
          }}
        />
      ) : (
        <div className="asset-card-placeholder">
          No Image
        </div>
      )}

      <div className="asset-card-content">
        <h3>
          {asset.filename || "Untitled"}
        </h3>

        <p>
          Category: {asset.category || "Unknown"}
        </p>

        <p>
          Quality: {asset.quality?.quality || "Unknown"}
        </p>

        <p>
          Score: {asset.quality?.overall_score ?? "N/A"}
        </p>
      </div>
    </div>
  );
}

export default AssetCard;