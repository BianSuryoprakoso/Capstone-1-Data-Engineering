import os
import pandas as pd


class DataTransformer:
    def __init__(self):
        self.raw_folder = "data/raw"
        self.transformed_folder = "data/transformed"
        os.makedirs(self.transformed_folder, exist_ok=True)

    def load_data(self):
        #Baca file parquet dan CSV dari folder raw
        taxi_path = os.path.join(self.raw_folder, "yellow_tripdata_2026-01.parquet")
        lookup_path = os.path.join(self.raw_folder, "taxi_zone_lookup.csv")

        print("Loading data...")
        self.df = pd.read_parquet(taxi_path)
        self.lookup_df = pd.read_csv(lookup_path)
        print(f"Data loaded: {len(self.df)} rows & {self.df.shape[1]} columns")

    def standardize_schema(self):
        print("Standardizing...")

        # Rename kolom ke snake_case
        self.df.columns = (
            self.df.columns
            .str.replace(r'(?<=[a-z])(?=[A-Z])', '_', regex=True)  # camelCase → snake
            .str.lower()
        )

        #print(self.df.columns.tolist())

        # Rename manual kolom yang tidak tertangkap regex
        self.df = self.df.rename(columns={
            "vendorid": "vendor_id",
            "ratecodeid": "ratecode_id",
            "pulocation_id": "pu_location_id",
            "dolocation_id": "do_location_id",
        })

        # Pastikan datetime
        self.df["tpep_pickup_datetime"] = pd.to_datetime(self.df["tpep_pickup_datetime"])
        self.df["tpep_dropoff_datetime"] = pd.to_datetime(self.df["tpep_dropoff_datetime"])

        # Pastikan float
        for col in ["fare_amount", "tip_amount", "total_amount"]:
            self.df[col] = self.df[col].astype(float)

        print("Schema standardized.")

    def transform_datetime(self):
        #Tambah kolom-kolom dari datetime
        print("Transforming datetime...")

        self.df["trip_duration_minutes"] = (
            self.df["tpep_dropoff_datetime"] - self.df["tpep_pickup_datetime"]
        ).dt.total_seconds() / 60

        self.df["pickup_date"] = self.df["tpep_pickup_datetime"].dt.date
        self.df["pickup_hour"] = self.df["tpep_pickup_datetime"].dt.hour
        self.df["pickup_day_name"] = self.df["tpep_pickup_datetime"].dt.day_name()
        self.df["is_weekend"] = self.df["pickup_day_name"].isin(["Saturday", "Sunday"])

        def categorize_time(hour):
            if 0 <= hour <= 5:
                return "Late Night"
            elif 6 <= hour <= 10:
                return "Morning"
            elif 11 <= hour <= 15:
                return "Afternoon"
            elif 16 <= hour <= 19:
                return "Evening Rush"
            else:
                return "Night"

        self.df["time_period"] = self.df["pickup_hour"].apply(categorize_time)

        print("Datetime transformed.")

    def categorical_mapping(self):
        #Mapping kode angka menjadi label 
        print("Mapping categorical columns...")

        payment_map = {
            1: "Credit Card",
            2: "Cash",
            3: "No Charge",
            4: "Dispute",
            0: "Unknown"
        }
        self.df["payment_type"] = self.df["payment_type"].map(payment_map).fillna("Unknown")

        flag_map = {
            "Y": "Store and Forward",
            "N": "Normal"
        }
        self.df["store_and_fwd_flag"] = self.df["store_and_fwd_flag"].map(flag_map).fillna("Normal")

        print("Categorical mapping done.")

    def map_location(self):
        #Join dengan taxi zone lookup untuk mapping lokasi
        print("Mapping locations...")

        # Standarisasi kolom lookup
        self.lookup_df.columns = self.lookup_df.columns.str.lower()
        self.lookup_df = self.lookup_df.rename(columns={"locationid": "location_id"})

        # Join untuk pickup location
        self.df = self.df.merge(
            self.lookup_df.rename(columns={
                "location_id": "pu_location_id",
                "borough": "pickup_borough",
                "zone": "pickup_zone",
                "service_zone": "pickup_service_zone"
            }),
            on="pu_location_id",
            how="left"
        )

        # Join untuk dropoff location
        self.df = self.df.merge(
            self.lookup_df.rename(columns={
                "location_id": "do_location_id",
                "borough": "dropoff_borough",
                "zone": "dropoff_zone",
                "service_zone": "dropoff_service_zone"
            }),
            on="do_location_id",
            how="left"
        )

        print("Location mapping done.")

    def save(self):
        #Simpan hasil transformasi ke folder transformed
        output_path = os.path.join(self.transformed_folder, "transformed_tripdata.parquet")
        self.df.to_parquet(output_path, index=False)
        print(f"Saved to {output_path}")

    def run(self):
        #Run semua method
        self.load_data()
        self.standardize_schema()
        self.transform_datetime()
        self.categorical_mapping()
        self.map_location()
        self.save()
        print("Transformation completed.")


if __name__ == "__main__":
    transformer = DataTransformer()
    transformer.run()