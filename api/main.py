import os
import json
import shutil
import uuid

from datetime import datetime

import cv2

from fastapi import (
    FastAPI,
    Query,
    HTTPException,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from processing.pipeline import process_image
from processing.comparison import build_comparison
from dataset.metadata.quality_scorer import score_image

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
    "catalog",
    "catalog.json"
)

DATASET_DIR = os.path.join(
    PROJECT_ROOT,
    "dataset"
)

IMAGE_DIR = os.path.join(
    DATASET_DIR,
    "images"
)

UPLOAD_DIR = os.path.join(
    IMAGE_DIR,
    "uploaded"
)

OUTPUTS_DIR = os.path.join(
    PROJECT_ROOT,
    "outputs"
)


# ========================================
# CREATE REQUIRED DIRECTORIES
# ========================================

os.makedirs(
    IMAGE_DIR,
    exist_ok=True
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    OUTPUTS_DIR,
    exist_ok=True
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


# ========================================
# REQUEST MODELS
# ========================================

class ProcessRequest(BaseModel):

    image_path: str


# ========================================
# CORS
# ========================================

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


# ========================================
# STATIC FILES
# ========================================

app.mount(
    "/images",
    StaticFiles(
        directory=IMAGE_DIR
    ),
    name="images"
)

app.mount(
    "/outputs",
    StaticFiles(
        directory=OUTPUTS_DIR
    ),
    name="outputs"
)


# ========================================
# LOAD CATALOG
# ========================================

def load_catalog():

    if not os.path.exists(
        CATALOG_PATH
    ):
        return []

    try:

        with open(
            CATALOG_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        # catalog/catalog.json stores assets inside
        # the top-level "assets" field.
        if isinstance(data, dict):
            assets = data.get("assets", [])
            return assets if isinstance(assets, list) else []

        # Keep compatibility with a plain list catalog.
        if isinstance(data, list):
            return data

        return []

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

    os.makedirs(
        os.path.dirname(
            CATALOG_PATH
        ),
        exist_ok=True
    )

    # Preserve the catalog JSON structure while
    # updating only the assets list.
    existing_data = {}

    if os.path.exists(CATALOG_PATH):
        try:
            with open(
                CATALOG_PATH,
                "r",
                encoding="utf-8"
            ) as existing_file:
                existing_data = json.load(existing_file)

        except Exception:
            existing_data = {}

    if isinstance(existing_data, dict):
        existing_data["assets"] = catalog
        data_to_save = existing_data
    else:
        data_to_save = {
            "assets": catalog
        }

    with open(
        CATALOG_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data_to_save,
            file,
            indent=4,
            ensure_ascii=False
        )


# ========================================
# FIND ASSET IN CATALOG
# ========================================

def find_asset_index(
    catalog,
    input_path
):
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

    for index, item in enumerate(
        catalog
    ):

        # --------------------------------
        # Check filename
        # --------------------------------

        catalog_filename = str(
            item.get(
                "filename",
                ""
            )
        ).lower()

        if (
            catalog_filename
            and catalog_filename
            == input_filename
        ):

            return index


        # --------------------------------
        # Check original.path
        # --------------------------------

        original = item.get(
            "original",
            {}
        )

        if isinstance(
            original,
            dict
        ):

            original_path = str(
                original.get(
                    "path",
                    ""
                )
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
            item.get(
                "path",
                ""
            )
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

    return str(
        value
    ).strip().lower()


def get_quality(item):

    quality = item.get(
        "quality"
    )

    if not isinstance(
        quality,
        dict
    ):
        return None

    return quality.get(
        "quality"
    )


def get_quality_score(item):

    quality = item.get(
        "quality"
    )

    if not isinstance(
        quality,
        dict
    ):
        return None

    return quality.get(
        "overall_score"
    )


def get_asset_identifier(item):
    """Return the canonical identifier regardless of catalog version."""
    if not isinstance(item, dict):
        return None

    return item.get("asset_id") or item.get("id")


def find_asset_by_id(catalog, asset_id):
    """Find an asset using either asset_id or the legacy id field."""
    target = str(asset_id)

    for item in catalog:
        if not isinstance(item, dict):
            continue

        if str(item.get("asset_id", "")) == target:
            return item

        if str(item.get("id", "")) == target:
            return item

    return None


def prepare_asset_for_api(item):
    """Expose compatibility fields without modifying catalog.json."""
    if not isinstance(item, dict):
        return item

    result = dict(item)

    # Current catalog uses asset_id; older dashboard code expects id.
    if not result.get("id") and result.get("asset_id"):
        result["id"] = result["asset_id"]

    # Current catalog stores the original path under original.path.
    if not result.get("path"):
        original = result.get("original")
        if isinstance(original, dict) and original.get("path"):
            result["path"] = original["path"]

    # Keep the quality object exactly as stored by the catalog.
    quality = result.get("quality")
    if isinstance(quality, dict):
        if "label" not in quality and quality.get("quality") is not None:
            quality["label"] = quality.get("quality")

    # processing_outputs already contains the comparison files.
    # Do not overwrite it with outputs because the frontend uses both.

    return result


def calculate_image_metrics(
    image_path
):

    image = cv2.imread(
        image_path
    )

    if image is None:

        raise ValueError(
            f"Cannot read image: {image_path}"
        )

    height, width = image.shape[:2]

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(
        gray.mean()
    )

    contrast = float(
        gray.std()
    )

    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    return {

        "brightness": round(
            brightness,
            2
        ),

        "contrast": round(
            contrast,
            2
        ),

        "sharpness": round(
            sharpness,
            2
        ),

        "width": int(
            width
        ),

        "height": int(
            height
        )

    }


def evaluate_image_quality(
    image_path,
    filename,
    relative_path,
    category="uploaded"
):

    metrics = calculate_image_metrics(
        image_path
    )

    metadata = {

        "filename": filename,

        "path": relative_path,

        "category": category,

        "brightness": (
            metrics["brightness"]
        ),

        "contrast": (
            metrics["contrast"]
        ),

        "sharpness": (
            metrics["sharpness"]
        ),

        "width": (
            metrics["width"]
        ),

        "height": (
            metrics["height"]
        )

    }

    return score_image(
        metadata
    )


# ========================================
# ROOT
# ========================================

@app.get("/")
def root():

    return {
        "project": (
            "VietHeritage Data Engine"
        ),
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
        "catalog_loaded": (
            len(catalog) > 0
        ),
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

    results = [
        prepare_asset_for_api(item)
        for item in catalog[
            offset:
            offset + limit
        ]
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

@app.get(
    "/assets/{asset_id}"
)
def get_asset(
    asset_id: str
):

    catalog = load_catalog()

    asset = find_asset_by_id(
        catalog,
        asset_id
    )

    if asset:
        return prepare_asset_for_api(asset)

    return {
        "error": "Asset not found",
        "asset_id": asset_id
    }


# ========================================
# UPLOAD IMAGE
# ========================================

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...)
):

    # ========================================
    # 1. CHECK FILE
    # ========================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    # ========================================
    # 2. CHECK EXTENSION
    # ========================================

    original_filename = os.path.basename(
        file.filename
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png"
    }

    if (
        extension
        not in allowed_extensions
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, and PNG "
                "images are supported."
            )
        )


    # ========================================
    # 3. CREATE SAFE FILENAME
    # ========================================

    filename_without_extension = (
        os.path.splitext(
            original_filename
        )[0]
    )

    safe_name = "".join(
        character
        if (
            character.isalnum()
            or character in (
                "_",
                "-"
            )
        )
        else "_"
        for character
        in filename_without_extension
    )

    if not safe_name:

        safe_name = (
            "uploaded_image"
        )


    # ========================================
    # 4. CREATE UNIQUE ID
    # ========================================

    unique_id = uuid.uuid4().hex[:8]

    saved_filename = (
        f"{safe_name}_"
        f"{unique_id}"
        f"{extension}"
    )


    # ========================================
    # 5. BUILD SAVE PATH
    # ========================================

    saved_path = os.path.join(
        UPLOAD_DIR,
        saved_filename
    )


    # ========================================
    # 6. SAVE IMAGE
    # ========================================

    try:

        with open(
            saved_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save image: "
                f"{error}"
            )
        )


    # ========================================
    # 7. CREATE ASSET ID
    # ========================================

    asset_id = (
        f"uploaded_"
        f"{unique_id}_"
        f"{safe_name}"
    )


    # ========================================
    # 8. CREATE RELATIVE IMAGE PATH
    # ========================================

    relative_image_path = (
        f"images/uploaded/"
        f"{saved_filename}"
    )


    # ========================================
    # 9. CREATE BASIC CATALOG ENTRY
    # ========================================

    asset = {

        "id": asset_id,

        "asset_id": asset_id,

        "filename": saved_filename,

        "path": relative_image_path,

        "category": "uploaded",

        "dynasty": "",

        "period": "",

        "motif": "",

        "region": "",

        "source": "User Upload",

        "original": {

            "path": relative_image_path,

            "filename": saved_filename

        },

        "processing": {

            "preprocessed": False,

            "restored": False,

            "normalized": False,

            "segmented": False,

            "vectorized": False

        },

        "processing_outputs": {},

        "uploaded_at": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

    }


    # ========================================
    # 10. QUALITY
    # ========================================
    #
    # Quality will be calculated by the
    # processing pipeline when the image
    # is processed.
    #

    quality_warning = None

    asset["quality"] = {}


    # ========================================
    # 11. LOAD CATALOG
    # ========================================

    catalog = load_catalog()


    # ========================================
    # 12. ADD NEW ASSET
    # ========================================

    catalog.append(
        asset
    )


    # ========================================
    # 13. SAVE CATALOG
    # ========================================

    try:

        save_catalog(
            catalog
        )

    except Exception as error:

        # Remove uploaded file if
        # catalog saving fails.

        if os.path.exists(
            saved_path
        ):

            os.remove(
                saved_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not update catalog: "
                f"{error}"
            )
        )


    # ========================================
    # 14. RETURN RESULT
    # ========================================

    response = {

        "success": True,

        "message": (
            "Image uploaded successfully."
        ),

        "asset": asset

    }

    return response


