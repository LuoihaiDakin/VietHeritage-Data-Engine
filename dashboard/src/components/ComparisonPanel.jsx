import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function resolveImageUrl(path) {
    if (!path) return "";

    let cleanPath = String(path).replaceAll("\\", "/");

    // Already a complete URL
    if (
        cleanPath.startsWith("http://") ||
        cleanPath.startsWith("https://")
    ) {
        return cleanPath;
    }

    // Already an API path
    if (cleanPath.startsWith("/images/")) {
        return `${API_BASE}${cleanPath}`;
    }

    if (cleanPath.startsWith("/outputs/")) {
        return `${API_BASE}${cleanPath}`;
    }

    // dataset/images/...
    if (cleanPath.startsWith("dataset/images/")) {
        cleanPath = cleanPath.replace(
            "dataset/images/",
            "images/"
        );

        return `${API_BASE}/${cleanPath}`;
    }

    // ./dataset/images/...
    if (cleanPath.startsWith("./dataset/images/")) {
        cleanPath = cleanPath.replace(
            "./dataset/images/",
            "images/"
        );

        return `${API_BASE}/${cleanPath}`;
    }

    // outputs/...
    if (cleanPath.startsWith("outputs/")) {
        return `${API_BASE}/${cleanPath}`;
    }

    // ./outputs/...
    if (cleanPath.startsWith("./outputs/")) {
        cleanPath = cleanPath.replace("./", "");
        return `${API_BASE}/${cleanPath}`;
    }

    // images/...
    if (cleanPath.startsWith("images/")) {
        return `${API_BASE}/${cleanPath}`;
    }

    // Fallback
    return `${API_BASE}/${cleanPath.replace(/^\/+/, "")}`;
}


function formatScore(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
        return "—";
    }

    return number.toFixed(2);
}


function QualityBadge({ quality }) {
    const normalized = String(quality || "UNKNOWN").toUpperCase();

    let background = "#eef2f7";
    let color = "#4b5563";

    if (normalized === "GOOD") {
        background = "#dcfce7";
        color = "#15803d";
    } else if (normalized === "ACCEPTABLE") {
        background = "#fef3c7";
        color = "#b45309";
    } else if (normalized === "POOR") {
        background = "#fee2e2";
        color = "#dc2626";
    }

    return (
        <span
            style={{
                display: "inline-flex",
                alignItems: "center",
                padding: "4px 10px",
                borderRadius: "999px",
                background,
                color,
                fontSize: "12px",
                fontWeight: 700,
            }}
        >
            {normalized}
        </span>
    );
}


function MetricRow({ label, before, after }) {
    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "1fr 120px 120px",
                alignItems: "center",
                padding: "10px 0",
                borderBottom: "1px solid #edf0f3",
                fontSize: "14px",
            }}
        >
            <div
                style={{
                    color: "#374151",
                    fontWeight: 500,
                }}
            >
                {label}
            </div>

            <div
                style={{
                    textAlign: "right",
                    color: "#6b7280",
                }}
            >
                {before}
            </div>

            <div
                style={{
                    textAlign: "right",
                    color: "#111827",
                    fontWeight: 600,
                }}
            >
                {after}
            </div>
        </div>
    );
}


