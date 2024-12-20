import pandas as pd
import seaborn as sns  # requires seaborn 0.13.2
import matplotlib.pyplot as plt


path_xiaomi = r"xiaomi_results.csv"
path_hp20 = r"hp20_results.csv"

df_xiaomi = pd.read_csv(path_xiaomi)
df_hp20 = pd.read_csv(path_hp20)

df_xiaomi_melted = df_xiaomi.melt(id_vars="image", var_name="method", value_name="snr")
df_hp20_melted = df_hp20.melt(id_vars="image", var_name="method", value_name="snr")

# Palette 1C7B8B, https://venngage.com/tools/accessible-color-palette-generator
custom_palette = sns.color_palette(["#b8a719", "#9348a4"])  # #5d226f


df_xiaomi_melted["device"] = "Xiaomi 13 Pro"
df_hp20_melted["device"] = "Huawei P20"

# Combine the two dataframes
df_combined = pd.concat([df_xiaomi_melted, df_hp20_melted], ignore_index=True)


fig, ax1 = plt.subplots(figsize=(10, 6))


dodge = 0.5

# Stripplot: Individual data points
sns.stripplot(
    data=df_combined,
    x="method",
    y="snr",
    hue="device",
    dodge=dodge,
    alpha=0.2,
    ax=ax1,
    palette=custom_palette,
)

# Pointplot: Mean values with error bars
sns.pointplot(
    data=df_combined,
    x="method",
    y="snr",
    hue="device",
    dodge=dodge - 0.1,
    join=False,
    ax=ax1,
    palette=custom_palette,
    markers=["_"] * df_combined["device"].nunique(),
    scale=1.5,
)

handles, labels = ax1.get_legend_handles_labels()
ax1.legend(
    handles[: df_combined["device"].nunique()],
    labels[: df_combined["device"].nunique()],
    title="Device",
    loc="upper left",  # Top-left placement
    bbox_to_anchor=(0, 1),  # Anchor to top-left of axes
    frameon=True,  # Optional: Add a frame around the legend
)

# Final adjustments
ax1.set_xlabel("")
ax1.set_ylabel("SNR", fontsize=14)

# Show the plot
plt.tight_layout()
plt.show()



