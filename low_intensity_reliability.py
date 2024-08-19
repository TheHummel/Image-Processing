import os
import pandas as pd
from helpers import get_df_from_csv_folder


def reliability_metrics(csv_metrics_folder: str, output_folder: str) -> None:
    df_single_capture_metrics = get_df_from_csv_folder(csv_metrics_folder)
    print(df_single_capture_metrics)

    # calculate reliability metrics
    mean = df_single_capture_metrics.mean()
    std = df_single_capture_metrics.std()
    cv = std / mean

    # save results to csv file
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "reliability_metrics.csv")
    df = pd.DataFrame({"mean": mean, "std": std, "cv": cv})
    print(df)
    df.to_csv(output_path)


metrics_folder = (
    "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/iso3200expo30_8DC/SNR_outputs_csv"
)
output_folder = (
    "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/iso3200expo30_8DC"
)

reliability_metrics(metrics_folder, output_folder)
