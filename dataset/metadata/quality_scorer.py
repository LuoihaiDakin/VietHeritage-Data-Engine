import os
import json


# ============================================================
# STRICT QUALITY CONFIGURATION
# ============================================================

# Brightness
BRIGHTNESS_VERY_DARK = 40
BRIGHTNESS_DARK = 70
BRIGHTNESS_IDEAL_MIN = 95
BRIGHTNESS_IDEAL_MAX = 175
BRIGHTNESS_BRIGHT = 205
BRIGHTNESS_VERY_BRIGHT = 235


# Contrast
CONTRAST_VERY_LOW = 15
CONTRAST_LOW = 30
CONTRAST_GOOD = 65
CONTRAST_EXCELLENT = 90


# Sharpness
SHARPNESS_VERY_LOW = 30
SHARPNESS_LOW = 100
SHARPNESS_GOOD = 400
SHARPNESS_EXCELLENT = 800


# Resolution
MIN_WIDTH = 512
MIN_HEIGHT = 512

GOOD_WIDTH = 1280
GOOD_HEIGHT = 1280

EXCELLENT_WIDTH = 1920
EXCELLENT_HEIGHT = 1920

GOOD_MEGAPIXELS = 2.0
EXCELLENT_MEGAPIXELS = 4.0


# Overall classification
GOOD_SCORE = 85
ACCEPTABLE_SCORE = 70


# ============================================================
# BRIGHTNESS
# ============================================================

def calculate_brightness_score(brightness):
    """
    Strict brightness scoring.

    Ideal range:
        95 - 175

    Images that are too dark or too bright
    receive significantly lower scores.
    """

    if brightness is None:
        return 0

    # Extremely dark
    if brightness <= BRIGHTNESS_VERY_DARK:
        return 0

    # Dark
    if brightness < BRIGHTNESS_DARK:

        score = (
            (brightness - BRIGHTNESS_VERY_DARK)
            / (BRIGHTNESS_DARK - BRIGHTNESS_VERY_DARK)
        ) * 50

        return round(score, 2)

    # Moving toward ideal range
    if brightness < BRIGHTNESS_IDEAL_MIN:

        score = 50 + (
            (brightness - BRIGHTNESS_DARK)
            / (
                BRIGHTNESS_IDEAL_MIN
                - BRIGHTNESS_DARK
            )
        ) * 50

        return round(score, 2)

    # Ideal brightness
    if brightness <= BRIGHTNESS_IDEAL_MAX:
        return 100

    # Slightly too bright
    if brightness < BRIGHTNESS_BRIGHT:

        score = 100 - (
            (brightness - BRIGHTNESS_IDEAL_MAX)
            / (
                BRIGHTNESS_BRIGHT
                - BRIGHTNESS_IDEAL_MAX
            )
        ) * 50

        return round(score, 2)

    # Very bright
    if brightness < BRIGHTNESS_VERY_BRIGHT:

        score = 50 - (
            (brightness - BRIGHTNESS_BRIGHT)
            / (
                BRIGHTNESS_VERY_BRIGHT
                - BRIGHTNESS_BRIGHT
            )
        ) * 50

        return round(max(score, 0), 2)

    return 0


# ============================================================
# CONTRAST
# ============================================================

def calculate_contrast_score(contrast):
    """
    Strict contrast scoring.

    Low contrast indicates faded,
    washed-out or flat images.
    """

    if contrast is None:
        return 0

    # Extremely low contrast
    if contrast <= CONTRAST_VERY_LOW:
        return 0

    # Low contrast
    if contrast < CONTRAST_LOW:

        score = (
            (contrast - CONTRAST_VERY_LOW)
            / (
                CONTRAST_LOW
                - CONTRAST_VERY_LOW
            )
        ) * 40

        return round(score, 2)

    # Moderate contrast
    if contrast < CONTRAST_GOOD:

        score = 40 + (
            (contrast - CONTRAST_LOW)
            / (
                CONTRAST_GOOD
                - CONTRAST_LOW
            )
        ) * 60

        return round(score, 2)

    # Good contrast
    if contrast < CONTRAST_EXCELLENT:

        score = 100

        return round(score, 2)

    # Extremely high contrast
    # can also indicate clipping
    if contrast >= 120:
        return 75

    return 95


# ============================================================
# SHARPNESS
# ============================================================

