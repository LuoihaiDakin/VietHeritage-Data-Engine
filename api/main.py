import os
import json

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
# ========================================
# PROCESS IMAGE
# ========================================

@app.post("/process")
def process_asset(request: ProcessRequest):

    input_path = request.image_path

    # Convert relative path to absolute path
    if not os.path.isabs(input_path):
        input_path = os.path.join(
            PROJECT_ROOT,
            input_path
        )

    input_path = os.path.abspath(input_path)

    # Check input image
    if not os.path.exists(input_path):
        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {input_path}"
        )

    try:
        # Create output folder based on filename
        filename = os.path.splitext(
            os.path.basename(input_path)
        )[0]

        output_dir = os.path.join(
            OUTPUTS_DIR,
            filename
        )

        # Run processing pipeline
        result = process_image(
            input_path,
            output_dir
        )

        # Convert local paths to browser URLs
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

        result["input"]["path"] = (
            request.image_path
        )

        result["restored"]["path"] = (
            f"/outputs/{filename}/restored.png"
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )