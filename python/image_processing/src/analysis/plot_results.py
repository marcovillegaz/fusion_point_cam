import matplotlib.pyplot as plt


def plot_temperature_vs_metric(df, metric_col):
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(df["temperature"], df[metric_col], marker=".")
    ax1.set_xlabel("Temperature °C")
    ax1.set_ylabel(metric_col)
    plt.title(f"Temperature vs {metric_col.capitalize()}")
    plt.grid(True)
    plt.show()


def plot_time_series(df, metric_col):
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.set_xlabel("Time [sec]")

    # Plot temperature on left y-axis
    color1 = "tab:red"
    ax1.set_ylabel("Temperature (°C)", color=color1)
    ax1.plot(df["time"] / 1000, df["temperature"], color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)

    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()

    # Plot metric on right y-axis
    color2 = "tab:green"
    ax2.set_ylabel(metric_col.capitalize(), color=color2)
    ax2.plot(df["time"] / 1000, df[metric_col], color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)

    plt.title(f"Time series of temperature and {metric_col}")
    plt.grid(True)
    plt.show()


def plot_slope_and_peaks(time, slope, peaks):
    plt.figure(figsize=(8, 4))
    plt.plot(time[1:], slope, label="Slope")
    plt.scatter(time[1:][peaks], slope[peaks], color="red", label="Peaks")
    plt.xlabel("Time")
    plt.ylabel("Slope")
    plt.title("Slope of Smoothed Metric with Detected Peaks")
    plt.legend()
    plt.grid(True)
    plt.show()
