"""
Module containing the HTML template for the presentation player.
PROGRAM_HTML_TEMPLATE contains doubled curly braces {{ and }} for CSS styles and JS code,
and a single {slides} placeholder for injecting the slides array via .format(slides=...).
"""

import json

PROGRAM_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation Studio</title>
  <style>
    :root {{
      --bg-workspace: #0f172a;
      --bg-panel: #1e293b;
      --bg-panel-hover: #334155;
      --border-color: #334155;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent: #f59e0b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --slide-bg: #ffffff;
      --slide-text: #0f172a;
      --slide-text-muted: #64748b;
      --slide-border: #e2e8f0;
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-family);
      background-color: var(--bg-workspace);
      color: var(--text-main);
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    /* Top toolbar (PowerPoint Ribbon / Header) */
    .top-toolbar {{
      height: 54px;
      background: var(--bg-panel);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      user-select: none;
      z-index: 10;
    }}

    .toolbar-left, .toolbar-center, .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-logo {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      font-size: 0.95rem;
      color: #38bdf8;
    }}

    .brand-logo svg {{
      width: 22px;
      height: 22px;
      fill: #38bdf8;
    }}

    .presentation-title {{
      font-size: 0.85rem;
      color: var(--text-muted);
      border-left: 1px solid var(--border-color);
      padding-left: 12px;
      max-width: 250px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .nav-btn {{
      background: var(--bg-panel-hover);
      color: var(--text-main);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 6px 14px;
      font-size: 0.85rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
      font-weight: 500;
    }}

    .nav-btn:hover:not(:disabled) {{
      background: #475569;
      border-color: #64748b;
    }}

    .nav-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .nav-btn.primary {{
      background: var(--primary);
      border-color: var(--primary);
      color: #ffffff;
    }}

    .nav-btn.primary:hover:not(:disabled) {{
      background: var(--primary-hover);
    }}

    .slide-counter {{
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-main);
      min-width: 100px;
      text-align: center;
    }}

    .keyboard-hint {{
      font-size: 0.75rem;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.06);
      padding: 4px 8px;
      border-radius: 4px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* Główny obszar roboczy */
    .workspace {{
      flex: 1;
      display: flex;
      overflow: hidden;
      position: relative;
    }}

    /* Panel boczny z miniaturami (jak w PowerPoint) */
    .thumbnails-sidebar {{
      width: 220px;
      background: #111827;
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      padding: 12px;
      gap: 12px;
      transition: width 0.2s ease, opacity 0.2s ease;
    }}

    .thumbnails-sidebar.collapsed {{
      width: 0;
      padding: 0;
      opacity: 0;
      pointer-events: none;
      border-right: none;
    }}

    .thumbnail-card {{
      background: #1e293b;
      border: 2px solid transparent;
      border-radius: 6px;
      padding: 8px 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.15s ease;
    }}

    .thumbnail-card:hover {{
      background: #334155;
    }}

    .thumbnail-card.active {{
      border-color: var(--primary);
      background: #1e3a8a;
    }}

    .thumbnail-num {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-muted);
      min-width: 20px;
    }}

    .thumbnail-card.active .thumbnail-num {{
      color: #93c5fd;
    }}

    .thumbnail-preview {{
      font-size: 0.75rem;
      color: var(--text-main);
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      flex: 1;
    }}

    /* Scena ze slajdem o stałym rozmiarze 16:9 */
    .slide-viewport {{
      flex: 1;
      background: #090d16;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      position: relative;
      overflow: hidden;
    }}

    /* Kontener slajdu - Sztywne proporcje 16:9, brak scrolla */
    .slide-frame {{
      aspect-ratio: 16 / 9;
      width: 100%;
      max-width: calc((100vh - 110px) * 16 / 9);
      max-height: calc(100vh - 110px);
      background: var(--slide-bg);
      color: var(--slide-text);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      overflow: hidden !important; /* Blokada scrolla */
      position: relative;
      display: flex;
      flex-direction: column;
    }}

    /* Tryb pełnoekranowy */
    body.is-fullscreen .top-toolbar,
    body.is-fullscreen .thumbnails-sidebar {{
      display: none !important;
    }}

    body.is-fullscreen .slide-viewport {{
      padding: 0;
      background: #000000;
    }}

    body.is-fullscreen .slide-frame {{
      border-radius: 0;
      max-width: calc(100vh * 16 / 9);
      max-height: 100vh;
      width: 100vw;
      height: 100vh;
      box-shadow: none;
    }}

    /* ========================================================
       SYSTEM DESIGNU SLAJDÓW DLA MODELU BIELIK (CSS Framework)
       Gotowe klasy, których model używa do budowy układu
       ======================================================== */
    .slide-container {{
      width: 100%;
      height: 100%;
      padding: 5% 6%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden !important;
      position: relative;
      box-sizing: border-box;
    }}

    /* Tytuł i nagłówek slajdu */
    .slide-header {{
      margin-bottom: 2%;
    }}

    .slide-tag {{
      display: inline-block;
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--primary);
      background: #eff6ff;
      padding: 4px 10px;
      border-radius: 20px;
      margin-bottom: 8px;
    }}

    .slide-title {{
      font-size: 2.2rem;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.2;
    }}

    .slide-subtitle {{
      font-size: 1.1rem;
      color: var(--slide-text-muted);
      margin-top: 6px;
      line-height: 1.4;
    }}

    /* Główna zawartość slajdu */
    .slide-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 16px;
      overflow: hidden !important;
    }}

    /* Układy kolumnowe */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: stretch;
      height: 100%;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 18px;
      align-items: stretch;
      height: 100%;
    }}

    /* Karta informacyjna */
    .card {{
      background: #f8fafc;
      border: 1px solid var(--slide-border);
      border-radius: 10px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
      overflow: hidden;
    }}

    .card.primary-accent {{
      border-top: 4px solid var(--primary);
      background: #ffffff;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
    }}

    .card.amber-accent {{
      border-top: 4px solid var(--accent);
      background: #ffffff;
    }}

    .card-title {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #1e293b;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .card-text {{
      font-size: 0.95rem;
      line-height: 1.5;
      color: #334155;
    }}

    /* Lista punktowana */
    .bullet-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .bullet-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      font-size: 1.05rem;
      color: #1e293b;
      line-height: 1.5;
    }}

    .bullet-icon {{
      flex-shrink: 0;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: #dbeafe;
      color: var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.75rem;
      margin-top: 3px;
    }}

    /* Wyróżniony cytat lub kluczowy wniosek */
    .highlight-box {{
      background: #f0f9ff;
      border-left: 5px solid #0284c7;
      border-radius: 0 8px 8px 0;
      padding: 18px 24px;
      margin: 8px 0;
    }}

    .highlight-box p {{
      font-size: 1.15rem;
      font-weight: 500;
      color: #0369a1;
      line-height: 1.5;
      font-style: italic;
    }}

    /* Kluczowa liczba / statystyka */
    .stat-display {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 16px;
    }}

    .stat-number {{
      font-size: 3.5rem;
      font-weight: 900;
      color: var(--primary);
      line-height: 1;
      margin-bottom: 8px;
    }}

    .stat-label {{
      font-size: 1rem;
      color: var(--slide-text-muted);
      font-weight: 600;
      max-width: 240px;
    }}

    /* Stopka slajdu */
    .slide-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid var(--slide-border);
      padding-top: 10px;
      font-size: 0.75rem;
      color: var(--slide-text-muted);
    }}
  </style>
