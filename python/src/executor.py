def run_pipeline(image, steps):
    """
    Run a sequence of processing steps on an image.

    Args:
        image: Input image (numpy array)
        steps: Ordered dict or list of (name, function) pairs

    Returns:
        Dict with all intermediate results, including original image.
    """
    results = {"original": image}
    current = image
    for name, step in steps.items():
        current = step(current)
        results[name] = current
    return results
