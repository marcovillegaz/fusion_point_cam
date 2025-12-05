# yaml_loader.py
import yaml
from des_sle.data.component import Component  # adjust path


def load_mixture(yaml_path, mixture_name):
    """
    Loads a mixture from a YAML file and returns:
      - list of Component objects
      - dict of NRTL parameters
    """
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    mixtures = data["mixtures"]

    if mixture_name not in mixtures:
        raise ValueError(f"Mixture '{mixture_name}' not found in {yaml_path}")

    mixture_data = mixtures[mixture_name]

    # Build component objects
    components = [
        Component(
            name=c["name"], Tm=c["Tm"], dHfus=c["dHfus"], MW=c.get("MW"), formula=c.get("formula")
        )
        for c in mixture_data["components"]
    ]

    # Extract NRTL parameters
    params = mixture_data["nrtl_params"]

    return components, params
