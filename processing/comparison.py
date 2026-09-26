import os
import json
import math
from datetime import datetime

import cv2
import numpy as np


# ============================================================
# BASIC IMAGE METRICS
# ============================================================

def calculate_basic_metrics(image_path):
    """
    Calculate basic technical metrics for an image.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
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
        "width": int(width),
        "height": int(height),
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
        )
    }


# ============================================================
# RESIZE FOR FULL-REFERENCE COMPARISON
# ============================================================

def prepare_images(
    before_path,
    after_path
):
    """
    Resize the AFTER image to the BEFORE image dimensions
    so pixel-level comparison can be performed.

    The original images are never modified.
    """

    before = cv2.imread(
        before_path
    )

    after = cv2.imread(
        after_path
    )

    if before is None:
        raise ValueError(
            f"Could not read BEFORE image: {before_path}"
        )

    if after is None:
        raise ValueError(
            f"Could not read AFTER image: {after_path}"
        )

    before_height, before_width = (
        before.shape[:2]
    )

    after_resized = cv2.resize(
        after,
        (
            before_width,
            before_height
        ),
        interpolation=cv2.INTER_AREA
    )

    return before, after_resized


# ============================================================
# MSE
# ============================================================

def calculate_mse(
    before,
    after
):
    """
    Mean Squared Error.
    """

    before_float = (
        before.astype(
            np.float32
        )
    )

    after_float = (
        after.astype(
            np.float32
        )
    )

    mse = np.mean(
        (
            before_float
            - after_float
        ) ** 2
    )

    return float(
        mse
    )


# ============================================================
# PSNR
# ============================================================

def calculate_psnr(
    before,
    after
):
    """
    Peak Signal-to-Noise Ratio.

    Higher value means the two images are
    numerically more similar.
    """

    mse = calculate_mse(
        before,
        after
    )

    if mse == 0:
        return float("inf")

    psnr = (
        10
        * math.log10(
            (255.0 ** 2)
            / mse
        )
    )

    return float(
        psnr
    )


# ============================================================
# SSIM
# ============================================================

def calculate_ssim(
    before,
    after
):
    """
    Simplified grayscale SSIM implementation.

    SSIM evaluates luminance, contrast and structural
    similarity between two aligned images.
    """

    before_gray = cv2.cvtColor(
        before,
        cv2.COLOR_BGR2GRAY
    )

    after_gray = cv2.cvtColor(
        after,
        cv2.COLOR_BGR2GRAY
    )

    before_gray = (
        before_gray.astype(
            np.float64
        )
    )

    after_gray = (
        after_gray.astype(
            np.float64
        )
    )

    kernel_size = 11
    sigma = 1.5

    mu_before = cv2.GaussianBlur(
        before_gray,
        (
            kernel_size,
            kernel_size
        ),
        sigma
    )

    mu_after = cv2.GaussianBlur(
        after_gray,
        (
            kernel_size,
            kernel_size
        ),
        sigma
    )

    mu_before_sq = (
        mu_before
        * mu_before
    )

    mu_after_sq = (
        mu_after
        * mu_after
    )

    mu_before_after = (
        mu_before
        * mu_after
    )

    sigma_before_sq = (
        cv2.GaussianBlur(
            before_gray * before_gray,
            (
                kernel_size,
                kernel_size
            ),
            sigma
        )
        - mu_before_sq
    )

    sigma_after_sq = (
        cv2.GaussianBlur(
            after_gray * after_gray,
            (
                kernel_size,
                kernel_size
            ),
            sigma
        )
        - mu_after_sq
    )

    sigma_before_after = (
        cv2.GaussianBlur(
            before_gray * after_gray,
            (
                kernel_size,
                kernel_size
            ),
            sigma
        )
        - mu_before_after
    )

    c1 = (
        0.01 * 255
    ) ** 2

    c2 = (
        0.03 * 255
    ) ** 2

    numerator = (
        (2 * mu_before_after + c1)
        *
        (2 * sigma_before_after + c2)
    )

    denominator = (
        (mu_before_sq + mu_after_sq + c1)
        *
        (sigma_before_sq + sigma_after_sq + c2)
    )

    ssim_map = (
        numerator
        / (
            denominator
            + 1e-12
        )
    )

    score = float(
        np.mean(
            ssim_map
        )
    )

    score = max(
        0.0,
        min(
            1.0,
            score
        )
    )

    return score


# ============================================================
# DIFFERENCE PERCENTAGE
# ============================================================

def calculate_changed_percentage(
    before,
    after
):
    """
    Calculate the percentage of pixels that changed
    significantly after processing.
    """

    before_gray = cv2.cvtColor(
        before,
        cv2.COLOR_BGR2GRAY
    )

    after_gray = cv2.cvtColor(
        after,
        cv2.COLOR_BGR2GRAY
    )

    difference = cv2.absdiff(
        before_gray,
        after_gray
    )

    changed_pixels = np.sum(
        difference > 10
    )

    total_pixels = difference.size

    if total_pixels == 0:
        return 0.0

    percentage = (
        changed_pixels
        / total_pixels
        * 100
    )

    return float(
        percentage
    )


# ============================================================
# DELTA HELPER
# ============================================================

def calculate_delta(
    before_value,
    after_value
):
    """
    Calculate absolute and percentage change.
    """

    if (
        before_value is None
        or after_value is None
    ):
        return {
            "before": before_value,
            "after": after_value,
            "delta": None,
            "percentage": None
        }

    delta = (
        after_value
        - before_value
    )

    if before_value == 0:
        percentage = None
    else:
        percentage = (
            delta
            / abs(before_value)
            * 100
        )

    return {
        "before": round(
            float(before_value),
            2
        ),
        "after": round(
            float(after_value),
            2
        ),
        "delta": round(
            float(delta),
            2
        ),
        "percentage": (
            round(
                float(percentage),
                2
            )
            if percentage is not None
            else None
        )
    }


# ============================================================
# CREATE COMPARISON PREVIEW
# ============================================================

def create_comparison_preview(
    before_path,
    after_path,
    output_path
):
    """
    Create a side-by-side BEFORE / AFTER preview image.
    """

    before = cv2.imread(
        before_path
    )

    after = cv2.imread(
        after_path
    )

    if before is None:
        raise ValueError(
            "Could not read BEFORE image."
        )

    if after is None:
        raise ValueError(
            "Could not read AFTER image."
        )

    # ----------------------------------------
    # Resize both images to a common display size
    # ----------------------------------------

    display_width = 600
    display_height = 600

    before_display = cv2.resize(
        before,
        (
            display_width,
            display_height
        ),
        interpolation=cv2.INTER_AREA
    )

    after_display = cv2.resize(
        after,
        (
            display_width,
            display_height
        ),
        interpolation=cv2.INTER_AREA
    )

    # ----------------------------------------
    # Labels
    # ----------------------------------------

    before_display = cv2.copyMakeBorder(
        before_display,
        50,
        0,
        0,
        0,
        cv2.BORDER_CONSTANT,
        value=(
            30,
            30,
            30
        )
    )

    after_display = cv2.copyMakeBorder(
        after_display,
        50,
        0,
        0,
        0,
        cv2.BORDER_CONSTANT,
        value=(
            30,
            30,
            30
        )
    )

    cv2.putText(
        before_display,
        "BEFORE - ORIGINAL",
        (
            20,
            35
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (
            255,
            255,
            255
        ),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        after_display,
        "AFTER - AI PROCESSED",
        (
            20,
            35
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (
            255,
            255,
            255
        ),
        2,
        cv2.LINE_AA
    )

    comparison = np.hstack(
        (
            before_display,
            after_display
        )
    )

    os.makedirs(
        os.path.dirname(
            output_path
        ),
        exist_ok=True
    )

    cv2.imwrite(
        output_path,
        comparison
    )


# ============================================================
# BUILD COMPARISON
# ============================================================

def build_comparison(
    before_path,
    after_path,
    before_quality,
    after_quality,
    output_path=None,
    preview_path=None
):
    """
    Build the complete BEFORE / AFTER comparison.
    """

    before_metrics = (
        calculate_basic_metrics(
            before_path
        )
    )

    after_metrics = (
        calculate_basic_metrics(
            after_path
        )
    )

    before_image, after_image = (
        prepare_images(
            before_path,
            after_path
        )
    )

    mse = calculate_mse(
        before_image,
        after_image
    )

    psnr = calculate_psnr(
        before_image,
        after_image
    )

    ssim = calculate_ssim(
        before_image,
        after_image
    )

    changed_percentage = (
        calculate_changed_percentage(
            before_image,
            after_image
        )
    )

    before_score = (
        before_quality.get(
            "overall_score"
        )
        if isinstance(
            before_quality,
            dict
        )
        else None
    )

    after_score = (
        after_quality.get(
            "score"
        )
        if isinstance(
            after_quality,
            dict
        )
        else None
    )

    before_classification = (
        before_quality.get(
            "quality"
        )
        if isinstance(
            before_quality,
            dict
        )
        else None
    )

    after_classification = (
        after_quality.get(
            "quality"
        )
        if isinstance(
            after_quality,
            dict
        )
        else None
    )

    score_change = None

    if (
        before_score is not None
        and after_score is not None
    ):

        score_change = round(
            float(after_score)
            - float(before_score),
            2
        )

    comparison = {

        "created_at": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),

        "before": {

            "path": before_path,

            "quality": before_classification,

            "score": before_score,

            "metrics": before_metrics,

            "quality_report": (
                before_quality
            )
        },

        "after": {

            "path": after_path,

            "quality": after_classification,

            "score": after_score,

            "metrics": after_metrics,

            "quality_report": (
                after_quality
            )
        },

        "improvement": {

            "score_change": score_change,

            "quality_changed": (
                before_classification
                != after_classification
            ),

            "classification": {

                "before": before_classification,

                "after": after_classification

            },

            "metrics": {

                "resolution": {
                    "before": (
                        before_metrics[
                            "width"
                        ],
                        before_metrics[
                            "height"
                        ]
                    ),
                    "after": (
                        after_metrics[
                            "width"
                        ],
                        after_metrics[
                            "height"
                        ]
                    )
                },

                "brightness": (
                    calculate_delta(
                        before_metrics[
                            "brightness"
                        ],
                        after_metrics[
                            "brightness"
                        ]
                    )
                ),

                "contrast": (
                    calculate_delta(
                        before_metrics[
                            "contrast"
                        ],
                        after_metrics[
                            "contrast"
                        ]
                    )
                ),

                "sharpness": (
                    calculate_delta(
                        before_metrics[
                            "sharpness"
                        ],
                        after_metrics[
                            "sharpness"
                        ]
                    )
                )

            }

        },

        "similarity": {

            "mse": round(
                mse,
                2
            ),

            "psnr_db": (
                None
                if math.isinf(psnr)
                else round(
                    psnr,
                    2
                )
            ),

            "ssim": round(
                ssim,
                4
            ),

            "ssim_percent": round(
                ssim * 100,
                2
            ),

            "changed_pixels_percent": round(
                changed_percentage,
                2
            )

        }

    }

    # ----------------------------------------
    # Save comparison JSON
    # ----------------------------------------

    if output_path:

        os.makedirs(
            os.path.dirname(
                output_path
            ),
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                comparison,
                file,
                indent=4,
                ensure_ascii=False
            )

    # ----------------------------------------
    # Save preview
    # ----------------------------------------

    if preview_path:

        create_comparison_preview(
            before_path,
            after_path,
            preview_path
        )

    return comparison