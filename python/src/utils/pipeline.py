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
