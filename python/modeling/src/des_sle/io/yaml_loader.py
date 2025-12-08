# yaml_loader.py
import yaml
from pathlib import Path
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


def save_fitted_parameters(
    filepath,
    mixture_name,
    components,
    nrtl_params,
    fitting_info=None,
):
    """
    Save fitted NRTL parameters to a YAML file.

    Args:
        filepath: Path to output YAML file
        mixture_name: Name for this mixture in the YAML
        components: List of Component objects
        nrtl_params: Dictionary with keys 'g12', 'g21', 'alpha12'
        fitting_info: Optional dictionary with fitting metadata (method, rmse, etc.)
    """
    # Prepare component data
    component_data = [
        {
            "name": comp.name,
            "Tm": float(comp.Tm),
            "dHfus": float(comp.dHfus),
        }
        for comp in components
    ]

    # Add optional fields if present
    for i, comp in enumerate(components):
        if hasattr(comp, "MW") and comp.MW is not None:
            component_data[i]["MW"] = float(comp.MW)
        if hasattr(comp, "formula") and comp.formula is not None:
            component_data[i]["formula"] = comp.formula

    # Prepare NRTL parameters
    nrtl_data = {
        "g12": float(nrtl_params["g12"]),
        "g21": float(nrtl_params["g21"]),
        "alpha12": float(nrtl_params["alpha12"]),
    }

    # Build YAML structure
    yaml_data = {
        "mixtures": {
            mixture_name: {
                "components": component_data,
                "nrtl_params": nrtl_data,
            }
        }
    }

    # Add fitting info if provided
    if fitting_info is not None:
        # Convert numpy types to Python types
        fitting_info_clean = {}
        for key, value in fitting_info.items():
            if hasattr(value, "item"):  # numpy scalar
                fitting_info_clean[key] = value.item()
            elif isinstance(value, dict):
                # Recursively clean nested dicts
                fitting_info_clean[key] = {
                    k: v.item() if hasattr(v, "item") else v for k, v in value.items()
                }
            else:
                fitting_info_clean[key] = value

        yaml_data["mixtures"][mixture_name]["fitting_info"] = fitting_info_clean

    # Ensure parent directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    with open(filepath, "w") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
