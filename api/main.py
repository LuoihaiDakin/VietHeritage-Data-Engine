import os
import json
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from processing.pipeline import process_image

# ========================================
# PROJECT PATH
# ========================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CATALOG_PATH = os.path.join(
    PROJECT_ROOT,
    "metadata",
    "heritage_catalog.json"
)


# ========================================
# FASTAPI APP
# ========================================

app = FastAPI(
    title="VietHeritage Data Engine API",
    description=(
        "API for searching and accessing "
        "Vietnamese heritage digital assets."
    ),
    version="1.0.0"
)
class ProcessRequest(BaseModel):
    image_path: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATASET_DIR = os.path.join(
    PROJECT_ROOT,
    "dataset"
)

OUTPUTS_DIR = os.path.join(
    PROJECT_ROOT,
    "outputs"
)

IMAGE_DIR = os.path.join(
    DATASET_DIR,
    "images"
)

app.mount(
    "/images",
    StaticFiles(directory=IMAGE_DIR),
    name="images"
)

OUTPUTS_DIR = os.path.join(
    PROJECT_ROOT,
    "outputs"
)

app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUTS_DIR),
    name="outputs"
)

# ========================================
# CORS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# LOAD CATALOG
# ========================================

def load_catalog():

    if not os.path.exists(CATALOG_PATH):
        return []

    try:
        with open(
            CATALOG_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"ERROR loading catalog: {error}"
        )

        return []


# ========================================
# SAVE CATALOG
# ========================================

def save_catalog(catalog):
    """
    Save the current catalog back to
    heritage_catalog.json.
    """

    with open(
        CATALOG_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            catalog,
            file,
            indent=4,
            ensure_ascii=False
        )


# ========================================
# FIND ASSET IN CATALOG
# ========================================

def find_asset_index(catalog, input_path):
    """
    Find the catalog asset corresponding
    to the processed image.
    """

    normalized_input = os.path.normpath(
        input_path
    ).lower()

    input_filename = os.path.basename(
        normalized_input
    ).lower()


    for index, item in enumerate(catalog):

        # --------------------------------
        # Check filename
        # --------------------------------

        catalog_filename = str(
            item.get("filename", "")
        ).lower()

        if (
            catalog_filename
            and catalog_filename == input_filename
        ):
            return index


        # --------------------------------
        # Check original.path
        # --------------------------------

        original = item.get(
            "original",
            {}
        )

        if isinstance(original, dict):

            original_path = str(
                original.get("path", "")
            )

            if original_path:

                normalized_original = (
                    os.path.normpath(
                        original_path
                    ).lower()
                )

                if (
                    normalized_original
                    == normalized_input
                ):
                    return index


        # --------------------------------
        # Check item.path
        # --------------------------------

        item_path = str(
            item.get("path", "")
        )

        if item_path:

            normalized_item_path = (
                os.path.normpath(
                    item_path
                ).lower()
            )

            if (
                normalized_item_path
                == normalized_input
            ):
                return index


    return None

# ========================================
# HELPER
# ========================================

def normalize_text(value):

    if value is None:
        return ""

    return str(value).strip().lower()


def get_quality(item):

    quality = item.get("quality")

    if not isinstance(quality, dict):
        return None

    return quality.get("quality")


def get_quality_score(item):

    quality = item.get("quality")

    if not isinstance(quality, dict):
        return None

    return quality.get("overall_score")


# ========================================
# ROOT
# ========================================

@app.get("/")
def root():

    return {
        "project": "VietHeritage Data Engine",
        "status": "running",
        "version": "1.0.0"
    }


# ========================================
# HEALTH CHECK
# ========================================

@app.get("/health")
def health():

    catalog = load_catalog()

    return {
        "status": "healthy",
        "catalog_loaded": len(catalog) > 0,
        "total_assets": len(catalog)
    }


# ========================================
# GET ALL ASSETS
# ========================================

@app.get("/assets")
def get_assets(
    limit: int = Query(
        50,
        ge=1,
        le=1000
    ),
    offset: int = Query(
        0,
        ge=0
    )
):

    catalog = load_catalog()

    total = len(catalog)

    results = catalog[
        offset:
        offset + limit
    ]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": results
    }


