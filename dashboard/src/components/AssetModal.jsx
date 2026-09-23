const API_URL = "http://127.0.0.1:8000";

function AssetModal({ asset, onClose }) {
  if (!asset) {
    return null;
  }

  // Dùng đúng đường dẫn giống AssetCard
  const imagePath = asset.path
    ? `${API_URL}/${asset.path}`
    : null;

  const original = asset.original || {};
  const quality = asset.quality || {};
  const qualityScores = quality.quality_scores || {};
  const technicalMetrics = quality.technical_metrics || {};
  const processing = asset.processing || {};

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
    >
      <div
        className="asset-modal"
        onClick={(event) => event.stopPropagation()}
      >
        {/* Close */}
        <button
          className="modal-close"
          onClick={onClose}
        >
          ×
        </button>

        {/* IMAGE */}
        <div className="modal-image-container">
          {imagePath ? (
            <img
              src={imagePath}
              alt={asset.filename || "Heritage asset"}
              className="modal-image"
              onError={(event) => {
                console.error(
                  "Modal image failed:",
                  event.target.src
                );
              }}
            />
          ) : (
            <div className="modal-image-placeholder">
              No Image
            </div>
          )}
        </div>

        {/* CONTENT */}
        <div className="modal-content">

          <h2>
            {asset.filename || "Untitled Asset"}
          </h2>

          {/* BASIC INFORMATION */}
          <div className="modal-section">
            <h3>Basic Information</h3>

            <p>
              <strong>ID:</strong>{" "}
              {asset.id || "Unknown"}
            </p>

            <p>
              <strong>Category:</strong>{" "}
              {asset.category || "Unknown"}
            </p>

            <p>
              <strong>Period:</strong>{" "}
              {asset.period || "Unknown"}
            </p>

            <p>
              <strong>Dynasty:</strong>{" "}
              {asset.dynasty || "Unknown"}
            </p>

            <p>
              <strong>Motif:</strong>{" "}
              {asset.motif || "Unknown"}
            </p>

            <p>
              <strong>Region:</strong>{" "}
              {asset.region || "Unknown"}
            </p>

            <p>
              <strong>Source:</strong>{" "}
              {asset.source || "Unknown"}
            </p>

            <p>
              <strong>License:</strong>{" "}
              {asset.license || "Unknown"}
            </p>
          </div>

          {/* ORIGINAL IMAGE */}
          <div className="modal-section">
            <h3>Original Image</h3>

            <p>
              <strong>Resolution:</strong>{" "}
              {original.width ?? "N/A"} ×{" "}
              {original.height ?? "N/A"}
            </p>

            <p>
              <strong>Format:</strong>{" "}
              {original.format || "N/A"}
            </p>

            <p>
              <strong>File size:</strong>{" "}
              {original.file_size_kb != null
                ? `${original.file_size_kb} KB`
                : "N/A"}
            </p>

            <p>
              <strong>Brightness:</strong>{" "}
              {original.brightness ?? "N/A"}
            </p>

            <p>
              <strong>Contrast:</strong>{" "}
              {original.contrast ?? "N/A"}
            </p>

            <p>
              <strong>Sharpness:</strong>{" "}
              {original.sharpness ?? "N/A"}
            </p>
          </div>

          {/* QUALITY */}
          <div className="modal-section">
            <h3>Quality Assessment</h3>

            <p>
              <strong>Quality:</strong>{" "}
              {quality.quality || "Unknown"}
            </p>

            <p>
              <strong>Overall Score:</strong>{" "}
              {quality.overall_score ?? "N/A"}
            </p>

            {quality.quality_flags &&
              quality.quality_flags.length > 0 && (
                <p>
                  <strong>Flags:</strong>{" "}
                  {quality.quality_flags.join(", ")}
                </p>
              )}

            {quality.recommendation && (
              <p>
                <strong>Recommendation:</strong>{" "}
                {quality.recommendation}
              </p>
            )}
          </div>

          {/* QUALITY SCORES */}
          <div className="modal-section">
            <h3>Quality Scores</h3>

            <p>
              <strong>Brightness:</strong>{" "}
              {qualityScores.brightness ?? "N/A"}
            </p>

            <p>
              <strong>Contrast:</strong>{" "}
              {qualityScores.contrast ?? "N/A"}
            </p>

            <p>
              <strong>Sharpness:</strong>{" "}
              {qualityScores.sharpness ?? "N/A"}
            </p>

            <p>
              <strong>Resolution:</strong>{" "}
              {qualityScores.resolution ?? "N/A"}
            </p>
          </div>

          {/* TECHNICAL METRICS */}
          <div className="modal-section">
            <h3>Technical Metrics</h3>

            <p>
              <strong>Brightness:</strong>{" "}
              {technicalMetrics.brightness ?? "N/A"}
            </p>

            <p>
              <strong>Contrast:</strong>{" "}
              {technicalMetrics.contrast ?? "N/A"}
            </p>

            <p>
              <strong>Sharpness:</strong>{" "}
              {technicalMetrics.sharpness ?? "N/A"}
            </p>

            <p>
              <strong>Width:</strong>{" "}
              {technicalMetrics.width ?? "N/A"}
            </p>

            <p>
              <strong>Height:</strong>{" "}
              {technicalMetrics.height ?? "N/A"}
            </p>
          </div>

          {/* PROCESSING */}
          <div className="modal-section">
            <h3>Processing Status</h3>

            <p>
              <strong>Preprocessed:</strong>{" "}
              {processing.preprocessed ? "Yes" : "No"}
            </p>

            <p>
              <strong>Restored:</strong>{" "}
              {processing.restored ? "Yes" : "No"}
            </p>

            <p>
              <strong>Normalized:</strong>{" "}
              {processing.normalized ? "Yes" : "No"}
            </p>

            <p>
              <strong>Segmented:</strong>{" "}
              {processing.segmented ? "Yes" : "No"}
            </p>

            <p>
              <strong>Vectorized:</strong>{" "}
              {processing.vectorized ? "Yes" : "No"}
            </p>
          </div>

          {/* FILE PATH */}
          <div className="modal-section">
            <h3>File</h3>

            <p>
              <strong>Path:</strong>{" "}
              {asset.path || "N/A"}
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default AssetModal;