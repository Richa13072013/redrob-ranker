import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

from narratives import SHIPPER_NARRATIVE, TECHNICAL_NARRATIVE


class SemanticScorer:
    def __init__(self, n_components=100):
        self.vectorizer = TfidfVectorizer(
            max_features=20000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=3
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.shipper_vec = None
        self.technical_vec = None
        self.fitted = False

    def fit(self, sample_texts: list):
        # Fit TF-IDF + SVD on a representative sample of candidate career text
        tfidf_matrix = self.vectorizer.fit_transform(sample_texts)
        self.svd.fit(tfidf_matrix)

        # Transform our two narratives into the same space, once
        narrative_tfidf = self.vectorizer.transform([SHIPPER_NARRATIVE, TECHNICAL_NARRATIVE])
        narrative_svd = self.svd.transform(narrative_tfidf)
        self.shipper_vec = narrative_svd[0].reshape(1, -1)
        self.technical_vec = narrative_svd[1].reshape(1, -1)
        self.fitted = True

    def score(self, career_text: str) -> dict:
        if not self.fitted:
            raise RuntimeError("SemanticScorer must be fit() before scoring")

        tfidf = self.vectorizer.transform([career_text])
        vec = self.svd.transform(tfidf)

        shipper_sim = cosine_similarity(vec, self.shipper_vec)[0][0]
        technical_sim = cosine_similarity(vec, self.technical_vec)[0][0]

        # JD explicitly says: tilt slightly toward shipper over researcher
        blended = 0.60 * shipper_sim + 0.40 * technical_sim

        # cosine similarity can be negative after SVD; clip to [0, 1]
        blended = max(0.0, min(blended, 1.0))

        return {
            "shipper_sim": round(float(shipper_sim), 4),
            "technical_sim": round(float(technical_sim), 4),
            "semantic_score": round(float(blended), 4)
        }
    def score_batch(self, texts: list) -> list:
        # Transform ALL texts in one batch operation instead of one at a time
        tfidf_matrix = self.vectorizer.transform(texts)
        vecs = self.svd.transform(tfidf_matrix)

        shipper_sims = cosine_similarity(vecs, self.shipper_vec).flatten()
        technical_sims = cosine_similarity(vecs, self.technical_vec).flatten()

        results = []
        for s_sim, t_sim in zip(shipper_sims, technical_sims):
            blended = 0.60 * s_sim + 0.40 * t_sim
            blended = max(0.0, min(float(blended), 1.0))
            results.append({
                "shipper_sim": round(float(s_sim), 4),
                "technical_sim": round(float(t_sim), 4),
                "semantic_score": round(blended, 4)
            })
        return results