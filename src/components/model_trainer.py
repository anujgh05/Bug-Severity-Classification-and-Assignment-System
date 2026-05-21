from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from dataclasses import dataclass
import os
import sys
from src.utils import save_object
from src.exception import CustomException
from src.logger import logging

@dataclass
class ModelTrainerConfig:
    trained_model_filepath = os.path.join('artifacts', "model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
    
    def initiate_model_trainer(self, train_arr, test_arr):
        try:
            logging.info("Splitting the dependent and independent variables")

            X_train, y_train, X_test, y_test = (
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )

            logging.info("Starting SVM..")

            model = SVC(kernel='rbf',C=10 ,probability=True, class_weight='balanced')
            model.fit(X_train, y_train)

            logging.info("Model Training Completed. Evaluating performance")

            predicted = model.predict(X_test)
            accuracy = accuracy_score(y_test, predicted)

            logging.info(f"Model Accuracy:{accuracy}")
            logging.info(f"Classification report:\n {classification_report(y_test,predicted)}")

            save_object(
                file_path=self.model_trainer_config.trained_model_filepath,
                obj=model
            )
            return accuracy
        except Exception as e:
            raise CustomException(e,sys)