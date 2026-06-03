import json
import re
import os
from collections import Counter
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"

class NLPExtractor:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.articles = []
        self.output_dir = f"{PROJECT_ROOT}/exports"

    def _load(self):
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            self.articles = json.load(f)

    @staticmethod
    def _build_stoplist():
        base = stopwords.words('spanish')
        extra = ['solo', 'mejor', 'vez', 'cómo', 'hace',
                 'año', 'años', 'ser', 'puede', 'parte', 'si', 'dos', 'tres',
                 'gran', 'mismo', 'misma', 'así', 'cada', 'menos', 'más',
                 'después', 'ahora', 'dijo', 'tras', 'también', 'durante']
        return set(base + extra)

    def _generate_cloud(self, text, filename):
        wc = WordCloud(
            width=500, height=360,
            background_color='#000000',
            colormap='plasma',
            stopwords=self._build_stoplist()
        ).generate(text)
        wc.to_file(os.path.join(self.output_dir, filename))

    def _compute_ngrams(self, token_list, n):
        return Counter(zip(*[token_list[i:] for i in range(n)]))

    def run(self):
        self._load()
        if not self.articles:
            print("[SKIP] No records to process.")
            return
        os.makedirs(self.output_dir, exist_ok=True)
        forbidden = self._build_stoplist()
        cat_tokens = {}
        all_texts = []
        global_tokens = []

        for art in self.articles:
            cat = art.get('topic', 'GENERAL').lower()
            cat_tokens.setdefault(cat, [])
            raw = f"{art['headline']} {art['body']}"
            all_texts.append(raw)
            cleaned = re.sub(r'[^\w\s]', '', raw.lower())
            cleaned = re.sub(r'\d+', '', cleaned)
            tokens = [w for w in cleaned.split() if w not in forbidden and len(w) > 2]
            cat_tokens[cat].extend(tokens)
            global_tokens.extend(tokens)

        joined_global = " ".join(global_tokens)
        self._generate_cloud(joined_global, "cloud_global.png")
        for cat_name, tlist in cat_tokens.items():
            if tlist:
                self._generate_cloud(" ".join(tlist), f"cloud_{cat_name}.png")

        def top_ngrams(tokens, n, k=5):
            return [" ".join(g) for g, _ in self._compute_ngrams(tokens, n).most_common(k)]

        unigrams_g = [w for w, _ in Counter(global_tokens).most_common(5)]
        bigrams_g = top_ngrams(global_tokens, 2)
        trigrams_g = top_ngrams(global_tokens, 3)

        full_text = " ".join(all_texts)
        entity_pattern = re.findall(
            r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*',
            full_text
        )
        entities = [e for e in entity_pattern if e.lower() not in forbidden and len(e) > 3]
        top_entities = [e[0] for e in Counter(entities).most_common(10)]

        per_cat = {}
        for cname, tkns in cat_tokens.items():
            if tkns:
                per_cat[cname] = {
                    "unigrams": [w for w, _ in Counter(tkns).most_common(5)],
                    "bigrams": top_ngrams(tkns, 2),
                    "trigrams": top_ngrams(tkns, 3),
                    "lexical_diversity": round(len(set(tkns)) / max(len(tkns), 1), 3),
                    "cloud_file": f"cloud_{cname}.png"
                }

        report = {
            "overview": {
                "top_unigrams": unigrams_g,
                "top_bigrams": bigrams_g,
                "top_trigrams": trigrams_g,
                "named_entities": top_entities
            },
            "by_category": per_cat
        }
        out_path = os.path.join(self.output_dir, "stats_nlp.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[EXPORT] Linguistic metrics written -> {out_path}")

if __name__ == "__main__":
    extractor = NLPExtractor(f"{PROJECT_ROOT}/storage/news_corpus.json")
    extractor.run()