</head>
<body>

  <!-- Pasek narzędziowy PowerPoint -->
  <header class="top-toolbar">
    <div class="toolbar-left">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
        <span>Presentation Studio</span>
      </div>
      <span class="presentation-title" id="pres-title">Prezentacja Edukacyjna</span>
      <button class="nav-btn" id="btn-toggle-sidebar" title="Pokaż/Ukryj miniatury">🗂 Miniatury</button>
    </div>

    <div class="toolbar-center">
      <button class="nav-btn" id="btn-prev" title="Poprzedni slajd (Strzałka w lewo)">◀ Poprzedni</button>
      <div class="slide-counter" id="slide-counter">Slajd 1 z 1</div>
      <button class="nav-btn primary" id="btn-next" title="Następny slajd (Strzałka w prawo lub Spacja)">Następny ▶</button>
    </div>

    <div class="toolbar-right">
      <span class="keyboard-hint">Nawigacja: ◄ ► Spacja | F11 Pełny ekran</span>
      <button class="nav-btn" id="btn-fullscreen" title="Pełny ekran">⛶ Pełny ekran</button>
    </div>
  </header>

  <!-- Obszar roboczy -->
  <main class="workspace">
    <!-- Miniatury slajdów -->
    <aside class="thumbnails-sidebar" id="thumbnails-container">
      <!-- Miniatury generowane przez JavaScript -->
    </aside>

    <!-- Scena slajdu o stałych wymiarach -->
    <section class="slide-viewport">
      <div class="slide-frame" id="slide-viewport-frame">
        <!-- Aktywny slajd renderowany tutaj -->
      </div>
    </section>
  </main>

  <script>
    /* ========================================================
       LISTA SLAJDÓW - MIEJSCE NA WSTRZYKNIĘCIE PRZEZ GENERATOR
       ======================================================== */
    const slidesData = {slides};

    /* ========================================================
       LOGIKA ODTWARZACZA PREZENTACJI (POWERPOINT VIEWER)
       ======================================================== */
    let currentSlideIndex = 0;

    const frameElement = document.getElementById("slide-viewport-frame");
    const counterElement = document.getElementById("slide-counter");
    const prevBtn = document.getElementById("btn-prev");
    const nextBtn = document.getElementById("btn-next");
    const fullscreenBtn = document.getElementById("btn-fullscreen");
    const toggleSidebarBtn = document.getElementById("btn-toggle-sidebar");
    const thumbnailsContainer = document.getElementById("thumbnails-container");

    function renderThumbnails() {{
      thumbnailsContainer.innerHTML = "";
      slidesData.forEach((slideHtml, index) => {{
        const card = document.createElement("div");
        card.className = `thumbnail-card ${{index === currentSlideIndex ? 'active' : ''}}`;
        
        // Wyciągamy tytuł lub tekst slajdu do podglądu na miniaturze
        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = slideHtml;
        const titleEl = tempDiv.querySelector(".slide-title") || tempDiv.querySelector("h1, h2, h3");
        const titleText = titleEl ? titleEl.textContent.trim() : `Slajd ${{index + 1}}`;

        card.innerHTML = `
          <span class="thumbnail-num">${{index + 1}}</span>
          <span class="thumbnail-preview">${{titleText}}</span>
        `;

        card.addEventListener("click", () => goToSlide(index));
        thumbnailsContainer.appendChild(card);
      }});
    }}

    function showSlide(index) {{
      if (slidesData.length === 0) {{
        frameElement.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:1.2rem;color:#64748b;">Brak slajdów do wyświetlenia</div>`;
        counterElement.textContent = "0 z 0";
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        return;
      }}

      currentSlideIndex = Math.max(0, Math.min(index, slidesData.length - 1));
      frameElement.innerHTML = slidesData[currentSlideIndex];
      counterElement.textContent = `Slajd ${{currentSlideIndex + 1}} z ${{slidesData.length}}`;

      prevBtn.disabled = currentSlideIndex === 0;
      nextBtn.disabled = currentSlideIndex === slidesData.length - 1;

      // Zaktualizuj aktywną miniaturę
      const cards = thumbnailsContainer.querySelectorAll(".thumbnail-card");
      cards.forEach((card, idx) => {{
        card.classList.toggle("active", idx === currentSlideIndex);
        if (idx === currentSlideIndex) {{
          card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
        }}
      }});
    }}

    function nextSlide() {{
      if (currentSlideIndex < slidesData.length - 1) {{
        showSlide(currentSlideIndex + 1);
      }}
    }}

    function prevSlide() {{
      if (currentSlideIndex > 0) {{
        showSlide(currentSlideIndex - 1);
      }}
    }}

    function goToSlide(index) {{
      showSlide(index);
    }}

    // Obsługa zdarzeń przycisków
    prevBtn.addEventListener("click", prevSlide);
    nextBtn.addEventListener("click", nextSlide);

    // Klawiatura
    window.addEventListener("keydown", (e) => {{
      if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") {{
        e.preventDefault();
        nextSlide();
      }} else if (e.key === "ArrowLeft" || e.key === "PageUp") {{
        e.preventDefault();
        prevSlide();
      }} else if (e.key === "Home") {{
        e.preventDefault();
        goToSlide(0);
      }} else if (e.key === "End") {{
        e.preventDefault();
        goToSlide(slidesData.length - 1);
      }} else if (e.key === "f" || e.key === "F" || e.key === "F11") {{
        if (e.key === "f" || e.key === "F") {{
          e.preventDefault();
          toggleFullscreen();
        }}
      }}
    }});

    // Pełny ekran
    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(() => {{}});
        document.body.classList.add("is-fullscreen");
      }} else {{
        if (document.exitFullscreen) {{
          document.exitFullscreen().catch(() => {{}});
        }}
        document.body.classList.remove("is-fullscreen");
      }}
    }}

    fullscreenBtn.addEventListener("click", toggleFullscreen);
    document.addEventListener("fullscreenchange", () => {{
      document.body.classList.toggle("is-fullscreen", !!document.fullscreenElement);
    }});

    // Pokaż / ukryj miniatury
    toggleSidebarBtn.addEventListener("click", () => {{
      thumbnailsContainer.classList.toggle("collapsed");
    }});

    // Inicjalizacja
    renderThumbnails();
    showSlide(0);
  </script>
</body>
</html>
"""


def render_presentation_html(slides: list[str]) -> str:
    """
    Renders the complete presentation HTML file by safely injecting the slides list.

    :param slides: List of HTML fragments representing individual slides.
    :return: Complete HTML document ready to be opened in any browser.
    """
    slides_json = json.dumps(slides, ensure_ascii=False)
    return PROGRAM_HTML_TEMPLATE.format(slides=slides_json)
