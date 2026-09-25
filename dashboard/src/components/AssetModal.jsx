import ProcessPanel from "./ProcessPanel";

const API_BASE = "http://127.0.0.1:8000";

function buildImageUrl(path) {
  if (!path) {
    return "";
  }

  let normalizedPath = String(path).replace(/\\/g, "/");

  if (
    normalizedPath.startsWith("http://") ||
    normalizedPath.startsWith("https://")
  ) {
    return normalizedPath;
  }

  normalizedPath = normalizedPath.replace(/^\/+/, "");

  // =========================
  // ORIGINAL DATASET IMAGE
  // =========================

  if (normalizedPath.startsWith("images/")) {
    return `${API_BASE}/${normalizedPath}`;
  }

  // =========================
  // DATASET/IMAGES PATH
  // =========================

  if (normalizedPath.startsWith("dataset/images/")) {
    const imagePath = normalizedPath.substring(
      "dataset/images/".length
    );

    return `${API_BASE}/images/${imagePath}`;
  }

  // =========================
  // OUTPUTS
  // =========================

  if (normalizedPath.startsWith("outputs/")) {
    return `${API_BASE}/${normalizedPath}`;
  }

  // =========================
  // OTHER DATASET PATHS
  // =========================

  if (normalizedPath.startsWith("dataset/")) {
    return `${API_BASE}/${normalizedPath}`;
  }

  return `${API_BASE}/${normalizedPath}`;
}

function formatValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Unknown";
  }

  return String(value);
}

function formatMetric(value, digits = 2) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return number.toFixed(digits);
}

function getQuality(asset) {
  return asset?.quality?.quality || "UNKNOWN";
}

function getQualityScore(asset) {
  const score = asset?.quality?.overall_score;

  if (
    score === null ||
    score === undefined
  ) {
    return null;
  }

  const number = Number(score);

  if (Number.isNaN(number)) {
    return null;
  }

  return number;
}

function getQualityClass(quality) {
  switch (quality) {
    case "GOOD":
      return "good";

    case "ACCEPTABLE":
      return "acceptable";

    case "POOR":
      return "poor";

    default:
      return "unknown";
  }
}

function getOriginalPath(asset) {
  return (
    asset?.original?.path ||
    asset?.path ||
    ""
  );
}

function getDisplayName(asset) {
  return (
    asset?.filename ||
    asset?.original?.filename ||
    asset?.id ||
    "Untitled asset"
  );
}