export default function ComparisonPanel({ asset }) {
    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    async function loadComparison() {
        if (!asset?.id) {
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            setError("");

            const response = await fetch(
                `${API_BASE}/assets/${asset.id}/comparison`
            );

            if (!response.ok) {
                throw new Error(
                    "Comparison data is not available yet."
                );
            }

            const data = await response.json();

            setComparison(data);
        } catch (err) {
            console.error("Comparison loading error:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }


    useEffect(() => {
        loadComparison();
    }, [asset?.id]);


    if (loading) {
        return (
            <section
                style={{
                    marginTop: "24px",
                    padding: "24px",
                    border: "1px solid #e5e7eb",
                    borderRadius: "14px",
                    background: "#ffffff",
                }}
            >
                <h2
                    style={{
                        margin: 0,
                        fontSize: "20px",
                        color: "#111827",
                    }}
                >
                    AI Processing Comparison
                </h2>

                <p
                    style={{
                        marginTop: "8px",
                        color: "#6b7280",
                    }}
                >
                    Loading comparison...
                </p>
            </section>
        );
    }


    if (!comparison) {
        return (
            <section
                style={{
                    marginTop: "24px",
                    padding: "24px",
                    border: "1px solid #e5e7eb",
                    borderRadius: "14px",
                    background: "#ffffff",
                }}
            >
                <h2
                    style={{
                        margin: 0,
                        fontSize: "20px",
                        color: "#111827",
                    }}
                >
                    AI Processing Comparison
                </h2>

                <p
                    style={{
                        marginTop: "8px",
                        color: "#6b7280",
                    }}
                >
                    {error || "No comparison data available."}
                </p>

                <button
                    onClick={loadComparison}
                    style={{
                        marginTop: "12px",
                        padding: "8px 14px",
                        border: "1px solid #d1d5db",
                        borderRadius: "8px",
                        background: "#ffffff",
                        cursor: "pointer",
                        fontWeight: 600,
                    }}
                >
                    Refresh
                </button>
            </section>
        );
    }


    const before =
        comparison.before ||
        comparison.original ||
        comparison.reference ||
        {};

    const after =
        comparison.after ||
        comparison.processed ||
        {};


    const beforeQuality =
        before.quality ||
        before.classification ||
        comparison.quality_change?.before_quality ||
        "UNKNOWN";

    const afterQuality =
        after.quality ||
        after.classification ||
        comparison.quality_change?.after_quality ||
        "UNKNOWN";


    const beforeScore =
        before.score ??
        before.overall_score ??
        comparison.quality_change?.before_score;

    const afterScore =
        after.score ??
        after.overall_score ??
        comparison.quality_change?.after_score;


    const beforeMetrics =
        before.metrics ||
        before.technical_metrics ||
        {};

    const afterMetrics =
        after.metrics ||
        after.technical_metrics ||
        {};


    const previewPath =
        comparison.files?.preview ||
        comparison.files?.comparison_preview ||
        comparison.comparison_preview;


    const originalPath =
        comparison.files?.original ||
        comparison.files?.before ||
        comparison.original_path;


    const processedPath =
        comparison.files?.processed ||
        comparison.files?.after ||
        comparison.processed_path;


    const originalUrl = resolveImageUrl(originalPath);
    const processedUrl = resolveImageUrl(processedPath);
    const previewUrl = resolveImageUrl(previewPath);


    const scoreDelta =
        comparison.quality_change?.score_delta ??
        (
            beforeScore !== undefined &&
            afterScore !== undefined
                ? Number(afterScore) - Number(beforeScore)
                : null
        );


    return (
        <section
            style={{
                marginTop: "24px",
                padding: "24px",
                border: "1px solid #e5e7eb",
                borderRadius: "14px",
                background: "#ffffff",
            }}
        >
            {/* Header */}
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: "16px",
                    marginBottom: "20px",
                }}
            >
                <div>
                    <h2
                        style={{
                            margin: 0,
                            fontSize: "20px",
                            color: "#111827",
                        }}
                    >
                        AI Processing Comparison
                    </h2>

                    <p
                        style={{
                            margin: "6px 0 0",
                            color: "#6b7280",
                            fontSize: "14px",
                        }}
                    >
                        Original image compared with the final
                        processed image.
                    </p>
                </div>

                <div
                    style={{
                        padding: "8px 12px",
                        borderRadius: "9px",
                        background: "#f3f4f6",
                        color: "#6b7280",
                        fontSize: "13px",
                    }}
                >
                    Final:{" "}
                    <strong style={{ color: "#111827" }}>
                        normalized
                    </strong>
                </div>
            </div>


            {/* Before / After cards */}
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns:
                        "minmax(0, 1fr) 42px minmax(0, 1fr)",
                    gap: "18px",
                    alignItems: "center",
                }}
            >
                {/* ORIGINAL */}
                <div
                    style={{
                        border: "1px solid #dfe3e8",
                        borderRadius: "14px",
                        padding: "14px",
                        background: "#ffffff",
                    }}
                >
                    <div
                        style={{
                            fontSize: "16px",
                            fontWeight: 700,
                            color: "#1f2937",
                            marginBottom: "10px",
                        }}
                    >
                        Original
                    </div>

                    <div
                        style={{
                            height: "280px",
                            borderRadius: "10px",
                            overflow: "hidden",
                            background: "#f3f4f6",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}
                    >
                        {originalUrl ? (
                            <img
                                src={originalUrl}
                                alt="Original"
                                style={{
                                    width: "100%",
                                    height: "100%",
                                    objectFit: "contain",
                                    display: "block",
                                }}
                                onError={(event) => {
                                    console.error(
                                        "Original image failed:",
                                        originalUrl
                                    );

                                    event.currentTarget.style.display =
                                        "none";
                                }}
                            />
                        ) : (
                            <span
                                style={{
                                    color: "#9ca3af",
                                    fontSize: "14px",
                                }}
                            >
                                Original image unavailable
                            </span>
                        )}
                    </div>

                    <div
                        style={{
                            marginTop: "12px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                        }}
                    >
                        <QualityBadge quality={beforeQuality} />

                        <strong
                            style={{
                                fontSize: "16px",
                                color: "#111827",
                            }}
                        >
                            {formatScore(beforeScore)}
                        </strong>
                    </div>
                </div>


                {/* ARROW */}
                <div
                    style={{
                        textAlign: "center",
                        fontSize: "28px",
                        color: "#6b7280",
                    }}
                >
                    →
                </div>


                {/* PROCESSED */}
                <div
                    style={{
                        border: "1px solid #dfe3e8",
                        borderRadius: "14px",
                        padding: "14px",
                        background: "#ffffff",
                    }}
                >
                    <div
                        style={{
                            fontSize: "16px",
                            fontWeight: 700,
                            color: "#1f2937",
                            marginBottom: "10px",
                        }}
                    >
                        Processed
                    </div>

                    <div
                        style={{
                            height: "280px",
                            borderRadius: "10px",
                            overflow: "hidden",
                            background: "#f3f4f6",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}
                    >
                        {processedUrl ? (
                            <img
                                src={processedUrl}
                                alt="Processed"
                                style={{
                                    width: "100%",
                                    height: "100%",
                                    objectFit: "contain",
                                    display: "block",
                                }}
                                onError={(event) => {
                                    console.error(
                                        "Processed image failed:",
                                        processedUrl
                                    );

                                    event.currentTarget.style.display =
                                        "none";
                                }}
                            />
                        ) : (
                            <span
                                style={{
                                    color: "#9ca3af",
                                    fontSize: "14px",
                                }}
                            >
                                Processed image unavailable
                            </span>
                        )}
                    </div>

                    <div
                        style={{
                            marginTop: "12px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                        }}
                    >
                        <QualityBadge quality={afterQuality} />

                        <strong
                            style={{
                                fontSize: "16px",
                                color: "#111827",
                            }}
                        >
                            {formatScore(afterScore)}
                        </strong>
                    </div>
                </div>
            </div>


            {/* Score change */}
            {scoreDelta !== null && (
                <div
                    style={{
                        marginTop: "18px",
                        padding: "14px 16px",
                        borderRadius: "10px",
                        background: "#f8fafc",
                        border: "1px solid #e5e7eb",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                    }}
                >
                    <span
                        style={{
                            color: "#4b5563",
                            fontWeight: 600,
                        }}
                    >
                        Quality score change
                    </span>

                    <strong
                        style={{
                            fontSize: "18px",
                            color:
                                Number(scoreDelta) >= 0
                                    ? "#15803d"
                                    : "#dc2626",
                        }}
                    >
                        {Number(scoreDelta) >= 0 ? "+" : ""}
                        {formatScore(scoreDelta)}
                    </strong>
                </div>
            )}


            {/* Metrics */}
            <div
                style={{
                    marginTop: "24px",
                }}
            >
                <h3
                    style={{
                        margin: "0 0 10px",
                        fontSize: "16px",
                        color: "#111827",
                    }}
                >
                    Technical Comparison
                </h3>

                <div
                    style={{
                        borderTop: "1px solid #edf0f3",
                    }}
                >
                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "1fr 120px 120px",
                            padding: "10px 0",
                            fontSize: "12px",
                            fontWeight: 700,
                            color: "#9ca3af",
                        }}
                    >
                        <div>Metric</div>
                        <div style={{ textAlign: "right" }}>
                            BEFORE
                        </div>
                        <div style={{ textAlign: "right" }}>
                            AFTER
                        </div>
                    </div>

                    <MetricRow
                        label="Width"
                        before={
                            beforeMetrics.width
                                ? `${beforeMetrics.width}px`
                                : "—"
                        }
                        after={
                            afterMetrics.width
                                ? `${afterMetrics.width}px`
                                : "—"
                        }
                    />

                    <MetricRow
                        label="Height"
                        before={
                            beforeMetrics.height
                                ? `${beforeMetrics.height}px`
                                : "—"
                        }
                        after={
                            afterMetrics.height
                                ? `${afterMetrics.height}px`
                                : "—"
                        }
                    />

                    <MetricRow
                        label="Brightness"
                        before={formatScore(
                            beforeMetrics.brightness
                        )}
                        after={formatScore(
                            afterMetrics.brightness
                        )}
                    />

                    <MetricRow
                        label="Contrast"
                        before={formatScore(
                            beforeMetrics.contrast
                        )}
                        after={formatScore(
                            afterMetrics.contrast
                        )}
                    />

                    <MetricRow
                        label="Sharpness"
                        before={formatScore(
                            beforeMetrics.sharpness
                        )}
                        after={formatScore(
                            afterMetrics.sharpness
                        )}
                    />
                </div>
            </div>


            {/* Similarity */}
            {comparison.similarity && (
                <div
                    style={{
                        marginTop: "24px",
                    }}
                >
                    <h3
                        style={{
                            margin: "0 0 10px",
                            fontSize: "16px",
                            color: "#111827",
                        }}
                    >
                        Image Similarity
                    </h3>

                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "repeat(2, minmax(0, 1fr))",
                            gap: "12px",
                        }}
                    >
                        <div
                            style={{
                                padding: "14px",
                                borderRadius: "10px",
                                background: "#f8fafc",
                                border: "1px solid #e5e7eb",
                            }}
                        >
                            <div
                                style={{
                                    fontSize: "12px",
                                    color: "#6b7280",
                                }}
                            >
                                SSIM
                            </div>

                            <strong
                                style={{
                                    display: "block",
                                    marginTop: "4px",
                                    fontSize: "20px",
                                    color: "#111827",
                                }}
                            >
                                {formatScore(
                                    comparison.similarity.ssim
                                )}
                            </strong>
                        </div>

                        <div
                            style={{
                                padding: "14px",
                                borderRadius: "10px",
                                background: "#f8fafc",
                                border: "1px solid #e5e7eb",
                            }}
                        >
                            <div
                                style={{
                                    fontSize: "12px",
                                    color: "#6b7280",
                                }}
                            >
                                PSNR
                            </div>

                            <strong
                                style={{
                                    display: "block",
                                    marginTop: "4px",
                                    fontSize: "20px",
                                    color: "#111827",
                                }}
                            >
                                {comparison.similarity.psnr_db !=
                                null
                                    ? `${formatScore(
                                          comparison.similarity
                                              .psnr_db
                                      )} dB`
                                    : "—"}
                            </strong>
                        </div>
                    </div>
                </div>
            )}


            {/* Preview */}
            {previewUrl && (
                <div
                    style={{
                        marginTop: "24px",
                    }}
                >
                    <h3
                        style={{
                            margin: "0 0 10px",
                            fontSize: "16px",
                            color: "#111827",
                        }}
                    >
                        Side-by-Side Preview
                    </h3>

                    <div
                        style={{
                            borderRadius: "10px",
                            overflow: "hidden",
                            border: "1px solid #e5e7eb",
                            background: "#f3f4f6",
                        }}
                    >
                        <img
                            src={previewUrl}
                            alt="AI processing comparison"
                            style={{
                                width: "100%",
                                display: "block",
                            }}
                        />
                    </div>
                </div>
            )}


            {/* Refresh */}
            <div
                style={{
                    marginTop: "18px",
                    textAlign: "right",
                }}
            >
                <button
                    onClick={loadComparison}
                    style={{
                        padding: "8px 14px",
                        border: "1px solid #d1d5db",
                        borderRadius: "8px",
                        background: "#ffffff",
                        color: "#374151",
                        cursor: "pointer",
                        fontWeight: 600,
                    }}
                >
                    Refresh Comparison
                </button>
            </div>
        </section>
    );
}