def calculate_sharpness_score(sharpness):
    """
    Strict sharpness scoring using
    Laplacian variance.
    """

    if sharpness is None:
        return 0

    # Extremely blurry
    if sharpness <= SHARPNESS_VERY_LOW:
        return 0

    # Very blurry
    if sharpness < SHARPNESS_LOW:

        score = (
            (sharpness - SHARPNESS_VERY_LOW)
            / (
                SHARPNESS_LOW
                - SHARPNESS_VERY_LOW
            )
        ) * 40

        return round(score, 2)

    # Moderate sharpness
    if sharpness < SHARPNESS_GOOD:

        score = 40 + (
            (sharpness - SHARPNESS_LOW)
            / (
                SHARPNESS_GOOD
                - SHARPNESS_LOW
            )
        ) * 60

        return round(score, 2)

    # Good sharpness
    if sharpness < SHARPNESS_EXCELLENT:
        return 100

    # Extremely high Laplacian variance
    # may indicate excessive noise or edges.
    return 90


# ============================================================
# RESOLUTION
# ============================================================

def calculate_resolution_score(width, height):
    """
    Strict resolution scoring.

    Considers:
        - minimum dimension
        - megapixels
    """

    if width is None or height is None:
        return 0

    if width <= 0 or height <= 0:
        return 0

    min_dimension = min(
        width,
        height
    )

    megapixels = (
        width * height
    ) / 1_000_000

    # Extremely low resolution
    if min_dimension < 256:
        return 0

    # Very low resolution
    if min_dimension < MIN_WIDTH:
        return 20

    # Low resolution
    if min_dimension < 768:
        return 40

    # Acceptable
    if min_dimension < GOOD_WIDTH:
        return 60

    # Good dimensions but insufficient pixels
    if megapixels < GOOD_MEGAPIXELS:
        return 65

    # Good resolution
    if (
        min_dimension >= GOOD_WIDTH
        and megapixels >= GOOD_MEGAPIXELS
    ):

        if (
            min_dimension >= EXCELLENT_WIDTH
            and megapixels >= EXCELLENT_MEGAPIXELS
        ):
            return 100

        return 85

    return 50


# ============================================================
# OVERALL SCORE
# ============================================================

def calculate_overall_score(
    brightness_score,
    contrast_score,
    sharpness_score,
    resolution_score
):
    """
    Calculate strict weighted quality score.

    Weights:

        Sharpness   = 40%
        Resolution  = 30%
        Contrast    = 20%
        Brightness  = 10%
    """

    score = (
        sharpness_score * 0.40
        + resolution_score * 0.30
        + contrast_score * 0.20
        + brightness_score * 0.10
    )

    return round(score, 2)


# ============================================================
# QUALITY CLASSIFICATION
# ============================================================

def classify_quality(score):
    """
    Strict quality classification.
    """

    if score >= GOOD_SCORE:
        return "GOOD"

    if score >= ACCEPTABLE_SCORE:
        return "ACCEPTABLE"

    return "POOR"


# ============================================================
# ADDITIONAL QUALITY FLAGS
# ============================================================

def generate_quality_flags(
    brightness_score,
    contrast_score,
    sharpness_score,
    resolution_score
):
    """
    Identify specific quality problems.
    """

    flags = []

    if brightness_score < 60:
        flags.append("poor_brightness")

    if contrast_score < 60:
        flags.append("poor_contrast")

    if sharpness_score < 60:
        flags.append("poor_sharpness")

    if resolution_score < 60:
        flags.append("low_resolution")

    return flags


# ============================================================
# RECOMMENDATION
# ============================================================

def generate_recommendation(
    quality,
    flags
):
    """
    Generate processing recommendation.
    """

    if quality == "GOOD":

        return (
            "High-quality image. "
            "Ready for downstream processing."
        )

    if quality == "ACCEPTABLE":

        if flags:

            problems = ", ".join(
                flags
            )

            return (
                "Image is usable but "
                "preprocessing is recommended: "
                + problems
                + "."
            )

        return (
            "Image is acceptable "
            "for downstream processing."
        )

    if flags:

        problems = ", ".join(
            flags
        )

        return (
            "Image requires restoration "
            "or preprocessing: "
            + problems
            + "."
        )

    return (
        "Image quality is insufficient "
        "for direct downstream processing."
    )


# ============================================================
# SCORE ONE IMAGE
# ============================================================

def score_image(metadata):
    """
    Calculate quality score for one image.
    """

    brightness = metadata.get(
        "brightness"
    )

    contrast = metadata.get(
        "contrast"
    )

    sharpness = metadata.get(
        "sharpness"
    )

    width = metadata.get(
        "width"
    )

    height = metadata.get(
        "height"
    )

    # Individual scores
    brightness_score = calculate_brightness_score(
        brightness
    )

    contrast_score = calculate_contrast_score(
        contrast
    )

    sharpness_score = calculate_sharpness_score(
        sharpness
    )

    resolution_score = calculate_resolution_score(
        width,
        height
    )

    # Overall
    overall_score = calculate_overall_score(
        brightness_score,
        contrast_score,
        sharpness_score,
        resolution_score
    )

    # Classification
    quality = classify_quality(
        overall_score
    )

    # Flags
    flags = generate_quality_flags(
        brightness_score,
        contrast_score,
        sharpness_score,
        resolution_score
    )

    # Recommendation
    recommendation = generate_recommendation(
        quality,
        flags
    )

    return {

        "filename": metadata.get(
            "filename"
        ),

        "path": metadata.get(
            "path"
        ),

        "category": metadata.get(
            "category"
        ),

        "technical_metrics": {

            "brightness": brightness,

            "contrast": contrast,

            "sharpness": sharpness,

            "width": width,

            "height": height
        },

        "quality_scores": {

            "brightness": brightness_score,

            "contrast": contrast_score,

            "sharpness": sharpness_score,

            "resolution": resolution_score
        },

        "overall_score": overall_score,

        "quality": quality,

        "quality_flags": flags,

        "recommendation": recommendation
    }