# ========================================
# METADATA UPDATE
# ========================================

class MetadataUpdate(BaseModel):

    category: str = ""

    dynasty: str = ""

    period: str = ""

    motif: str = ""

    region: str = ""

    source: str = ""

    license: str = ""


@app.patch(
    "/assets/{asset_id}/metadata"
)
def update_asset_metadata(
    asset_id: str,
    metadata: MetadataUpdate
):

    catalog = load_catalog()

    asset_index = None

    for index, asset in enumerate(
        catalog
    ):

        if str(
            get_asset_identifier(asset)
        ) == str(
            asset_id
        ):

            asset_index = index

            break


    if asset_index is None:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )


    asset = catalog[
        asset_index
    ]

    asset[
        "category"
    ] = metadata.category.strip()

    asset[
        "dynasty"
    ] = metadata.dynasty.strip()

    asset[
        "period"
    ] = metadata.period.strip()

    asset[
        "motif"
    ] = metadata.motif.strip()

    asset[
        "region"
    ] = metadata.region.strip()

    asset[
        "source"
    ] = metadata.source.strip()

    asset[
        "license"
    ] = metadata.license.strip()


    save_catalog(
        catalog
    )


    return {

        "success": True,

        "message": (
            "Metadata updated successfully"
        ),

        "asset": asset

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
                normalize_text(
                    keyword
                )
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
                != normalize_text(
                    category
                )
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
                != normalize_text(
                    dynasty
                )
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
                != normalize_text(
                    period
                )
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
                != normalize_text(
                    motif
                )
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
                != normalize_text(
                    region
                )
            ):

                continue


        # -----------------------------
        # QUALITY
        # -----------------------------

        if quality:

            item_quality = get_quality(
                item
            )

            if (
                normalize_text(
                    item_quality
                )
                != normalize_text(
                    quality
                )
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


        results.append(
            item
        )


    return {

        "total": len(
            results
        ),

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
            categories.get(
                category,
                0
            ) + 1
        )


        # -----------------------------
        # QUALITY
        # -----------------------------

        item_quality = get_quality(
            item
        )

        if item_quality:

            quality[item_quality] = (
                quality.get(
                    item_quality,
                    0
                ) + 1
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


        classification = (
            item_quality.get(
                "quality"
            )
        )

        score = (
            item_quality.get(
                "overall_score"
            )
        )


        if (
            classification
            in classifications
        ):

            classifications[
                classification
            ] += 1


        if isinstance(
            score,
            (int, float)
        ):

            scores.append(
                score
            )


    average_score = 0

    if scores:

        average_score = round(
            sum(scores) / len(scores),
            2
        )


    return {

        "total_scored": len(
            scores
        ),

        "average_score": (
            average_score
        ),

        "classifications": (
            classifications
        )

    }


# ========================================
# SAVE COMPARISON HISTORY
# ========================================

def save_comparison_history(
    output_dir,
    comparison
):
    """
    Keep a history of every comparison instead
    of overwriting the previous comparison.
    """

    history_path = os.path.join(
        output_dir,
        "comparison_history.json"
    )

    history = []

    if os.path.exists(
        history_path
    ):

        try:

            with open(
                history_path,
                "r",
                encoding="utf-8"
            ) as file:

                history = json.load(
                    file
                )

            if not isinstance(
                history,
                list
            ):

                history = []

        except Exception:

            history = []

    history.append(
        comparison
    )

    with open(
        history_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )


# ========================================
# GET ASSET COMPARISON
# ========================================

@app.get(
    "/assets/{asset_id}/comparison"
)
def get_asset_comparison(
    asset_id: str
):

    catalog = load_catalog()

    asset = next(
        (
            item
            for item in catalog
            if str(get_asset_identifier(item)) == str(asset_id)
        ),
        None
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    filename = asset.get(
        "filename"
    )

    if not filename:

        raise HTTPException(
            status_code=404,
            detail="Asset filename not found"
        )

    output_name = os.path.splitext(
        filename
    )[0]

    output_dir = os.path.join(
        OUTPUTS_DIR,
        output_name
    )

    comparison_path = os.path.join(
        output_dir,
        "comparison.json"
    )

    if not os.path.exists(
        comparison_path
    ):

        raise HTTPException(
            status_code=404,
            detail="Comparison has not been generated yet"
        )

    try:

        with open(
            comparison_path,
            "r",
            encoding="utf-8"
        ) as file:

            comparison = json.load(
                file
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to read comparison: "
                f"{str(error)}"
            )
        )


# ---------------------------------------------------------
# ORIGINAL IMAGE URL
# ---------------------------------------------------------

    original_path = None

    original = asset.get("original")

    if isinstance(original, dict):
        original_path = original.get("path")

    if not original_path:
        original_path = asset.get("path")

    if not original_path:
        original_path = asset.get("image_path")

    if original_path:
        original_path = str(original_path).replace("\\", "/")

        if original_path.startswith("dataset/images/"):
            original_url = "/" + original_path.replace(
                "dataset/",
                "",
                1
            )

        elif original_path.startswith("./dataset/images/"):
            original_url = "/" + original_path.replace(
                "./dataset/",
                "",
                1
            )

        elif original_path.startswith("images/"):
            original_url = "/" + original_path

        elif original_path.startswith("/images/"):
            original_url = original_path

        else:
            original_url = "/images/" + os.path.basename(
                original_path
            )

    else:
        original_url = None

    # ---------------------------------------------------------
    # PROCESSED IMAGE URL
    # ---------------------------------------------------------

    processed_url = None

    processing_outputs = asset.get(
        "processing_outputs",
        {}
    )

    if isinstance(processing_outputs, dict):
        processed_url = (
            processing_outputs.get("normalized")
            or processing_outputs.get("processed")
        )

    if processed_url:
        processed_url = str(processed_url).replace(
            "\\",
            "/"
        )

        if processed_url.startswith("outputs/"):
            processed_url = "/" + processed_url

        elif not processed_url.startswith("/"):
            processed_url = "/" + processed_url

    # If catalog does not contain it, use normalized.png
    if not processed_url:
        normalized_path = os.path.join(
            output_dir,
            "normalized.png"
        )

        if os.path.exists(normalized_path):
            processed_url = (
                f"/outputs/{output_name}/normalized.png"
            )

    # ---------------------------------------------------------
    # COMPARISON PREVIEW
    # ---------------------------------------------------------

    preview_url = None

    preview_path = os.path.join(
        output_dir,
        "comparison_preview.png"
    )

    if os.path.exists(preview_path):
        preview_url = (
            f"/outputs/{output_name}/comparison_preview.png"
        )

    # ---------------------------------------------------------
    # FORCE CORRECT FILE URL STRUCTURE
    # ---------------------------------------------------------

    if "files" not in comparison:
        comparison["files"] = {}

    comparison["files"]["original"] = original_url
    comparison["files"]["processed"] = processed_url
    comparison["files"]["preview"] = preview_url

    # Useful aliases for frontend/debugging
    comparison["asset_id"] = asset_id
    comparison["filename"] = filename

    return comparison


# ========================================
# PROCESS IMAGE
# ========================================

@app.post("/process")
def process_asset(
    request: ProcessRequest
):

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
            detail=(
                f"Image not found: "
                f"{input_path}"
            )
        )

    try:

        # ====================================
        # 3. CREATE OUTPUT DIRECTORY
        # ====================================

        filename = os.path.splitext(
            os.path.basename(
                input_path
            )
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
        # 4. EVALUATE ORIGINAL IMAGE BEFORE AI
        # ====================================

        relative_path = None

        catalog_before = load_catalog()

        asset_index_before = find_asset_index(
            catalog_before,
            input_path
        )

        before_asset = None

        if asset_index_before is not None:

            before_asset = (
                catalog_before[
                    asset_index_before
                ]
            )

            relative_path = before_asset.get(
                "path",
                request.image_path
            )

        else:

            relative_path = request.image_path

        try:

            before_quality = (
                evaluate_image_quality(
                    input_path,
                    (
                        before_asset.get(
                            "filename",
                            os.path.basename(
                                input_path
                            )
                        )
                        if before_asset
                        else os.path.basename(
                            input_path
                        )
                    ),
                    relative_path,
                    (
                        before_asset.get(
                            "category",
                            "uploaded"
                        )
                        if before_asset
                        else "uploaded"
                    )
                )
            )

        except Exception as quality_error:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Could not evaluate original "
                    f"image quality: {quality_error}"
                )
            )

        # ========================================
        # 5. SAVE BEFORE QUALITY
        # ========================================

        before_quality_path = os.path.join(
            output_dir,
            "before_quality.json"
        )

        with open(
            before_quality_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                before_quality,
                file,
                indent=4,
                ensure_ascii=False
            )

        # ========================================
        # 6. RUN PROCESSING PIPELINE
        # ========================================

        result = process_image(
            input_path,
            output_dir
        )

        # ====================================
        # CREATE BEFORE / AFTER COMPARISON
        # ====================================

        comparison_data = None

        comparison_json_path = os.path.join(
            output_dir,
            "comparison.json"
        )

        comparison_preview_path = os.path.join(
            output_dir,
            "comparison_preview.png"
        )

        comparison_history_path = os.path.join(
            output_dir,
            "comparison_history.json"
        )

        # ----------------------------------------
        # Find normalized output
        # ----------------------------------------

        normalized_output_path = os.path.join(
            output_dir,
            "normalized.png"
        )

        # ----------------------------------------
        # Determine AFTER quality
        # ----------------------------------------

        after_quality = {}

        for stage_name in [
            "normalized",
            "cleaned",
            "restored"
        ]:

            stage = result.get(
                stage_name
            )

            if not isinstance(
                stage,
                dict
            ):
                continue

            stage_quality = stage.get(
                "quality"
            )

            if isinstance(
                stage_quality,
                dict
            ):

                after_quality = (
                    stage_quality
                )

                break

        # ----------------------------------------
        # Build comparison
        # ----------------------------------------

        if os.path.exists(
            normalized_output_path
        ):

            try:

                comparison_data = (
                    build_comparison(
                        before_path=input_path,
                        after_path=normalized_output_path,
                        before_quality=before_quality,
                        after_quality=after_quality,
                        output_path=(
                            comparison_json_path
                        ),
                        preview_path=(
                            comparison_preview_path
                        )
                    )
                )

                save_comparison_history(
                    output_dir,
                    comparison_data
                )

                print(
                    "COMPARISON CREATED: "
                    f"{comparison_data['before']['quality']} "
                    "-> "
                    f"{comparison_data['after']['quality']}"
                )

            except Exception as comparison_error:

                print(
                    "WARNING: Comparison failed: "
                    f"{comparison_error}"
                )

                comparison_data = {
                    "error": str(
                        comparison_error
                    )
                }

        # ====================================
        # 7. BUILD OUTPUT URLS
        # ====================================

        restored_url = (
            f"/outputs/"
            f"{filename}/"
            f"restored.png"
        )

        normalized_url = (
            f"/outputs/"
            f"{filename}/"
            f"normalized.png"
        )

        segmented_url = (
            f"/outputs/"
            f"{filename}/"
            f"segmented.png"
        )

        edges_url = (
            f"/outputs/"
            f"{filename}/"
            f"edges.png"
        )

        svg_url = (
            f"/outputs/"
            f"{filename}/"
            f"pattern.svg"
        )

        quality_report_url = (
            f"/outputs/"
            f"{filename}/"
            f"quality_report.json"
        )

        comparison_url = (
            f"/outputs/"
            f"{filename}/"
            f"comparison.json"
        )

        comparison_preview_url = (
            f"/outputs/"
            f"{filename}/"
            f"comparison_preview.png"
        )

        before_quality_url = (
            f"/outputs/"
            f"{filename}/"
            f"before_quality.json"
        )

        comparison_history_url = (
            f"/outputs/"
            f"{filename}/"
            f"comparison_history.json"
        )

        # ====================================
        # 8. UPDATE RESPONSE OUTPUT PATHS
        # ====================================

        if "outputs" not in result:
            result["outputs"] = {}

        result["outputs"]["restored"] = restored_url
        result["outputs"]["normalized"] = normalized_url
        result["outputs"]["segmented"] = segmented_url
        result["outputs"]["edges"] = edges_url
        result["outputs"]["svg"] = svg_url
        result["outputs"]["quality_report"] = (
            quality_report_url
        )
        result["outputs"]["comparison"] = (
            comparison_url
        )
        result["outputs"]["comparison_preview"] = (
            comparison_preview_url
        )
        result["outputs"]["before_quality"] = (
            before_quality_url
        )
        result["outputs"]["comparison_history"] = (
            comparison_history_url
        )

        # ====================================
        # 9. UPDATE RESPONSE INPUT PATH
        # ====================================

        if "input" not in result:
            result["input"] = {}

        result["input"]["path"] = request.image_path

        # ====================================
        # 10. UPDATE STAGE PATHS
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
        # 11. LOAD CATALOG
        # ====================================

        catalog = load_catalog()

        # ====================================
        # 12. FIND ASSET
        # ====================================

        asset_index = find_asset_index(
            catalog,
            input_path
        )

        catalog_updated = False

        # ====================================
        # 13. UPDATE CATALOG
        # ====================================

        if asset_index is not None:

            asset = catalog[
                asset_index
            ]

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

            asset["processing"] = processing

            # --------------------------------
            # PROCESSING OUTPUTS
            # --------------------------------

            asset["processing_outputs"] = {

                "restored": restored_url,

                "normalized": normalized_url,

                "segmented": segmented_url,

                "edges": edges_url,

                "svg": svg_url,

                "quality_report": (
                    quality_report_url
                ),

                "before_quality": (
                    before_quality_url
                ),

                "comparison": (
                    comparison_url
                ),

                "comparison_preview": (
                    comparison_preview_url
                ),

                "comparison_history": (
                    comparison_history_url
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
            # COMPARISON
            # --------------------------------

            if isinstance(
                comparison_data,
                dict
            ):

                asset["comparison"] = (
                    comparison_data
                )

            # =================================
            # QUALITY CLASSIFICATION
            # =================================
            #
            # Quality được lấy trực tiếp từ
            # processing pipeline.
            #
            # Không chấm lại bằng
            # dataset.metadata.quality_scorer
            # vì pipeline đã có quality_classifier
            # riêng.
            #

            pipeline_quality = None

            if isinstance(
                result.get("input"),
                dict
            ):

                input_quality = result[
                    "input"
                ].get(
                    "quality"
                )

                if isinstance(
                    input_quality,
                    dict
                ):

                    pipeline_quality = (
                        input_quality
                    )

            # --------------------------------
            # SAVE PIPELINE QUALITY
            # --------------------------------

            if pipeline_quality:

                asset["quality"] = {

                    "quality": pipeline_quality.get(
                        "quality"
                    ),

                    "overall_score": pipeline_quality.get(
                        "score"
                    ),

                    "quality_scores": pipeline_quality.get(
                        "component_scores",
                        {}
                    ),

                    "technical_metrics": (
                        result.get(
                            "input",
                            {}
                        ).get(
                            "metrics",
                            {}
                        )
                    )

                }

                result["quality"] = (
                    asset["quality"]
                )

                print(
                    "QUALITY FROM PIPELINE: "
                    f"{pipeline_quality.get('quality')} "
                    f"- "
                    f"{pipeline_quality.get('score')}"
                )

            else:

                # Pipeline không trả quality.
                # Giữ quality cũ nếu catalog đã có.

                current_quality = asset.get(
                    "quality"
                )

                if (
                    isinstance(
                        current_quality,
                        dict
                    )
                    and current_quality.get(
                        "quality"
                    )
                ):

                    result["quality"] = (
                        current_quality
                    )

                else:

                    result[
                        "quality_warning"
                    ] = (
                        "Pipeline did not return "
                        "quality classification."
                    )

            # --------------------------------
            # SAVE RESTORED METRICS
            # --------------------------------

            if result.get("restored"):

                restored_metrics = (
                    result[
                        "restored"
                    ].get(
                        "metrics"
                    )
                )

                if restored_metrics:

                    asset[
                        "processed_quality"
                    ] = restored_metrics

            # --------------------------------
            # SAVE NORMALIZED METRICS
            # --------------------------------

            if result.get("normalized"):

                normalized_metrics = (
                    result[
                        "normalized"
                    ].get(
                        "metrics"
                    )
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
        # 14. RETURN CATALOG STATUS
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
        # 15. RETURN UPDATED ASSET
        # ====================================

        if (
            catalog_updated
            and asset_index is not None
        ):

            result[
                "catalog"
            ][
                "asset"
            ] = catalog[
                asset_index
            ]

        # ====================================
        # 16. RETURN RESULT
        # ====================================

        return result

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )