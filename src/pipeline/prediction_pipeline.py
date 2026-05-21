import sys
from dataclasses import dataclass
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import os
from src.utils import load_object
from sklearn.feature_extraction.text import TfidfVectorizer
from src.exception import CustomException
from src.logger import logging

class PredictPipeline:
    def __init__(self):
        try:
            logging.info("Initializing PredictPipeline: Loading ML models into memory...")
            self.model_path=os.path.join("artifacts","model.pkl")
            self.preprocessor_path=os.path.join("artifacts","preprocessor.pkl")

            self.model = load_object(file_path=self.model_path)
            self.preprocessor = load_object(file_path=self.preprocessor_path)

            self.decode_map = {3: "Critical", 2: "High", 1: "Medium", 0: "Low"}
            self.lemmatizer = WordNetLemmatizer()

            self.stop_word = set(stopwords.words("english"))
            logging.info("PredictPipeline initialization successful. Models loaded.")
        except Exception as e:
            raise CustomException(e, sys)

    def clean_text(self, text):
        try:
            if not isinstance(text, str):
                return ""
            
            text = text.lower()
            text = re.sub(r'[^a-z\s]','',text)
            words = text.split()
            words = [self.lemmatizer.lemmatize(w) for w in words if w not in self.stop_word]
            return " ".join(words)

        except Exception as e:
            raise CustomException(e, sys)
     
    def predict(self, summary, description):
        try:
            combined_text = f"{summary} {description}"
            cleaned_text = self.clean_text(combined_text)

            numerical_vector = self.preprocessor.transform([cleaned_text]).toarray()
            
            probabilities = self.model.predict_proba(numerical_vector)[0]
            max_confidence = max(probabilities)
            predicted_encoded = probabilities.tolist().index(max_confidence)

            CONFIDENCE_THRESHOLD = 0.55

            if max_confidence >= CONFIDENCE_THRESHOLD:
                severity_result = self.decode_map[int(predicted_encoded)]
                flag_status = "Automated"
            else:
                severity_result = f"Pending Manual Review (Low Confidence: {max_confidence*100:.1f}%)"
                flag_status = "Flagged"

            logging.info(f"Prediction Status: {flag_status} | Assigned Tag: {severity_result}")
            return {
                "severity": severity_result,
                "confidence": f"{max_confidence * 100:.2f}%",
                "status": flag_status
            }

        except Exception as e:
            raise CustomException(e, sys)