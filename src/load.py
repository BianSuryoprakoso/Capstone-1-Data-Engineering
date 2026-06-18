import os
import pandas as pd


class DataLoader:
    def __init__(self):
        self.transformed_folder = "data/transformed"
        self.mart_folder = "data/mart"
        os.makedirs(self.mart_folder, exist_ok=True)

    def load_data(self):
        #Baca hasil transformasi dari folder transformed
        input_path = os.path.join(self.transformed_folder, "transformed_tripdata.parquet")

        print("Loading transformed data...")
        self.df = pd.read_parquet(input_path)
        print(f"Data loaded: {len(self.df)} rows")

    def save(self):
        #Simpan data ke folder mart dalam format CSV
        output_path = os.path.join(self.mart_folder, "tripdata_mart.csv")

        print("Saving to CSV...")
        self.df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

    def run(self):
        # run semua method
        self.load_data()
        self.save()
        print("Load completed.")


if __name__ == "__main__":
    loader = DataLoader()
    loader.run()