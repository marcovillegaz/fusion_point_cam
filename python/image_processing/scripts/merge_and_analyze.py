from mpc_img_processing.analysis import plot_time_series, load_data

experiment = "test4"


plot_time_series(
    df=load_data(experiment, "contrast_rms.csv"),
    metric_col="contrast_rms",
)

plot_time_series(
    df=load_data(experiment, "brightness_stats.csv"),
    metric_col="brightness",
)
