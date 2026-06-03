import json
import numpy as np
import nltk
from nltk.corpus import stopwords
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_validate, StratifiedKFold

nltk.download('stopwords', quiet=True)

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"

class ModelEvaluator:
    def __init__(self):
        self.registry = {
            'NB': MultinomialNB(alpha=0.3),
            'SVM': LinearSVC(max_iter=2500, C=0.9, dual=False),
            'LogReg': LogisticRegression(max_iter=1200, C=0.8),
            'RF': RandomForestClassifier(n_estimators=80, random_state=7),
        }
        sw = stopwords.words('spanish')
        noise = ['el', 'la', 'los', 'las', 'un', 'una',
                 'solo', 'mejor', 'cómo', 'hace', 'año']
        self.stop_list = sw + noise
        self.vectorizer = TfidfVectorizer(
            max_features=2800,
            ngram_range=(1, 3),
            stop_words=self.stop_list
        )
        self.champion = None
        self.leaderboard = {}

    def _build_pipeline(self, model):
        from sklearn.pipeline import Pipeline
        return Pipeline([
            ('vect', self.vectorizer),
            ('clf', model)
        ])

    def evaluate_all(self, corpus, targets, folds=5):
        X_vec = self.vectorizer.fit_transform(corpus)
        cv_scheme = StratifiedKFold(n_splits=folds, shuffle=True, random_state=23)
        for label, clf in self.registry.items():
            try:
                scores = cross_validate(
                    clf, X_vec, targets, cv=cv_scheme,
                    scoring='accuracy', return_estimator=True
                )
                self.leaderboard[label] = {
                    'mean': scores['test_score'].mean(),
                    'std': scores['test_score'].std(),
                    'scores': scores['test_score'].tolist()
                }
            except Exception as err:
                self.leaderboard[label] = {'error': str(err)}
        qualified = {k: v for k, v in self.leaderboard.items() if 'mean' in v}
        if qualified:
            best_key = max(qualified, key=lambda k: qualified[k]['mean'])
            self.champion = (best_key, self.registry[best_key])
            self.champion[1].fit(X_vec, targets)
        return self.leaderboard

    def classify(self, items):
        if self.champion is None:
            raise RuntimeError("Call evaluate_all() before classify()")
        X = self.vectorizer.transform(items)
        return self.champion[1].predict(X)

    def report(self):
        import json as _json
        entries = []
        for name, rec in sorted(
            self.leaderboard.items(),
            key=lambda x: x[1].get('mean', 0),
            reverse=True
        ):
            if 'mean' in rec:
                champion = bool(self.champion and name == self.champion[0])
                entries.append({
                    'model': name,
                    'accuracy': round(rec['mean'], 4),
                    'std': round(rec['std'], 4),
                    'champion': champion
                })
            else:
                entries.append({
                    'model': name,
                    'accuracy': None,
                    'error': rec.get('error', '')[:40]
                })
        return _json.dumps({'leaderboard': entries, 'top': self.champion[0] if self.champion else None}, indent=2)

if __name__ == '__main__':
    data_path = f"{PROJECT_ROOT}/storage/news_corpus.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    texts = [f"{n['headline']}. {n['body']}" for n in articles]
    labels = [n['topic'] for n in articles]
    print(f">>> CLASSIFIER EVALUATION ===")
    print(f"Corpus size: {len(texts)} documents\n")
    evaluator = ModelEvaluator()
    evaluator.evaluate_all(texts, labels, folds=5)
    print(evaluator.report())
    print(f"\nTop model: {evaluator.champion[0]}")
    tests = [
        "El banco central sube tasas para frenar la inflacion",
        "Cientificos hallan nueva especie en la fosa abisal",
        "Modelo de inteligencia artificial generativa lanzado al mercado",
        "Congresistas discuten el presupuesto fiscal del proximo ano"
    ]
    preds = evaluator.classify(tests)
    print(f"\n--- Inference Samples ---")
    for t, p in zip(tests, preds):
        print(f"  [{p.upper()}] -> {t}")
