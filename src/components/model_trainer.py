from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.utils.class_weight import compute_sample_weight
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
                'max_depth': 26,
                'max_features': 'sqrt',
                'min_samples_leaf': 5,
                'n_estimators': 500,
            }

            # Step A: dimensionality reduction with TruncatedSVD (works with sparse input)
            n_features = getattr(X_train, 'shape', (None, None))[1] or None
            if n_features is None:
                n_components = 300
            else:
                # ensure n_components < n_features to avoid errors
                n_components = min(300, max(1, n_features - 1))

            logging.info(f"Applying TruncatedSVD with n_components={n_components} to reduce dimensionality...")
            svd = TruncatedSVD(n_components=n_components, random_state=42)
            X_train_reduced = svd.fit_transform(X_train)
            X_test_reduced = svd.transform(X_test)

            # persist the SVD transformer for later use in prediction pipeline
            try:
                save_object(file_path=os.path.join('artifacts', 'svd.pkl'), obj=svd)
            except Exception:
                logging.warning('Unable to save svd transformer to artifacts/svd.pkl')

            # compute balanced sample weights for training
            sample_weight = compute_sample_weight('balanced', y_train)

            logging.info("Training final Random Forest model with best parameters...")
            final_rf_estimator = RandomForestClassifier(
                n_estimators=best_params['n_estimators'],
                max_depth=best_params['max_depth'],
                min_samples_leaf=best_params['min_samples_leaf'],
                max_features=best_params['max_features'],
                random_state=42,
                n_jobs=-1
            )

            logging.info("Calibrating classifier with isotonic calibration and cv=5...")
            calibrated_model = CalibratedClassifierCV(
                estimator=final_rf_estimator,
                method='isotonic',
                cv=5
            )
            # pass sample_weight so the base estimator sees balanced weights
            calibrated_model.fit(X_train_reduced, y_train, sample_weight=sample_weight)

            logging.info("Model Training & Calibration Completed. Evaluating performance...")

            predicted = calibrated_model.predict(X_test_reduced)
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
