import os
import requests


class DataExtractor:
    def __init__(self, data_url, lookup_url):
        self.data_url = data_url
        self.lookup_url = lookup_url
        self.raw_folder = "data/raw"
        os.makedirs(self.raw_folder, exist_ok=True)

    def download_file(self, url, output_path):
        # Download file dari URL dan simpan ke output_path

        print(f"Downloading: {url}")

        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Saved: {output_path}")

    def extract(self):
        # Download seluruh source data

        taxi_output = os.path.join(self.raw_folder, "yellow_tripdata_2026-01.parquet") #output path taxi
        lookup_output = os.path.join(self.raw_folder, "taxi_zone_lookup.csv") #output path lookup

        #Run Download File
        self.download_file(
            self.data_url,
            taxi_output
        )

        self.download_file(
            self.lookup_url,
            lookup_output
        )

        print("Extraction completed.")


if __name__ == "__main__":

    DATA_URL = os.getenv(
        "DATA_URL",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet"
    )

    LOOKUP_URL = os.getenv(
        "LOOKUP_URL",
        "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    )

    extractor = DataExtractor(
        DATA_URL,
        LOOKUP_URL
    )

    extractor.extract()