import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";


function convertToApiImageUrl(path) {
    if (!path) {
        return "";
    }

    let normalizedPath = String(path).replace(/\\/g, "/");

    normalizedPath = normalizedPath.replace(/^\/+/, "");

    if (normalizedPath.startsWith("dataset/images/")) {
        normalizedPath = normalizedPath.replace(
            "dataset/images/",
            ""
        );

        return `${API_BASE}/images/${normalizedPath}`;
    }

    if (normalizedPath.startsWith("images/")) {
        normalizedPath = normalizedPath.replace(
            "images/",
            ""
        );

        return `${API_BASE}/images/${normalizedPath}`;
    }

    if (normalizedPath.startsWith("outputs/")) {
        return `${API_BASE}/${normalizedPath}`;
    }

    if (normalizedPath.startsWith("http://") ||
        normalizedPath.startsWith("https://")) {
        return normalizedPath;
    }

    return `${API_BASE}/${normalizedPath}`;
}


function convertToProcessingPath(path) {
    if (!path) {
        return "";
    }

    let normalizedPath = String(path).replace(/\\/g, "/");

    normalizedPath = normalizedPath.replace(/^\/+/, "");

    if (
        normalizedPath.startsWith(
            "dataset/images/"
        )
    ) {
        return normalizedPath;
    }

    if (
        normalizedPath.startsWith(
            "images/"
        )
    ) {
        return `dataset/${normalizedPath}`;
    }

    return normalizedPath;
}


function formatNumber(value, decimals = 2) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
        return value;
    }

    return number.toFixed(decimals);
}


