import json
import feedparser
import re
import hashlib
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"

class ArticleFilter:
    def __init__(self, enable_time_check=False, max_months=6):
        self.known_urls = set()
        self.known_signatures = set()
        self.denied = []
        self.scanned_total = 0
        self.time_check = enable_time_check
        self.window_days = max_months * 30

    def _build_signature(self, title):
        raw = title.strip().lower()
        return hashlib.md5(raw.encode()).hexdigest()

    def evaluate(self, entry):
        self.scanned_total += 1
        title = entry.get('headline', '')
        body = entry.get('body', '')
        url = str(entry.get('url', ''))
        if self.time_check:
            date_str = entry.get('date', '')
            try:
                parsed = parsedate_to_datetime(date_str)
                if parsed.tzinfo:
                    parsed = parsed.astimezone().replace(tzinfo=None)
                age = datetime.now() - parsed
                if age.days > self.window_days:
                    self._register_denial(entry, f"Outside time window ({self.window_days}d)")
                    return False
            except Exception:
                self._register_denial(entry, "Unparseable date")
                return False
        clean_url = url.split('?')[0]
        sig = self._build_signature(title)
        if clean_url in self.known_urls:
            self._register_denial(entry, "Duplicate URL hash")
            return False
        if not url.startswith(('http://', 'https://')):
            self._register_denial(entry, "Improper URL scheme")
            return False
        if sig in self.known_signatures:
            self._register_denial(entry, "Duplicate title signature")
            return False
        if not all([title.strip(), body.strip(), url.strip()]):
            self._register_denial(entry, "Empty metadata field")
            return False
        if len(body.strip()) < 50:
            self._register_denial(entry, "Insufficient body length")
            return False
        self.known_urls.add(clean_url)
        self.known_signatures.add(sig)
        return True

    def _register_denial(self, entry, cause):
        self.denied.append({
            'title': entry.get('headline', 'UNKNOWN'),
            'url': entry.get('url', 'UNKNOWN'),
            'cause': cause
        })

    def write_audit_log(self, path=f"{PROJECT_ROOT}/exports/quality_report.txt"):
        passed = self.scanned_total - len(self.denied)
        status = "ENABLED" if self.time_check else "DISABLED"
        lines = [
            "#" * 60,
            "  PIPELINE QUALITY REPORT",
            "#" * 60,
            "",
            f"Time gate: {status}",
            f"Entries evaluated: {self.scanned_total}",
            f"Accepted: {passed}",
            f"Discarded: {len(self.denied)}",
            "",
            "Filtered items:",
            "-" * 40
        ]
        for idx, r in enumerate(self.denied, 1):
            lines.append(f"{idx}. Reason: {r['cause']}")
            lines.append(f"   Title: {r['title']}")
            lines.append(f"   URL: {r['url']}")
            lines.append("")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

class FeedScanner:
    def __init__(self, config_location, cap_per_topic=30, filter_age=False):
        self.config_location = config_location
        self.cap = cap_per_topic
        self.collected = []
        self.filter = ArticleFilter(enable_time_check=filter_age)

    def _parse_source(self):
        with open(self.config_location, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        if 'feeds' in raw:
            return {item['topic']: item['urls'] for item in raw['feeds']}
        return raw

    @staticmethod
    def _strip_html(html_text):
        if not html_text:
            return ""
        return re.sub(r'<[^<]+?>', '', html_text).strip()

    def run(self):
        sources = self._parse_source()
        filter_flag = "ENABLED" if self.filter.time_check else "DISABLED"
        print(f">>> LAUNCHING PIPELINE (FILTERS ACTIVE | AGE GATE: {filter_flag}) <<<")
        for topic, feed_urls in sources.items():
            print(f"\n[STREAM] Category: {topic.upper()} (target: {self.cap})")
            gathered = 0
            for feed_url in feed_urls:
                if gathered >= self.cap:
                    break
                print(f"  |_ Reading: {feed_url}")
                try:
                    parsed = feedparser.parse(feed_url)
                    for item in parsed.entries:
                        if gathered >= self.cap:
                            break
                        title = item.get('title', '')
                        link = item.get('link', '')
                        raw_body = item.get('summary', item.get('description', ''))
                        clean_body = self._strip_html(raw_body)
                        candidate = {
                            'headline': title,
                            'body': clean_body,
                            'topic': topic,
                            'url': link,
                            'date': item.get('published', datetime.now().strftime("%Y-%m-%d")),
                            'author': item.get('author', item.get('publisher', 'Unknown')),
                            'source': feed_url
                        }
                        if self.filter.evaluate(candidate):
                            self.collected.append(candidate)
                            gathered += 1
                except Exception as exc:
                    print(f"  [FAIL] {feed_url} -> {exc}")
        return self.collected

    def persist(self, destination=f"{PROJECT_ROOT}/storage/news_corpus.json"):
        with open(destination, 'w', encoding='utf-8') as f:
            json.dump(self.collected, f, ensure_ascii=False, indent=2)
        print(f"\n[OUTPUT] {len(self.collected)} entries saved -> '{destination}'")
        self.filter.write_audit_log()

if __name__ == '__main__':
    scanner = FeedScanner(
        config_location=f'{PROJECT_ROOT}/storage/settings/feed_sources.json',
        cap_per_topic=250,
        filter_age=False
    )
    scanner.run()
    scanner.persist()