# ========================================
# GET ASSET BY ID
# ========================================

@app.get("/assets/{asset_id}")
def get_asset(asset_id: str):

    catalog = load_catalog()

    for item in catalog:

        if item.get("id") == asset_id:

            return item

    return {
        "error": "Asset not found",
        "asset_id": asset_id
    }


# ========================================
# SEARCH
# ========================================

@app.get("/search")
def search_assets(
    keyword: str | None = None,
    category: str | None = None,
    dynasty: str | None = None,
    period: str | None = None,
    motif: str | None = None,
    region: str | None = None,
    quality: str | None = None,
    vectorized: bool = False,
    segmented: bool = False,
    normalized: bool = False,
    restored: bool = False,
    preprocessed: bool = False
):

    catalog = load_catalog()

    results = []

    for item in catalog:

        # -----------------------------
        # KEYWORD
        # -----------------------------

        if keyword:

            searchable_text = " ".join([
                normalize_text(
                    item.get("filename")
                ),
                normalize_text(
                    item.get("category")
                ),
                normalize_text(
                    item.get("period")
                ),
                normalize_text(
                    item.get("dynasty")
                ),
                normalize_text(
                    item.get("motif")
                ),
                normalize_text(
                    item.get("region")
                ),
                normalize_text(
                    item.get("source")
                )
            ])

            if (
                normalize_text(keyword)
                not in searchable_text
            ):
                continue

        # -----------------------------
        # CATEGORY
        # -----------------------------

        if category:

            if (
                normalize_text(
                    item.get("category")
                )
                != normalize_text(category)
            ):
                continue

        # -----------------------------
        # DYNASTY
        # -----------------------------

        if dynasty:

            if (
                normalize_text(
                    item.get("dynasty")
                )
                != normalize_text(dynasty)
            ):
                continue

        # -----------------------------
        # PERIOD
        # -----------------------------

        if period:

            if (
                normalize_text(
                    item.get("period")
                )
                != normalize_text(period)
            ):
                continue

        # -----------------------------
        # MOTIF
        # -----------------------------

        if motif:

            if (
                normalize_text(
                    item.get("motif")
                )
                != normalize_text(motif)
            ):
                continue

        # -----------------------------
        # REGION
        # -----------------------------

        if region:

            if (
                normalize_text(
                    item.get("region")
                )
                != normalize_text(region)
            ):
                continue

        # -----------------------------
        # QUALITY
        # -----------------------------

        if quality:

            item_quality = get_quality(item)

            if (
                normalize_text(item_quality)
                != normalize_text(quality)
            ):
                continue

        # -----------------------------
        # PROCESSING
        # -----------------------------

        processing = item.get(
            "processing",
            {}
        )

        if (
            vectorized
            and not processing.get(
                "vectorized",
                False
            )
        ):
            continue

        if (
            segmented
            and not processing.get(
                "segmented",
                False
            )
        ):
            continue

        if (
            normalized
            and not processing.get(
                "normalized",
                False
            )
        ):
            continue

        if (
            restored
            and not processing.get(
                "restored",
                False
            )
        ):
            continue

        if (
            preprocessed
            and not processing.get(
                "preprocessed",
                False
            )
        ):
            continue

        results.append(item)

    return {
        "total": len(results),
        "results": results
    }


# ========================================
# STATISTICS
# ========================================

@app.get("/statistics")
def statistics():

    catalog = load_catalog()

    total = len(catalog)

    categories = {}
    quality = {}

    processing = {
        "preprocessed": 0,
        "restored": 0,
        "normalized": 0,
        "segmented": 0,
        "vectorized": 0
    }

    for item in catalog:

        # -----------------------------
        # CATEGORY
        # -----------------------------

        category = item.get(
            "category",
            "unknown"
        )

        categories[category] = (
            categories.get(category, 0) + 1
        )

        # -----------------------------
        # QUALITY
        # -----------------------------

        item_quality = get_quality(item)

        if item_quality:

            quality[item_quality] = (
                quality.get(item_quality, 0) + 1
            )

        # -----------------------------
        # PROCESSING
        # -----------------------------

        item_processing = item.get(
            "processing",
            {}
        )

        for stage in processing:

            if item_processing.get(
                stage,
                False
            ):

                processing[stage] += 1

    return {
        "total_assets": total,
        "categories": categories,
        "quality": quality,
        "processing": processing
    }


