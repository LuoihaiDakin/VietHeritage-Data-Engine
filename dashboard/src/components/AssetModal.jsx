import ProcessPanel from "./ProcessPanel";

const API_BASE = "http://127.0.0.1:8000";

function buildImageUrl(path) {
    if (!path) {
        return "";
    }

    // Already full URL
    if (
        path.startsWith("http://") ||
        path.startsWith("https://")
    ) {
        return path;
    }

    // Normalize Windows slashes
    let normalizedPath = path.replace(/\\/g, "/");

    // Remove leading slash
    normalizedPath = normalizedPath.replace(/^\/+/, "");

    /*
        Possible paths:

        dataset/images/dong_ho/dong_ho_003.jpg
        images/dong_ho/dong_ho_003.jpg
        /images/dong_ho/dong_ho_003.jpg
    */

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

    return `${API_BASE}/${normalizedPath}`;
}

export default function AssetModal({
    asset,
    onClose
}) {
    if (!asset) {
        return null;
    }

    const imagePath =
        asset.original?.path ||
        asset.path ||
        "";

    const imageUrl = buildImageUrl(imagePath);

    const quality =
        asset.quality?.quality ||
        "UNKNOWN";

    const sharpness =
        asset.quality?.sharpness ??
        asset.quality?.score ??
        "-";

    return (
        <div
            className="modal-overlay"
            onClick={onClose}
        >
            <div
                className="modal"
                onClick={(event) =>
                    event.stopPropagation()
                }
            >

                {/* HEADER */}
                <div className="modal-header">

                    <div>
                        <h2>
                            {asset.filename || "Asset"}
                        </h2>

                        <p>
                            Heritage Digital Asset
                        </p>
                    </div>

                    <button
                        className="modal-close"
                        onClick={onClose}
                    >
                        ×
                    </button>

                </div>


                {/* ORIGINAL IMAGE */}
                <div className="modal-image-container">

                    {imageUrl ? (
                        <img
                            src={imageUrl}
                            alt={
                                asset.filename ||
                                "Heritage asset"
                            }
                            className="modal-image"
                        />
                    ) : (
                        <div className="image-placeholder">
                            No image available
                        </div>
                    )}

                </div>


                {/* ASSET INFORMATION */}
                <div className="asset-info">

                    <div className="info-item">

                        <span className="info-label">
                            Filename
                        </span>

                        <span className="info-value">
                            {asset.filename || "-"}
                        </span>

                    </div>


                    <div className="info-item">

                        <span className="info-label">
                            Category
                        </span>

                        <span className="info-value">
                            {asset.category || "-"}
                        </span>

                    </div>


                    <div className="info-item">

                        <span className="info-label">
                            Quality
                        </span>

                        <span
                            className={`quality-badge ${quality.toLowerCase()}`}
                        >
                            {quality}
                        </span>

                    </div>


                    <div className="info-item">

                        <span className="info-label">
                            Sharpness
                        </span>

                        <span className="info-value">
                            {sharpness}
                        </span>

                    </div>

                </div>


                {/* PROCESSING */}
                <ProcessPanel
                    asset={asset}
                />

            </div>
        </div>
    );
}