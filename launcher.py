import flet as ft
import os
import asyncio
import json
import sys
import re
import uuid
from datetime import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from rdflib import Graph

nltk.download('vader_lexicon', quiet=True)

BASE = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"
sys.path.append(BASE)

from engine.feed_collector import FeedScanner
from engine.search_eval import RetrievalComparator
from engine.model_benchmark import ModelEvaluator
from engine.wikidata_agent import WikidataBridge
from engine.dialogue_core import QuickFinder, ChatController
from engine.rdf_builder import GraphAssembler
from engine.alert_engine import MonitorEngine

CORPUS_PATH = f"{BASE}/storage/news_corpus.json"
QC_REPORT_PATH = f"{BASE}/exports/quality_report.txt"
RSS_CONFIG_PATH = f"{BASE}/storage/settings/feed_sources.json"
CLOUD_IMG = f"{BASE}/exports/cloud_global.png"
TREND_IMG = f"{BASE}/exports/trend_chart.png"
ALERT_INBOX = f"{BASE}/exports/alert_inbox.json"

BG_PRIMARY = "#0a0a0f"
BG_CARD = "#151528"
BG_SIDEBAR = "#0f0f1a"
PRIMARY = "#a78bfa"
PRIMARY_LIGHT = "#c084fc"
ACCENT = "#e879f9"
SUCCESS = "#34d399"
ERROR = "#fb7185"
TEXT_PRIMARY = "#e2e8f0"
TEXT_MUTED = "#64748b"
BORDER = "#1e293b"

def _bd(color, w=1):
    return ft.border.Border(ft.border.BorderSide(w, color), ft.border.BorderSide(w, color), ft.border.BorderSide(w, color), ft.border.BorderSide(w, color))


