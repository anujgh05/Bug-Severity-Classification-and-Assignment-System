import os
import sys
from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

from src.exception import CustomException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    train_data_path: str = os.path.join('artifacts', 'train.csv')
    test_data_path: str = os.path.join('artifacts', 'test.csv')
    cleaned_data_path: str = os.path.join('artifacts', 'cleaned_bug_dataset.csv')


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Entered the data ingestion method")
        try:
            if not os.path.exists(self.ingestion_config.cleaned_data_path):
                raise FileNotFoundError(
                    f"Cleaned dataset not found at {self.ingestion_config.cleaned_data_path}"
                )

            logging.info(f"Loading data from {self.ingestion_config.cleaned_data_path}")
            df = pd.read_csv(self.ingestion_config.cleaned_data_path)
            if 'short_desc' in df.columns:
                df.dropna(subset=['short_desc'], inplace=True)
            df.reset_index(drop=True, inplace=True)

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)
            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header=True)

            logging.info("Ingestion of cleaned dataset completed")
            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
            )
        except Exception as e:
            raise CustomException(e, sys)

