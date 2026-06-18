import os
import pandas as pd


class DataQualityChecker:
    def __init__(self):
        self.mart_folder = "data/mart"
        self.mart_cleaned_folder = "data/mart_cleaned"
        os.makedirs(self.mart_cleaned_folder, exist_ok=True)

    def load_data(self):
        #Baca data dari folder mart
        input_path = os.path.join(self.mart_folder, "tripdata_mart.csv")

        print("Loading data from mart...")
        self.df = pd.read_csv(input_path)
        print(f"Data loaded: {len(self.df)} rows")

    def validate(self):
        """Validasi durasi dan jarak, pisahkan data valid dan invalid."""
        print("Validating data...")

        self.df["error_type"] = None

        # Validasi durasi > 0
        invalid_duration = self.df["trip_duration_minutes"] <= 0
        self.df.loc[invalid_duration, "error_type"] = "duration invalid"

        # Validasi jarak > 0 (hanya tandai kalau belum ada error_type sebelumnya)
        invalid_distance = (self.df["trip_distance"] <= 0) & (self.df["error_type"].isnull())
        self.df.loc[invalid_distance, "error_type"] = "distance invalid"

        # Pisahkan data valid dan invalid
        self.df_valid = self.df[self.df["error_type"].isnull()].drop(columns=["error_type"])
        self.df_invalid = self.df[self.df["error_type"].notnull()]

        print(f"Valid rows: {len(self.df_valid)}")
        print(f"Invalid rows: {len(self.df_invalid)}")

    def save(self):
        #Simpan data valid dan karantina ke folder mart_cleaned
        valid_path = os.path.join(self.mart_cleaned_folder, "tripdata_valid.csv")
        quarantine_path = os.path.join(self.mart_cleaned_folder, "tripdata_quarantine.csv")

        self.df_valid.to_csv(valid_path, index=False)
        self.df_invalid.to_csv(quarantine_path, index=False)

        print(f"Saved valid data to {valid_path}")
        print(f"Saved quarantine data to {quarantine_path}")

    def generate_report(self):
        #report sederhana hasil temuan 
        report_path = os.path.join(self.mart_cleaned_folder, "data_quality_report.txt")

        total_rows = len(self.df)
        valid_rows = len(self.df_valid)
        invalid_rows = len(self.df_invalid)

        error_summary = self.df_invalid["error_type"].value_counts()

        with open(report_path, "w") as f:
            f.write("DATA QUALITY REPORT\n")
            f.write("=" * 40 + "\n")
            f.write(f"Total rows processed : {total_rows}\n")
            f.write(f"Valid rows            : {valid_rows} ({valid_rows/total_rows:.2%})\n")
            f.write(f"Invalid rows          : {invalid_rows} ({invalid_rows/total_rows:.2%})\n")
            f.write("\nBreakdown by error type:\n")
            for error_type, count in error_summary.items():
                f.write(f"  - {error_type}: {count}\n")

        print(f"Report saved to {report_path}")

    def run(self):
        #run semua method
        self.load_data()
        self.validate()
        self.save()
        self.generate_report()
        print("Data quality check completed.")


if __name__ == "__main__":
    checker = DataQualityChecker()
    checker.run()