def main(page: ft.Page):
    page.title = "PulseNews"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 1440
    page.window_height = 900

    page.searcher = None
    page.classifier_model = None
    page.sia = SentimentIntensityAnalyzer()
    page.monitor = MonitorEngine(match_threshold=0.18)

    # ========== ALERTS PANEL ==========
    subscription_list = ft.ListView(spacing=5, height=150, padding=5)
    notification_list = ft.ListView(expand=True, spacing=10, padding=5)

    def remove_subscription(qid):
        page.monitor.watchlist = [c for c in page.monitor.watchlist if c['id'] != qid]
        with open(page.monitor.watchlist_file, 'w', encoding='utf-8') as f:
            json.dump(page.monitor.watchlist, f, ensure_ascii=False, indent=2)
        render_alerts()

    def render_alerts():
        subscription_list.controls.clear()
        for c in page.monitor.watchlist:
            subscription_list.controls.append(
                ft.Row([
                    ft.Text(c['nombre'], size=12, color=PRIMARY, weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ERROR, icon_size=16, tooltip="Dejar de seguir", on_click=lambda e, qid=c['id']: remove_subscription(qid))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        notification_list.controls.clear()
        if os.path.exists(ALERT_INBOX):
            with open(ALERT_INBOX, 'r') as f:
                inbox = json.load(f)
            if not inbox:
                notification_list.controls.append(ft.Text("No hay nuevos artículos para tus temas.", color=TEXT_MUTED, text_align=ft.TextAlign.CENTER))
            else:
                for a in reversed(inbox):
                    notification_list.controls.append(
                        ft.Container(
                            bgcolor=BG_CARD, padding=10, border_radius=8,
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.Icons.CIRCLE, color=ERROR, size=10), ft.Text(f"ALERTA: {a['consulta_nombre']}", size=10, color=ERROR, weight=ft.FontWeight.BOLD)]),
                                ft.Text(a['article_headline'], size=12, color=TEXT_PRIMARY),
                                ft.Row([
                                    ft.Text(f"Puntaje: {a['similarity_score']}", size=10, color=TEXT_MUTED),
                                    ft.TextButton("Leer artículo", on_click=lambda e, u=a['url']: os.startfile(u), style=ft.ButtonStyle(padding=0))
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            ], spacing=2)
                        )
                    )
        page.update()

    def close_alerts(e):
        alerts_panel.width = 0
        alerts_panel.padding = 0
        alerts_btn.icon_color = TEXT_PRIMARY
        page.update()

    def toggle_alerts(e):
        if alerts_panel.width == 0:
            render_alerts()
            alerts_panel.width = 350
            alerts_panel.padding = 20
            alerts_btn.icon_color = TEXT_PRIMARY
        else:
            alerts_panel.width = 0
            alerts_panel.padding = 0
        page.update()

    alerts_panel = ft.Container(
        width=0, padding=0, bgcolor=BG_SIDEBAR, animate=300,
        content=ft.Column([
            ft.Row([
                ft.Text("Centro de Alertas", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.IconButton(ft.Icons.CLOSE, on_click=close_alerts)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(thickness=1, color=BORDER),
            ft.Text("Temas Seguidos", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            subscription_list,
            ft.Divider(thickness=1, color=BORDER),
            ft.Text("Coincidencias Recientes", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            notification_list
        ])
    )

    # ========== SEMANTIC WEB MODAL ==========
    semantic_content = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=15)

    def close_semantic(e):
        semantic_overlay.visible = False
        page.update()

    semantic_overlay = ft.Container(
        expand=True, bgcolor="black54", visible=False,
        content=ft.Row(controls=[
            ft.Column(controls=[
                ft.Container(
                    bgcolor=BG_CARD, padding=0, border_radius=16,
                    width=1000, height=800,
                    content=ft.Column([
                        ft.Container(
                            padding=ft.Padding(30, 24, 24, 16),
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(
                                        bgcolor="#a78bfa18", padding=12, border_radius=12,
                                        content=ft.Icon(ft.Icons.ACCOUNT_TREE, color=PRIMARY, size=22)
                                    ),
                                    ft.Column([
                                        ft.Text("Explorador Semántico", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                        ft.Text("Ontologías · SPARQL · SHACL · Datos Enlazados", size=12, color=TEXT_MUTED),
                                    ], spacing=2),
                                ], spacing=14),
                                ft.IconButton(ft.Icons.CLOSE, on_click=close_semantic, icon_color=TEXT_MUTED, icon_size=22)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ),
                        ft.Divider(color=BORDER, height=1),
                        ft.Container(content=semantic_content, expand=True, padding=ft.Padding(30, 20, 30, 24))
                    ], spacing=0)
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    )

    def open_semantic(e):
        spinner.visible = True
        page.update()
        builder = GraphAssembler()
        ok = builder.construct()
        if not ok:
            semantic_content.controls = [ft.Text("El corpus está vacío. Actualiza el corpus primero.", color=ERROR)]
        else:
            r1, r2, r3 = builder.query_insights()
            shacl_ok = builder.validate()
            builder.serialize()
            shacl_color = SUCCESS if shacl_ok else ERROR
            shacl_text = "VÁLIDO (Compatible W3C)" if shacl_ok else "NO VÁLIDO"

            def make_data_card(cols, rows_dict):
                cards = []
                for row in rows_dict:
                    vals = list(row.values())
                    primary = str(vals[0]) if len(vals) > 0 else ""
                    secondary = str(vals[1]) if len(vals) > 1 else ""
                    cards.append(
                        ft.Container(
                            bgcolor="#0f0f1a", padding=14, border_radius=10,
                            border=_bd("#1e293b"),
                            content=ft.Column([
                                ft.Row([
                                    ft.Container(width=4, height=20, bgcolor=PRIMARY, border_radius=2),
                                    ft.Text(primary, size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, expand=True),
                                ], spacing=10),
                                ft.Text(secondary, size=13, color=TEXT_MUTED),
                            ], spacing=6)
                        )
                    )
                return ft.Column(cards, spacing=8)

            def section_card(content, expand=False):
                return ft.Container(
                    padding=16, border_radius=12, bgcolor=BG_SIDEBAR,
                    content=ft.Column(content, spacing=6), expand=expand
                )

            semantic_content.controls = [
                ft.Row([
                    section_card([
                        ft.Row([ft.Icon(ft.Icons.BAR_CHART, color=PRIMARY, size=18), ft.Text("Distribución Cuantitativa por Categoría", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                        ft.Divider(color=BORDER, height=12),
                        make_data_card(["Categoría Semántica", "Total Nodos de Artículo"], r1),
                    ], expand=True),
                    ft.Container(width=12),
                    section_card([
                        ft.Row([ft.Icon(ft.Icons.LINK, color=ACCENT, size=18), ft.Text("Enlaces Externos a la Nube de Datos Enlazados", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                        ft.Divider(color=BORDER, height=12),
                        make_data_card(["Nodo de Ontología Local", "URI de Wikidata Mapeada"], r3),
                    ], expand=True),
                ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START),
                section_card([
                    ft.Row([ft.Icon(ft.Icons.PERSON, color=SUCCESS, size=18), ft.Text("Auditoría de Nodos de Autoría", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                    ft.Divider(color=BORDER, height=12),
                    make_data_card(["Nodo de Autor", "Título del Artículo"], r2),
                ]),
                ft.Row([
                    section_card([
                        ft.Row([ft.Icon(ft.Icons.FOLDER_OPEN, color="#fbbf24", size=18), ft.Text("Archivos Generados", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                        ft.Divider(color=BORDER, height=12),
                        ft.Row([
                            ft.TextButton("Turtle (.ttl)", icon=ft.Icons.CODE, on_click=lambda e: os.startfile(builder.ttl_path), style=ft.ButtonStyle(color=PRIMARY, bgcolor="#0f0f1a")),
                            ft.TextButton("RDF/XML (.rdf)", icon=ft.Icons.CODE, on_click=lambda e: os.startfile(builder.rdf_path), style=ft.ButtonStyle(color=PRIMARY, bgcolor="#0f0f1a")),
                            ft.TextButton("JSON-LD", icon=ft.Icons.DATA_OBJECT, on_click=lambda e: os.startfile(builder.jsonld_path), style=ft.ButtonStyle(color=PRIMARY, bgcolor="#0f0f1a")),
                        ], spacing=10, wrap=True)
                    ], expand=True),
                    ft.Container(width=12),
                    ft.Container(
                        padding=16, border_radius=12, bgcolor=BG_SIDEBAR,
                        content=ft.Row([
                            ft.Row([ft.Icon(ft.Icons.VERIFIED, color=shacl_color, size=18), ft.Text("Validación SHACL", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                            ft.Container(
                                content=ft.Row([ft.Icon(ft.Icons.CIRCLE, color=shacl_color, size=8), ft.Text(shacl_text, size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=4),
                                bgcolor=shacl_color + "30", padding=ft.Padding(10, 5, 10, 5), border_radius=20
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ),
                ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START),
            ]
        spinner.visible = False
        semantic_overlay.visible = True
        page.update()

    # ========== CHAT OVERLAY ==========
    chat_history = ft.ListView(expand=True, spacing=15, auto_scroll=True, padding=10)
    chat_input = ft.TextField(hint_text="Pregunta a OrbitalView...", expand=True, border_radius=20, bgcolor=BG_CARD, border_color="transparent")

    chat_overlay = ft.Container(
        expand=True, bgcolor="black54", visible=False,
        content=ft.Row(controls=[
            ft.Column(controls=[
                ft.Container(
                    bgcolor=BG_SIDEBAR, padding=20, border_radius=10,
                    width=500, height=600,
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Asistente IA", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Row([
                                ft.IconButton(ft.Icons.DELETE_SWEEP, icon_color=TEXT_MUTED, tooltip="Limpiar historial", on_click=lambda e: reset_chat(e)),
                                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: setattr(chat_overlay, 'visible', False) or page.update())
                            ])
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(thickness=1, color=BORDER),
                        chat_history,
                        ft.Row([chat_input, ft.IconButton(icon=ft.Icons.SEND, icon_color=PRIMARY, on_click=lambda e: send_chat(e))])
                    ])
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    )

    def send_chat(e):
        text = chat_input.value.strip()
        if not text or not hasattr(page, 'chatbot') or not page.chatbot:
            return
        chat_input.value = ""
        chat_history.controls.append(ft.Row([ft.Container(content=ft.Text(text, color=TEXT_PRIMARY), bgcolor=PRIMARY, padding=12, border_radius=15)], alignment=ft.MainAxisAlignment.END))
        page.update()
        reply, rtype, confidence = page.chatbot.respond(text)
        badge_color = SUCCESS if confidence > 0.1 else ERROR
        chat_history.controls.append(ft.Row([ft.Container(content=ft.Column([ft.Row([ft.Text("OrbitalView", weight=ft.FontWeight.BOLD, color=TEXT_MUTED), ft.Container(content=ft.Text(f"{rtype.upper()} | {(confidence*100):.1f}%", size=10, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD), bgcolor=badge_color, padding=3, border_radius=5)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Text(reply, color=TEXT_PRIMARY)]), bgcolor=BG_CARD, padding=12, border_radius=15, width=350)], alignment=ft.MainAxisAlignment.START))
        page.update()

    def reset_chat(e):
        chat_history.controls.clear()
        if hasattr(page, 'chatbot') and page.chatbot:
            page.chatbot.memory.clear()
            page.chatbot.interests.clear()
        page.update()

    chat_input.on_submit = send_chat

    def open_chat(e):
        chat_overlay.visible = True
        page.update()

    # ========== INSPECTOR MODAL ==========
    inspector_content = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=15)

    def close_inspector(e):
        inspector_overlay.visible = False
        page.update()

    def subscribe_topic(article):
        nid = "Q_" + str(uuid.uuid4())[:6]
        words = [p for p in re.sub(r'[^\w\s]', '', article['headline'].lower()).split() if len(p) > 3]
        query_str = " ".join(words[:5])
        new_query = {
            "id": nid,
            "nombre": f"[{article['topic'].upper()}] {query_str}",
            "query": query_str,
            "created_at": datetime.now().isoformat()
        }
        page.monitor.watchlist.append(new_query)
        with open(page.monitor.watchlist_file, 'w', encoding='utf-8') as f:
            json.dump(page.monitor.watchlist, f, ensure_ascii=False, indent=2)
        page.snack_bar = ft.SnackBar(ft.Text(f"Tracking enabled: '{query_str}'", color=TEXT_PRIMARY), bgcolor=SUCCESS)
        page.snack_bar.open = True
        render_alerts()
        page.update()

    inspector_overlay = ft.Container(
        expand=True, bgcolor="black54", visible=False,
        content=ft.Row(controls=[
            ft.Column(controls=[
                ft.Container(
                    bgcolor=BG_CARD, padding=30, border_radius=10,
                    width=960, height=760,
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Inspector Predictivo", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.IconButton(ft.Icons.CLOSE, on_click=close_inspector)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(color=BORDER),
                        ft.Container(content=inspector_content, expand=True)
                    ])
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    )

    def open_inspector(article):
        title = str(article.get("headline", "Sin título"))
        body = str(article.get("body", "Sin contenido"))
        real_cat = str(article.get("topic", "Desconocida")).upper()
        url = str(article.get("url", "#"))
        date = str(article.get("date", "Desconocida"))
        author = str(article.get("author", "Desconocido"))
        source = str(article.get("source", "Desconocida"))

        prediction, model_used = "PROCESANDO...", "Desconocido"
        if page.classifier_model and getattr(page.classifier_model, 'champion', None):
            try:
                pred_arr = page.classifier_model.classify([f"{title}. {body}"])
                prediction = str(pred_arr[0]).upper()
                model_used = str(page.classifier_model.champion[0])
            except Exception:
                pass

        pred_color = SUCCESS if prediction == real_cat else ERROR
        sentiment_score = page.sia.polarity_scores(body)['compound']
        sent_color = SUCCESS if sentiment_score >= 0.07 else (ERROR if sentiment_score <= -0.07 else TEXT_MUTED)
        sent_label = 'POSITIVO' if sentiment_score >= 0.07 else ('NEGATIVO' if sentiment_score <= -0.07 else 'NEUTRAL')

        def badge(text, bg, fg=TEXT_PRIMARY):
            return ft.Container(content=ft.Text(text, color=fg, weight=ft.FontWeight.BOLD, size=11), bgcolor=bg, padding=ft.Padding(10, 5, 10, 5), border_radius=12)

        kg = Graph()
        connector = WikidataBridge(kg)
        wd_data = connector.get_fallback(real_cat.lower())

        # -------- TAB 1: ARTÍCULO --------
        def meta_chip(icon, label, value):
            return ft.Container(
                bgcolor=BG_SIDEBAR, padding=ft.Padding(12, 8, 12, 8), border_radius=10,
                border=_bd("#1e293b", 1),
                expand=True,
                content=ft.Column([
                    ft.Row([ft.Icon(icon, size=14, color=TEXT_MUTED), ft.Text(label, size=10, color=TEXT_MUTED)], spacing=4),
                    ft.Text(value, size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ], spacing=2)
            )

        meta_row = ft.Row([
            meta_chip(ft.Icons.CALENDAR_MONTH, "FECHA", date),
            meta_chip(ft.Icons.PERSON, "AUTOR", author),
            meta_chip(ft.Icons.NEWSPAPER, "FUENTE", source),
        ], spacing=8)

        article_tab = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Container(
                    padding=ft.Padding(0, 0, 0, 8),
                    content=ft.Column([
                        ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, height=None),
                        ft.Container(height=10),
                        meta_row,
                    ], spacing=0)
                ),
                ft.Divider(color=BORDER, height=1),
                ft.Container(
                    expand=True,
                    content=ft.Text(body, size=15, color=TEXT_PRIMARY, text_align=ft.TextAlign.JUSTIFY),
                ),
            ], spacing=0)
        )

        # -------- TAB 2: PREDICCIÓN --------
        def comp_card(label, value, color, icon):
            return ft.Container(
                bgcolor=BG_SIDEBAR, padding=20, border_radius=12, expand=True,
                border=_bd(color, 1),
                content=ft.Column([
                    ft.Row([ft.Icon(icon, color=color, size=20), ft.Text(label, size=11, color=TEXT_MUTED)], spacing=6),
                    ft.Container(height=6),
                    ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )

        sent_bar_width = int(abs(sentiment_score) * 200)
        sent_bar_width = max(8, min(sent_bar_width, 200))

        def section_card(content, icon, title_text, accent=PRIMARY):
            return ft.Container(
                bgcolor=BG_CARD, padding=18, border_radius=12, border=_bd(BORDER),
                content=ft.Column([
                    ft.Row([ft.Icon(icon, color=accent, size=18), ft.Text(title_text, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                    ft.Divider(color=BORDER, height=12),
                    content,
                ], spacing=0)
            )

        pred_tab = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Row([
                    comp_card("CATEGORÍA REAL", real_cat, SUCCESS, ft.Icons.CHECK_CIRCLE),
                    ft.Container(width=12),
                    comp_card("PREDICCIÓN IA", prediction, pred_color, ft.Icons.PRECISION_MANUFACTURING),
                ], spacing=0),
                ft.Container(height=12),
                section_card(
                    ft.Column([
                        ft.Row([
                            ft.Text("Modelo:", size=13, color=TEXT_MUTED),
                            ft.Container(content=ft.Text(model_used, size=13, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD), bgcolor="#a78bfa20", padding=ft.Padding(10, 4, 10, 4), border_radius=8),
                        ], spacing=10),
                        ft.Row([
                            ft.Text("Coincidencia:", size=13, color=TEXT_MUTED),
                            ft.Text("SÍ" if prediction == real_cat else "NO", size=14, color=SUCCESS if prediction == real_cat else ERROR, weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.Icons.CHECK_CIRCLE if prediction == real_cat else ft.Icons.CANCEL, color=SUCCESS if prediction == real_cat else ERROR, size=16),
                        ], spacing=10),
                    ], spacing=8),
                    ft.Icons.MODEL_TRAINING, "Detalles del Modelo", PRIMARY
                ),
                ft.Container(height=12),
                section_card(
                    ft.Column([
                        ft.Row([
                            badge(sent_label, sent_color),
                            ft.Text(f"Score: {sentiment_score:.3f}", size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        ], spacing=12),
                        ft.Container(height=6),
                        ft.Stack([
                            ft.Container(height=8, border_radius=4, bgcolor="#1e293b"),
                            ft.Container(height=8, border_radius=4, bgcolor=sent_color, width=sent_bar_width),
                        ]),
                        ft.Row([
                            ft.Text("Negativo", size=10, color=TEXT_MUTED),
                            ft.Text("Positivo", size=10, color=TEXT_MUTED),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=0),
                    ft.Icons.SENTIMENT_SATISFIED_ALT, "Análisis de Sentimiento", sent_color
                ),
            ], spacing=0, scroll=ft.ScrollMode.ADAPTIVE)
        )

        # -------- TAB 3: CONTEXTO --------
        wd_cards = []
        if wd_data:
            for item in wd_data:
                wd_label = item['itemLabel']['value']
                wd_desc = item.get('description', {}).get('value', '')
                wd_uri = item['item']['value']
                wd_id = wd_uri.split('/')[-1]
                wd_cards.append(
                    ft.Container(
                        bgcolor=BG_SIDEBAR, padding=0, border_radius=10,
                        border=_bd("#1e293b", 1),
                        content=ft.Column([
                            ft.Container(
                                bgcolor=PRIMARY + "20", padding=ft.Padding(14, 10, 14, 10),
                                content=ft.Row([
                                    ft.Container(
                                        bgcolor=PRIMARY, padding=ft.Padding(8, 4, 8, 4), border_radius=6,
                                        content=ft.Text(wd_id, size=10, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD)
                                    ),
                                    ft.Text(wd_label.upper(), size=14, weight=ft.FontWeight.BOLD, color=PRIMARY, expand=True),
                                ], spacing=10)
                            ),
                            ft.Container(
                                padding=ft.Padding(14, 8, 14, 12),
                                content=ft.Column([
                                    ft.Text(wd_desc if wd_desc else "Sin descripción disponible", size=12, color=TEXT_MUTED),
                                    ft.Container(height=8),
                                    ft.Container(
                                        on_click=lambda e, u=wd_uri: os.startfile(u),
                                        bgcolor=PRIMARY, padding=ft.Padding(10, 6, 10, 6), border_radius=8,
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.OPEN_IN_NEW, size=14, color=TEXT_PRIMARY),
                                            ft.Text("Abrir en Wikidata", size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                                    ),
                                ], spacing=0)
                            ),
                        ], spacing=0)
                    )
                )

        context_tab = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_TREE, color=SUCCESS, size=20),
                        ft.Text("Conexiones con Wikidata", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ], spacing=8),
                    padding=ft.Padding(0, 0, 0, 8),
                ),
                ft.Divider(color=BORDER, height=1),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        wd_cards if wd_cards else [ft.Container(
                            padding=40,
                            content=ft.Column([
                                ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=TEXT_MUTED),
                                ft.Text("Sin datos de Wikidata para esta categoría", color=TEXT_MUTED, size=14),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                        )],
                        spacing=10, scroll=ft.ScrollMode.ADAPTIVE
                    ),
                ),
            ], spacing=0)
        )

        # -------- TABS + FOOTER --------
        tabs = ft.Tabs(
            length=3,
            expand=True,
            content=ft.Column([
                ft.TabBar(
                    label_color=TEXT_PRIMARY, unselected_label_color=TEXT_MUTED,
                    indicator_color=PRIMARY,
                    tabs=[
                        ft.Tab(label="Artículo", icon=ft.Icons.ARTICLE),
                        ft.Tab(label="Predicción", icon=ft.Icons.INSIGHTS),
                        ft.Tab(label="Contexto", icon=ft.Icons.ACCOUNT_TREE),
                    ],
                ),
                ft.TabBarView(expand=True, controls=[article_tab, pred_tab, context_tab]),
            ])
        )

        inspector_content.controls = [
            tabs,
            ft.Divider(color=BORDER, height=1),
            ft.Container(
                padding=ft.Padding(0, 6, 0, 0),
                content=ft.Row([
                    ft.TextButton("Abrir original", icon=ft.Icons.OPEN_IN_NEW, on_click=lambda e: os.startfile(url), style=ft.ButtonStyle(color=TEXT_MUTED)),
                    ft.ElevatedButton("Seguir similares", icon=ft.Icons.NOTIFICATION_ADD, on_click=lambda e: subscribe_topic(article), style=ft.ButtonStyle(bgcolor=PRIMARY, color=TEXT_PRIMARY)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        ]
        inspector_overlay.visible = True
        page.update()

    # ========== EXTRACTION MODAL ==========
    extraction_overlay = ft.Container(
        expand=True, bgcolor="black54", visible=False,
        content=ft.Row(controls=[ft.Column(controls=[ft.Container(bgcolor=BG_CARD, padding=30, border_radius=10, width=500, content=ft.Column([ft.Text("Pipeline Complete", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY), ft.Divider(color=BORDER), ft.Text("Ingestion phase finished. Check the quality log for details.", size=16, color=TEXT_PRIMARY), ft.Container(height=10), ft.Row([ft.TextButton("Close", on_click=lambda e: setattr(extraction_overlay, 'visible', False) or page.update()), ft.TextButton("View Log", on_click=lambda e: os.startfile(QC_REPORT_PATH), style=ft.ButtonStyle(bgcolor=PRIMARY, color=TEXT_PRIMARY))], alignment=ft.MainAxisAlignment.END)], tight=True))], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    )

    # ========== ASYNC EXTRACTION ==========
    spinner = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

    async def run_extraction(e):
        update_btn.disabled = True
        spinner.visible = True
        page.update()

        def extraction_task():
            os.makedirs(os.path.dirname(CORPUS_PATH), exist_ok=True)
            scanner = FeedScanner(config_location=RSS_CONFIG_PATH, cap_per_topic=250, filter_age=False)
            scanner.run()
            scanner.persist(destination=CORPUS_PATH)
            from engine.text_miner import NLPExtractor
            import matplotlib
            matplotlib.use('Agg')
            from engine.analysis_hub import ContentProfiler
            NLPExtractor(CORPUS_PATH).run()
            ContentProfiler(CORPUS_PATH).analyze_timeline()

        await asyncio.to_thread(extraction_task)

        with open(CORPUS_PATH, 'r', encoding='utf-8') as f:
            fresh_data = json.load(f)

        new_alerts = page.monitor.inspect(fresh_data)
        if new_alerts:
            alerts_btn.icon_color = ERROR
            alert_inbox_data = []
            if os.path.exists(ALERT_INBOX):
                with open(ALERT_INBOX, 'r') as f:
                    alert_inbox_data = json.load(f)
            alert_inbox_data.extend(new_alerts)
            with open(ALERT_INBOX, 'w') as f:
                json.dump(alert_inbox_data, f, indent=2)
            render_alerts()
            page.snack_bar = ft.SnackBar(ft.Text(f"{len(new_alerts)} new articles match your interests!"), bgcolor=ERROR)
            page.snack_bar.open = True

        update_btn.disabled = False
        spinner.visible = False
        evaluate_dataset()
        extraction_overlay.visible = True
        page.update()

    # ========== SIDEBAR ==========
    sidebar_btn_style = ft.ButtonStyle(color=TEXT_MUTED, bgcolor="transparent")
    sidebar_active_style = ft.ButtonStyle(color=TEXT_PRIMARY, bgcolor=BG_CARD)

    nav_search_btn = ft.TextButton("Buscar", icon=ft.Icons.SEARCH, style=sidebar_btn_style)
    nav_dash_btn = ft.TextButton("Panel", icon=ft.Icons.INSIGHTS, style=sidebar_btn_style)

    def switch_view(view):
        if view == "search":
            main_area.content = search_container
            nav_search_btn.style = sidebar_active_style
            nav_dash_btn.style = sidebar_btn_style
        else:
            main_area.content = dashboard_container
            nav_search_btn.style = sidebar_btn_style
            nav_dash_btn.style = sidebar_active_style
        page.update()

    nav_search_btn.on_click = lambda e: switch_view("search")
    nav_dash_btn.on_click = lambda e: switch_view("dashboard")

    vector_toggle = ft.Switch(label="Vector IA", value=False, tooltip="Alternar búsqueda Booleana vs Vectorial", active_color=PRIMARY, active_track_color="#a78bfa40", inactive_thumb_color=PRIMARY)
    alerts_btn = ft.IconButton(ft.Icons.NOTIFICATIONS, icon_color=TEXT_PRIMARY, tooltip="Alertas", on_click=toggle_alerts)
    update_btn = ft.TextButton("Actualizar Corpus", icon=ft.Icons.DOWNLOAD, on_click=run_extraction, style=ft.ButtonStyle(color=TEXT_PRIMARY, bgcolor=PRIMARY, padding=ft.Padding(10, 5, 10, 5)))

    sidebar = ft.Container(
        width=220, bgcolor=BG_SIDEBAR, padding=ft.Padding(left=10, top=12, right=10, bottom=0),
        content=ft.Column([
            ft.Text("InfoStream", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY),
            ft.Container(content=update_btn, padding=ft.Padding(0, 0, 0, 4), alignment=ft.alignment.Alignment.CENTER),
            ft.Divider(color=BORDER),
            ft.Row([
                ft.Row([ft.Icon(ft.Icons.TUNE, size=16, color=TEXT_MUTED), vector_toggle], spacing=6),
                alerts_btn,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color=BORDER, height=8),
            nav_search_btn,
            ft.Container(height=5),
            nav_dash_btn,
            ft.Container(height=5),
            ft.TextButton("Web Semántica", icon=ft.Icons.ACCOUNT_TREE, on_click=open_semantic, style=sidebar_btn_style),
            ft.Container(height=5),
            ft.TextButton("Chat IA", icon=ft.Icons.CHAT, on_click=open_chat, style=sidebar_btn_style),
            ft.Container(expand=True),
            ft.Text("v1.0.0", size=10, color=TEXT_MUTED)
        ])
    )

    # ========== TOP BAR ==========
    search_field = ft.TextField(hint_text="Buscar artículos...", dense=True, border_radius=20, prefix_icon=ft.Icons.SEARCH, expand=True, bgcolor=BG_CARD, border_color="transparent", on_submit=lambda e: execute_search(e))

    top_bar = ft.Container(
        bgcolor=BG_SIDEBAR, padding=ft.Padding(left=20, top=5, right=20, bottom=5),
        content=ft.Row([spinner, ft.Container(width=10), search_field], expand=True, spacing=0)
    )

    # ========== SEARCH VIEW ==========
    search_container = ft.Container(expand=True)
    empty_view = ft.Row([ft.Column([ft.Icon(ft.Icons.DATA_USAGE, size=80, color=TEXT_MUTED), ft.Text("El corpus está vacío", size=24, weight=ft.FontWeight.BOLD, color=TEXT_MUTED)], alignment=ft.MainAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER, expand=True)

    def make_article_card(article):
        cat = str(article.get("topic") or "GENERAL").upper()
        date = str(article.get("date") or "Sin fecha")[:10]
        title = str(article.get("headline") or "Sin título")
        body = str(article.get("body") or "Sin contenido")
        snippet = body[:200] + "..." if len(body) > 200 else body
        return ft.Card(
            elevation=2,
            content=ft.Container(
                bgcolor=BG_CARD, padding=15,
                on_click=lambda e, n=article: open_inspector(n),
                content=ft.Column([
                    ft.Row([ft.Text(cat, size=12, color=PRIMARY, weight=ft.FontWeight.BOLD), ft.Text(date, size=12, color=TEXT_MUTED)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text(snippet, size=14, color=TEXT_PRIMARY),
                ], spacing=5)
            )
        )

    def evaluate_dataset():
        if not os.path.exists(CORPUS_PATH):
            search_container.content = empty_view
        else:
            try:
                with open(CORPUS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    page.searcher = RetrievalComparator(data)
                    searcher_obj = QuickFinder(data)
                    page.chatbot = ChatController(searcher_obj)
                    page.classifier_model = ModelEvaluator()
                    train_texts = [f"{n.get('headline','')} {n.get('body','')}" for n in data]
                    train_labels = [n.get('topic', 'GENERAL') for n in data]
                    page.classifier_model.evaluate_all(train_texts, train_labels, folds=3)
                if not data or not isinstance(data, list):
                    search_container.content = empty_view
                else:
                    render_dashboard(data)
                    news_list = ft.ListView(expand=True, spacing=10, padding=20, controls=[])
                    for article in data[:50]:
                        news_list.controls.append(make_article_card(article))
                    search_container.content = news_list
            except Exception as e:
                search_container.content = ft.Row([ft.Container(content=ft.Text(f"Critical error:\n{str(e)}", color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD), bgcolor=ERROR, padding=20, border_radius=10)], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        page.update()

    def execute_search(e):
        query = search_field.value.strip()
        if not page.searcher:
            return
        if not query:
            news_list = ft.ListView(expand=True, spacing=10, padding=20, controls=[])
            for article in page.searcher.records[:50]:
                news_list.controls.append(make_article_card(article))
            search_container.content = news_list
            page.update()
            return
        spinner.visible = True
        page.update()
        results_list = ft.ListView(expand=True, spacing=10, padding=20, controls=[])
        is_vector = vector_toggle.value
        if is_vector:
            raw = page.searcher.vector_retrieve(query, top=20)
            found_indices = [idx for idx, sim in raw]
        else:
            found_indices = page.searcher.boolean_retrieve(query)
            if not found_indices:
                raw = page.searcher.vector_retrieve(query, top=15)
                found_indices = [idx for idx, sim in raw]
        if not found_indices:
            results_list.controls.append(ft.Row([ft.Text(f"Sin resultados para '{query}'.", color=TEXT_MUTED, size=18)], alignment=ft.MainAxisAlignment.CENTER))
        else:
            for idx in found_indices:
                results_list.controls.append(make_article_card(page.searcher.records[idx]))
        search_container.content = results_list
        spinner.visible = False
        page.update()

    # ========== DASHBOARD ==========
    dashboard_container = ft.Container(expand=True, padding=20)

    def render_dashboard(data):
        if not data:
            dashboard_container.content = ft.Row([ft.Text("No hay datos para analizar.", color=ERROR)], alignment=ft.MainAxisAlignment.CENTER)
            return
        import collections
        categories = [d.get("topic", "GENERAL").upper() for d in data]
        counts = collections.Counter(categories)
        max_val = max(counts.values()) if counts else 1

        # --- KPI row ---
        total_articles = len(data)
        total_cats = len(counts)
        top_cat, top_val = counts.most_common(1)[0] if counts else ("—", 0)

        def kpi_card(icon, label, value, clr):
            return ft.Container(
                bgcolor=BG_CARD, padding=20, border_radius=12,
                border=_bd(BORDER), expand=1,
                content=ft.Column([
                    ft.Row([ft.Icon(icon, color=clr, size=18), ft.Text(label, size=11, color=TEXT_MUTED)], spacing=8),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ], spacing=2)
            )

        kpi_row = ft.Row([
            kpi_card(ft.Icons.ARTICLE, "Total Artículos", total_articles, PRIMARY),
            kpi_card(ft.Icons.CATEGORY, "Categorías", total_cats, SUCCESS),
            kpi_card(ft.Icons.TRENDING_UP, "Categoría Principal", f"{top_cat} ({top_val})", "#fbbf24"),
        ], spacing=15)

        # --- Category distribution ---
        palette = [PRIMARY, SUCCESS, "#fbbf24", ERROR, "#c084fc", "#fb923c"]
        bars = []
        for i, (cat, val) in enumerate(counts.most_common()):
            color = palette[i % len(palette)]
            pct = val / max_val
            bars.append(
                ft.Container(
                    padding=12, bgcolor="#0f0f1a", border_radius=8,
                    border=_bd("#1e293b"),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(cat, weight=ft.FontWeight.BOLD, size=12, color=TEXT_PRIMARY, expand=True),
                            ft.Text(str(val), size=12, color=TEXT_MUTED),
                        ]),
                        ft.Stack([
                            ft.Container(height=8, border_radius=4, bgcolor="#1e293b"),
                            ft.Container(height=8, border_radius=4, bgcolor=color, width=max(int(pct * 280), 10)),
                        ])
                    ], spacing=6)
                )
            )

        cat_card = ft.Container(
            bgcolor=BG_CARD, padding=20, border_radius=12,
            border=_bd(BORDER), expand=1,
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.BAR_CHART, color=PRIMARY, size=18), ft.Text("Distribución del Corpus", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                ft.Divider(color=BORDER, height=14),
                ft.Column(bars, spacing=8, scroll=ft.ScrollMode.ADAPTIVE, expand=True),
            ], spacing=0)
        )

        # --- Stats & per-category ---
        stats_path = f"{BASE}/exports/stats_nlp.json"
        per_cat_cards = []
        cloud_visuals = []

        if os.path.exists(stats_path):
            with open(stats_path, 'r') as f:
                stats = json.load(f)
            global_stats = stats.get("overview", {})

            sections = []
            for key, label in [("top_unigrams", "Unigramas"), ("top_bigrams", "Bigramas"), ("top_trigrams", "Trigramas")]:
                items = global_stats.get(key, [])
                if items:
                    sections.append(
                        ft.Column([
                            ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color=PRIMARY),
                            ft.Row([ft.Container(content=ft.Text(w, size=11, color=TEXT_PRIMARY), bgcolor="#0f0f1a", padding=ft.Padding(8, 4, 8, 4), border_radius=12) for w in items[:6]], wrap=True, spacing=4),
                        ], spacing=4)
                    )

            entities = global_stats.get("named_entities", [])
            if entities:
                sections.append(
                    ft.Column([
                        ft.Text("Entidades (NER)", size=10, weight=ft.FontWeight.BOLD, color=SUCCESS),
                        ft.Row([ft.Container(content=ft.Text(w, size=11, color=TEXT_PRIMARY), bgcolor="#34d39920", padding=ft.Padding(8, 4, 8, 4), border_radius=12) for w in entities[:6]], wrap=True, spacing=4),
                    ], spacing=4)
                )

            stats_card = ft.Container(
                bgcolor=BG_CARD, padding=20, border_radius=12,
                border=_bd(BORDER), expand=1,
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.ANALYTICS, color=ACCENT, size=18), ft.Text("Métricas Globales", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                    ft.Divider(color=BORDER, height=14),
                    ft.Column(sections, spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True),
                ], spacing=0)
            )

            cats_data = stats.get("by_category", {})
            for cat_name, c_data in cats_data.items():
                lexical = c_data.get('lexical_diversity', 0)
                rows = []
                for key, label in [("unigrams", "Uni"), ("bigrams", "Bi"), ("trigrams", "Tri")]:
                    items = c_data.get(key, [])
                    if items:
                        rows.append(ft.Row([ft.Text(f"{label}:", size=10, color=TEXT_MUTED, width=25), ft.Text(", ".join(items[:5]), size=10, color=TEXT_PRIMARY, expand=True)], spacing=4))
                per_cat_cards.append(
                    ft.Container(
                        bgcolor="#0f0f1a", padding=14, border_radius=10,
                        border=_bd("#1e293b"),
                        content=ft.Column([
                            ft.Row([
                                ft.Container(width=4, height=16, bgcolor="#fbbf24", border_radius=2),
                                ft.Text(cat_name.upper(), weight=ft.FontWeight.BOLD, size=12, color="#fbbf24", expand=True),
                                ft.Container(content=ft.Text(f"Riqueza: {lexical}", size=9, color=TEXT_PRIMARY), bgcolor="#fbbf2418", padding=ft.Padding(6, 2, 6, 2), border_radius=8),
                            ], spacing=8),
                            ft.Column(rows, spacing=2),
                        ], spacing=6)
                    )
                )
                img_path_cat = f"{BASE}/exports/{c_data.get('cloud_file')}"
                if os.path.exists(img_path_cat):
                    cloud_visuals.append(
                        ft.Container(
                            content=ft.Column([ft.Text(cat_name.upper(), size=10, weight=ft.FontWeight.BOLD, color=TEXT_MUTED), ft.Image(src=img_path_cat, width=200, height=120, fit="contain", border_radius=6)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                            bgcolor="#0f0f1a", padding=10, border_radius=10, border=_bd("#1e293b"),
                        )
                    )
            if os.path.exists(CLOUD_IMG):
                cloud_visuals.insert(0,
                    ft.Container(
                        content=ft.Column([ft.Text("GLOBAL", size=10, weight=ft.FontWeight.BOLD, color=TEXT_MUTED), ft.Image(src=CLOUD_IMG, width=200, height=120, fit="contain", border_radius=6)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        bgcolor="#0f0f1a", padding=10, border_radius=10, border=_bd("#1e293b"),
                    )
                )
        else:
            stats_card = ft.Container(
                bgcolor=BG_CARD, padding=20, border_radius=12,
                border=_bd(BORDER), expand=1,
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.ANALYTICS, color=ACCENT, size=18), ft.Text("Métricas Globales", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                    ft.Divider(color=BORDER, height=14),
                    ft.Text("Actualiza el corpus para ver métricas.", color=TEXT_MUTED, size=12),
                ], spacing=0)
            )

        # --- Per-category section ---
        per_cat_section = ft.Container(
            bgcolor=BG_CARD, padding=20, border_radius=12,
            border=_bd(BORDER),
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.DATASET, color="#fbbf24", size=18), ft.Text("Métricas por Categoría", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                ft.Divider(color=BORDER, height=14),
                ft.Column(per_cat_cards, spacing=8) if per_cat_cards else ft.Text("Actualiza el corpus...", color=TEXT_MUTED, size=12),
            ], spacing=0)
        )

        # --- Word clouds ---
        cloud_card = ft.Container(
            bgcolor=BG_CARD, padding=20, border_radius=12,
            border=_bd(BORDER),
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.CLOUD, color=PRIMARY, size=18), ft.Text("Nubes de Palabras", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                ft.Divider(color=BORDER, height=14),
                ft.Row(cloud_visuals, scroll=ft.ScrollMode.ADAPTIVE, spacing=12) if cloud_visuals else ft.Text("Actualiza el corpus...", color=TEXT_MUTED, size=12),
            ], spacing=0)
        )

        # --- Trend chart ---
        trend_card = ft.Container(
            bgcolor=BG_CARD, padding=20, border_radius=12,
            border=_bd(BORDER),
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.TIMELINE, color=SUCCESS, size=18), ft.Text("Evolución Temporal", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)], spacing=8),
                ft.Divider(color=BORDER, height=14),
                ft.Container(content=ft.Image(src=TREND_IMG, fit="contain", border_radius=8) if os.path.exists(TREND_IMG) else ft.Text("Actualiza el corpus...", color=TEXT_MUTED, size=12), expand=True),
            ], spacing=0)
        )

        dashboard_container.content = ft.ListView(
            controls=[
                trend_card,
                ft.Row([cat_card, stats_card], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START),
                per_cat_section,
                cloud_card,
                kpi_row,
            ],
            expand=True, spacing=15, padding=10
        )

    # ========== ASSEMBLY ==========
    main_area = ft.Container(content=search_container, expand=True)

    body = ft.Row([sidebar, ft.Column([top_bar, main_area], expand=True, spacing=0), alerts_panel], expand=True, spacing=0)

    stack = ft.Stack([body, extraction_overlay, inspector_overlay, semantic_overlay, chat_overlay], expand=True)

    page.add(stack)
    evaluate_dataset()


ft.run(main)
