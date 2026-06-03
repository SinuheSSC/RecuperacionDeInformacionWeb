import json
import re
from collections import Counter, deque
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"

LABELS = ['tecnologia', 'ciencia', 'economia', 'politica', 'deportes']

class QuickFinder:
    def __init__(self, documents):
        self.documents = documents
        self.texts = [f"{d['headline']}. {d['body']}" for d in documents]
        sw = stopwords.words('spanish') + ['solo', 'mejor', 'vez', 'cómo']
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words=sw, max_features=2500)
        self.matrix = self.vectorizer.fit_transform(self.texts)

    def lookup(self, query, limit=3):
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix)[0]
        top = scores.argsort()[::-1][:limit]
        results = []
        for idx in top:
            if scores[idx] > 0.05:
                doc = self.documents[idx]
                results.append({
                    'title': doc['headline'],
                    'snippet': doc['body'][:150] + '...',
                    'category': doc['topic'],
                    'relevance': float(scores[idx])
                })
        return results

    def filter_by_topic(self, topic, limit=5):
        out = []
        for i, doc in enumerate(self.documents):
            if doc.get('topic', '').lower() == topic.lower():
                out.append({
                    'title': doc['headline'],
                    'snippet': doc['body'][:150] + '...',
                    'category': doc['topic'],
                    'relevance': 1.0
                })
                if len(out) >= limit:
                    break
        return out


