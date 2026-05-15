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
            'blocker': 'Critical',
            'critical': 'Critical',
            'major': 'High',
            'normal': 'Medium',
            'S3': 'Medium',
            'minor': 'Low',
            'trivial': 'Low',
            'S4': 'Low'
        }

    def clean_text(self, text):
        try:
            if not isinstance(text, str):
                return ""
            
            text = text.lower()
            text = re.sub(r'[^a-z\s]','',text)
            words = text.split()
            cleaned_words = [self.lemmatizer.lemmatize(w) for w in words if w not in self.stop_word]
            return " ".join(cleaned_words)
        
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Successfully read train and test dataset")

            logging.info("Mapping Severity Labels")

            for df in [train_df, test_df]:
                df.dropna(subset=['severity'], inplace=True)
                df.drop(df[df['severity']== '--'].index, inplace=True)

                df['severity'] = df['severity'].map(self.severity_map)

                df['summary'] = df['summary'].fillna('')
                df['description'] = df['description'].fillna('')

                df['text_features'] = df['summary'] + " " + df['description']
                df['text_features'] = df['text_features'].map(self.clean_text)

            logging.info("Applying TF-IDF Vectorization")

            tfidf = TfidfVectorizer(max_features=5000)
            
            input_feature_train_arr = tfidf.fit_transform(train_df['text_features']).toarray()
            input_feature_test_arr = tfidf.transform(test_df['text_features']).toarray()

            target_feature_train_df = train_df['severity']
            target_feature_test_df = test_df['severity']

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info("Saving preprocessor (TF-IDF) object")

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=tfidf
            )

            return(
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )

        except Exception as e:
            raise CustomException(e, sys)
