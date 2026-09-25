function getQualityClass(quality) {
    if (!quality) {
        return "";
    }

    return quality.toLowerCase();
}


export default function AssetCard({
    asset,
    onClick
}) {

    const quality =
        asset.quality?.quality ||
        "UNKNOWN";

    const processing =
        asset.processing || {};


    const isProcessed =
        processing.restored &&
        processing.segmented &&
        processing.vectorized;


    return (
        <div
            className="asset-card"
            onClick={() => onClick(asset)}
        >

            {/* IMAGE */}

            <div className="asset-image-wrapper">

                <img
                    src={
                        `http://127.0.0.1:8000/images/` +
                        asset.path
                            .replace(
                                /^images\//,
                                ""
                            )
                    }
                    alt={asset.filename}
                    className="asset-image"
                />

            </div>


            {/* CONTENT */}

            <div className="asset-content">

                <h3>
                    {asset.filename}
                </h3>


                <p className="asset-category">
                    {asset.category || "Unknown"}
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

                {asset.processing_outputs && (

                    <div className="asset-output-info">

                        Outputs available

                    </div>

                )}

            </div>

        </div>
    );
}