class ChatController:
    def __init__(self, finder):
        self.finder = finder
        self.memory = deque(maxlen=10)
        self.interests = Counter()

    def _update_state(self, question, mode, label=None):
        self.memory.append({'q': question, 'mode': mode})
        if label:
            self.interests[label] += 1

    def _match_intent(self, text):
        patterns = {
            'fetch': re.compile(r'\b(dame|busca|localiza|encuentra|listar|consulta)\b'),
            'rel': re.compile(r'\b(parecida|similar|relacionado|vinculado|conexo)\b'),
            'story': re.compile(r'\b(articulo|post|entrada|noticia|reporte|cronica)\b'),
            'alt': re.compile(r'\b(otra|alternativa|distinta|diferente|nueva)\b'),
            'prev': re.compile(r'\b(anterior|previa|ultima|anteriormente|precedente)\b'),
            'tell': re.compile(r'\b(cuentame|explica|describe|muestrame|ensename)\b'),
            'more': re.compile(r'\b(mas|adicional|extra|amplia|profundiza)\b'),
            'on': re.compile(r'\b(sobre|acerca|respecto|tema|acerca_de)\b'),
            'about': re.compile(r'\b(de|del|en|un|una|el|la|los|las|que|hay)\b'),
            'for': re.compile(r'\b(para|por|cual|como|donde|categoria)\b'),
            'any': re.compile(r'\b(hay|existe|algun|ningun|tienes)\b'),
        }
        matches = {}
        for name, pat in patterns.items():
            m = pat.search(text)
            if m:
                matches[name] = m.start()
        return matches

    def _rank_intents(self, matched):
        intent_map = {
            ('rel', 'prev'): ('reference', 'context'),
            ('rel',): ('reference', 'general'),
            ('tell', 'fetch'): ('request', 'specific'),
            ('fetch',): ('request', 'any'),
            ('tell',): ('request', 'any'),
            ('story', 'alt'): ('request', 'alternate'),
            ('story',): ('request', 'any'),
            ('more', 'on'): ('reference', 'extend'),
            ('on', 'prev'): ('reference', 'context'),
            ('on',): ('reference', 'general'),
            ('any',): ('topic_query', 'broad'),
            ('for',): ('topic_query', 'broad'),
        }
        keys = tuple(sorted(matched.keys()))
        if keys in intent_map:
            return intent_map[keys]
        if keys:
            return ('topic_query', 'broad')
        return ('fallback', 'none')

    def _pick_template(self, primary, sub, best, topic_results, stripped):
        templates = {
            'reference': {
                'context': lambda: f"Claro, siguiendo ese hilo: {best['title']}",
                'general': lambda: f"Algo vinculado: {best['title']}",
                'extend': lambda: f"Ampliando el tema: {best['snippet']}",
            },
            'request': {
                'specific': lambda: f"Aqui tienes: {best['title']}",
                'any': lambda: f"Mira esto: {best['title']}.\n   {best['snippet']}",
                'alternate': lambda: f"Otra opcion: {best['title']}",
            },
            'topic_query': {
                'broad': lambda: f"Sobre {stripped.upper()} encontre: {best['title']}",
            },
            'fallback': {
                'none': lambda: f"No tengo datos sobre '{stripped}' en este momento. Prueba con otras palabras.",
            },
        }
        return templates.get(primary, {}).get(sub, lambda: f"{best['title']}")()

    def respond(self, question):
        lower_q = question.lower()
        intent_matches = self._match_intent(lower_q)
        primary, sub = self._rank_intents(intent_matches)

        filler_pattern = re.compile(r'\b(dame|busca|localiza|cuentame|explica|muestrame|mas|sobre|otra|hay|de|en|un|una|el|la|los|las|que|para|por)\b')
        stripped = filler_pattern.sub('', lower_q).strip()
        if not stripped:
            dominant = self.interests.most_common(1)
            stripped = dominant[0][0] if dominant else "tecnologia"

        detected_topic = None
        for cat in LABELS:
            if cat in stripped:
                detected_topic = cat
                break

        if primary == 'reference':
            if self.memory:
                last = self.memory[-1]
                expanded = f"{last['q']} {stripped}"
                results = self.finder.lookup(expanded, limit=2)
                if len(results) > 1:
                    r = results[1]
                    resp = self._pick_template('reference', 'context', r, None, stripped)
                    self._update_state(question, 'reference', r['category'])
                    return resp, 'reference', r['relevance']
            results = self.finder.lookup(stripped, limit=2)
            if results:
                r = results[0]
                resp = self._pick_template('reference', 'general', r, None, stripped)
                self._update_state(question, 'reference', r['category'])
                return resp, 'reference', r['relevance']
            primary = 'topic_query'
            sub = 'broad'

        if detected_topic and primary in ('topic_query', 'request'):
            results = self.finder.filter_by_topic(detected_topic, limit=5)
            if results:
                lines = [f"Noticias de {detected_topic.upper()}:"]
                for i, r in enumerate(results, 1):
                    lines.append(f"  {i}. {r['title']}")
                resp = "\n".join(lines)
                self._update_state(question, 'topic_query', detected_topic)
                return resp, 'topic_query', 1.0

        results = self.finder.lookup(stripped, limit=5)
        if results:
            best = results[0]
            if self.interests and best['relevance'] < 0.3:
                fav = self.interests.most_common(1)[0][0]
                for r in results:
                    if r['category'] == fav:
                        resp = f"Se que te gusta '{fav.upper()}', mira: {r['title']}"
                        self._update_state(question, 'personalized', r['category'])
                        return resp, 'personalized', r['relevance']
            resp = self._pick_template(primary, sub, best, results, stripped)
            self._update_state(question, primary, best['category'])
            return resp, primary, best['relevance']
        resp = self._pick_template('fallback', 'none', None, None, stripped)
        self._update_state(question, 'fallback')
        return resp, 'fallback', 0.0

    def stats(self):
        return {
            'total_queries': len(self.memory),
            'topics': dict(self.interests.most_common()),
            'response_types': Counter(m['mode'] for m in self.memory)
        }

if __name__ == '__main__':
    path = f"{PROJECT_ROOT}/storage/news_corpus.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    searcher = QuickFinder(data)
    bot = ChatController(searcher)
    print(">>> DIALOGUE ENGINE ===\n")
    dialog = [
        "Que hay sobre Linux y lenguajes de programacion?",
        "Sobre eso mismo, ensename otra parecida.",
        "Ahora dime algo de energias renovables.",
        "Hay algo de ciencia de datos o inteligencia artificial?",
    ]
    for q in dialog:
        print(f"User: {q}")
        answer, atype, conf = bot.respond(q)
        print(f"Bot [{atype.upper()}] ({conf:.2f}):\n   {answer}\n")
    s = bot.stats()
    print("-" * 50)
    print(f"Queries: {s['total_queries']}")
    print(f"Topics: {s['topics']}")
    print(f"Breakdown: {dict(s['response_types'])}")
