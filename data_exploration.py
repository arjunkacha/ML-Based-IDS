import os
import pandas as pd

# ✅ Set the path to your dataset folder
DATA_FOLDER = 'MachineLearningCSV/MachineLearningCVE'


def load_all_csvs(folder_path):
    dataframes = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            print(f"🔹 Loading: {filename}")
            df = pd.read_csv(file_path)
            df['source_file'] = filename  # Optional: track file origin
            dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True)


def explore_dataset(df):
    print("\n✅ Shape of Dataset:", df.shape)

    print("\n✅ First 5 Rows:")
    print(df.head())

    print("\n✅ Columns:")
    print(df.columns.tolist())

    print("\n✅ Null Values:")
    print(df.isnull().sum())

    print("\n✅ Label Distribution:")
    label_col = [col for col in df.columns if 'label' in col.lower()]
    if label_col:
        print(df[label_col[0]].value_counts())
    else:
        print("❗ No label column found.")


if __name__ == "__main__":
    df = load_all_csvs(DATA_FOLDER)
    explore_dataset(df)
