import sys
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.exception import CustomException
from src.logger import logging
from src.components.model_trainer import ModelTrainer
class TrainPipeline:
    def run_pipeline(self):
        try:
            logging.info("Training Pipeling Started")

            ingestion = DataIngestion()
            train_data_path, test_data_path = ingestion.initiate_data_ingestion()

            data_transformation = DataTransformation()
            X_train, X_test, y_train, y_test, preprocessor_path = data_transformation.initiate_data_transformation(
                train_data_path, test_data_path
            )

            model_trainer = ModelTrainer()
            accuracy = model_trainer.initiate_model_trainer(
                X_train=X_train,
                X_test=X_test,
                y_train=y_train,
                y_test=y_test
            )


            logging.info(f"Pipeline Finished Successfully with accuracy{accuracy:.4f}")

        except Exception as e:
            raise CustomException(error_message=e, error_detail=sys)

if __name__ == "__main__":
    obj = TrainPipeline()
    obj.run_pipeline()
