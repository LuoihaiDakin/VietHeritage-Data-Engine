function AssetModal({ asset, onClose }) {
  const quality = asset.quality?.quality || "UNKNOWN";

  const score =
    asset.quality?.overall_score ?? "-";

  const category =
    asset.category || "Unknown";

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
    >
      <div
        className="modal"
        onClick={(e) => e.stopPropagation()}
      >

        <div className="modal-header">
          <h2>
            Asset Details
          </h2>

          <button
            className="close-button"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <div className="modal-body">

          <div className="detail-row">
            <strong>ID:</strong>
            <span>{asset.id}</span>
          </div>

          <div className="detail-row">
            <strong>Filename:</strong>
            <span>{asset.filename}</span>
          </div>

          <div className="detail-row">
            <strong>Category:</strong>
            <span>{category}</span>
          </div>

          <div className="detail-row">
            <strong>Quality:</strong>

            <span
              className={`quality-badge ${quality.toLowerCase()}`}
            >
              {quality}
            </span>
          </div>

          <div className="detail-row">
            <strong>Overall Score:</strong>
            <span>{score}</span>
          </div>

          <div className="detail-row">
            <strong>Path:</strong>
            <span>{asset.path}</span>
          </div>

          <div className="detail-row">
            <strong>Processing:</strong>

            <span>
              {asset.processing
                ? Object.entries(asset.processing)
                    .filter(([, value]) => value)
                    .map(([key]) => key)
                    .join(", ")
                : "None"}
            </span>
          </div>

        </div>

      </div>
    </div>
  );
}

export default AssetModal;