# ============================================================
# LOAD METADATA
# ============================================================

def load_metadata(metadata_path):
    """
    Load metadata.json.
    """

    if not os.path.exists(
        metadata_path
    ):

        print(
            "ERROR: Metadata file not found:"
        )

        print(
            metadata_path
        )

        return []

    try:

        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError:

        print(
            "ERROR: Invalid JSON metadata file."
        )

        return []


# ============================================================
# SAVE REPORT
# ============================================================

def save_quality_report(
    report,
    output_path
):
    """
    Save quality report.
    """

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# SUMMARY
# ============================================================

def generate_summary(results):
    """
    Generate dataset quality statistics.
    """

    total = len(
        results
    )

    good = 0
    acceptable = 0
    poor = 0

    total_score = 0

    for result in results:

        quality = result[
            "quality"
        ]

        if quality == "GOOD":
            good += 1

        elif quality == "ACCEPTABLE":
            acceptable += 1

        elif quality == "POOR":
            poor += 1

        total_score += result[
            "overall_score"
        ]

    average_score = 0

    if total > 0:

        average_score = round(
            total_score / total,
            2
        )

    return {

        "total_images": total,

        "good": good,

        "acceptable": acceptable,

        "poor": poor,

        "average_score": average_score,

        "good_percentage": round(
            (good / total) * 100,
            2
        ) if total else 0,

        "acceptable_percentage": round(
            (acceptable / total) * 100,
            2
        ) if total else 0,

        "poor_percentage": round(
            (poor / total) * 100,
            2
        ) if total else 0
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "========================================"
    )

    print(
        "   VietHeritage STRICT Quality Scoring"
    )

    print(
        "========================================"
    )

    print()

    # Project root
    project_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    # Input
    metadata_path = os.path.join(
        project_root,
        "dataset",
        "metadata",
        "metadata.json"
    )

    # Output
    output_path = os.path.join(
        project_root,
        "dataset",
        "metadata",
        "quality_report.json"
    )

    print(
        "Loading metadata:"
    )

    print(
        metadata_path
    )

    print()

    metadata_list = load_metadata(
        metadata_path
    )

    if not metadata_list:

        print(
            "No metadata available."
        )

        return

    # Score images
    results = []

    for metadata in metadata_list:

        result = score_image(
            metadata
        )

        results.append(
            result
        )

    # Summary
    summary = generate_summary(
        results
    )

    # Report
    report = {

        "project":
            "VietHeritage Data Engine",

        "module":
            "Strict Dataset Quality Scoring",

        "total_images":
            summary["total_images"],

        "summary":
            summary,

        "scoring_configuration": {

            "brightness_weight":
                0.10,

            "contrast_weight":
                0.20,

            "sharpness_weight":
                0.40,

            "resolution_weight":
                0.30,

            "good_threshold":
                GOOD_SCORE,

            "acceptable_threshold":
                ACCEPTABLE_SCORE
        },

        "results":
            results
    }

    # Save
    save_quality_report(
        report,
        output_path
    )

    # Console
    print(
        "Strict quality scoring completed."
    )

    print()

    print(
        "----------------------------------------"
    )

    print(
        f"Total images : "
        f"{summary['total_images']}"
    )

    print(
        f"GOOD         : "
        f"{summary['good']}"
    )

    print(
        f"ACCEPTABLE   : "
        f"{summary['acceptable']}"
    )

    print(
        f"POOR         : "
        f"{summary['poor']}"
    )

    print(
        f"Average score: "
        f"{summary['average_score']}"
    )

    print()

    print(
        f"GOOD         : "
        f"{summary['good_percentage']}%"
    )

    print(
        f"ACCEPTABLE   : "
        f"{summary['acceptable_percentage']}%"
    )

    print(
        f"POOR         : "
        f"{summary['poor_percentage']}%"
    )

    print(
        "----------------------------------------"
    )

    print()

    print(
        "Report saved to:"
    )

    print(
        output_path
    )


if __name__ == "__main__":
    main()