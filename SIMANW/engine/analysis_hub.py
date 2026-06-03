import json
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"


class ContentProfiler:
    def __init__(self, source_path=None):
        self.source_path = source_path
        self.frame = None
        self.thread_data = None
        self.sia = SentimentIntensityAnalyzer()
        self.sw = stopwords.words('spanish')
        if source_path:
            self._load_data()

    def _load_data(self):
        with open(self.source_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        self.frame = pd.DataFrame(raw)
        self.frame['date'] = pd.to_datetime(self.frame['date'], format='mixed', utc=True)
        extra = ['solo', 'mejor', 'vez', 'cómo', 'hace',
                 'año', 'años', 'ser', 'puede', 'parte', 'si', 'dos', 'tres',
                 'gran', 'mismo', 'misma', 'así', 'cada', 'menos', 'más',
                 'después', 'ahora', 'dijo', 'tras', 'también']
        self.filter_words = set(self.sw + extra)

    def _pick_granularity(self):
        span = (self.frame['date'].max() - self.frame['date'].min()).days
        if span <= 21:
            self.frame['bucket'] = self.frame['date'].dt.strftime('%Y-%m-%d')
            return "Daily", "short observation window (<=21 days); daily grouping avoids information loss."
        else:
            self.frame['bucket'] = self.frame['date'].dt.strftime('%Y-W%U')
            return "Weekly", "multi-week span enables macro-level trend detection."

    def _term_frequencies(self, text_series):
        joined = " ".join(text_series).lower()
        cleaned = re.sub(r'[^\w\s]', '', joined)
        cleaned = re.sub(r'\d+', '', cleaned)
        words = [w for w in cleaned.split() if w not in self.filter_words and len(w) > 2]
        return Counter(words)

    def analyze_timeline(self):
        print(">>> BEGINNING TEMPORAL ANALYSIS ===")
        gran, explanation = self._pick_granularity()
        print(f"[RESOLUTION] Bucket: {gran}")
        pivot = self.frame.groupby(['bucket', 'topic']).size().unstack(fill_value=0)
        csv_dest = f"{PROJECT_ROOT}/exports/trend_data.csv"
        pivot.to_csv(csv_dest)
        print(f"[SAVED] Frequency table -> {csv_dest}")
        fig, ax = plt.subplots(figsize=(12, 6))
        pivot.plot(ax=ax, marker='s', linewidth=2)
        ax.set_title(f'Trend Evolution by Category ({gran})', fontsize=14)
        ax.set_xlabel('Time Bucket')
        ax.set_ylabel('Article Count')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(title='Categories')
        plt.tight_layout()
        chart_path = f"{PROJECT_ROOT}/exports/trend_chart.png"
        plt.savefig(chart_path)
        plt.close()
        print(f"[CHART] Timeline chart -> {chart_path}")
        max_vol = pivot.max().max()
        peak_cat = pivot.max().idxmax()
        peak_bucket = pivot[peak_cat].idxmax()
        peak_rows = self.frame[(self.frame['bucket'] == peak_bucket) & (self.frame['topic'] == peak_cat)]
        sample_titles = peak_rows['headline'].head(3).tolist()
        buckets_sorted = sorted(self.frame['bucket'].unique())
        first_bucket = buckets_sorted[0]
        last_bucket = buckets_sorted[-1]
        top3_cats = self.frame['topic'].value_counts().head(3).index.tolist()
        analysis_lines = ""
        for cat in top3_cats:
            early = self.frame[(self.frame['bucket'] == first_bucket) & (self.frame['topic'] == cat)]['body'].tolist()
            late = self.frame[(self.frame['bucket'] == last_bucket) & (self.frame['topic'] == cat)]['body'].tolist()
            freq_a = self._term_frequencies(early)
            freq_b = self._term_frequencies(late)
            shifts = {}
            vocab = set(freq_a.keys()) | set(freq_b.keys())
            for w in vocab:
                total = freq_a.get(w, 0) + freq_b.get(w, 0)
                if total >= 3:
                    shifts[w] = freq_b.get(w, 0) - freq_a.get(w, 0)
            rising = sorted(shifts.items(), key=lambda x: x[1], reverse=True)[:3]
            falling = sorted(shifts.items(), key=lambda x: x[1])[:3]
            analysis_lines += f"\n>> Topic: {cat.upper()}\n"
            analysis_lines += f"   Up: {', '.join([f'{k} (+{v})' for k,v in rising if v > 0])}\n"
            analysis_lines += f"   Down: {', '.join([f'{k} ({v})' for k,v in falling if v < 0])}\n"

        conclusion = f"""=== TREND ANALYSIS REPORT ===

1. GRANULARITY
   Mode: {gran}
   Rationale: {explanation}

2. PEAK EVENT
   Highest concentration: {peak_cat.upper()} during {peak_bucket} ({int(max_vol)} articles).
   Representative headlines from that window:
""" + "\n".join([f"   - \"{t}\"" for t in sample_titles]) + f"""

3. LEXICAL SHIFTS
   Comparing earliest period ({first_bucket}) vs latest ({last_bucket}):
{analysis_lines}
4. SYNTHESIS
    Activity patterns shift with publication cycles and editorial agendas.
    Terminology adapts to match ongoing coverage themes and emerging
    institutional voices across the observation window.
"""
        txt_dest = f"{PROJECT_ROOT}/exports/trend_conclusions.txt"
        with open(txt_dest, 'w', encoding='utf-8') as f:
            f.write(conclusion)
        print(f"[REPORT] Narrative report -> {txt_dest}")
        print(">>> ANALYSIS FINISHED ===")

    def analyze_discourse(self, thread_data):
        self.thread_data = thread_data
        for msg in self.thread_data:
            msg['sentiment'] = self.sia.polarity_scores(msg['texto'])['compound']

    def sentiment_curve(self, decay=0.6):
        if not self.thread_data:
            return []
        scores = [m['sentiment'] for m in self.thread_data]
        curve = []
        ema = 0.0
        for i, s in enumerate(scores):
            ema = decay * ema + (1 - decay) * s
            curve.append({
                'index': i + 1,
                'raw': s,
                'smoothed': ema
            })
        return curve

    def discover_clusters(self, clusters=3):
        if not self.thread_data:
            return {}
        texts = [m['texto'] for m in self.thread_data]
        if len(texts) < clusters:
            clusters = max(1, len(texts))
        vec = TfidfVectorizer(max_features=500, stop_words=self.sw)
        mat = vec.fit_transform(texts)
        km = MiniBatchKMeans(n_clusters=clusters, random_state=13, n_init=10)
        labels = km.fit_predict(mat)
        groups = defaultdict(list)
        for idx, cid in enumerate(labels):
            groups[cid].append(idx)
        terms = vec.get_feature_names_out()
        result = {}
        for cid, indices in groups.items():
            centroid = km.cluster_centers_[cid]
            top_pos = centroid.argsort()[-4:][::-1]
            keywords = [terms[j] for j in top_pos]
            result[cid] = {
                'keywords': keywords,
                'count': len(indices),
                'indices': indices
            }
        return result

    def active_users(self, limit=3):
        if not self.thread_data:
            return []
        freq = Counter(m['usuario'] for m in self.thread_data)
        return freq.most_common(limit)

    def summarize_discourse(self):
        if not self.thread_data:
            return None
        total = len(self.thread_data)
        avg_s = sum(m['sentiment'] for m in self.thread_data) / total
        pos = sum(1 for m in self.thread_data if m['sentiment'] > 0.07)
        neg = sum(1 for m in self.thread_data if m['sentiment'] < -0.07)
        tags = Counter()
        for m in self.thread_data:
            found = re.findall(r'#(\S+)', m['texto'])
            tags.update(found)
        return {
            'total_posts': total,
            'unique_users': len(set(m['usuario'] for m in self.thread_data)),
            'avg_sentiment': avg_s,
            'mood': 'positive' if avg_s > 0.07 else 'negative' if avg_s < -0.07 else 'neutral',
            'pos_pct': 100 * pos / total,
            'neg_pct': 100 * neg / total,
            'top_tags': tags.most_common(3),
            'top_users': self.active_users(2),
        }


if __name__ == "__main__":
    profiler = ContentProfiler(f"{PROJECT_ROOT}/storage/news_corpus.json")
    profiler.analyze_timeline()
    print("\n=== DISCOURSE ANALYSIS ===")
    sample_thread = [
        {"usuario": "@eco_watcher", "texto": "Los vehiculos electricos chinos estan desembarcando en Europa con precios muy competitivos #EV #China", "timestamp": "10:02"},
        {"usuario": "@green_analyst", "texto": "BYD ya supera a Tesla en volumen de produccion global. Dato impresionante. #MovilidadElectrica", "timestamp": "10:08"},
        {"usuario": "@policy_tracker", "texto": "La UE prepara aranceles a la importacion para proteger su industria. Lectura compleja.", "timestamp": "10:14"},
        {"usuario": "@eco_watcher", "texto": "Proteccionismo no frena la innovacion. La competencia baja los precios finales.", "timestamp": "10:20"},
        {"usuario": "@tech_investor", "texto": "Las baterias de estado solido prometen 1000 km de autonomia. 2027 clave. #Baterias #Futuro", "timestamp": "10:25"},
        {"usuario": "@green_analyst", "texto": "El litio sigue siendo el cuello de botella. Reciclaje es la prioridad. #Sostenibilidad", "timestamp": "10:31"},
        {"usuario": "@policy_tracker", "texto": "Europa subsidia fabricas locales pero la materia prima viene de Asia. Dependencia.", "timestamp": "10:38"},
        {"usuario": "@eco_watcher", "texto": "Noruega ya tiene 80% de ventas electricas. El cambio es imparable.", "timestamp": "10:44"},
        {"usuario": "@tech_investor", "texto": "El hidrogeno verde tambien avanza para flotas pesadas. No todo es bateria.", "timestamp": "10:50"},
    ]
    discourse = ContentProfiler()
    discourse.analyze_discourse(sample_thread)
    summary = discourse.summarize_discourse()
    print(f"\n--- Overview ---")
    print(f"  Posts: {summary['total_posts']}")
    print(f"  Participants: {summary['unique_users']}")
    print(f"  Mood: {summary['mood'].upper()} ({summary['avg_sentiment']:+.3f})")
    print(f"  Clusters: {len(discourse.discover_clusters(3))}")
