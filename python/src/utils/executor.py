from collections import OrderedDict


def execute_pipeline_steps(input_data, steps: OrderedDict, abort_on_none=True):
    """
    Executes a pipeline of steps on the input data.

    Parameters:
        input_data: Any object (e.g., image, list, dict) to be processed
        steps (OrderedDict): Key=step name, Value=function to apply
        abort_on_none (bool): If True, aborts if any step returns None

    Returns:
        OrderedDict of intermediate results, or None if aborted
    """
    results = OrderedDict()
    current = input_data

    for name, step in steps.items():
        current = step(current)
        if current is None and abort_on_none:
            return None
        results[name] = current

    return results


def execute_postprocess(input_data, steps, output_path, abort_on_none=True):
    """
    Executes a list of function that compute metric of a batch of images.

    Parameters:
        images (list): List of (img, filename) tuples from ImagePipeline
        steps (OrderedDict): step name → function(images) -> DataFrame
        output_folder (str): Where to save the resulting CSVs

    Returns:
        OrderedDict of intermediate results, or None if aborted
    """

    results = OrderedDict()
    current = input_data

    for name, step_fn in steps.items():
        result = step_fn(current)  # whole batch is passed
        if result is None and abort_on_none:
            return None
        results[name] = result
        current = result  # result passed to next step

    return results
