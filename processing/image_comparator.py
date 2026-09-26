import math


# ========================================
# HELPER
# ========================================

def _safe_number(value):
    """
    Convert a value to float safely.
    """

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _round(value, digits=2):
    """
    Safely round a numeric value.
    """

    if value is None:
        return None

    return round(
        float(value),
        digits
    )


def _percentage_change(
    original,
    processed
):
    """
    Calculate percentage change.

    Returns None when the original value
    cannot be used as a denominator.
    """

    original = _safe_number(
        original
    )

    processed = _safe_number(
        processed
    )

    if (
        original is None
        or processed is None
    ):
        return None

    if abs(original) < 1e-12:
        return None

    return round(
        (
            (processed - original)
            / abs(original)
        ) * 100,
        2
    )


# ========================================
# QUALITY DIRECTION
# ========================================

def _direction_for_metric(
    metric,
    original,
    processed
):
    """
    Determine whether a metric moved in
    a technically favorable direction.

    This is intentionally conservative.

    Brightness and contrast are not judged
    simply by increasing/decreasing because
    their ideal values depend on the image.
    """

    original = _safe_number(
        original
    )

    processed = _safe_number(
        processed
    )

    if (
        original is None
        or processed is None
    ):
        return "UNKNOWN"

    difference = processed - original

    if abs(difference) < 1e-12:
        return "UNCHANGED"

    if metric in {
        "resolution",
        "sharpness"
    }:

        if difference > 0:
            return "IMPROVED"

        return "DECREASED"

    if metric == "noise":

        if difference < 0:
            return "IMPROVED"

        return "INCREASED"

    return "CHANGED"


# ========================================
# QUALITY CLASSIFICATION
# ========================================

def _quality_rank(quality):
    """
    Convert quality classification into
    an ordered technical level.

    This is used only to describe movement
    between classifications.
    """

    mapping = {
        "POOR": 1,
        "ACCEPTABLE": 2,
        "GOOD": 3
    }

    return mapping.get(
        str(
            quality or ""
        ).upper(),
        0
    )


def compare_quality(
    original_quality,
    processed_quality
):
    """
    Compare two quality classifier results.

    Expected format:

    {
        "quality": "GOOD",
        "score": 96.25,
        "component_scores": {...}
    }
    """

    original_quality = (
        original_quality
        if isinstance(
            original_quality,
            dict
        )
        else {}
    )

    processed_quality = (
        processed_quality
        if isinstance(
            processed_quality,
            dict
        )
        else {}
    )

    original_classification = (
        original_quality.get(
            "quality"
        )
    )

    processed_classification = (
        processed_quality.get(
            "quality"
        )
    )

    original_score = _safe_number(
        original_quality.get(
            "score"
        )
    )

    processed_score = _safe_number(
        processed_quality.get(
            "score"
        )
    )

    score_difference = None

    if (
        original_score is not None
        and processed_score is not None
    ):

        score_difference = round(
            processed_score
            - original_score,
            2
        )

    rank_difference = (
        _quality_rank(
            processed_classification
        )
        -
        _quality_rank(
            original_classification
        )
    )

    if rank_difference > 0:

        classification_change = (
            "IMPROVED"
        )

    elif rank_difference < 0:

        classification_change = (
            "DECREASED"
        )

    else:

        classification_change = (
            "UNCHANGED"
        )

    return {
        "original": {
            "quality": (
                original_classification
            ),
            "score": (
                original_score
            )
        },

        "processed": {
            "quality": (
                processed_classification
            ),
            "score": (
                processed_score
            )
        },

        "score_difference": (
            score_difference
        ),

        "score_percentage_change": (
            _percentage_change(
                original_score,
                processed_score
            )
        ),

        "classification_change": (
            classification_change
        )
    }


# ========================================
# METRIC COMPARISON
# ========================================

