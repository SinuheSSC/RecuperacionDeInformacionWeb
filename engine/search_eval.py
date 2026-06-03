import json
import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"

class RetrievalComparator:
    def __init__(self, records):
        self.records = records
        self.texts = [f"{d['headline']} {d['body']}" for d in records]
        sw = stopwords.words('spanish') + ['solo', 'mejor', 'vez', 'cómo']
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words=sw, max_features=3200)
        self.matrix = self.vectorizer.fit_transform(self.texts)
        self.index = defaultdict(set)
        for pos, txt in enumerate(self.texts):
            cleaned = re.sub(r'[^\w\s]', '', txt.lower())
            for token in cleaned.split():
                self.index[token].add(pos)

    def boolean_retrieve(self, expression):
        terms = [t for t in re.sub(r'[^\w\s]', '', expression.lower()).split() if len(t) > 2]
        if not terms:
            return []
        combined = set()
        for t in terms:
            combined |= self.index.get(t, set())
        return sorted(combined)[:50]

    def vector_retrieve(self, expression, top=5):
        q_vec = self.vectorizer.transform([expression])
        scores = cosine_similarity(q_vec, self.matrix)[0]
        ranked = scores.argsort()[::-1][:top]
        return [(i, scores[i]) for i in ranked if scores[i] > 0]

    def ground_truth(self, expression, target_cat):
        rel = []
        raw = re.sub(r'[^\w\s]', '', expression.lower()).split()
        clean = [t for t in raw if t not in stopwords.words('spanish')]
        if not clean:
            clean = raw
        for i, rec in enumerate(self.records):
            if rec['topic'] == target_cat:
                content = re.sub(r'[^\w\s]', '', f"{rec['headline']} {rec['body']}".lower())
                words = set(content.split())
                if any(t in words for t in clean):
                    rel.append(i)
        return rel

    def compare(self, expression, target_cat):
        relevant = self.ground_truth(expression, target_cat)
        bool_hits = self.boolean_retrieve(expression)
        bp = len(set(bool_hits) & set(relevant)) / max(len(bool_hits), 1)
        br = len(set(bool_hits) & set(relevant)) / max(len(relevant), 1)
        k = max(len(bool_hits), 5)
        vec_hits = [idx for idx, _ in self.vector_retrieve(expression, top=k)]
        vp = len(set(vec_hits) & set(relevant)) / max(len(vec_hits), 1)
        vr = len(set(vec_hits) & set(relevant)) / max(len(relevant), 1)
        return {
            'query': expression,
            'total_relevant': len(relevant),
            'boolean': {
                'retrieved': len(bool_hits),
                'precision': bp,
                'recall': br
            },
            'vector': {
                'retrieved': len(vec_hits),
                'precision': vp,
                'recall': vr
            }
        }

if __name__ == '__main__':
    path = f"{PROJECT_ROOT}/storage/news_corpus.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cmp = RetrievalComparator(data)
    queries = [
        {"q": "robotica y aprendizaje automatico", "cat": "tecnologia"},
        {"q": "mercados financieros globales", "cat": "economia"},
        {"q": "laboratorio estudio cientifico", "cat": "ciencia"},
        {"q": "conflicto diplomatico sanciones", "cat": "politica"},
    ]
    print("=== Retrieval Method Comparison ===")
    bp_sum, vp_sum = 0, 0
    br_sum, vr_sum = 0, 0
    for q in queries:
        r = cmp.compare(q['q'], q['cat'])
        b = r['boolean']
        v = r['vector']
        bp_sum += b['precision']
        vp_sum += v['precision']
        br_sum += b['recall']
        vr_sum += v['recall']
        print(json.dumps({
            'q': q['q'],
            'target': q['cat'],
            'relevant': r['total_relevant'],
            'boolean': {'hits': b['retrieved'], 'p': round(b['precision'], 3), 'r': round(b['recall'], 3)},
            'vector': {'hits': v['retrieved'], 'p': round(v['precision'], 3), 'r': round(v['recall'], 3)}
        }, ensure_ascii=False))
    n = len(queries)
    print(json.dumps({
        'summary': 'averages',
        'boolean': {'p': round(bp_sum / n, 3), 'r': round(br_sum / n, 3)},
        'vector': {'p': round(vp_sum / n, 3), 'r': round(vr_sum / n, 3)}
    }, ensure_ascii=False))
