import os
import sys
from src.exception import CustomException
from src.logger import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
import requests
import json


@dataclass
class DataIngestionConfig:
    train_data_path: str=os.path.join('artifacts', 'train.csv')
    test_data_path: str=os.path.join('artifacts', 'test.csv')
    raw_data_path: str=os.path.join('artifacts', 'raw_data.csv')


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        if os.path.exists(self.ingestion_config.raw_data_path):
            logging.info("Data already exists in arifacts. Skipping downloading")
            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        logging.info("Entered the data ingestion method")
        try:
            url = "https://bugzilla.mozilla.org/rest/bug"
            params = {
            'status': 'RESOLVED',
            'limit': 10000,
            'include_fields': 'id,summary,description,severity,assigned_to'
            }

            response = requests.get(url, params=params)
            data = response.json()
            df = pd.DataFrame(data['bugs'])
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path),exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path,index=False,header=True)
            
            logging.info("Saved raw data and starting train test split")

            train_set, test_set=train_test_split(df,test_size=0.2,random_state=42)

            train_set.to_csv(self.ingestion_config.train_data_path,index=False,header=True)

            test_set.to_csv(self.ingestion_config.test_data_path,index=False,header=True)

            logging.info("Ingestion of the data is completed")

            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
            )
        except Exception as e:
            raise CustomException(e,sys)

if __name__ == "__main__":
    obj = DataIngestion()
    obj.initiate_data_ingestion()