export default function ProcessPanel({ asset }) {

    const [processing, setProcessing] =
        useState(false);

    const [result, setResult] =
        useState(null);

    const [error, setError] =
        useState("");


    const handleProcess = async () => {

        setProcessing(true);
        setResult(null);
        setError("");


        try {

            const originalPath =
                asset.original?.path ||
                asset.path ||
                "";


            const imagePath =
                convertToProcessingPath(
                    originalPath
                );


            console.log(
                "Original path:",
                originalPath
            );

            console.log(
                "Processing path:",
                imagePath
            );


            const response =
                await fetch(
                    `${API_BASE}/process`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            image_path:
                                imagePath
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Processing failed"
                );
            }


            setResult(data);


        } catch (err) {

            console.error(
                "Processing error:",
                err
            );

            setError(
                err.message ||
                "Processing failed"
            );


        } finally {

            setProcessing(false);
        }
    };


    const outputs =
        result?.outputs || {};


    const metrics =
        result?.restored?.metrics || {};


    return (
        <div className="vh-process-panel">

            <style>{`

                .vh-process-panel {
                    width: 100%;
                    box-sizing: border-box;
                    color: #e8e8e8;
                    font-family:
                        Inter,
                        -apple-system,
                        BlinkMacSystemFont,
                        "Segoe UI",
                        sans-serif;
                }


                /* =====================================
                   PROCESS BUTTON
                ===================================== */

                .vh-process-button {
                    width: 100%;
                    border: none;
                    border-radius: 12px;
                    padding: 14px 20px;

                    background:
                        linear-gradient(
                            135deg,
                            #8f2f2f,
                            #b34a3d
                        );

                    color: white;
                    font-size: 14px;
                    font-weight: 700;

                    cursor: pointer;

                    transition:
                        transform 0.2s ease,
                        box-shadow 0.2s ease,
                        opacity 0.2s ease;

                    box-shadow:
                        0 8px 22px
                        rgba(143, 47, 47, 0.22);
                }


                .vh-process-button:hover:not(:disabled) {
                    transform: translateY(-1px);

                    box-shadow:
                        0 12px 28px
                        rgba(143, 47, 47, 0.30);
                }


                .vh-process-button:disabled {
                    opacity: 0.65;
                    cursor: wait;
                }


                /* =====================================
                   ERROR
                ===================================== */

                .vh-process-error {
                    margin-top: 16px;
                    padding: 14px 16px;

                    border-radius: 10px;

                    background: rgba(180, 55, 55, 0.12);

                    border:
                        1px solid
                        rgba(220, 80, 80, 0.30);

                    color: #ff9d9d;

                    font-size: 13px;
                    line-height: 1.5;
                }


                /* =====================================
                   RESULT CONTAINER
                ===================================== */

                .vh-result {
                    margin-top: 24px;

                    border:
                        1px solid
                        rgba(255, 255, 255, 0.09);

                    border-radius: 18px;

                    background:
                        linear-gradient(
                            180deg,
                            rgba(255,255,255,0.045),
                            rgba(255,255,255,0.018)
                        );

                    overflow: hidden;

                    box-shadow:
                        0 18px 50px
                        rgba(0, 0, 0, 0.22);
                }


                /* =====================================
                   RESULT HEADER
                ===================================== */

                .vh-result-header {
                    padding: 20px 22px;

                    border-bottom:
                        1px solid
                        rgba(255,255,255,0.08);

                    display: flex;
                    align-items: center;
                    justify-content: space-between;

                    gap: 16px;
                }


                .vh-result-title {
                    margin: 0;

                    font-size: 18px;
                    font-weight: 750;

                    letter-spacing: -0.2px;

                    color: #ffffff;
                }


                .vh-result-subtitle {
                    margin: 5px 0 0;

                    font-size: 12px;

                    color: #999;

                    line-height: 1.5;
                }


                .vh-status-badge {
                    flex-shrink: 0;

                    display: inline-flex;
                    align-items: center;
                    gap: 7px;

                    padding: 7px 11px;

                    border-radius: 999px;

                    background:
                        rgba(67, 180, 120, 0.10);

                    border:
                        1px solid
                        rgba(67, 180, 120, 0.25);

                    color: #78d8a3;

                    font-size: 11px;
                    font-weight: 700;
                }


                .vh-status-dot {
                    width: 7px;
                    height: 7px;

                    border-radius: 50%;

                    background: #5bd391;

                    box-shadow:
                        0 0 8px
                        rgba(91,211,145,0.7);
                }


                /* =====================================
                   OUTPUT SECTION
                ===================================== */

                .vh-output-section {
                    padding: 22px;
                }


                .vh-section-label {
                    margin: 0 0 14px;

                    color: #ffffff;

                    font-size: 13px;
                    font-weight: 700;

                    text-transform: uppercase;

                    letter-spacing: 0.8px;
                }


                .vh-output-grid {
                    display: grid;

                    grid-template-columns:
                        repeat(2, minmax(0, 1fr));

                    gap: 14px;
                }


                .vh-output-card {
                    min-width: 0;

                    overflow: hidden;

                    border:
                        1px solid
                        rgba(255,255,255,0.08);

                    border-radius: 13px;

                    background:
                        rgba(0,0,0,0.18);

                    transition:
                        border-color 0.2s ease,
                        transform 0.2s ease;
                }


                .vh-output-card:hover {
                    border-color:
                        rgba(255,255,255,0.18);

                    transform: translateY(-2px);
                }


                .vh-output-preview {
                    height: 180px;

                    display: flex;
                    align-items: center;
                    justify-content: center;

                    padding: 10px;

                    background:
                        #101010;

                    border-bottom:
                        1px solid
                        rgba(255,255,255,0.07);
                }


                .vh-output-preview img {
                    width: 100%;
                    height: 100%;

                    object-fit: contain;

                    display: block;
                }


                .vh-output-info {
                    padding: 12px 13px;
                }


                .vh-output-name {
                    margin: 0;

                    font-size: 13px;
                    font-weight: 700;

                    color: #f3f3f3;
                }


                .vh-output-description {
                    margin: 4px 0 0;

                    font-size: 11px;

                    color: #777;

                    line-height: 1.45;
                }


                /* =====================================
                   VECTOR
                ===================================== */

                .vh-vector-card {
                    margin-top: 14px;

                    border:
                        1px solid
                        rgba(180, 90, 65, 0.22);

                    border-radius: 14px;

                    overflow: hidden;

                    background:
                        linear-gradient(
                            135deg,
                            rgba(180,90,65,0.07),
                            rgba(255,255,255,0.018)
                        );
                }


                .vh-vector-preview {
                    height: 220px;

                    padding: 14px;

                    background:
                        #0c0c0c;

                    display: flex;
                    align-items: center;
                    justify-content: center;

                    border-bottom:
                        1px solid
                        rgba(255,255,255,0.07);
                }


                .vh-vector-preview img {
                    width: 100%;
                    height: 100%;

                    object-fit: contain;
                }


                .vh-vector-info {
                    padding: 15px;
                }


                .vh-vector-heading {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;

                    gap: 10px;
                }


                .vh-vector-title {
                    margin: 0;

                    color: #ffffff;

                    font-size: 14px;
                    font-weight: 700;
                }


                .vh-vector-tag {
                    padding: 5px 9px;

                    border-radius: 6px;

                    background:
                        rgba(180,90,65,0.14);

                    color: #dc8d78;

                    font-size: 10px;
                    font-weight: 700;

                    text-transform: uppercase;

                    letter-spacing: 0.5px;
                }


                .vh-vector-description {
                    margin: 7px 0 14px;

                    color: #888;

                    font-size: 11px;

                    line-height: 1.5;
                }


                .vh-primary-link {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;

                    padding: 9px 13px;

                    border-radius: 8px;

                    background:
                        rgba(255,255,255,0.08);

                    border:
                        1px solid
                        rgba(255,255,255,0.10);

                    color: #ffffff;

                    font-size: 11px;
                    font-weight: 650;

                    text-decoration: none;

                    transition:
                        background 0.2s ease,
                        border-color 0.2s ease;
                }


                .vh-primary-link:hover {
                    background:
                        rgba(255,255,255,0.13);

                    border-color:
                        rgba(255,255,255,0.18);
                }


                /* =====================================
                   QUALITY METRICS
                ===================================== */

                .vh-metrics-section {
                    margin-top: 24px;

                    padding-top: 22px;

                    border-top:
                        1px solid
                        rgba(255,255,255,0.08);
                }


                .vh-metrics-grid {
                    display: grid;

                    grid-template-columns:
                        repeat(2, minmax(0, 1fr));

                    gap: 10px;
                }


                .vh-metric {
                    padding: 13px;

                    border-radius: 10px;

                    background:
                        rgba(255,255,255,0.035);

                    border:
                        1px solid
                        rgba(255,255,255,0.06);
                }


                .vh-metric-label {
                    display: block;

                    margin-bottom: 6px;

                    color: #777;

                    font-size: 10px;

                    text-transform: uppercase;

                    letter-spacing: 0.7px;
                }


                .vh-metric-value {
                    display: block;

                    color: #f1f1f1;

                    font-size: 15px;
                    font-weight: 700;
                }


                /* =====================================
                   DOWNLOADS
                ===================================== */

                .vh-download-section {
                    margin-top: 24px;

                    padding-top: 22px;

                    border-top:
                        1px solid
                        rgba(255,255,255,0.08);
                }


                .vh-download-grid {
                    display: grid;

                    grid-template-columns:
                        repeat(2, minmax(0, 1fr));

                    gap: 9px;
                }


                .vh-download-button {
                    display: flex;
                    align-items: center;
                    justify-content: center;

                    min-height: 40px;

                    padding: 9px 10px;

                    border-radius: 9px;

                    background:
                        rgba(255,255,255,0.045);

                    border:
                        1px solid
                        rgba(255,255,255,0.08);

                    color: #d9d9d9;

                    font-size: 11px;
                    font-weight: 600;

                    text-decoration: none;

                    transition:
                        background 0.2s ease,
                        border-color 0.2s ease,
                        transform 0.2s ease;
                }


                .vh-download-button:hover {
                    background:
                        rgba(255,255,255,0.09);

                    border-color:
                        rgba(255,255,255,0.15);

                    transform: translateY(-1px);

                    color: #ffffff;
                }


                .vh-download-button.primary {
                    background:
                        rgba(180,90,65,0.12);

                    border-color:
                        rgba(180,90,65,0.25);

                    color: #e49a87;
                }


                .vh-download-button.primary:hover {
                    background:
                        rgba(180,90,65,0.20);

                    border-color:
                        rgba(180,90,65,0.38);
                }


                /* =====================================
                   RESPONSIVE
                ===================================== */

                @media (max-width: 650px) {

                    .vh-output-grid {
                        grid-template-columns: 1fr;
                    }

                    .vh-output-preview {
                        height: 200px;
                    }

                    .vh-result-header {
                        align-items: flex-start;
                        flex-direction: column;
                    }

                    .vh-download-grid {
                        grid-template-columns: 1fr;
                    }
                }

            `}</style>


            {/* =====================================
                PROCESS BUTTON
            ===================================== */}

            <button
                className="vh-process-button"
                onClick={handleProcess}
                disabled={processing}
            >
                {processing
                    ? "Processing image..."
                    : "Process Image"}
            </button>


            {/* =====================================
                ERROR
            ===================================== */}

            {error && (
                <div className="vh-process-error">
                    <strong>
                        Processing failed
                    </strong>

                    <div>
                        {error}
                    </div>
                </div>
            )}


            {/* =====================================
                RESULT
            ===================================== */}

            {result && (
                <div className="vh-result">

                    {/* HEADER */}

                    <div className="vh-result-header">

                        <div>
                            <h3 className="vh-result-title">
                                Processing Result
                            </h3>

                            <p className="vh-result-subtitle">
                                Processed outputs generated from
                                the heritage asset.
                            </p>
                        </div>


                        <div className="vh-status-badge">
                            <span className="vh-status-dot"></span>
                            Completed
                        </div>

                    </div>


                    {/* OUTPUTS */}

                    <div className="vh-output-section">

                        <h4 className="vh-section-label">
                            Generated Outputs
                        </h4>


                        <div className="vh-output-grid">

                            {/* RESTORED */}

                            <div className="vh-output-card">

                                <div className="vh-output-preview">

                                    {outputs.restored && (
                                        <img
                                            src={
                                                convertToApiImageUrl(
                                                    outputs.restored
                                                )
                                            }
                                            alt="Restored"
                                        />
                                    )}

                                </div>

                                <div className="vh-output-info">

                                    <p className="vh-output-name">
                                        Restored
                                    </p>

                                    <p className="vh-output-description">
                                        Cleaned and restored image
                                    </p>

                                </div>

                            </div>


                            {/* NORMALIZED */}

                            <div className="vh-output-card">

                                <div className="vh-output-preview">

                                    {outputs.normalized ? (
                                        <img
                                            src={
                                                convertToApiImageUrl(
                                                    outputs.normalized
                                                )
                                            }
                                            alt="Normalized"
                                        />
                                    ) : (
                                        <span>
                                            No preview
                                        </span>
                                    )}

                                </div>

                                <div className="vh-output-info">

                                    <p className="vh-output-name">
                                        Normalized
                                    </p>

                                    <p className="vh-output-description">
                                        Standardized image dimensions
                                    </p>

                                </div>

                            </div>


                            {/* SEGMENTED */}

                            <div className="vh-output-card">

                                <div className="vh-output-preview">

                                    {outputs.segmented && (
                                        <img
                                            src={
                                                convertToApiImageUrl(
                                                    outputs.segmented
                                                )
                                            }
                                            alt="Segmented"
                                        />
                                    )}

                                </div>

                                <div className="vh-output-info">

                                    <p className="vh-output-name">
                                        Segmented
                                    </p>

                                    <p className="vh-output-description">
                                        Extracted visual regions
                                    </p>

                                </div>

                            </div>


                            {/* EDGES */}

                            <div className="vh-output-card">

                                <div className="vh-output-preview">

                                    {outputs.edges && (
                                        <img
                                            src={
                                                convertToApiImageUrl(
                                                    outputs.edges
                                                )
                                            }
                                            alt="Edges"
                                        />
                                    )}

                                </div>

                                <div className="vh-output-info">

                                    <p className="vh-output-name">
                                        Edge Map
                                    </p>

                                    <p className="vh-output-description">
                                        Structural edge representation
                                    </p>

                                </div>

                            </div>

                        </div>


                        {/* =================================
                            VECTOR
                        ================================= */}

                        {outputs.svg && (
                            <div className="vh-vector-card">

                                <div className="vh-vector-preview">

                                    <img
                                        src={
                                            convertToApiImageUrl(
                                                outputs.svg
                                            )
                                        }
                                        alt="Vector pattern"
                                    />

                                </div>


                                <div className="vh-vector-info">

                                    <div className="vh-vector-heading">

                                        <h4 className="vh-vector-title">
                                            Vector Pattern
                                        </h4>

                                        <span className="vh-vector-tag">
                                            SVG
                                        </span>

                                    </div>


                                    <p className="vh-vector-description">
                                        Vector pattern generated from
                                        the segmented heritage mask.
                                    </p>


                                    <a
                                        className="vh-primary-link"
                                        href={
                                            convertToApiImageUrl(
                                                outputs.svg
                                            )
                                        }
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        Open SVG →
                                    </a>

                                </div>

                            </div>
                        )}


                        {/* =================================
                            QUALITY METRICS
                        ================================= */}

                        {result.restored?.metrics && (
                            <div className="vh-metrics-section">

                                <h4 className="vh-section-label">
                                    Quality Metrics
                                </h4>


                                <div className="vh-metrics-grid">

                                    <div className="vh-metric">

                                        <span className="vh-metric-label">
                                            Resolution
                                        </span>

                                        <span className="vh-metric-value">
                                            {metrics.width}
                                            {" × "}
                                            {metrics.height}
                                        </span>

                                    </div>


                                    <div className="vh-metric">

                                        <span className="vh-metric-label">
                                            Brightness
                                        </span>

                                        <span className="vh-metric-value">
                                            {
                                                formatNumber(
                                                    metrics.brightness
                                                )
                                            }
                                        </span>

                                    </div>


                                    <div className="vh-metric">

                                        <span className="vh-metric-label">
                                            Contrast
                                        </span>

                                        <span className="vh-metric-value">
                                            {
                                                formatNumber(
                                                    metrics.contrast
                                                )
                                            }
                                        </span>

                                    </div>


                                    <div className="vh-metric">

                                        <span className="vh-metric-label">
                                            Sharpness
                                        </span>

                                        <span className="vh-metric-value">
                                            {
                                                formatNumber(
                                                    metrics.sharpness
                                                )
                                            }
                                        </span>

                                    </div>

                                </div>

                            </div>
                        )}


                        {/* =================================
                            DOWNLOADS
                        ================================= */}

                        <div className="vh-download-section">

                            <h4 className="vh-section-label">
                                Downloads
                            </h4>


                            <div className="vh-download-grid">

                                {outputs.restored && (
                                    <a
                                        className="vh-download-button"
                                        href={
                                            convertToApiImageUrl(
                                                outputs.restored
                                            )
                                        }
                                        download
                                    >
                                        ↓ Restored
                                    </a>
                                )}


                                {outputs.normalized && (
                                    <a
                                        className="vh-download-button"
                                        href={
                                            convertToApiImageUrl(
                                                outputs.normalized
                                            )
                                        }
                                        download
                                    >
                                        ↓ Normalized
                                    </a>
                                )}


                                {outputs.segmented && (
                                    <a
                                        className="vh-download-button"
                                        href={
                                            convertToApiImageUrl(
                                                outputs.segmented
                                            )
                                        }
                                        download
                                    >
                                        ↓ Segmented
                                    </a>
                                )}


                                {outputs.edges && (
                                    <a
                                        className="vh-download-button"
                                        href={
                                            convertToApiImageUrl(
                                                outputs.edges
                                            )
                                        }
                                        download
                                    >
                                        ↓ Edges
                                    </a>
                                )}


                                {outputs.svg && (
                                    <a
                                        className="vh-download-button primary"
                                        href={
                                            convertToApiImageUrl(
                                                outputs.svg
                                            )
                                        }
                                        download
                                    >
                                        ↓ SVG Vector
                                    </a>
                                )}

                            </div>

                        </div>

                    </div>

                </div>
            )}

        </div>
    );
}