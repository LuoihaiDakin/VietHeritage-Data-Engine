function getQualityClass(quality) {
    if (!quality) {
        return "";
    }

    return quality.toLowerCase();
}


function getImageUrl(asset) {

    const rawPath =
        asset.path ||
        asset.original?.path ||
        "";

    if (!rawPath) {
        return "";
    }

    let imagePath = rawPath.replaceAll("\\", "/");

    // dataset/images/dong_ho/xxx.jpg
    imagePath = imagePath.replace(
        /^dataset\/images\//,
        ""
    );

    // images/dong_ho/xxx.jpg
    imagePath = imagePath.replace(
        /^images\//,
        ""
    );

    return (
        "http://127.0.0.1:8000/images/" +
        imagePath
    );
}


export default function AssetCard({
    asset,
    onClick
}) {

    const quality =
        asset.quality?.quality ||
        "UNKNOWN";

    const processing =
        asset.processing ||
        {};

    const processingOutputs =
        asset.processing_outputs ||
        {};

    const isProcessed =
        processing.restored &&
        processing.segmented &&
        processing.vectorized;

    const hasOutputs =
        Object.keys(processingOutputs).length > 0;

    const imageUrl =
        getImageUrl(asset);

    return (

        <div
            className="asset-card"
            onClick={() => onClick(asset)}
        >

            {/* IMAGE */}

            <div className="asset-image-wrapper">

                {imageUrl ? (

                    <img
                        src={imageUrl}
                        alt={
                            asset.filename ||
                            asset.asset_id ||
                            "Heritage asset"
                        }
                        className="asset-image"
                        onError={(event) => {
                            console.error(
                                "Image failed to load:",
                                imageUrl
                            );

                            event.currentTarget.style.display =
                                "none";
                        }}
                    />

                ) : (

                    <div className="asset-image-placeholder">
                        Image unavailable
                    </div>

                )}

            </div>


            {/* CONTENT */}

            <div className="asset-content">

                <h3>
                    {asset.filename ||
                        asset.asset_id ||
                        "Unknown asset"}
                </h3>


                <p className="asset-category">

                    {asset.category ||
                        "Unknown"}

                </p>


                {/* QUALITY */}

                <div className="asset-quality-row">

                    <span>
                        Quality:
                    </span>

                    <span
                        className={
                            `quality-badge ` +
                            getQualityClass(
                                quality
                            )
                        }
                    >
                        {quality}
                    </span>

                </div>


                {/* PROCESSING STATUS */}

                <div className="asset-processing-row">

                    <span>
                        Processing:
                    </span>

                    {isProcessed ? (

                        <span className="processing-badge processed">
                            Processed
                        </span>

                    ) : (

                        <span className="processing-badge pending">
                            Not Processed
                        </span>

                    )}

                </div>


                {/* OUTPUT COUNT */}

                {hasOutputs && (

                    <div className="asset-output-info">

                        Outputs available

                    </div>

                )}

            </div>

        </div>
    );
}