import json
import csv
import os

class DataExporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_csv(self, records, filename="corpus_export.csv"):
        path = os.path.join(self.output_dir, filename)
        if not records:
            return path
        fieldnames = list(records[0].keys())
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        print(f"[Exporter] CSV -> {path}")
        return path

    def export_pretty_json(self, records, filename="corpus_formatted.json"):
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        print(f"[Exporter] Pretty JSON -> {path}")
        return path

    def export_summary(self, records, filename="corpus_summary.txt"):
        path = os.path.join(self.output_dir, filename)
        total = len(records)
        cats = {}
        for r in records:
            c = r.get('topic', 'GENERAL')
            cats[c] = cats.get(c, 0) + 1
        lines = [
            "=== CORPUS SUMMARY ===",
            f"Total articles: {total}",
            f"Categories: {len(cats)}",
            "---"
        ]
        for c, n in sorted(cats.items(), key=lambda x: -x[1]):
            lines.append(f"  {c}: {n} articles")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"[Exporter] Summary -> {path}")
        return path

if __name__ == "__main__":
    base = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"
    src = f"{base}/storage/news_corpus.json"
    out = f"{base}/exports"
    import json
    with open(src, 'r', encoding='utf-8') as f:
        data = json.load(f)
    x = DataExporter(out)
    x.export_csv(data)
    x.export_pretty_json(data)
    x.export_summary(data)
    print("Done.")