# ========================================
# QUALITY STATISTICS
# ========================================

@app.get("/quality")
def quality_statistics():

    catalog = load_catalog()

    scores = []

    classifications = {
        "GOOD": 0,
        "ACCEPTABLE": 0,
        "POOR": 0
    }

    for item in catalog:

        item_quality = item.get(
            "quality"
        )

        if not isinstance(
            item_quality,
            dict
        ):
            continue

        classification = item_quality.get(
            "quality"
        )

        score = item_quality.get(
            "overall_score"
        )

        if classification in classifications:

            classifications[
                classification
            ] += 1

        if isinstance(score, (int, float)):

            scores.append(score)

    average_score = 0

    if scores:

        average_score = round(
            sum(scores) / len(scores),
            2
        )

    return {
        "total_scored": len(scores),
        "average_score": average_score,
        "classifications": classifications
    }
"""
# ========================================
# PROCESS IMAGE
# ========================================

@app.post("/process")
def process_asset(request: ProcessRequest):

    input_path = request.image_path


    # ========================================
# 1. CONVERT INPUT PATH
# ========================================

raw_input_path = str(request.image_path).strip()

# Normalize slash
normalized_path = raw_input_path.replace("\\", "/")

candidate_paths = []

# ----------------------------------------
# Candidate 1: path exactly as provided
# ----------------------------------------

if os.path.isabs(raw_input_path):
    candidate_paths.append(raw_input_path)

else:
    candidate_paths.append(
        os.path.join(
            PROJECT_ROOT,
            raw_input_path
        )
    )


# ----------------------------------------
# Candidate 2: dataset/<path>
# ----------------------------------------

clean_relative = normalized_path.lstrip("/")

candidate_paths.append(
    os.path.join(
        PROJECT_ROOT,
        clean_relative.replace("/", os.sep)
    )
)

candidate_paths.append(
    os.path.join(
        PROJECT_ROOT,
        "dataset",
        clean_relative.replace("/", os.sep)
    )
)


# ----------------------------------------
# Candidate 3:
# If path contains "images/...",
# force it into dataset/images/...
# ----------------------------------------

images_marker = "/images/"

if images_marker in normalized_path:

    images_relative = normalized_path.split(
        images_marker,
        1
    )[1]

    candidate_paths.append(
        os.path.join(
            DATASET_DIR,
            "images",
            images_relative.replace("/", os.sep)
        )
    )


# ----------------------------------------
# Find first existing file
# ----------------------------------------

input_path = None

for candidate in candidate_paths:

    candidate = os.path.abspath(candidate)

    if os.path.isfile(candidate):

        input_path = candidate

        break


# ----------------------------------------
# File not found
# ----------------------------------------

if input_path is None:

    raise HTTPException(
        status_code=404,
        detail=(
            f"Image not found. "
            f"Received path: {raw_input_path}"
        )
    )


    # ========================================
    # 2. CHECK INPUT IMAGE
    # ========================================

    if not os.path.exists(input_path):

        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {input_path}"
        )


    try:

        # ====================================
        # 3. CREATE OUTPUT DIRECTORY
        # ====================================

        filename = os.path.splitext(
            os.path.basename(input_path)
        )[0]


        output_dir = os.path.join(
            OUTPUTS_DIR,
            filename
        )


        # ====================================
        # 4. RUN PROCESSING PIPELINE
        # ====================================

        result = process_image(
            input_path,
            output_dir
        )


        # ====================================
        # 5. CONVERT OUTPUT PATHS
        #    INTO BROWSER URLS
        # ====================================

        result["outputs"]["restored"] = (
            f"/outputs/{filename}/restored.png"
        )

        result["outputs"]["segmented"] = (
            f"/outputs/{filename}/segmented.png"
        )

        result["outputs"]["edges"] = (
            f"/outputs/{filename}/edges.png"
        )

        result["outputs"]["svg"] = (
            f"/outputs/{filename}/pattern.svg"
        )


        # ====================================
        # 6. UPDATE INPUT PATH IN RESPONSE
        # ====================================

        result["input"]["path"] = (
            request.image_path
        )


        result["restored"]["path"] = (
            f"/outputs/{filename}/restored.png"
        )


        # ====================================
        # 7. LOAD CATALOG
        # ====================================

        catalog = load_catalog()


        # ====================================
        # 8. FIND ASSET
        # ====================================

        asset_index = find_asset_index(
            catalog,
            input_path
        )


        catalog_updated = False


        # ====================================
        # 9. UPDATE CATALOG
        # ====================================

        if asset_index is not None:

            asset = catalog[asset_index]


            # --------------------------------
            # Existing processing object
            # --------------------------------

            processing = asset.get(
                "processing"
            )


            if not isinstance(
                processing,
                dict
            ):

                processing = {}


            # --------------------------------
            # Processing status
            # --------------------------------

            processing["preprocessed"] = True

            processing["restored"] = True

            processing["segmented"] = True

            processing["vectorized"] = True


            # --------------------------------
            # Keep normalized status
            # --------------------------------

            if "normalized" not in processing:

                processing["normalized"] = False


            asset["processing"] = processing


            # --------------------------------
            # Save output references
            # --------------------------------

            asset["processing_outputs"] = {

                "restored": (
                    f"/outputs/"
                    f"{filename}/restored.png"
                ),

                "segmented": (
                    f"/outputs/"
                    f"{filename}/segmented.png"
                ),

                "edges": (
                    f"/outputs/"
                    f"{filename}/edges.png"
                ),

                "svg": (
                    f"/outputs/"
                    f"{filename}/pattern.svg"
                ),

                "quality_report": (
                    f"/outputs/"
                    f"{filename}/quality_report.json"
                )
            }


            # --------------------------------
            # Save processing timestamp
            # --------------------------------

            asset["processed_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )


            # --------------------------------
            # Save restored metrics
            # --------------------------------

            if result.get("restored"):

                restored_metrics = result[
                    "restored"
                ].get(
                    "metrics"
                )


                if restored_metrics:

                    asset[
                        "processed_quality"
                    ] = restored_metrics


            # --------------------------------
            # Save catalog
            # --------------------------------

            save_catalog(
                catalog
            )


            catalog_updated = True


        # ====================================
        # 10. ADD CATALOG STATUS TO RESPONSE
        # ====================================

        result["catalog"] = {

            "updated": catalog_updated,

            "asset_index": asset_index

        }


        # ====================================
        # 11. RETURN RESULT
        # ====================================

        return result


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
"""


