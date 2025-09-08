"""
HELPER SCRIPT (Fig. 2f):
Given outputs for n total runs, read all output csvs and create a summary csv containing means for RAW, ROF columns and last outputs of NREA runs
"""

import os
import pandas as pd
from natsort import natsorted

# input path to root of all runs / series folders
input_dir = ""


df_summary = pd.DataFrame(
    columns=[
        "series",
        "RAW_SNR",
        "RAW_Signal",
        "RAW_Noise",
        "ROF_SNR",
        "ROF_Signal",
        "ROF_Noise",
        "NREA_SNR",
        "NREA_Signal",
        "NREA_Noise",
        "NREA_ROF_SNR",
        "NREA_ROF_Signal",
        "NREA_ROF_Noise",
    ]
)

df_all = pd.DataFrame(
    columns=[
        "series",
        "RAW_SNR",
        "RAW_Signal",
        "RAW_Noise",
        "ROF_SNR",
        "ROF_Signal",
        "ROF_Noise",
        "NREA_SNR",
        "NREA_Signal",
        "NREA_Noise",
        "NREA_ROF_SNR",
        "NREA_ROF_Signal",
        "NREA_ROF_Noise",
    ]
)

for dirname in os.listdir(input_dir):
    dir_path = os.path.join(input_dir, dirname)
    if os.path.isdir(dir_path):
        metrics_file = os.path.join(
            dir_path, "cropped3", "channel_0", "metrics_overview.csv"
        )
        if os.path.exists(metrics_file):
            df = pd.read_csv(metrics_file)
            # calc the mean of the RAW and ROF columns
            new_row = (
                df[
                    [
                        "RAW_SNR",
                        "RAW_Signal",
                        "RAW_Noise",
                        "ROF_SNR",
                        "ROF_Signal",
                        "ROF_Noise",
                    ]
                ]
                .mean()
                .to_frame()
                .T
            )
            # the values for the remaining columns are the entries of the last rof of df
            new_row["series"] = dirname
            new_row["NREA_SNR"] = df["NREA_SNR"].iloc[-1]
            new_row["NREA_Signal"] = df["NREA_Signal"].iloc[-1]
            new_row["NREA_Noise"] = df["NREA_Noise"].iloc[-1]
            new_row["NREA_ROF_SNR"] = df["NREA_ROF_SNR"].iloc[-1]
            new_row["NREA_ROF_Signal"] = df["NREA_ROF_Signal"].iloc[-1]
            new_row["NREA_ROF_Noise"] = df["NREA_ROF_Noise"].iloc[-1]
            # append the new row to df_all

            df_summary = pd.concat([df_summary, new_row], ignore_index=True)

            # df_all contains ALL data, not just the mean
            # drop col in df if "Unnamed" in the column name
            df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])
            df["series"] = dirname
            df_all = pd.concat([df_all, df], ignore_index=True)

# sort dfs by series name by natsort
sorted_indices_summary = natsorted(
    df_summary.index, key=lambda x: df_summary.loc[x, "series"]
)
df_summary = df_summary.reindex(sorted_indices_summary).reset_index(drop=True)

sorted_indices = natsorted(df_all.index, key=lambda x: df_all.loc[x, "series"])
df_all = df_all.reindex(sorted_indices).reset_index(drop=True)


# save dfs to csv files
output_file_summary = os.path.join(input_dir, "metrics_summary.csv")
df_summary.to_csv(output_file_summary, index=False)
print(f"Saved all metrics overview to {output_file_summary}")

output_file_all = os.path.join(input_dir, "metrics_all.csv")
df_all.to_csv(output_file_all, index=False)
print(f"Saved summary metrics overview to {output_file_all}")
