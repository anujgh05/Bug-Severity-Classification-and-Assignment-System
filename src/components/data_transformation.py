import sys
from dataclasses import dataclass
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import os
from src.utils import save_object
from sklearn.feature_extraction.text import TfidfVectorizer
from src.exception import CustomException
from src.logger import logging
from bs4 import BeautifulSoup
from cleantext import clean
'''
nltk.download('stopwords')
nltk.download('wordnet')
run this once and comment it
'''
@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts', "preprocessor.pkl")


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_word = set(stopwords.words('english'))
        self.severity_map = {
            'blocker':  2,   # High
            'critical': 2,
            'major':    1,   # Medium
            'minor':    0,   # Low
            'trivial':  0,
            's3':       0,   # Low
            's4':       0,   # Low
            # 'normal' intentionally excluded
        }

    def clean_text(self, text):
        try:
            if not isinstance(text, str):
                return ""
            # Patterns that appear in every Mozilla Bugzilla description — zero severity signal
            BUGZILLA_NOISE_PATTERNS = [
                r'created by .+? on \w+, \w+ \d+, \d{4} [\d:]+ [apm]+ p[ds]t',
                r'updated by .+? on \w+, \w+ \d+, \d{4} [\d:]+ [apm]+ p[ds]t',
                r'additional details\s*:',
                r'i have this on my internal buglist.*',
                r'so i will take it\.?',
            ]

            NOISE_RE = re.compile('|'.join(BUGZILLA_NOISE_PATTERNS), re.IGNORECASE)

            custom_stops = {
                'mozilla', 'firefox', 'please', 'thanks',
                'would', 'could', 'should', 'also', 'use', 'used', 'using',
                # Bugzilla metadata stragglers
                'created', 'updated', 'additional', 'detail', 'details',
                'internal', 'buglist', 'netscape', 'pdt', 'pst',
            }
            # 1. Use BeautifulSoup to remove HTML tags, especially script/style
            soup = BeautifulSoup(text, "html.parser")
            for element in soup(["script", "style"]):
                element.decompose()
            text = soup.get_text()

            # 2. Strip Bugzilla boilerplate first, before any other processing
            text = NOISE_RE.sub(' ', text)

            # 3. Use cleantext for general cleaning (lowercase, remove URLs, emails, phone numbers, numbers, punctuation)
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
                and w not in custom_stops
                and len(w) > 1
            ]
            return " ".join(words)
        
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Successfully read train and test dataset")

            logging.info("Mapping Severity Labels")

            for df in [train_df, test_df]:
                df['severity'] = df['severity'].fillna('').astype(str).str.strip().str.lower()
                df.drop(df[df['severity'].isin(['--', 'normal', 'nan', '','NEEDS_REVIEW'])].index, inplace=True)
                df['severity'] = df['severity'].map(self.severity_map)
                df.dropna(subset=['severity'], inplace=True)

                if 'short_desc' in df.columns:
                    df['short_desc'] = df['short_desc'].fillna('')
                    df['text_features'] = df['short_desc'].map(self.clean_text)
                else:
                    df['summary'] = df['summary'].fillna('')
                    df['description'] = df['description'].fillna('')
                    df['text_features'] = (df['summary'] + " " + df['description']).map(self.clean_text)

                df.drop(df[df['text_features'].str.strip() == ''].index, inplace=True)

            logging.info("Applying TF-IDF Vectorization")

            tfidf = TfidfVectorizer(
            max_features=3000,   # was 10000 — short descriptions don't need a bigger vocab
            ngram_range=(1, 2), sublinear_tf=True,
            min_df=2, max_df=0.95, strip_accents='unicode', analyzer='word',
            )

            
            X_train = tfidf.fit_transform(train_df['text_features'])
            X_test  = tfidf.transform(test_df['text_features'])
            y_train = train_df['severity'].values.astype(int)
            y_test  = test_df['severity'].values.astype(int)

            logging.info(f"X_train shape: {X_train.shape} | X_test shape: {X_test.shape}")
            logging.info("Saving preprocessor (TF-IDF) object")

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=tfidf
            )

            return (
                X_train,
                X_test,
                y_train,
                y_test,
                self.data_transformation_config.preprocessor_obj_file_path,
            )

        except Exception as e:
            raise CustomException(e, sys)
