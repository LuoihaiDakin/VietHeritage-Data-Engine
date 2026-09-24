import React from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

function getImageUrl(asset) {
  const imagePath =
    asset?.original?.path ||
    asset?.path ||
    "";

  if (!imagePath) {
    return "";
  }

  // Nếu API đã trả về URL đầy đủ
  if (
    imagePath.startsWith("http://") ||
    imagePath.startsWith("https://")
  ) {
    return imagePath;
  }

  // Chuẩn hóa path Windows
  const normalizedPath = imagePath
    .replaceAll("\\", "/")
    .replace(/^\/+/, "");

  return `${API_BASE_URL}/${normalizedPath}`;
}

function AssetModal({ asset, onClose }) {
  if (!asset) {
    return null;
  }

  const imageUrl = getImageUrl(asset);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content"
        onClick={(event) => event.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose}>
          ×
        </button>

        <div className="modal-image-container">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={asset.filename || "Heritage asset"}
              className="modal-image"
              onError={(event) => {
                console.error(
                  "Cannot load image:",
                  imageUrl
                );

                event.currentTarget.style.display = "none";
              }}
            />
          ) : (
            <div className="no-image">
              No image available
            </div>
          )}
        </div>

        <div className="modal-info">
          <h2>{asset.filename}</h2>

          <div className="info-row">
            <span>Category</span>
            <strong>
              {asset.category || "Unknown"}
            </strong>
          </div>

          <div className="info-row">
            <span>Quality</span>
            <strong>
              {asset.quality?.quality || "Unknown"}
            </strong>
          </div>

          {asset.quality?.score !== undefined && (
            <div className="info-row">
              <span>Quality Score</span>
              <strong>
                {asset.quality.score}
              </strong>
            </div>
          )}

          {asset.path && (
            <div className="info-row">
              <span>Path</span>
              <strong className="path-text">
                {asset.path}
              </strong>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AssetModal;