# ========================================
# PROCESS IMAGE
# ========================================

# ========================================
# PROCESS IMAGE
# ========================================

@app.post("/process")
def process_asset(request: ProcessRequest):

    input_path = request.image_path


    # ========================================
    # 1. CONVERT INPUT PATH
    # ========================================

    if not os.path.isabs(input_path):

        input_path = os.path.join(
            PROJECT_ROOT,
            input_path
        )


    input_path = os.path.abspath(
        input_path
    )


    # ========================================
    # 2. CHECK INPUT IMAGE
    # ========================================

    if not os.path.exists(input_path):

        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {input_path}"
        )


    try:

        # ====================================
        # 3. CREATE OUTPUT DIRECTORY
        # ====================================

        filename = os.path.splitext(
            os.path.basename(input_path)
        )[0]


        output_dir = os.path.join(
            OUTPUTS_DIR,
            filename
        )


        os.makedirs(
            output_dir,
            exist_ok=True
        )


        # ====================================
        # 4. RUN PROCESSING PIPELINE
        # ====================================

        result = process_image(
            input_path,
            output_dir
        )


        # ====================================
        # 5. BUILD OUTPUT URLS
        # ====================================

        restored_url = (
            f"/outputs/{filename}/restored.png"
        )

        normalized_url = (
            f"/outputs/{filename}/normalized.png"
        )

        segmented_url = (
            f"/outputs/{filename}/segmented.png"
        )

        edges_url = (
            f"/outputs/{filename}/edges.png"
        )

        svg_url = (
            f"/outputs/{filename}/pattern.svg"
        )

        quality_report_url = (
            f"/outputs/{filename}/quality_report.json"
        )


        # ====================================
        # 6. UPDATE RESPONSE OUTPUT PATHS
        # ====================================

        result["outputs"]["restored"] = (
            restored_url
        )

        result["outputs"]["normalized"] = (
            normalized_url
        )

        result["outputs"]["segmented"] = (
            segmented_url
        )

        result["outputs"]["edges"] = (
            edges_url
        )

        result["outputs"]["svg"] = (
            svg_url
        )

        result["outputs"]["quality_report"] = (
            quality_report_url
        )


        # ====================================
        # 7. UPDATE RESPONSE INPUT PATH
        # ====================================

        result["input"]["path"] = (
            request.image_path
        )


        # ====================================
        # 8. UPDATE STAGE PATHS
        # ====================================

        if result.get("restored"):

            result["restored"]["path"] = (
                restored_url
            )


        if result.get("normalized"):

            result["normalized"]["path"] = (
                normalized_url
            )


        # ====================================
        # 9. LOAD CATALOG
        # ====================================

        catalog = load_catalog()


        # ====================================
        # 10. FIND ASSET
        # ====================================

        asset_index = find_asset_index(
            catalog,
            input_path
        )


        catalog_updated = False


        # ====================================
        # 11. UPDATE CATALOG
        # ====================================

        if asset_index is not None:

            asset = catalog[asset_index]


            # --------------------------------
            # PROCESSING STATUS
            # --------------------------------

            processing = asset.get(
                "processing"
            )


            if not isinstance(
                processing,
                dict
            ):

                processing = {}


            # --------------------------------
            # ALL PIPELINE STAGES COMPLETED
            # --------------------------------

            processing["preprocessed"] = True

            processing["restored"] = True

            processing["normalized"] = True

            processing["segmented"] = True

            processing["vectorized"] = True


            asset["processing"] = (
                processing
            )


            # --------------------------------
            # PROCESSING OUTPUTS
            # --------------------------------

            asset["processing_outputs"] = {

                "restored": (
                    restored_url
                ),

                "normalized": (
                    normalized_url
                ),

                "segmented": (
                    segmented_url
                ),

                "edges": (
                    edges_url
                ),

                "svg": (
                    svg_url
                ),

                "quality_report": (
                    quality_report_url
                )
            }


            # --------------------------------
            # PROCESSING TIMESTAMP
            # --------------------------------

            asset["processed_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )


            # --------------------------------
            # SAVE QUALITY INFORMATION
            # --------------------------------

            if result.get("restored"):

                restored_metrics = result[
                    "restored"
                ].get(
                    "metrics"
                )


                if restored_metrics:

                    asset[
                        "processed_quality"
                    ] = restored_metrics


            # --------------------------------
            # SAVE NORMALIZED METRICS
            # --------------------------------

            if result.get("normalized"):

                normalized_metrics = result[
                    "normalized"
                ].get(
                    "metrics"
                )


                if normalized_metrics:

                    asset[
                        "normalized_quality"
                    ] = normalized_metrics


            # --------------------------------
            # SAVE CATALOG
            # --------------------------------

            save_catalog(
                catalog
            )


            catalog_updated = True


        # ====================================
        # 12. RETURN CATALOG STATUS
        # ====================================

        result["catalog"] = {

            "updated": (
                catalog_updated
            ),

            "asset_index": (
                asset_index
            )
        }


        # ====================================
        # 13. RETURN UPDATED ASSET
        # ====================================

        if (
            catalog_updated
            and asset_index is not None
        ):

            result["catalog"]["asset"] = (
                catalog[asset_index]
            )


        # ====================================
        # 14. RETURN RESULT
        # ====================================

        return result


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )