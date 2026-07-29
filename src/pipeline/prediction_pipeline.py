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
import psycopg2


from bs4 import BeautifulSoup
from cleantext import clean

BUGZILLA_NOISE_PATTERNS = [
    r'created by .+? on \w+, \w+ \d+, \d{4} [\d:]+ [apm]+ p[ds]t',
    r'updated by .+? on \w+, \w+ \d+, \d{4} [\d:]+ [apm]+ p[ds]t',
    r'additional details\s*:',
    r'i have this on my internal buglist.*',
    r'so i will take it\.?',
]

NOISE_RE = re.compile('|'.join(BUGZILLA_NOISE_PATTERNS), re.IGNORECASE)

CUSTOM_STOPS = {
    'mozilla', 'firefox', 'please', 'thanks',
    'would', 'could', 'should', 'also', 'use', 'used', 'using',
    'created', 'updated', 'additional', 'detail', 'details',
    'internal', 'buglist', 'netscape', 'pdt', 'pst',
}


class PredictPipeline:
    def __init__(self):
        try:
            logging.info("Initializing PredictPipeline: Loading ML models into memory...")
            self.model_path=os.path.join("artifacts","model.pkl")
            self.preprocessor_path=os.path.join("artifacts","preprocessor.pkl")

            self.model = load_object(file_path=self.model_path)
            self.preprocessor = load_object(file_path=self.preprocessor_path)

            self.decode_map = {2: "High Priority", 1: "Medium Priority", 0: "Low Priority"}
            self.lemmatizer = WordNetLemmatizer()

            self.stop_word = set(stopwords.words("english"))
            logging.info("PredictPipeline initialization successful. Models loaded.")
        except Exception as e:
            raise CustomException(e, sys)

    def clean_text(self, text):
        try:
            if not isinstance(text, str):
                return ""

            # 1. HTML parsing
            soup = BeautifulSoup(text, "html.parser")
            for element in soup(["script", "style"]):
                element.decompose()
            text = soup.get_text()

            # 2. Boilerplate noise removal
            text = NOISE_RE.sub(' ', text)

            # 3. cleantext cleaning
            text = clean(text,
                        lower=True,
                        no_urls=True,
                        no_emails=True,
                        no_phone_numbers=True,
                        no_numbers=True,
                        no_punct=True,
                        replace_with_url=" ",
                        replace_with_email=" ",
                        replace_with_phone_number=" ",
                        replace_with_number=" "
                        )

            words = text.split()
            words = [
                self.lemmatizer.lemmatize(w)
                for w in words
                if w not in self.stop_word
                and w not in CUSTOM_STOPS
                and len(w) > 1
            ]
            return " ".join(words)

        except Exception as e:
            raise CustomException(e, sys)
     
    def predict(self, summary, description):
        try:
            combined_text = f"{summary} {description}"
            cleaned_text = self.clean_text(combined_text)

            numerical_vector = self.preprocessor.transform([cleaned_text]).toarray()
            
            predicted_class = int(self.model.predict(numerical_vector)[0])

            probabilities = self.model.predict_proba(numerical_vector)[0]
            max_confidence = max(probabilities)

            CONFIDENCE_THRESHOLD = 0.55

            if max_confidence >= CONFIDENCE_THRESHOLD:
                severity_result = self.decode_map[predicted_class]
                routing_status = "automated"
            else:
                severity_result = f"Pending Manual Review (Low Confidence: {max_confidence*100:.1f}%)"
                routing_status = "pending_review"

            conn_info = "host=localhost dbname='Minor Project' user='postgres' password=2005 port=5432"

            with psycopg2.connect(conn_info) as conn:
                with conn.cursor() as cur:
                    query = """
                    INSERT INTO bug_reports (summary, description, predicted_severity, final_severity, confidence_score, routing_status)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING bug_id;
                    """
                    final_sev = severity_result if routing_status == "automated" else None
                    conf_float = float(max_confidence*100)

                    cur.execute(query,(summary, description, severity_result, final_sev, conf_float, routing_status))
                    bug_id = cur.fetchone()[0]
            logging.info(f"Bug saved to database with ID: {bug_id} | Status: {routing_status}")
            return {
                "bug_id": bug_id,
                "severity": severity_result,
                "confidence": f"{conf_float:.2f}%",
                "status": routing_status,
                "cleaned_text": cleaned_text # Passed along so assignment engine doesn't have to clean text again
            }

        except Exception as e:
            raise CustomException(e, sys)