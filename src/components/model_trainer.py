from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
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
    
    def initiate_model_trainer(self, X_train, X_test, y_train, y_test):
        try:
            logging.info("Received X_train, X_test, y_train, y_test for training...")

            logging.info("Starting Random Forest model training...")

            best_n_estimators = 500
            best_max_depth = None

            best_params = {
                'class_weight': 'balanced',
                'max_depth': 16,
                'max_features': 'sqrt',
                'min_samples_leaf': 5,
                'n_estimators': 500,
            }

            logging.info("Training final Random Forest model with best parameters...")
            final_rf_estimator = RandomForestClassifier(
                n_estimators=best_params['n_estimators'],
                max_depth=best_params['max_depth'],
                min_samples_leaf=best_params['min_samples_leaf'],
                max_features=best_params['max_features'],
                random_state=42,
                class_weight=best_params['class_weight'],
                n_jobs=-1
            )

            logging.info("Calibrating classifier with isotonic calibration and cv=5...")
            calibrated_model = CalibratedClassifierCV(
                estimator=final_rf_estimator,
                method='isotonic',
                cv=5
            )
            calibrated_model.fit(X_train, y_train)

            logging.info("Model Training & Calibration Completed. Evaluating performance...")

            predicted = calibrated_model.predict(X_test)
            accuracy = accuracy_score(y_test, predicted)

            logging.info(f"Calibrated Model Accuracy: {accuracy:.4f}")
            logging.info(f"Classification report:\n {classification_report(y_test, predicted)}")

            save_object(
                file_path=self.model_trainer_config.trained_model_filepath,
                obj=calibrated_model
            )
            return accuracy
        except Exception as e:
            raise CustomException(e, sys)
