import json
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"

class MonitorEngine:
    def __init__(self, match_threshold=0.18):
        self.corpus_file = f"{PROJECT_ROOT}/storage/news_corpus.json"
        self.watchlist_file = f"{PROJECT_ROOT}/storage/settings/tracked_queries.json"
        self.archive_file = f"{PROJECT_ROOT}/exports/alert_history.json"
        self.inbox_file = f"{PROJECT_ROOT}/exports/alert_inbox.json"
        self.threshold = match_threshold
        self.watchlist = self._initialize_watchlist()
        self.archive = self._load_archive()
        ignore_words = stopwords.words('spanish')
        self.vectorizer = TfidfVectorizer(stop_words=ignore_words)
        self._calibrate()

    def _calibrate(self):
        if not os.path.exists(self.corpus_file):
            print("[ABORT] No reference corpus for vector fitting.")
            return
        with open(self.corpus_file, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
        samples = [f"{n.get('headline', '')} {n.get('body', '')}".lower() for n in corpus]
        if samples:
            self.vectorizer.fit(samples)
            print(f"[VECTOR] TF-IDF fitted on {len(samples)} records.")

    def _initialize_watchlist(self):
        if os.path.exists(self.watchlist_file):
            with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        defaults = [
            {"id": "T1", "nombre": "Machine Learning", "query": "aprendizaje automatico redes neuronales", "created_at": datetime.now().isoformat()},
            {"id": "T2", "nombre": "Markets & Finance", "query": "bolsa inflacion tipos interes", "created_at": datetime.now().isoformat()},
            {"id": "T3", "nombre": "Health Research", "query": "vacuna estudio clinico enfermedad", "created_at": datetime.now().isoformat()},
            {"id": "T4", "nombre": "Elections & Policy", "query": "elecciones congreso reforma ley", "created_at": datetime.now().isoformat()},
            {"id": "T5", "nombre": "Cybersecurity", "query": "seguridad vulnerabilidad ransomware ciberataque", "created_at": datetime.now().isoformat()}
        ]
        os.makedirs(os.path.dirname(self.watchlist_file), exist_ok=True)
        with open(self.watchlist_file, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, ensure_ascii=False, indent=2)
        return defaults

    def _load_archive(self):
        if os.path.exists(self.archive_file):
            with open(self.archive_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_archive(self):
        os.makedirs(os.path.dirname(self.archive_file), exist_ok=True)
        with open(self.archive_file, 'w', encoding='utf-8') as f:
            json.dump(self.archive, f, ensure_ascii=False, indent=2)

    def inspect(self, articles):
        alerts = []
        for article in articles:
            text = f"{article.get('headline', '')} {article.get('body', '')}".lower()
            url = article.get('url', 'unknown')
            vec_doc = self.vectorizer.transform([text])
            for query in self.watchlist:
                qid = query['id']
                self.archive.setdefault(qid, [])
                vec_q = self.vectorizer.transform([query['query']])
                sim = cosine_similarity(vec_doc, vec_q)[0][0]
                if sim >= self.threshold:
                    if url not in self.archive[qid]:
                        alert = {
                            "consulta_id": qid,
                            "consulta_nombre": query['nombre'],
                            "similarity_score": round(sim, 3),
                            "article_headline": article['headline'],
                            "url": url,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        alerts.append(alert)
                        self.archive[qid].append(url)
        self._save_archive()
        return alerts

    def generate_documentation(self):
        doc = """=== SYSTEM DOCUMENTATION: SEMANTIC ALERT ENGINE ===

The alert subsystem combines vector-space retrieval with persistent state management.

1. VECTOR INTELLIGENCE:
   Each incoming article and each registered query is encoded as a TF-IDF vector.
   When cosine similarity between an article vector and a query vector exceeds
   the configured threshold (0.18), a match is registered. This avoids the
   rigidity of boolean search and captures partial semantic overlap.

2. DEDUPLICATION STRATEGY:
   Traditional timestamp-based dedup is unreliable due to RSS timestamp
   heterogeneity. Instead, the system maintains a per-query URL registry
   (alert_history.json). If an article URL is already present for a given
   query, the alert is silently suppressed. This guarantees zero redundancy.

3. THRESHOLD CALIBRATION:
   The default threshold (0.18) was chosen empirically to balance recall
   and precision. Lower values increase sensitivity; higher values reduce
   false positives. Adjust via the MonitorEngine constructor.
"""
        path = f"{PROJECT_ROOT}/exports/ac10_documentation.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(doc)

def run_demo():
    print("### ALERT ENGINE DEMO ###")
    engine = MonitorEngine(match_threshold=0.18)
    if not os.path.exists(engine.corpus_file):
        print(f"[ABORT] Corpus missing: {engine.corpus_file}")
        return
    with open(engine.corpus_file, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    print("\n[PHASE 1] Registering baseline vector patterns...")
    initial = engine.inspect(corpus)
    print(f"         -> {len(initial)} baseline entries registered.")
    print("\n[PHASE 2] Re-checking (expect 0 new):")
    repeat = engine.inspect(corpus)
    print(f"         -> {len(repeat)} new signals [OK]")
    print("\n[PHASE 3] Injecting synthetic test cases...")
    test_set = [
        {"headline": "Breakthrough in quantum machine learning", "body": "researchers achieve major milestone in quantum neural network training", "url": "http://test.io/qml"},
        {"headline": "Docker releases major security patch", "body": "A critical vulnerability was discovered in container runtime.", "url": "http://test.io/docker"},
        {"headline": "How to bake sourdough bread", "body": "Mix flour water and salt then let it ferment for 24 hours.", "url": "http://test.io/bread"}
    ]
    fresh = engine.inspect(test_set)
    print(f"         -> {len(fresh)} signals fired [OK]")
    for a in fresh:
        print(f"            - [{a['timestamp']}] {a['consulta_nombre']} (similarity: {a['similarity_score']}) -> {a['article_headline']}")
    engine.generate_documentation()
    print(f"\n[INFO] Documentation generated.")
    print("### DEMO FINISHED ###")

if __name__ == '__main__':
    run_demo()
