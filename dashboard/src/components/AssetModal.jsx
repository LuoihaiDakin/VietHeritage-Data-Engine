import ProcessPanel from "./ProcessPanel";

const API_BASE = "http://127.0.0.1:8000";


function buildImageUrl(path) {

  if (!path) {
    return "";
  }

  let normalizedPath =
    String(path).replace(/\\/g, "/");

  if (
    normalizedPath.startsWith("http://") ||
    normalizedPath.startsWith("https://")
  ) {
    return normalizedPath;
  }

  normalizedPath =
    normalizedPath.replace(/^\/+/, "");


  // ========================================
  // ORIGINAL DATASET IMAGE
  // ========================================

  if (
    normalizedPath.startsWith("images/")
  ) {
    return `${API_BASE}/${normalizedPath}`;
  }


  // ========================================
  // DATASET/IMAGES PATH
  // ========================================

  if (
    normalizedPath.startsWith("dataset/images/")
  ) {

    const imagePath =
      normalizedPath.substring(
        "dataset/images/".length
      );

    return `${API_BASE}/images/${imagePath}`;
  }


  // ========================================
  // OUTPUTS
  // ========================================

  if (
    normalizedPath.startsWith("outputs/")
  ) {
    return `${API_BASE}/${normalizedPath}`;
  }


  // ========================================
  // OTHER DATASET PATHS
  // ========================================

  if (
    normalizedPath.startsWith("dataset/")
  ) {
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

  const number =
    Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return number.toFixed(digits);
}


function getQuality(asset) {

  return (
    asset?.quality?.quality ||
    "UNKNOWN"
  );

}


function getQualityScore(asset) {

  const score =
    asset?.quality?.overall_score;

  if (
    score === null ||
    score === undefined
  ) {
    return null;
  }

  const number =
    Number(score);

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
  onProcessed
}) {

  if (!asset) {
    return null;
  }


  const quality =
    getQuality(asset);


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
    asset?.processing ||
    {};


  const outputs =
    asset?.outputs ||
    asset?.processing_outputs ||
    {};


  const processingStages = [

    {
      key: "preprocessed",
      label: "Preprocessed"
    },

    {
      key: "restored",
      label: "Restored"
    },

    {
      key: "normalized",
      label: "Normalized"
    },

    {
      key: "segmented",
      label: "Segmented"
    },

    {
      key: "vectorized",
      label: "Vectorized"
    }

  ];


  const outputEntries = [

    {
      key: "restored",
      label: "Restored Image"
    },

    {
      key: "normalized",
      label: "Normalized Image"
    },

    {
      key: "segmented",
      label: "Segmented Image"
    },

    {
      key: "edges",
      label: "Edge Map"
    },

    {
      key: "svg",
      label: "Vector SVG"
    },

    {
      key: "quality_report",
      label: "Quality Report"
    }

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

          <div>

            <div className="vh-modal-eyebrow">
              HERITAGE ASSET
            </div>

            <h2>
              {getDisplayName(asset)}
            </h2>

            <div className="vh-modal-id">
              {formatValue(asset.id)}
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
                className={
                  `vh-quality-badge ${qualityClass}`
                }
              >
                {quality}
              </div>

            </div>


            <div className="vh-quality-overview">


              {/* OVERALL SCORE */}

              <div className="vh-score-card">

                <span>
                  Overall Score
                </span>

                <strong>

                  {qualityScore !== null
                    ? qualityScore.toFixed(2)
                    : "—"}

                </strong>

                <small>
                  / 100
                </small>

              </div>


              {/* QUALITY METRICS */}

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
                        )}%`
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
                        )}%`
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
                        )}%`
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
                        )}%`
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

                <span>
                  Filename
                </span>

                <strong>
                  {formatValue(
                    asset.filename
                  )}
                </strong>

              </div>


              <div className="vh-meta-item">

                <span>
                  Category
                </span>

                <strong>
                  {formatValue(
                    asset.category
                  )}
                </strong>

              </div>


              <div className="vh-meta-item">

                <span>
                  Dynasty
                </span>

                <strong>
                  {formatValue(
                    asset.dynasty
                  )}
                </strong>

              </div>


              <div className="vh-meta-item">

                <span>
                  Period
                </span>

                <strong>
                  {formatValue(
                    asset.period
                  )}
                </strong>

              </div>


              <div className="vh-meta-item">

                <span>
                  Motif
                </span>

                <strong>
                  {formatValue(
                    asset.motif
                  )}
                </strong>

              </div>


              <div className="vh-meta-item">

                <span>
                  Region
                </span>

                <strong>
                  {formatValue(
                    asset.region
                  )}
                </strong>

              </div>


              <div className="vh-meta-item">

                <span>
                  Source
                </span>

                <strong>
                  {formatValue(
                    asset.source
                  )}
                </strong>

              </div>


              <div className="vh-meta-item">

                <span>
                  License
                </span>

                <strong>
                  {formatValue(
                    asset.license
                  )}
                </strong>

              </div>


            </div>

          </section>


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

                <span>
                  Width
                </span>

                <strong>
                  {formatValue(
                    technicalMetrics.width
                  )} px
                </strong>

              </div>


              <div className="vh-technical-item">

                <span>
                  Height
                </span>

                <strong>
                  {formatValue(
                    technicalMetrics.height
                  )} px
                </strong>

              </div>


              <div className="vh-technical-item">

                <span>
                  Format
                </span>

                <strong>
                  {formatValue(
                    asset.original?.format
                  )}
                </strong>

              </div>


              <div className="vh-technical-item">

                <span>
                  File Size
                </span>

                <strong>
                  {asset.original?.file_size_kb !== undefined
                    ? `${formatMetric(
                        asset.original.file_size_kb
                      )} KB`
                    : "—"}
                </strong>

              </div>


              <div className="vh-technical-item">

                <span>
                  Brightness
                </span>

                <strong>
                  {formatMetric(
                    technicalMetrics.brightness
                  )}
                </strong>

              </div>


              <div className="vh-technical-item">

                <span>
                  Contrast
                </span>

                <strong>
                  {formatMetric(
                    technicalMetrics.contrast
                  )}
                </strong>

              </div>


              <div className="vh-technical-item">

                <span>
                  Sharpness
                </span>

                <strong>
                  {formatMetric(
                    technicalMetrics.sharpness
                  )}
                </strong>

              </div>


            </div>

          </section>


          {/* ================= PROCESSING ================= */}

          <section className="vh-section">

            <div className="vh-section-header">

              <div>

                <span className="vh-section-label">
                  DATA PIPELINE
                </span>

                <h3>
                  Processing Status
                </h3>

              </div>

            </div>


            <div className="vh-processing-list">

              {processingStages.map(
                (stage, index) => {

                  const completed =
                    processing?.[stage.key] === true;


                  return (

                    <div
                      className="vh-processing-item"
                      key={stage.key}
                    >

                      <div
                        className={
                          `vh-processing-number ${
                            completed
                              ? "completed"
                              : ""
                          }`
                        }
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
                        className={
                          `vh-processing-status ${
                            completed
                              ? "completed"
                              : ""
                          }`
                        }
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

          </section>


          {/* ================= OUTPUTS ================= */}

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


            <div className="vh-output-list">

              {outputEntries.map(
                (output) => {

                  const path =
                    getOutputPath(
                      output.key
                    );


                  return (

                    <div
                      className="vh-output-item"
                      key={output.key}
                    >

                      <div>

                        <strong>
                          {output.label}
                        </strong>

                        <span>
                          {path
                            ? path
                            : "Not available"}
                        </span>

                      </div>


                      {path && (

                        <a
                          href={buildImageUrl(path)}
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


      <style>{`

        .vh-modal-overlay {
          position: fixed;
          inset: 0;
          z-index: 1000;

          display: flex;
          align-items: center;
          justify-content: center;

          padding: 30px;

          background: rgba(0, 0, 0, 0.72);

          backdrop-filter: blur(8px);
        }


        .vh-modal {
          width: min(1050px, 100%);
          max-height: 92vh;

          overflow: hidden;

          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 20px;

          background: #111;

          box-shadow:
            0 30px 80px rgba(0,0,0,0.55);
        }


        .vh-modal-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;

          padding: 24px 28px;

          border-bottom: 1px solid rgba(255,255,255,0.07);
        }


        .vh-modal-eyebrow,
        .vh-section-label {
          color: #8d6459;

          font-size: 9px;
          font-weight: 700;

          letter-spacing: 1.5px;
        }


        .vh-modal-header h2 {
          margin: 6px 0 3px;

          color: #eee;

          font-size: 20px;
          font-weight: 700;
        }


        .vh-modal-id {
          color: #555;

          font-size: 10px;
        }


        .vh-close-button {
          width: 34px;
          height: 34px;

          border: 0;
          border-radius: 9px;

          background: rgba(255,255,255,0.05);

          color: #888;

          font-size: 22px;

          cursor: pointer;
        }


        .vh-close-button:hover {
          background: rgba(255,255,255,0.09);
          color: #ddd;
        }


        .vh-modal-body {
          max-height: calc(92vh - 90px);

          overflow-y: auto;

          padding: 24px 28px 35px;
        }


        .vh-image-section {
          margin-bottom: 24px;
        }


        .vh-image-container {
          display: flex;
          align-items: center;
          justify-content: center;

          min-height: 280px;

          overflow: hidden;

          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 14px;

          background: #0b0b0b;
        }


        .vh-main-image {
          display: block;

          max-width: 100%;
          max-height: 480px;

          object-fit: contain;
        }


        .vh-image-placeholder {
          padding: 60px;

          color: #555;

          font-size: 12px;
        }


        .vh-section {
          margin-top: 18px;
          padding: 20px;

          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 14px;

          background: rgba(255,255,255,0.018);
        }


        .vh-section-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;

          margin-bottom: 18px;
        }


        .vh-section-header h3 {
          margin: 5px 0 0;

          color: #e6e6e6;

          font-size: 14px;
        }


        .vh-quality-badge {
          padding: 5px 10px;

          border-radius: 999px;

          font-size: 9px;
          font-weight: 700;
          letter-spacing: 0.5px;
        }


        .vh-quality-badge.good {
          background: rgba(101,197,141,0.12);
          color: #65c58d;
        }


        .vh-quality-badge.acceptable {
          background: rgba(203,167,93,0.12);
          color: #cba75d;
        }


        .vh-quality-badge.poor {
          background: rgba(201,111,111,0.12);
          color: #c96f6f;
        }


        .vh-quality-badge.unknown {
          background: rgba(255,255,255,0.06);
          color: #777;
        }


        .vh-quality-overview {
          display: grid;
          grid-template-columns: 180px 1fr;
          gap: 14px;
        }


        .vh-score-card {
          display: flex;
          flex-direction: column;
          justify-content: center;

          padding: 18px;

          border-radius: 12px;

          background: rgba(255,255,255,0.035);
        }


        .vh-score-card span {
          color: #666;
          font-size: 9px;
        }


        .vh-score-card strong {
          margin-top: 5px;

          color: #eee;

          font-size: 32px;
        }


        .vh-score-card small {
          color: #555;
          font-size: 9px;
        }


        .vh-quality-metrics {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 8px;
        }


        .vh-quality-metric {
          padding: 13px;

          border-radius: 10px;

          background: rgba(255,255,255,0.025);
        }


        .vh-quality-metric-header {
          display: flex;
          align-items: center;
          justify-content: space-between;

          margin-bottom: 10px;
        }


        .vh-quality-metric-header span {
          color: #666;

          font-size: 9px;
        }


        .vh-quality-metric-header strong {
          color: #ddd;

          font-size: 12px;
        }


        .vh-quality-track {
          width: 100%;
          height: 5px;

          overflow: hidden;

          border-radius: 999px;

          background: rgba(255,255,255,0.06);
        }


        .vh-quality-fill {
          height: 100%;

          border-radius: inherit;

          background: #a36a5d;

          transition:
            width 0.45s ease;
        }


        .vh-quality-flags,
        .vh-recommendation {
          margin-top: 18px;
        }


        .vh-subtitle {
          display: block;

          margin-bottom: 8px;

          color: #666;

          font-size: 9px;
          font-weight: 700;

          text-transform: uppercase;
          letter-spacing: 0.7px;
        }


        .vh-tag-list {
          display: flex;
          flex-wrap: wrap;
          gap: 7px;
        }


        .vh-tag {
          padding: 5px 8px;

          border: 1px solid rgba(201,111,111,0.2);
          border-radius: 6px;

          background: rgba(201,111,111,0.06);

          color: #c98282;

          font-size: 9px;
        }


        .vh-recommendation p {
          margin: 0;

          color: #888;

          font-size: 10px;
          line-height: 1.6;
        }


        .vh-metadata-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 8px;
        }


        .vh-meta-item,
        .vh-technical-item {
          min-width: 0;

          padding: 13px;

          border-radius: 9px;

          background: rgba(255,255,255,0.025);
        }


        .vh-meta-item span,
        .vh-technical-item span {
          display: block;

          margin-bottom: 6px;

          color: #5f5f5f;

          font-size: 9px;
        }


        .vh-meta-item strong,
        .vh-technical-item strong {
          display: block;

          overflow: hidden;

          color: #cfcfcf;

          font-size: 10px;

          text-overflow: ellipsis;
          white-space: nowrap;
        }


        .vh-technical-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 8px;
        }


        .vh-processing-list {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }


        .vh-processing-item {
          display: flex;
          align-items: center;

          padding: 11px 12px;

          border-radius: 9px;

          background: rgba(255,255,255,0.025);
        }


        .vh-processing-number {
          display: flex;
          align-items: center;
          justify-content: center;

          width: 26px;
          height: 26px;

          border-radius: 50%;

          background: rgba(255,255,255,0.06);

          color: #666;

          font-size: 9px;
          font-weight: 700;
        }


        .vh-processing-number.completed {
          background: rgba(101,197,141,0.12);
          color: #65c58d;
        }


        .vh-processing-info {
          display: flex;
          flex-direction: column;

          margin-left: 10px;
        }


        .vh-processing-info strong {
          color: #ccc;

          font-size: 10px;
        }


        .vh-processing-info span {
          margin-top: 3px;

          color: #555;

          font-size: 8px;
        }


        .vh-processing-status {
          margin-left: auto;

          color: #555;

          font-size: 8px;
          font-weight: 700;
          letter-spacing: 0.7px;
        }


        .vh-processing-status.completed {
          color: #65c58d;
        }


        .vh-output-list {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }


        .vh-output-item {
          display: flex;
          align-items: center;
          justify-content: space-between;

          gap: 15px;

          padding: 11px 12px;

          border-radius: 9px;

          background: rgba(255,255,255,0.025);
        }


        .vh-output-item > div {
          min-width: 0;
        }


        .vh-output-item strong {
          display: block;

          color: #ccc;

          font-size: 10px;
        }


        .vh-output-item span {
          display: block;

          max-width: 650px;

          margin-top: 3px;

          overflow: hidden;

          color: #555;

          font-size: 8px;

          text-overflow: ellipsis;
          white-space: nowrap;
        }


        .vh-output-link {
          flex-shrink: 0;

          padding: 6px 10px;

          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 6px;

          color: #999;

          font-size: 8px;

          text-decoration: none;
        }


        .vh-output-link:hover {
          border-color: rgba(163,106,93,0.5);
          color: #d29a8a;
        }


        .vh-process-section {
          margin-bottom: 0;
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
            grid-template-columns: repeat(2, 1fr);
          }


          .vh-metadata-grid,
          .vh-technical-grid {
            grid-template-columns: repeat(2, 1fr);
          }

        }


        @media (max-width: 500px) {

          .vh-quality-metrics {
            grid-template-columns: 1fr;
          }


          .vh-metadata-grid,
          .vh-technical-grid {
            grid-template-columns: 1fr;
          }

        }

      `}</style>

    </div>

  );

}


export default AssetModal;