def compare_metrics(
    original_metrics,
    processed_metrics
):
    """
    Compare technical metrics from two
    processing stages.
    """

    original_metrics = (
        original_metrics
        if isinstance(
            original_metrics,
            dict
        )
        else {}
    )

    processed_metrics = (
        processed_metrics
        if isinstance(
            processed_metrics,
            dict
        )
        else {}
    )

    comparison = {}

    # ------------------------------------
    # Resolution
    # ------------------------------------

    original_width = _safe_number(
        original_metrics.get(
            "width"
        )
    )

    original_height = _safe_number(
        original_metrics.get(
            "height"
        )
    )

    processed_width = _safe_number(
        processed_metrics.get(
            "width"
        )
    )

    processed_height = _safe_number(
        processed_metrics.get(
            "height"
        )
    )

    original_resolution = None
    processed_resolution = None

    if (
        original_width is not None
        and original_height is not None
    ):

        original_resolution = (
            int(original_width)
            * int(original_height)
        )

    if (
        processed_width is not None
        and processed_height is not None
    ):

        processed_resolution = (
            int(processed_width)
            * int(processed_height)
        )

    comparison["resolution"] = {

        "original": {
            "width": (
                int(original_width)
                if original_width is not None
                else None
            ),
            "height": (
                int(original_height)
                if original_height is not None
                else None
            ),
            "pixels": (
                original_resolution
            )
        },

        "processed": {
            "width": (
                int(processed_width)
                if processed_width is not None
                else None
            ),
            "height": (
                int(processed_height)
                if processed_height is not None
                else None
            ),
            "pixels": (
                processed_resolution
            )
        },

        "pixel_percentage_change": (
            _percentage_change(
                original_resolution,
                processed_resolution
            )
        ),

        "direction": (
            _direction_for_metric(
                "resolution",
                original_resolution,
                processed_resolution
            )
        )
    }

    # ------------------------------------
    # Numeric metrics
    # ------------------------------------

    for metric in [
        "brightness",
        "contrast",
        "sharpness",
        "noise",
        "edge_density"
    ]:

        original_value = (
            _safe_number(
                original_metrics.get(
                    metric
                )
            )
        )

        processed_value = (
            _safe_number(
                processed_metrics.get(
                    metric
                )
            )
        )

        difference = None

        if (
            original_value is not None
            and processed_value is not None
        ):

            difference = round(
                processed_value
                - original_value,
                4
            )

        comparison[metric] = {

            "original": (
                _round(
                    original_value,
                    4
                )
            ),

            "processed": (
                _round(
                    processed_value,
                    4
                )
            ),

            "difference": difference,

            "percentage_change": (
                _percentage_change(
                    original_value,
                    processed_value
                )
            ),

            "direction": (
                _direction_for_metric(
                    metric,
                    original_value,
                    processed_value
                )
            )
        }

    return comparison


# ========================================
# STAGE COMPARISON
# ========================================

def compare_stages(
    original_stage,
    processed_stage
):
    """
    Compare two pipeline stages.

    Example:

        input -> normalized

    Each stage should contain:

        {
            "metrics": {...},
            "quality": {...}
        }
    """

    original_stage = (
        original_stage
        if isinstance(
            original_stage,
            dict
        )
        else {}
    )

    processed_stage = (
        processed_stage
        if isinstance(
            processed_stage,
            dict
        )
        else {}
    )

    original_metrics = (
        original_stage.get(
            "metrics",
            {}
        )
    )

    processed_metrics = (
        processed_stage.get(
            "metrics",
            {}
        )
    )

    original_quality = (
        original_stage.get(
            "quality",
            {}
        )
    )

    processed_quality = (
        processed_stage.get(
            "quality",
            {}
        )
    )

    return {

        "original": {
            "path": original_stage.get(
                "path"
            ),
            "metrics": original_metrics,
            "quality": original_quality
        },

        "processed": {
            "path": processed_stage.get(
                "path"
            ),
            "metrics": processed_metrics,
            "quality": processed_quality
        },

        "quality_comparison": (
            compare_quality(
                original_quality,
                processed_quality
            )
        ),

        "metric_comparison": (
            compare_metrics(
                original_metrics,
                processed_metrics
            )
        )
    }


# ========================================
# COMPLETE REPORT
# ========================================

def build_comparison_report(
    pipeline_result
):
    """
    Build a complete comparison report
    from the result returned by process_image().

    Comparisons are generated against the
    original input image.

    Supported stages:

        restored
        cleaned
        normalized
    """

    if not isinstance(
        pipeline_result,
        dict
    ):

        raise ValueError(
            "Pipeline result must be a dictionary."
        )

    input_stage = (
        pipeline_result.get(
            "input"
        )
    )

    if not isinstance(
        input_stage,
        dict
    ):

        raise ValueError(
            "Pipeline result does not contain input stage."
        )

    comparisons = {}

    stage_names = [
        "restored",
        "cleaned",
        "normalized"
    ]

    for stage_name in stage_names:

        stage = (
            pipeline_result.get(
                stage_name
            )
        )

        if not isinstance(
            stage,
            dict
        ):
            continue

        if not stage.get(
            "metrics"
        ):
            continue

        comparisons[
            stage_name
        ] = compare_stages(
            input_stage,
            stage
        )

    # ------------------------------------
    # Final stage
    # ------------------------------------

    final_stage_name = None

    for candidate in [
        "normalized",
        "cleaned",
        "restored"
    ]:

        if candidate in comparisons:

            final_stage_name = (
                candidate
            )

            break

    final_comparison = None

    if final_stage_name:

        final_comparison = (
            comparisons[
                final_stage_name
            ]
        )

    return {

        "version": "1.0",

        "comparison_type": (
            "original_vs_processed"
        ),

        "original": {
            "path": input_stage.get(
                "path"
            ),
            "metrics": input_stage.get(
                "metrics",
                {}
            ),
            "quality": input_stage.get(
                "quality",
                {}
            )
        },

        "stages": comparisons,

        "final_stage": (
            final_stage_name
        ),

        "final_comparison": (
            final_comparison
        )
    }