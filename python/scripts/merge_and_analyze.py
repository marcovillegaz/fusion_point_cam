from src.analysis.plot_results import *
from src.analysis.io import *

experiment = "test4"


plot_time_series(
    df=load_data(experiment, "contrast_rms.csv"),
    metric_col="contrast_rms",
)

plot_temperature_vs_metric(
    df=load_data(experiment, "contrast_rms.csv"),
    metric_col="contrast_rms",
)

plot_time_series(
    df=load_data(experiment, "brightness_stats.csv"),
    metric_col="brightness",
)
