def _score_resolution(width, height):
    """
    Score image resolution.

    The current dataset mainly contains small source images,
    so resolution is treated as a technical limitation rather
    than a direct measure of visual quality.
    """

    min_dimension = min(
        width,
        height
    )

    if min_dimension >= 120:
        return 100.0

    if min_dimension >= 90:
        return 85.0

    if min_dimension >= 60:
        return 70.0

    if min_dimension >= 40:
        return 50.0

    return 30.0


def _score_brightness(brightness):
    """
    Score brightness.

    Moderate brightness receives a higher score.
    Very dark or very bright images receive lower scores.
    """

    if 100 <= brightness <= 180:
        return 100.0

    if 90 <= brightness < 100:
        return 85.0

    if 180 < brightness <= 195:
        return 85.0

    if 80 <= brightness < 90:
        return 65.0

    if 195 < brightness <= 210:
        return 65.0

    return 40.0


def _score_contrast(contrast):
    """
    Score grayscale contrast.

    Extremely low contrast can make patterns difficult
    to distinguish. Extremely high contrast can indicate
    harsh tonal separation.

    This is a technical heuristic.
    """

    if 40 <= contrast <= 90:
        return 100.0

    if 35 <= contrast < 40:
        return 85.0

    if 90 < contrast <= 100:
        return 85.0

    if 30 <= contrast < 35:
        return 70.0

    if 100 < contrast <= 110:
        return 70.0

    return 50.0


def _score_noise(noise):
    """
    Lower estimated noise receives a higher score.
    """

    if noise <= 8:
        return 100.0

    if noise <= 15:
        return 85.0

    if noise <= 22:
        return 70.0

    if noise <= 30:
        return 50.0

    return 30.0


def classify_quality(metrics):
    """
    Classify technical image quality.

    Main factors:
        - Resolution
        - Brightness
        - Contrast
        - Noise

    Sharpness and edge density are intentionally not used
    as primary quality factors because they are strongly
    dependent on image content and texture.

    Returns:
        quality
        score
        component_scores
    """

    width = metrics["width"]
    height = metrics["height"]
    brightness = metrics["brightness"]
    contrast = metrics["contrast"]
    noise = metrics["noise"]

    resolution_score = _score_resolution(
        width,
        height
    )

    brightness_score = _score_brightness(
        brightness
    )

    contrast_score = _score_contrast(
        contrast
    )

    noise_score = _score_noise(
        noise
    )

    # --------------------------------------------------------
    # Weighted technical quality score
    # --------------------------------------------------------

    score = (
        resolution_score * 0.25
        + brightness_score * 0.20
        + contrast_score * 0.25
        + noise_score * 0.30
    )

    score = round(
        score,
        2
    )

    # --------------------------------------------------------
    # Quality classification
    # --------------------------------------------------------

    if score >= 80:
        quality = "GOOD"

    elif score >= 60:
        quality = "ACCEPTABLE"

    else:
        quality = "POOR"

    return {
        "quality": quality,
        "score": score,
        "component_scores": {
            "resolution": round(
                resolution_score,
                2
            ),
            "brightness": round(
                brightness_score,
                2
            ),
            "contrast": round(
                contrast_score,
                2
            ),
            "noise": round(
                noise_score,
                2
            )
        }
    }