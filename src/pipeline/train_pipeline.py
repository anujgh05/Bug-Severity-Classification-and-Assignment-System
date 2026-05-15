import sys
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.exception import CustomException
from src.logger import logging

class TrainPipeline:
    def run_pipeline(self):
        try:
            logging.info("Training Pipeling Started")

            ingestion = DataIngestion()
            train_data_path, test_data_path = ingestion.initiate_data_ingestion()

            data_transformation = DataTransformation()
            train_arr, test_arr, preprocessor_path = data_transformation.initiate_data_transformation(
                train_data_path, test_data_path
            )

            '''
            For Model Training
            '''

            logging.info("Pipeline Finished Successfully")

        except Exception as e:
            raise CustomException(error_message=e, error_detail=sys)

if __name__ == "__main__":
    obj = TrainPipeline()
    obj.run_pipeline()
