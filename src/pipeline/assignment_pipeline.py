import sys
from psycopg2.extras import RealDictCursor
import os
import psycopg2
from src.exception import CustomException
from src.logger import logging
from src.utils import load_object
from sklearn.metrics.pairwise import cosine_similarity

class AssignmentPipeline:
    def __init__(self):
        self.conn_info = "host=localhost dbname='Minor Project' user=postgres password=2005 port=5432"
        self.preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")
        
        try:
            logging.info("Loading preprocessor for text vectorization...")
            self.preprocessor = load_object(file_path=self.preprocessor_path)
        except Exception as e:
            raise CustomException(e, sys)

    def _get_active_developers(self):
        query = """
        SELECT developer_id, name, expertise_profile, current_workload
        FROM developer_profiles WHERE is_active = TRUE;
        """
        with psycopg2.connect(self.conn_info) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()

    def assign_developer(self, bug_id, cleaned_bug_text):
        try:
            logging.info(f"Initiating matching algorithm for Bug ID: {bug_id}")
            developers = self._get_active_developers()

            if not developers:
                logging.warning("No active developers found")
                return None, 0.0
            
            from sklearn.feature_extraction.text import TfidfVectorizer

            corpus = [cleaned_bug_text] +[dev['expertise_profile'] for dev in developers]

            local_vectorizer = TfidfVectorizer()
            tfidf_matrix = local_vectorizer.fit_transform(corpus).toarray()

            bug_vector = tfidf_matrix[0:1]

            best_dev_id = None
            max_score = -1.0
            best_dev_name = ""
            actual_text_similarity = 0.0
            
            for index,dev in enumerate(developers):
                dev_vector = tfidf_matrix[index +1 : index +2]

                similarity = cosine_similarity(bug_vector, dev_vector)[0][0]
                logging.info(f"Developer Match Check -> Name: {dev['name']} | Score: {similarity:.4f}")

                final_matching_score = similarity
                if dev['current_workload']>=5:
                    final_matching_score -= 0.15
                
                if final_matching_score > max_score:
                    max_score = final_matching_score
                    actual_text_similarity = similarity
                    best_dev_id = dev['developer_id']
                    best_dev_name = dev['name']

            if best_dev_id:
                with psycopg2.connect(self.conn_info) as conn:
                    with conn.cursor() as cur:
                        update_bug_query = """
                                UPDATE bug_reports 
                                SET assigned_dev_id = %s, similarity_score = %s 
                                WHERE bug_id = %s;
                            """
                        cur.execute(update_bug_query, (best_dev_id, float(actual_text_similarity), bug_id))

                        update_dev_query = """
                            UPDATE developer_profiles 
                            SET current_workload = current_workload + 1 
                            WHERE developer_id = %s;
                        """
                        cur.execute(update_dev_query, (best_dev_id,))

                        history_query = """
                            INSERT INTO assignment_history (bug_id, developer_id, assignment_mode)
                            VALUES (%s, %s, 'automated');
                        """
                        cur.execute(history_query, (bug_id, best_dev_id))

                logging.info(f"Successfully routed Bug {bug_id} to {best_dev_name} (Score: {actual_text_similarity:.4f})")
                return best_dev_id, actual_text_similarity
        except Exception as e:
            raise CustomException(e, sys)