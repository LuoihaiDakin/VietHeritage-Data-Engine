import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";


function convertToApiImageUrl(path) {
    if (!path) {
        return "";
    }

    let normalizedPath = path.replace(/\\/g, "/");

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

    if (normalizedPath.startsWith("/images/")) {
        return `${API_BASE}${normalizedPath}`;
    }

    return `${API_BASE}/${normalizedPath}`;
}


function convertToProcessingPath(path) {
    if (!path) {
        return "";
    }

    let normalizedPath = path.replace(/\\/g, "/");

    normalizedPath = normalizedPath.replace(/^\/+/, "");

    /*
        API cần:

        dataset/images/...
    */

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


export default function ProcessPanel({
    asset
}) {
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
                err.message
            );

        } finally {

            setProcessing(false);
        }
    };


    return (
        <div className="process-panel">

            {/* PROCESS BUTTON */}

            <button
                className="process-button"
                onClick={handleProcess}
                disabled={processing}
            >
                {processing
                    ? "Processing..."
                    : "Process Image"}
            </button>


            {/* ERROR */}

            {error && (
                <div className="process-error">
                    {error}
                </div>
            )}


            {/* RESULT */}

            {result && (

                <div className="process-result">

                    <h3>
                        Processing Result
                    </h3>


                    {/* OUTPUT IMAGES */}

                    <div className="result-grid">


                        {/* RESTORED */}

                        <div className="result-item">

                            <h4>
                                Restored
                            </h4>

                            <img
                                src={
                                    convertToApiImageUrl(
                                        result.outputs
                                            ?.restored
                                    )
                                }
                                alt="Restored"
                            />

                        </div>


                        {/* SEGMENTED */}

                        <div className="result-item">

                            <h4>
                                Segmented
                            </h4>

                            <img
                                src={
                                    convertToApiImageUrl(
                                        result.outputs
                                            ?.segmented
                                    )
                                }
                                alt="Segmented"
                            />

                        </div>


                        {/* EDGES */}

                        <div className="result-item">

                            <h4>
                                Edges
                            </h4>

                            <img
                                src={
                                    convertToApiImageUrl(
                                        result.outputs
                                            ?.edges
                                    )
                                }
                                alt="Edges"
                            />

                        </div>

                    </div>


                    {/* DOWNLOAD LINKS */}

                    <div className="result-links">

                        <a
                            href={
                                convertToApiImageUrl(
                                    result.outputs
                                        ?.svg
                                )
                            }
                            target="_blank"
                            rel="noreferrer"
                        >
                            Open SVG
                        </a>


                        <a
                            href={
                                convertToApiImageUrl(
                                    result.outputs
                                        ?.restored
                                )
                            }
                            download
                        >
                            Download Restored
                        </a>


                        <a
                            href={
                                convertToApiImageUrl(
                                    result.outputs
                                        ?.segmented
                                )
                            }
                            download
                        >
                            Download Segmented
                        </a>

                    </div>


                    {/* QUALITY METRICS */}

                    {result.restored?.metrics && (

                        <div className="metrics">

                            <h4>
                                Quality Metrics
                            </h4>


                            <p>
                                <strong>
                                    Resolution:
                                </strong>{" "}
                                {
                                    result.restored
                                        .metrics
                                        .width
                                }
                                {" × "}
                                {
                                    result.restored
                                        .metrics
                                        .height
                                }
                            </p>


                            <p>
                                <strong>
                                    Brightness:
                                </strong>{" "}
                                {
                                    result.restored
                                        .metrics
                                        .brightness
                                }
                            </p>


                            <p>
                                <strong>
                                    Contrast:
                                </strong>{" "}
                                {
                                    result.restored
                                        .metrics
                                        .contrast
                                }
                            </p>


                            <p>
                                <strong>
                                    Sharpness:
                                </strong>{" "}
                                {
                                    result.restored
                                        .metrics
                                        .sharpness
                                }
                            </p>

                        </div>

                    )}

                </div>

            )}

        </div>
    );
}