function AssetModal({
  asset,
  onClose,
  onProcessed,
}) {
  if (!asset) {
    return null;
  }

  const quality = getQuality(asset);

  const qualityScore =
    getQualityScore(asset);

  const qualityClass =
    getQualityClass(quality);

  const originalPath =
    getOriginalPath(asset);

  const originalImageUrl =
    buildImageUrl(originalPath);

  const technicalMetrics =
    asset?.quality?.technical_metrics ||
    asset?.original ||
    {};

  const qualityScores =
    asset?.quality?.quality_scores ||
    {};

  const qualityFlags =
    asset?.quality?.quality_flags ||
    [];

  const recommendation =
    asset?.quality?.recommendation ||
    "No recommendation available.";

  const processing =
    asset?.processing || {};

  const outputs =
    asset?.processing_outputs ||
    asset?.outputs ||
    {};

  const processingStages = [
    {
      key: "preprocessed",
      label: "Preprocessed",
      description: "Image preprocessing completed",
    },
    {
      key: "restored",
      label: "Restored",
      description: "Image restoration completed",
    },
    {
      key: "normalized",
      label: "Normalized",
      description: "Image normalization completed",
    },
    {
      key: "segmented",
      label: "Segmented",
      description: "Pattern segmentation completed",
    },
    {
      key: "vectorized",
      label: "Vectorized",
      description: "SVG vectorization completed",
    },
  ];

  const outputEntries = [
    {
      key: "restored",
      label: "Restored Image",
      icon: "↗",
    },
    {
      key: "normalized",
      label: "Normalized Image",
      icon: "↗",
    },
    {
      key: "segmented",
      label: "Segmented Image",
      icon: "↗",
    },
    {
      key: "edges",
      label: "Edge Map",
      icon: "↗",
    },
    {
      key: "svg",
      label: "Vector SVG",
      icon: "↗",
    },
    {
      key: "quality_report",
      label: "Quality Report",
      icon: "↗",
    },
  ];

  function getOutputPath(key) {
    return outputs?.[key] || "";
  }

  return (
    <div
      className="vh-modal-overlay"
      onClick={onClose}
    >
      <div
        className="vh-modal"
        onClick={(event) =>
          event.stopPropagation()
        }
      >

        {/* ================= HEADER ================= */}

        <div className="vh-modal-header">

          <div className="vh-title-area">

            <div className="vh-modal-eyebrow">
              HERITAGE ASSET
            </div>

            <h2>
              {getDisplayName(asset)}
            </h2>

            <div className="vh-modal-id">
              ID: {formatValue(asset.id)}
            </div>

          </div>

          <button
            className="vh-close-button"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>

        </div>

        {/* ================= BODY ================= */}

        <div className="vh-modal-body">

          {/* ================= IMAGE ================= */}

          <section className="vh-image-section">

            <div className="vh-image-container">

              {originalImageUrl ? (
                <img
                  src={originalImageUrl}
                  alt={getDisplayName(asset)}
                  className="vh-main-image"
                />
              ) : (
                <div className="vh-image-placeholder">
                  <span>IMAGE</span>
                  No preview available
                </div>
              )}

            </div>

          </section>

          {/* ================= QUALITY ================= */}

          <section className="vh-section">

            <div className="vh-section-header">

              <div>
                <span className="vh-section-label">
                  DATA QUALITY
                </span>

                <h3>
                  Quality Assessment
                </h3>
              </div>

              <div
                className={`vh-quality-badge ${qualityClass}`}
              >
                {quality}
              </div>

            </div>

            <div className="vh-quality-overview">

              {/* SCORE */}

              <div className="vh-score-card">

                <span>
                  Overall Score
                </span>

                <div className="vh-score-value">
                  {qualityScore !== null
                    ? qualityScore.toFixed(2)
                    : "—"}
                </div>

                <small>
                  / 100
                </small>

              </div>

              {/* METRICS */}

              <div className="vh-quality-metrics">

                {/* BRIGHTNESS */}

                <div className="vh-quality-metric">

                  <div className="vh-quality-metric-header">

                    <span>
                      Brightness
                    </span>

                    <strong>
                      {formatMetric(
                        qualityScores.brightness
                      )}
                    </strong>

                  </div>

                  <div className="vh-quality-track">

                    <div
                      className="vh-quality-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            Number(
                              qualityScores.brightness
                            ) || 0,
                            0
                          ),
                          100
                        )}%`,
                      }}
                    />

                  </div>

                </div>

                {/* CONTRAST */}

                <div className="vh-quality-metric">

                  <div className="vh-quality-metric-header">

                    <span>
                      Contrast
                    </span>

                    <strong>
                      {formatMetric(
                        qualityScores.contrast
                      )}
                    </strong>

                  </div>

                  <div className="vh-quality-track">

                    <div
                      className="vh-quality-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            Number(
                              qualityScores.contrast
                            ) || 0,
                            0
                          ),
                          100
                        )}%`,
                      }}
                    />

                  </div>

                </div>

                {/* SHARPNESS */}

                <div className="vh-quality-metric">

                  <div className="vh-quality-metric-header">

                    <span>
                      Sharpness
                    </span>

                    <strong>
                      {formatMetric(
                        qualityScores.sharpness
                      )}
                    </strong>

                  </div>

                  <div className="vh-quality-track">

                    <div
                      className="vh-quality-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            Number(
                              qualityScores.sharpness
                            ) || 0,
                            0
                          ),
                          100
                        )}%`,
                      }}
                    />

                  </div>

                </div>

                {/* RESOLUTION */}

                <div className="vh-quality-metric">

                  <div className="vh-quality-metric-header">

                    <span>
                      Resolution
                    </span>

                    <strong>
                      {formatMetric(
                        qualityScores.resolution
                      )}
                    </strong>

                  </div>

                  <div className="vh-quality-track">

                    <div
                      className="vh-quality-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            Number(
                              qualityScores.resolution
                            ) || 0,
                            0
                          ),
                          100
                        )}%`,
                      }}
                    />

                  </div>

                </div>

              </div>

            </div>

            {/* FLAGS */}

            {qualityFlags.length > 0 && (
              <div className="vh-quality-flags">

                <span className="vh-subtitle">
                  Quality Flags
                </span>

                <div className="vh-tag-list">

                  {qualityFlags.map(
                    (flag, index) => (
                      <span
                        className="vh-tag"
                        key={`${flag}-${index}`}
                      >
                        {flag}
                      </span>
                    )
                  )}

                </div>

              </div>
            )}

            {/* RECOMMENDATION */}

            <div className="vh-recommendation">

              <span className="vh-subtitle">
                Recommendation
              </span>

              <p>
                {recommendation}
              </p>

            </div>

          </section>

          {/* ================= METADATA ================= */}

          <section className="vh-section">

            <div className="vh-section-header">

              <div>
                <span className="vh-section-label">
                  HERITAGE METADATA
                </span>

                <h3>
                  Asset Information
                </h3>
              </div>

            </div>

            <div className="vh-metadata-grid">

              <div className="vh-meta-item">
                <span>Filename</span>
                <strong>
                  {formatValue(
                    asset.filename
                  )}
                </strong>
              </div>

              <div className="vh-meta-item">
                <span>Category</span>
                <strong>
                  {formatValue(
                    asset.category
                  )}
                </strong>
              </div>

              <div className="vh-meta-item">
                <span>Dynasty</span>
                <strong>
                  {formatValue(
                    asset.dynasty
                  )}
                </strong>
              </div>

              <div className="vh-meta-item">
                <span>Period</span>
                <strong>
                  {formatValue(
                    asset.period
                  )}
                </strong>
              </div>

              <div className="vh-meta-item">
                <span>Motif</span>
                <strong>
                  {formatValue(
                    asset.motif
                  )}
                </strong>
              </div>

              <div className="vh-meta-item">
                <span>Region</span>
                <strong>
                  {formatValue(
                    asset.region
                  )}
                </strong>
              </div>

              <div className="vh-meta-item">
                <span>Source</span>
                <strong>
                  {formatValue(
                    asset.source
                  )}
                </strong>
              </div>

              <div className="vh-meta-item">
                <span>License</span>
                <strong>
                  {formatValue(
                    asset.license
                  )}
                </strong>
              </div>

            </div>

          </section>

          {/* ================= PROCESSING STATUS ================= */}

          <section className="vh-processing-panel">

            <div className="vh-processing-header">

              <div>

                <span className="vh-section-label">
                  DATA PIPELINE
                </span>

                <h3>
                  Processing Status
                </h3>

                <p>
                  Current processing stages
                  and generated results
                </p>

              </div>

              <div className="vh-processing-summary">

                <strong>
                  {
                    processingStages.filter(
                      (stage) =>
                        processing?.[
                          stage.key
                        ] === true
                    ).length
                  }
                </strong>

                <span>
                  / {processingStages.length}
                </span>

              </div>

            </div>

            <div className="vh-processing-grid">

              {processingStages.map(
                (stage, index) => {

                  const completed =
                    processing?.[
                      stage.key
                    ] === true;

                  return (
                    <div
                      className={`vh-processing-card ${
                        completed
                          ? "completed"
                          : ""
                      }`}
                      key={stage.key}
                    >

                      <div
                        className={`vh-processing-icon ${
                          completed
                            ? "completed"
                            : ""
                        }`}
                      >
                        {completed
                          ? "✓"
                          : index + 1}
                      </div>

                      <div className="vh-processing-info">

                        <strong>
                          {stage.label}
                        </strong>

                        <span>
                          {completed
                            ? "Completed"
                            : "Not processed"}
                        </span>

                      </div>

                      <div
                        className={`vh-processing-status ${
                          completed
                            ? "completed"
                            : ""
                        }`}
                      >
                        {completed
                          ? "READY"
                          : "PENDING"}
                      </div>

                    </div>
                  );
                }
              )}

            </div>

            {asset.processed_at && (
              <div className="processed-time">
                <span>
                  Last processed
                </span>

                <strong>
                  {asset.processed_at}
                </strong>
              </div>
            )}

          </section>

          {/* ================= SAVED OUTPUTS ================= */}

          {Object.keys(outputs).length > 0 && (
            <section className="vh-section">

              <div className="vh-section-header">

                <div>

                  <span className="vh-section-label">
                    GENERATED DATA
                  </span>

                  <h3>
                    Processing Outputs
                  </h3>

                </div>

              </div>

              <div className="vh-output-grid">

                {outputEntries.map(
                  (output) => {

                    const path =
                      getOutputPath(
                        output.key
                      );

                    return (
                      <div
                        className={`vh-output-card ${
                          path
                            ? "available"
                            : ""
                        }`}
                        key={output.key}
                      >

                        <div className="vh-output-icon">
                          {output.icon}
                        </div>

                        <div className="vh-output-content">

                          <strong>
                            {output.label}
                          </strong>

                          <span>
                            {path
                              ? "Available"
                              : "Not available"}
                          </span>

                        </div>

                        {path && (
                          <a
                            href={buildImageUrl(
                              path
                            )}
                            target="_blank"
                            rel="noreferrer"
                            className="vh-output-link"
                          >
                            Open
                          </a>
                        )}

                      </div>
                    );
                  }
                )}

              </div>

            </section>
          )}

          {/* ================= TECHNICAL ================= */}

          <section className="vh-section">

            <div className="vh-section-header">

              <div>

                <span className="vh-section-label">
                  TECHNICAL DATA
                </span>

                <h3>
                  Source Image Metrics
                </h3>

              </div>

            </div>

            <div className="vh-technical-grid">

              <div className="vh-technical-item">
                <span>Width</span>
                <strong>
                  {formatValue(
                    technicalMetrics.width
                  )}{" "}
                  px
                </strong>
              </div>

              <div className="vh-technical-item">
                <span>Height</span>
                <strong>
                  {formatValue(
                    technicalMetrics.height
                  )}{" "}
                  px
                </strong>
              </div>

              <div className="vh-technical-item">
                <span>Format</span>
                <strong>
                  {formatValue(
                    asset.original?.format
                  )}
                </strong>
              </div>

              <div className="vh-technical-item">
                <span>File Size</span>
                <strong>
                  {asset.original
                    ?.file_size_kb !==
                  undefined
                    ? `${formatMetric(
                        asset.original
                          .file_size_kb
                      )} KB`
                    : "—"}
                </strong>
              </div>

              <div className="vh-technical-item">
                <span>Brightness</span>
                <strong>
                  {formatMetric(
                    technicalMetrics.brightness
                  )}
                </strong>
              </div>

              <div className="vh-technical-item">
                <span>Contrast</span>
                <strong>
                  {formatMetric(
                    technicalMetrics.contrast
                  )}
                </strong>
              </div>

              <div className="vh-technical-item">
                <span>Sharpness</span>
                <strong>
                  {formatMetric(
                    technicalMetrics.sharpness
                  )}
                </strong>
              </div>

            </div>

          </section>

          {/* ================= PROCESS PANEL ================= */}

          <section className="vh-section vh-process-section">

            <div className="vh-section-header">

              <div>

                <span className="vh-section-label">
                  PIPELINE CONTROL
                </span>

                <h3>
                  Process Asset
                </h3>

              </div>

            </div>

            <ProcessPanel
              asset={asset}
              onProcessed={onProcessed}
            />

          </section>

        </div>
      </div>

      {/* ================= STYLES ================= */}

      <style>{`

        /* ========================================
           MODAL
        ======================================== */

        .vh-modal-overlay {
          position: fixed;
          inset: 0;
          z-index: 1000;

          display: flex;
          align-items: center;
          justify-content: center;

          padding: 24px;

          background:
            rgba(3, 5, 8, 0.82);

          backdrop-filter: blur(12px);
        }

        .vh-modal {
          width: min(1180px, 100%);
          max-height: 94vh;

          overflow: hidden;

          border: 1px solid
            rgba(255,255,255,0.09);

          border-radius: 22px;

          background:
            linear-gradient(
              145deg,
              #151515 0%,
              #101010 55%,
              #0d0d0d 100%
            );

          box-shadow:
            0 30px 100px
              rgba(0,0,0,0.65);

        }

        /* ========================================
           HEADER
        ======================================== */

        .vh-modal-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;

          padding: 24px 28px;

          border-bottom:
            1px solid
            rgba(255,255,255,0.07);

          background:
            linear-gradient(
              180deg,
              rgba(255,255,255,0.025),
              transparent
            );
        }

        .vh-modal-eyebrow,
        .vh-section-label {
          color: #a87869;

          font-size: 9px;
          font-weight: 800;

          letter-spacing: 1.7px;
        }

        .vh-modal-header h2 {
          margin: 7px 0 4px;

          color: #f0f0f0;

          font-size: 22px;
          font-weight: 700;

          letter-spacing: -0.3px;
        }

        .vh-modal-id {
          color: #5d5d5d;
          font-size: 10px;
        }

        .vh-close-button {
          width: 38px;
          height: 38px;

          border:
            1px solid
            rgba(255,255,255,0.08);

          border-radius: 10px;

          background:
            rgba(255,255,255,0.035);

          color: #888;

          font-size: 23px;

          cursor: pointer;

          transition:
            background 0.2s ease,
            color 0.2s ease,
            transform 0.2s ease;
        }

        .vh-close-button:hover {
          background:
            rgba(255,255,255,0.08);

          color: #eee;

          transform: rotate(90deg);
        }

        /* ========================================
           BODY
        ======================================== */

        .vh-modal-body {
          max-height:
            calc(94vh - 88px);

          overflow-y: auto;

          padding:
            24px 28px 36px;
        }

        .vh-modal-body::-webkit-scrollbar {
          width: 7px;
        }

        .vh-modal-body::-webkit-scrollbar-track {
          background: transparent;
        }

        .vh-modal-body::-webkit-scrollbar-thumb {
          border-radius: 10px;

          background:
            rgba(255,255,255,0.12);
        }

        /* ========================================
           IMAGE
        ======================================== */

        .vh-image-section {
          margin-bottom: 22px;
        }

        .vh-image-container {
          display: flex;

          align-items: center;
          justify-content: center;

          min-height: 300px;

          overflow: hidden;

          border:
            1px solid
            rgba(255,255,255,0.08);

          border-radius: 16px;

          background:
            radial-gradient(
              circle at center,
              #191919,
              #0a0a0a 75%
            );

          box-shadow:
            inset 0 0 50px
              rgba(0,0,0,0.3);
        }

        .vh-main-image {
          display: block;

          max-width: 100%;
          max-height: 430px;

          object-fit: contain;
        }

        .vh-image-placeholder {
          display: flex;

          flex-direction: column;
          align-items: center;

          gap: 8px;

          color: #555;

          font-size: 11px;
        }

        .vh-image-placeholder span {
          display: flex;

          align-items: center;
          justify-content: center;

          width: 42px;
          height: 42px;

          border-radius: 10px;

          background:
            rgba(255,255,255,0.05);

          color: #777;

          font-size: 9px;
          font-weight: 700;
        }

        /* ========================================
           GENERAL SECTION
        ======================================== */

        .vh-section {
          margin-top: 18px;

          padding: 21px;

          border:
            1px solid
            rgba(255,255,255,0.065);

          border-radius: 16px;

          background:
            rgba(255,255,255,0.018);
        }

        .vh-section-header {
          display: flex;

          align-items: flex-start;
          justify-content: space-between;

          margin-bottom: 17px;
        }

        .vh-section-header h3,
        .vh-processing-header h3 {
          margin: 5px 0 0;

          color: #e8e8e8;

          font-size: 15px;
          font-weight: 700;
        }

        /* ========================================
           QUALITY
        ======================================== */

        .vh-quality-badge {
          padding: 6px 11px;

          border-radius: 999px;

          font-size: 9px;
          font-weight: 800;

          letter-spacing: 0.6px;
        }

        .vh-quality-badge.good {
          background:
            rgba(101,197,141,0.12);

          color: #65c58d;
        }

        .vh-quality-badge.acceptable {
          background:
            rgba(203,167,93,0.12);

          color: #cba75d;
        }

        .vh-quality-badge.poor {
          background:
            rgba(201,111,111,0.12);

          color: #c96f6f;
        }

        .vh-quality-badge.unknown {
          background:
            rgba(255,255,255,0.06);

          color: #777;
        }

        .vh-quality-overview {
          display: grid;

          grid-template-columns:
            180px 1fr;

          gap: 14px;
        }

        .vh-score-card {
          display: flex;

          flex-direction: column;
          justify-content: center;

          padding: 18px;

          border:
            1px solid
            rgba(255,255,255,0.055);

          border-radius: 13px;

          background:
            linear-gradient(
              145deg,
              rgba(255,255,255,0.045),
              rgba(255,255,255,0.018)
            );
        }

        .vh-score-card span {
          color: #666;
          font-size: 9px;
        }

        .vh-score-value {
          margin-top: 4px;

          color: #f1f1f1;

          font-size: 34px;
          font-weight: 700;
        }

        .vh-score-card small {
          color: #555;
          font-size: 9px;
        }

        .vh-quality-metrics {
          display: grid;

          grid-template-columns:
            repeat(2, 1fr);

          gap: 8px;
        }

        .vh-quality-metric {
          padding: 13px;

          border:
            1px solid
            rgba(255,255,255,0.04);

          border-radius: 10px;

          background:
            rgba(255,255,255,0.025);
        }

        .vh-quality-metric-header {
          display: flex;

          align-items: center;
          justify-content: space-between;

          margin-bottom: 9px;
        }

        .vh-quality-metric-header span {
          color: #666;
          font-size: 9px;
        }

        .vh-quality-metric-header strong {
          color: #ddd;
          font-size: 11px;
        }

        .vh-quality-track {
          width: 100%;
          height: 4px;

          overflow: hidden;

          border-radius: 999px;

          background:
            rgba(255,255,255,0.06);
        }

        .vh-quality-fill {
          height: 100%;

          border-radius: inherit;

          background:
            linear-gradient(
              90deg,
              #8d5c50,
              #c38b78
            );

          transition:
            width 0.45s ease;
        }

        .vh-quality-flags,
        .vh-recommendation {
          margin-top: 17px;
        }

        .vh-subtitle {
          display: block;

          margin-bottom: 8px;

          color: #666;

          font-size: 9px;
          font-weight: 700;

          text-transform: uppercase;
          letter-spacing: 0.8px;
        }

        .vh-tag-list {
          display: flex;

          flex-wrap: wrap;

          gap: 7px;
        }

        .vh-tag {
          padding: 6px 9px;

          border:
            1px solid
            rgba(201,111,111,0.2);

          border-radius: 7px;

          background:
            rgba(201,111,111,0.06);

          color: #c98282;

          font-size: 9px;
        }

        .vh-recommendation p {
          margin: 0;

          color: #888;

          font-size: 10px;
          line-height: 1.6;
        }

        /* ========================================
           METADATA
        ======================================== */

        .vh-metadata-grid {
          display: grid;

          grid-template-columns:
            repeat(4, 1fr);

          gap: 9px;
        }

        .vh-meta-item,
        .vh-technical-item {
          min-width: 0;

          padding: 14px;

          border:
            1px solid
            rgba(255,255,255,0.045);

          border-radius: 11px;

          background:
            rgba(255,255,255,0.025);

          transition:
            background 0.2s ease,
            border-color 0.2s ease;
        }

        .vh-meta-item:hover,
        .vh-technical-item:hover {
          border-color:
            rgba(255,255,255,0.09);

          background:
            rgba(255,255,255,0.04);
        }

        .vh-meta-item span,
        .vh-technical-item span {
          display: block;

          margin-bottom: 7px;

          color: #5f5f5f;

          font-size: 9px;
          font-weight: 600;

          text-transform: uppercase;
          letter-spacing: 0.4px;
        }

        .vh-meta-item strong,
        .vh-technical-item strong {
          display: block;

          overflow: hidden;

          color: #d2d2d2;

          font-size: 11px;

          text-overflow: ellipsis;
          white-space: nowrap;
        }

        /* ========================================
           PROCESSING STATUS
        ======================================== */

        .vh-processing-panel {
          margin-top: 18px;

          padding: 21px;

          border:
            1px solid
            rgba(255,255,255,0.08);

          border-radius: 16px;

          background:
            linear-gradient(
              145deg,
              rgba(255,255,255,0.035),
              rgba(255,255,255,0.012)
            );

          box-shadow:
            inset 0 1px 0
              rgba(255,255,255,0.025);
        }

        .vh-processing-header {
          display: flex;

          align-items: flex-start;
          justify-content: space-between;

          margin-bottom: 17px;
        }

        .vh-processing-header p {
          margin: 5px 0 0;

          color: #5e5e5e;

          font-size: 9px;
        }

        .vh-processing-summary {
          display: flex;

          align-items: baseline;

          padding: 8px 12px;

          border:
            1px solid
            rgba(101,197,141,0.15);

          border-radius: 9px;

          background:
            rgba(101,197,141,0.06);

          color: #65c58d;
        }

        .vh-processing-summary strong {
          font-size: 17px;
        }

        .vh-processing-summary span {
          margin-left: 2px;

          color: #567c67;

          font-size: 10px;
        }

        .vh-processing-grid {
          display: grid;

          grid-template-columns:
            repeat(5, 1fr);

          gap: 9px;
        }

        .vh-processing-card {
          position: relative;

          display: flex;

          align-items: center;

          min-width: 0;

          padding: 13px;

          border:
            1px solid
            rgba(255,255,255,0.05);

          border-radius: 11px;

          background:
            rgba(255,255,255,0.025);

          transition:
            transform 0.2s ease,
            background 0.2s ease,
            border-color 0.2s ease;
        }

        .vh-processing-card:hover {
          transform: translateY(-2px);

          background:
            rgba(255,255,255,0.045);
        }

        .vh-processing-card.completed {
          border-color:
            rgba(101,197,141,0.16);

          background:
            linear-gradient(
              145deg,
              rgba(101,197,141,0.075),
              rgba(255,255,255,0.02)
            );
        }

        .vh-processing-icon {
          display: flex;

          align-items: center;
          justify-content: center;

          flex-shrink: 0;

          width: 30px;
          height: 30px;

          border-radius: 9px;

          background:
            rgba(255,255,255,0.055);

          color: #666;

          font-size: 10px;
          font-weight: 800;
        }

        .vh-processing-icon.completed {
          background:
            rgba(101,197,141,0.14);

          color: #65c58d;

          box-shadow:
            0 0 14px
              rgba(101,197,141,0.08);
        }

        .vh-processing-info {
          min-width: 0;

          margin-left: 9px;
        }

        .vh-processing-info strong {
          display: block;

          overflow: hidden;

          color: #d3d3d3;

          font-size: 10px;

          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .vh-processing-info span {
          display: block;

          margin-top: 3px;

          color: #5c5c5c;

          font-size: 8px;
        }

        .vh-processing-status {
          display: none;
        }

        .vh-processing-status.completed {
          color: #65c58d;
        }

        .processed-time {
          display: flex;

          justify-content: space-between;

          margin-top: 13px;
          padding-top: 12px;

          border-top:
            1px solid
            rgba(255,255,255,0.05);

          color: #555;

          font-size: 9px;
        }

        .processed-time strong {
          color: #777;
          font-weight: 500;
        }

        /* ========================================
           OUTPUTS
        ======================================== */

        .vh-output-grid {
          display: grid;

          grid-template-columns:
            repeat(3, 1fr);

          gap: 9px;
        }

        .vh-output-card {
          display: flex;

          align-items: center;

          min-width: 0;

          padding: 13px;

          border:
            1px solid
            rgba(255,255,255,0.045);

          border-radius: 11px;

          background:
            rgba(255,255,255,0.02);
        }

        .vh-output-card.available {
          border-color:
            rgba(255,255,255,0.065);
        }

        .vh-output-icon {
          display: flex;

          align-items: center;
          justify-content: center;

          flex-shrink: 0;

          width: 30px;
          height: 30px;

          border-radius: 8px;

          background:
            rgba(163,106,93,0.12);

          color: #b47b6d;

          font-size: 13px;
        }

        .vh-output-content {
          min-width: 0;

          margin-left: 9px;
        }

        .vh-output-content strong {
          display: block;

          overflow: hidden;

          color: #ccc;

          font-size: 10px;

          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .vh-output-content span {
          display: block;

          margin-top: 3px;

          color: #555;

          font-size: 8px;
        }

        .vh-output-card.available
        .vh-output-content span {
          color: #65a47e;
        }

        .vh-output-link {
          flex-shrink: 0;

          margin-left: auto;

          padding: 6px 9px;

          border:
            1px solid
            rgba(255,255,255,0.08);

          border-radius: 7px;

          color: #999;

          font-size: 8px;
          font-weight: 600;

          text-decoration: none;

          transition:
            background 0.2s ease,
            color 0.2s ease;
        }

        .vh-output-link:hover {
          background:
            rgba(163,106,93,0.12);

          color: #d29a8a;
        }

        /* ========================================
           TECHNICAL
        ======================================== */

        .vh-technical-grid {
          display: grid;

          grid-template-columns:
            repeat(4, 1fr);

          gap: 9px;
        }

        /* ========================================
           PROCESS PANEL
        ======================================== */

        .vh-process-section {
          margin-bottom: 0;
        }

        /* ========================================
           RESPONSIVE
        ======================================== */

        @media (max-width: 1000px) {

          .vh-processing-grid {
            grid-template-columns:
              repeat(3, 1fr);
          }

          .vh-output-grid {
            grid-template-columns:
              repeat(2, 1fr);
          }

        }

        @media (max-width: 800px) {

          .vh-modal-overlay {
            padding: 10px;
          }

          .vh-modal-header,
          .vh-modal-body {
            padding-left: 17px;
            padding-right: 17px;
          }

          .vh-quality-overview {
            grid-template-columns: 1fr;
          }

          .vh-quality-metrics {
            grid-template-columns:
              repeat(2, 1fr);
          }

          .vh-metadata-grid,
          .vh-technical-grid {
            grid-template-columns:
              repeat(2, 1fr);
          }

          .vh-processing-grid {
            grid-template-columns:
              repeat(2, 1fr);
          }

        }

        @media (max-width: 500px) {

          .vh-quality-metrics,
          .vh-metadata-grid,
          .vh-technical-grid,
          .vh-processing-grid,
          .vh-output-grid {
            grid-template-columns: 1fr;
          }

          .vh-processing-header {
            flex-direction: column;
            gap: 12px;
          }

        }

      `}</style>

    </div>
  );
}

export default AssetModal;