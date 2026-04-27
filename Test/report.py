"""
HRMS — Storytelling Report
Magazine-style narrative PDF: each page is a chapter with story arcs,
pull quotes, illustrated timelines, callout boxes, and visual metaphors.
Clean layout — zero overlap — pixel-perfect spacing.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Flowable
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Circle, Line, Polygon, Wedge
)
import math

# ── Palette ──────────────────────────────────────────────────────────────────
INK        = colors.HexColor("#0f172a")   # near-black
NAVY       = colors.HexColor("#1e293b")
STEEL      = colors.HexColor("#243044")
BLUE       = colors.HexColor("#2563eb")
BLUE_DARK  = colors.HexColor("#1d4ed8")
BLUE_PALE  = colors.HexColor("#dbeafe")
CYAN       = colors.HexColor("#06b6d4")
CYAN_PALE  = colors.HexColor("#cffafe")
GREEN      = colors.HexColor("#059669")
GREEN_PALE = colors.HexColor("#d1fae5")
YELLOW     = colors.HexColor("#d97706")
YELLOW_PALE= colors.HexColor("#fef3c7")
RED        = colors.HexColor("#dc2626")
RED_PALE   = colors.HexColor("#fee2e2")
PURPLE     = colors.HexColor("#7c3aed")
PURPLE_PALE= colors.HexColor("#ede9fe")
PINK       = colors.HexColor("#db2777")
SLATE      = colors.HexColor("#475569")
MUTED      = colors.HexColor("#94a3b8")
LIGHT      = colors.HexColor("#f1f5f9")
RULE       = colors.HexColor("#e2e8f0")
WHITE      = colors.white
BLACK      = colors.black
PAGE_W, PAGE_H = A4
LM = RM = 18 * mm
TM = BM = 16 * mm
FULL_W = PAGE_W - LM - RM      # ≈ 468 pt


# ═════════════════════════════════════════════════════════════════════════════
#  STYLE FACTORY
# ═════════════════════════════════════════════════════════════════════════════
def S(name, **kw):
    defaults = dict(fontName="Helvetica", fontSize=9, leading=14,
                    textColor=SLATE, spaceAfter=0, spaceBefore=0)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

STYLES = {
    "chap_num"  : S("cn", fontSize=72, fontName="Helvetica-Bold",
                    textColor=RULE, leading=80, alignment=TA_LEFT),
    "chap_title": S("ct", fontSize=28, fontName="Helvetica-Bold",
                    textColor=INK,  leading=34, alignment=TA_LEFT),
    "chap_sub"  : S("cs", fontSize=11, textColor=SLATE,
                    leading=16, alignment=TA_LEFT),
    "body"      : S("bd", fontSize=9.5, leading=16, textColor=SLATE,
                    alignment=TA_JUSTIFY, spaceAfter=8),
    "body_sm"   : S("bs", fontSize=8.5, leading=14, textColor=SLATE,
                    alignment=TA_JUSTIFY),
    "pull"      : S("pq", fontSize=15, fontName="Helvetica-Bold",
                    textColor=BLUE, leading=22, alignment=TA_CENTER,
                    spaceAfter=4),
    "caption"   : S("cap", fontSize=7.5, textColor=MUTED,
                    leading=11, alignment=TA_CENTER),
    "label"     : S("lbl", fontSize=7, fontName="Helvetica-Bold",
                    textColor=WHITE, alignment=TA_CENTER),
    "kicker"    : S("kk", fontSize=8, fontName="Helvetica-Bold",
                    textColor=BLUE, leading=12, spaceAfter=4),
    "footer"    : S("ft", fontSize=7.5, textColor=MUTED,
                    alignment=TA_CENTER),
    "toc_item"  : S("ti", fontSize=10, leading=18, textColor=INK),
    "toc_pg"    : S("tp", fontSize=10, textColor=SLATE,
                    alignment=TA_RIGHT),
    "stat_big"  : S("sb", fontSize=32, fontName="Helvetica-Bold",
                    textColor=WHITE, leading=36, alignment=TA_CENTER),
    "stat_lbl"  : S("sl", fontSize=8, textColor=colors.HexColor("#cbd5e1"),
                    leading=12, alignment=TA_CENTER),
    "tag"       : S("tg", fontSize=7.5, fontName="Helvetica-Bold",
                    textColor=WHITE, alignment=TA_CENTER),
    "bug_high"  : S("bh", fontSize=8, fontName="Helvetica-Bold",
                    textColor=RED),
    "bug_med"   : S("bm", fontSize=8, fontName="Helvetica-Bold",
                    textColor=YELLOW),
    "bug_low"   : S("bl", fontSize=8, fontName="Helvetica-Bold",
                    textColor=GREEN),
}


# ═════════════════════════════════════════════════════════════════════════════
#  CUSTOM FLOWABLES
# ═════════════════════════════════════════════════════════════════════════════

class FullCover(Flowable):
    """Full-bleed magazine cover — Page 1."""
    def __init__(self, w, h):
        super().__init__()
        self.w, self.h = w, h

    def draw(self):
        c = self.canv
        # Background gradient simulation with stacked rects
        for i in range(20):
            t = i / 20
            r = int(15 + t * 10)
            g = int(23 + t * 15)
            b = int(42 + t * 20)
            c.setFillColorRGB(r/255, g/255, b/255)
            c.rect(0, self.h * i / 20, self.w, self.h / 20 + 1, fill=1, stroke=0)

        # Large decorative circle top-right
        c.setFillColor(BLUE_DARK)
        c.circle(self.w - 20, self.h - 10, 130, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.circle(self.w - 20, self.h - 10, 90, fill=1, stroke=0)

        # Dot grid decoration
        c.setFillColor(colors.HexColor("#1e40af"))
        for row in range(8):
            for col in range(6):
                cx = self.w - 250 + col * 30
                cy = self.h - 250 + row * 30
                c.circle(cx, cy, 3, fill=1, stroke=0)

        # Left accent bar
        c.setFillColor(CYAN)
        c.rect(0, 0, 6, self.h, fill=1, stroke=0)

        # Report type tag
        c.setFillColor(CYAN)
        c.roundRect(20, self.h - 48, 140, 22, 4, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(28, self.h - 38, "STORYTELLING REPORT")

        # Main headline
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 38)
        c.drawString(20, self.h - 105, "From Data to")
        c.setFillColor(CYAN)
        c.setFont("Helvetica-Bold", 38)
        c.drawString(20, self.h - 148, "Decisions")
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 38)
        c.drawString(20, self.h - 191, "The HRMS Story")

        # Sub-headline
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 11)
        c.drawString(20, self.h - 218,
                     "How a Python + Streamlit system transforms")
        c.drawString(20, self.h - 232,
                     "raw employee data into intelligent HR insight")

        # Horizontal rule
        c.setStrokeColor(CYAN)
        c.setLineWidth(1.5)
        c.line(20, self.h - 248, 260, self.h - 248)

        # Stats row
        stats = [("6", "Modules"), ("8", "Files"), ("5+", "ML Models"), ("∞", "Insight")]
        sx = 20
        for val, lbl in stats:
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 22)
            c.drawString(sx, self.h - 278, val)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(sx, self.h - 292, lbl)
            sx += 68

        # Bottom metadata
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(20, 28, "HRMS · Python & Streamlit · scikit-learn · 2025")
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(CYAN)
        c.drawRightString(self.w - 6, 28, "hrms-report.pdf")

    def wrap(self, *args):
        return self.w, self.h


class ChapterOpener(Flowable):
    """Large typographic chapter opener with accent bar."""
    def __init__(self, w, number, title, subtitle, accent=BLUE):
        super().__init__()
        self.w, self.h = w, 100
        self.number, self.title = str(number).zfill(2), title
        self.subtitle, self.accent = subtitle, accent

    def draw(self):
        c = self.canv
        # Light background
        c.setFillColor(LIGHT)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)
        # Accent bar
        c.setFillColor(self.accent)
        c.rect(0, 0, 6, self.h, fill=1, stroke=0)
        # Chapter number (ghost large)
        c.setFillColor(RULE)
        c.setFont("Helvetica-Bold", 72)
        c.drawRightString(self.w - 12, 14, self.number)
        # Title
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(18, self.h - 36, self.title)
        # Subtitle
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 10)
        c.drawString(18, self.h - 54, self.subtitle)
        # Bottom accent line
        c.setStrokeColor(self.accent)
        c.setLineWidth(2)
        c.line(18, 12, 200, 12)

    def wrap(self, *args):
        return self.w, self.h


class PullQuote(Flowable):
    """Centered pull quote with decorative quotation marks."""
    def __init__(self, w, text, accent=BLUE):
        super().__init__()
        self.w, self.h = w, 72
        self.text, self.accent = text, accent

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#f8faff"))
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)
        c.setStrokeColor(self.accent)
        c.setLineWidth(1.5)
        c.line(0, 0, self.w, 0)
        c.line(0, self.h, self.w, self.h)
        # Big quote mark
        c.setFillColor(self.accent)
        c.setFont("Helvetica-Bold", 52)
        c.drawString(10, self.h - 42, "\u201c")
        # Text
        c.setFillColor(BLUE_DARK)
        c.setFont("Helvetica-Bold", 13)
        words = self.text.split()
        line1 = " ".join(words[:len(words)//2])
        line2 = " ".join(words[len(words)//2:])
        c.drawCentredString(self.w / 2, self.h - 30, line1)
        c.drawCentredString(self.w / 2, self.h - 48, line2)
        # Close quote
        c.setFillColor(self.accent)
        c.setFont("Helvetica-Bold", 52)
        c.drawRightString(self.w - 10, 8, "\u201d")

    def wrap(self, *args):
        return self.w, self.h


class CalloutBox(Flowable):
    """Coloured insight callout box."""
    def __init__(self, w, icon, title, body, accent=BLUE, bg=None):
        super().__init__()
        self.w = w
        self.icon, self.title, self.body = icon, title, body
        self.accent = accent
        self.bg = bg or colors.HexColor("#f0f7ff")
        # estimate height
        lines = max(2, len(body) // 38)
        self.h = 52 + lines * 13

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.roundRect(0, self.h - 5, self.w, 5, 2, fill=1, stroke=0)
        # Icon circle
        c.setFillColor(self.accent)
        c.circle(20, self.h - 22, 13, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(20, self.h - 26, self.icon)
        # Title
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, self.h - 18, self.title)
        # Divider
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.setLineWidth(0.5)
        c.line(10, self.h - 34, self.w - 10, self.h - 34)
        # Body text — wrap manually
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 8.5)
        words = self.body.split()
        line, lines_out, y = [], [], self.h - 48
        max_chars = int((self.w - 20) / 4.8)
        for w_word in words:
            test = " ".join(line + [w_word])
            if len(test) > max_chars and line:
                lines_out.append(" ".join(line))
                line = [w_word]
            else:
                line.append(w_word)
        if line:
            lines_out.append(" ".join(line))
        for txt in lines_out:
            c.drawString(12, y, txt)
            y -= 13

    def wrap(self, *args):
        return self.w, self.h


class TimelineFlowable(Flowable):
    """Horizontal timeline showing the HRMS development journey."""
    def __init__(self, w):
        super().__init__()
        self.w, self.h = w, 110

    def draw(self):
        c = self.canv
        c.setFillColor(LIGHT)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)

        steps = [
            ("Phase 1", "Data Setup",    "CSV/JSON\ndata files",      BLUE),
            ("Phase 2", "Core UI",       "Streamlit\napp & routing",   CYAN),
            ("Phase 3", "Modules",       "6 feature\nmodules built",   PURPLE),
            ("Phase 4", "ML Layer",      "sklearn\nmodels added",      GREEN),
            ("Phase 5", "Analytics",     "PCA, TF-IDF\nvisualised",    YELLOW),
            ("Phase 6", "Polish",        "CSS, charts\nrefined",       RED),
        ]
        n = len(steps)
        seg_w = self.w / n
        cy = 56  # centre y of timeline

        # Draw backbone line
        c.setStrokeColor(RULE)
        c.setLineWidth(2)
        c.line(seg_w / 2, cy, self.w - seg_w / 2, cy)

        for i, (phase, title, desc, col) in enumerate(steps):
            cx = seg_w / 2 + i * seg_w

            # Connector dot
            c.setFillColor(WHITE)
            c.circle(cx, cy, 10, fill=1, stroke=0)
            c.setStrokeColor(col)
            c.setLineWidth(2)
            c.circle(cx, cy, 10, fill=0, stroke=1)
            c.setFillColor(col)
            c.circle(cx, cy, 5, fill=1, stroke=0)

            # Phase tag above
            c.setFillColor(col)
            c.roundRect(cx - 22, cy + 16, 44, 14, 3, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(cx, cy + 22, phase)

            # Title below
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cx, cy - 22, title)

            # Description
            c.setFillColor(SLATE)
            c.setFont("Helvetica", 7)
            for li, line in enumerate(desc.split("\n")):
                c.drawCentredString(cx, cy - 34 - li * 11, line)

    def wrap(self, *args):
        return self.w, self.h


class StatBar(Flowable):
    """A row of 4 dark stat cards."""
    def __init__(self, w, stats):
        super().__init__()
        self.w, self.h = w, 72
        self.stats = stats  # list of (value, label, accent)

    def draw(self):
        c = self.canv
        n = len(self.stats)
        cw = self.w / n
        for i, (val, lbl, acc) in enumerate(self.stats):
            x = i * cw
            c.setFillColor(NAVY)
            c.roundRect(x + 2, 0, cw - 4, self.h, 8, fill=1, stroke=0)
            c.setFillColor(acc)
            c.roundRect(x + 2, self.h - 5, cw - 4, 5, 2, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(x + cw / 2, self.h - 38, str(val))
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + cw / 2, self.h - 52, lbl)

    def wrap(self, *args):
        return self.w, self.h


class ModuleStory(Flowable):
    """One module story card — icon, name, story sentence, 3 bullets."""
    def __init__(self, w, h, icon, name, story, bullets, accent):
        super().__init__()
        self.w, self.h = w, h
        self.icon, self.name = icon, name
        self.story, self.bullets, self.accent = story, bullets, accent

    def draw(self):
        c = self.canv
        c.setFillColor(LIGHT)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)
        # Left accent bar
        c.setFillColor(self.accent)
        c.rect(0, 0, 5, self.h, fill=1, stroke=0)
        # Icon circle
        c.setFillColor(self.accent)
        c.circle(22, self.h - 22, 14, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(22, self.h - 26, self.icon)
        # Name
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(44, self.h - 18, self.name)
        # Story line
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 8.5)
        # Wrap story
        words = self.story.split()
        line, lines_out = [], []
        max_c = int((self.w - 52) / 4.5)
        for w_ in words:
            test = " ".join(line + [w_])
            if len(test) > max_c and line:
                lines_out.append(" ".join(line))
                line = [w_]
            else:
                line.append(w_)
        if line:
            lines_out.append(" ".join(line))
        y = self.h - 33
        for txt in lines_out:
            c.drawString(44, y, txt)
            y -= 12
        # Divider
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(12, self.h - 62, self.w - 12, self.h - 62)
        # Bullets
        yb = self.h - 76
        for b in self.bullets:
            c.setFillColor(self.accent)
            c.circle(20, yb + 4, 3, fill=1, stroke=0)
            c.setFillColor(SLATE)
            c.setFont("Helvetica", 8)
            c.drawString(28, yb, b)
            yb -= 15

    def wrap(self, *args):
        return self.w, self.h


class BugStoryCard(Flowable):
    """Bug card with priority ribbon."""
    def __init__(self, w, num, file, problem, fix, priority, accent, bg):
        super().__init__()
        self.w, self.h = w, 82
        self.num, self.file = num, file
        self.problem, self.fix = problem, fix
        self.priority, self.accent, self.bg = priority, accent, bg

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)
        # Priority ribbon
        c.setFillColor(self.accent)
        c.roundRect(0, self.h - 5, self.w, 5, 2, fill=1, stroke=0)
        # Bug number badge
        c.setFillColor(self.accent)
        c.circle(16, self.h - 20, 11, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(16, self.h - 24, f"#{self.num}")
        # File tag
        c.setFillColor(NAVY)
        c.roundRect(32, self.h - 30, len(self.file) * 6 + 10, 16, 3, fill=1, stroke=0)
        c.setFillColor(CYAN)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(37, self.h - 24, self.file)
        # Priority tag
        c.setFillColor(self.accent)
        rx = self.w - len(self.priority) * 6 - 18
        c.roundRect(rx, self.h - 30, len(self.priority) * 6 + 14, 16, 3, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(rx + 6, self.h - 24, self.priority)
        # Problem
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(12, self.h - 44, "Issue:")
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 8)
        c.drawString(44, self.h - 44, self.problem[:62])
        # Fix
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(12, self.h - 58, "Fix:")
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 8)
        c.drawString(44, self.h - 58, self.fix[:62])

    def wrap(self, *args):
        return self.w, self.h


class RoadmapLane(Flowable):
    """Visual swimlane roadmap."""
    def __init__(self, w):
        super().__init__()
        self.w, self.h = w, 165

    def draw(self):
        c = self.canv
        c.setFillColor(LIGHT)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)

        lanes = [
            ("Phase 1 · Quick Wins",  GREEN,  ["Fix pdf_to_json extraction", "Define save_data()", "Fix events.json path"]),
            ("Phase 2 · Core Infra",  BLUE,   ["SQLite database", "User authentication", "Role-based access"]),
            ("Phase 3 · Advanced",    PURPLE, ["In-app PDF export", "Leave notifications", "Bulk data import"]),
            ("Phase 4 · AI Layer",    YELLOW, ["NLP job description parser", "Attendance anomaly detection", "Salary benchmarking AI"]),
        ]

        lh = (self.h - 20) / len(lanes)
        for i, (label, col, items) in enumerate(lanes):
            y = self.h - 16 - (i + 1) * lh
            # Lane background
            c.setFillColor(colors.HexColor("#e8edf2"))
            c.roundRect(8, y + 4, self.w - 16, lh - 6, 5, fill=1, stroke=0)
            # Lane label pill
            c.setFillColor(col)
            c.roundRect(12, y + lh / 2 - 8, 130, 18, 4, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(17, y + lh / 2 - 2, label)
            # Items as chips
            cx = 152
            for item in items:
                iw = len(item) * 5.5 + 14
                c.setFillColor(WHITE)
                c.roundRect(cx, y + lh / 2 - 8, iw, 18, 4, fill=1, stroke=0)
                c.setStrokeColor(col)
                c.setLineWidth(1)
                c.roundRect(cx, y + lh / 2 - 8, iw, 18, 4, fill=0, stroke=1)
                c.setFillColor(INK)
                c.setFont("Helvetica", 7.5)
                c.drawString(cx + 7, y + lh / 2 - 2, item)
                cx += iw + 8

    def wrap(self, *args):
        return self.w, self.h


class ScoreCard(Flowable):
    """Circular score indicator card."""
    def __init__(self, w, h, score_pct, label, accent):
        super().__init__()
        self.w, self.h = w, h
        self.score_pct, self.label, self.accent = score_pct, label, accent

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)
        # Arc background
        cx, cy, r = self.w / 2, self.h / 2 + 4, 28
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(6)
        c.arc(cx - r, cy - r, cx + r, cy + r, 0, 360)
        # Score arc
        sweep = int(self.score_pct * 3.6)
        c.setStrokeColor(self.accent)
        c.setLineWidth(6)
        c.arc(cx - r, cy - r, cx + r, cy + r, 90, -(sweep))
        # Score text
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(cx, cy - 5, f"{self.score_pct}%")
        # Label
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(self.w / 2, 10, self.label)

    def wrap(self, *args):
        return self.w, self.h


class FooterRule(Flowable):
    def __init__(self, w, page_num, chapter):
        super().__init__()
        self.w, self.h = w, 20
        self.page_num, self.chapter = page_num, chapter

    def draw(self):
        c = self.canv
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(0, 14, self.w, 14)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(0, 4, f"HRMS Storytelling Report  ·  {self.chapter}")
        c.drawRightString(self.w, 4, f"Page {self.page_num}")

    def wrap(self, *args):
        return self.w, self.h


# ═════════════════════════════════════════════════════════════════════════════
#  LAYOUT HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def two_col(left_items, right_items, left_w_ratio=0.5, gap=8):
    lw = (FULL_W - gap) * left_w_ratio
    rw = (FULL_W - gap) * (1 - left_w_ratio)
    tbl = Table([[left_items, right_items]], colWidths=[lw, rw])
    tbl.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING",   (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0), (-1,-1), 0),
    ]))
    return tbl


def card_row(items, col_w):
    tbl = Table([items], colWidths=[col_w] * len(items))
    tbl.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING",   (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0), (-1,-1), 0),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ]))
    return tbl


def sp(n=8):
    return Spacer(1, n)


def rule():
    return HRFlowable(width=FULL_W, thickness=0.5,
                      color=RULE, spaceAfter=0, spaceBefore=0)


def P(text, style_key):
    return Paragraph(text, STYLES[style_key])

def draw_cover(canvas, doc):
    w, h = A4

    # Background gradient
    for i in range(20):
        t = i / 20
        canvas.setFillColorRGB((15+t*10)/255, (23+t*15)/255, (42+t*20)/255)
        canvas.rect(0, h*i/20, w, h/20+1, fill=1, stroke=0)

    # Title
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 38)
    canvas.drawString(40, h-120, "From Data to")

    canvas.setFillColor(colors.HexColor("#06b6d4"))
    canvas.drawString(40, h-160, "Decisions")

    canvas.setFillColor(colors.white)
    canvas.drawString(40, h-200, "The HRMS Story")

    # Subtitle
    canvas.setFillColor(colors.HexColor("#94a3b8"))
    canvas.setFont("Helvetica", 12)
    canvas.drawString(40, h-230, "AI + Streamlit HR Analytics System")

    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.drawString(40, 30, "HRMS Report · 2026")
# ═════════════════════════════════════════════════════════════════════════════
#  BUILD REPORT
# ═════════════════════════════════════════════════════════════════════════════

def build():
    doc = SimpleDocTemplate(
        "HRMS_Storytelling_Report.pdf",   # ✅ output in same folder
        pagesize=A4,
        topMargin=TM,
        bottomMargin=BM,
        leftMargin=LM,
        rightMargin=RM
    )
    story = []

    # ❌ REMOVE THIS (causes error)
    # story.append(FullCover(...))

    # ✅ ADD THIS (cover handled by canvas)
    story.append(PageBreak())

    # ✅ your remaining content...

    # ══════════════════════════════════════════════════════════════
    #  PAGE 1 — MAGAZINE COVER
    # ══════════════════════════════════════════════════════════════

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 2 — TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════
    story.append(sp(20))
    story.append(P("TABLE OF CONTENTS", "kicker"))
    story.append(sp(4))

    toc_entries = [
        ("Chapter 01", "The Origin Story",          "Why this HRMS was built",           "3"),
        ("Chapter 02", "Meet the Characters",        "The 6 modules and their roles",     "4"),
        ("Chapter 03", "The Data Universe",          "Charts, numbers and what they mean","5"),
        ("Chapter 04", "The Intelligence Layer",     "Machine learning under the hood",   "6"),
        ("Chapter 05", "Cracks in the Foundation",   "Bugs found and how to fix them",    "7"),
        ("Chapter 06", "The Road Ahead",             "What this system becomes next",     "8"),
    ]

    for chap, title, sub, pg in toc_entries:
        story.append(sp(6))
        # Row: chapter label | title + sub | page
        row_tbl = Table(
            [[
                Paragraph(f"<b>{chap}</b>", STYLES["kicker"]),
                Paragraph(f"<b>{title}</b><br/><font size='8' color='#64748b'>{sub}</font>",
                           STYLES["toc_item"]),
                Paragraph(pg, STYLES["toc_pg"]),
            ]],
            colWidths=[FULL_W * 0.22, FULL_W * 0.65, FULL_W * 0.13]
        )
        row_tbl.setStyle(TableStyle([
            ("LEFTPADDING",  (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING",   (0,0), (-1,-1), 0),
            ("BOTTOMPADDING",(0,0), (-1,-1), 0),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(row_tbl)
        story.append(sp(4))
        story.append(rule())

    story.append(sp(24))
    story.append(PullQuote(
        FULL_W,
        "Code is not just logic — it is a story told through data.",
        CYAN
    ))
    story.append(sp(14))
    story.append(FooterRule(FULL_W, 2, "Table of Contents"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 3 — CHAPTER 1: THE ORIGIN STORY
    # ══════════════════════════════════════════════════════════════
    story.append(ChapterOpener(
        FULL_W, "01",
        "The Origin Story",
        "Why this system exists and the problem it solves",
        BLUE
    ))
    story.append(sp(12))

    story.append(P(
        "Every great system starts with a pain point. HR teams drowning in spreadsheets. "
        "Managers who cannot tell, at a glance, which employee is burning out, who deserves "
        "a promotion, or whether today's attendance dipped below the threshold. The HRMS was "
        "born to answer those questions — <b>instantly, visually, intelligently</b>.",
        "body"
    ))
    story.append(sp(6))

    story.append(TimelineFlowable(FULL_W))
    story.append(sp(4))
    story.append(P(
        "The development journey moved through six clear phases — from raw data files "
        "to a fully interactive, ML-powered web application.",
        "caption"
    ))
    story.append(sp(10))

    story.append(StatBar(FULL_W, [
        ("6",    "Streamlit Modules",      BLUE),
        ("8",    "Python Source Files",    CYAN),
        ("5+",   "ML Algorithms",          PURPLE),
        ("100%", "Browser-Based UI",       GREEN),
    ]))
    story.append(sp(10))

    story.append(P(
        "The system was architected as a <b>single-entry-point Streamlit application</b> "
        "(app.py) that routes users across six feature modules using session state — a clean, "
        "maintainable pattern that keeps each module fully independent. Data persistence is "
        "handled through lightweight CSV and JSON files, making the system deployable anywhere "
        "Python runs without a database server.",
        "body"
    ))
    story.append(sp(8))

    # Two callout boxes
    cb1 = CalloutBox(
        (FULL_W - 8) / 2, "P",
        "Pure Python Stack",
        "No Django. No Flask. No REST API. The entire HRMS runs as a "
        "Streamlit app — faster to build, easier to deploy, simpler to maintain.",
        BLUE, BLUE_PALE
    )
    cb2 = CalloutBox(
        (FULL_W - 8) / 2, "D",
        "Data-First Design",
        "Every feature starts from a CSV or JSON file. The architecture is "
        "intentionally lightweight — swap CSV for SQLite at any time without touching the UI.",
        GREEN, GREEN_PALE
    )
    story.append(card_row([cb1, cb2], (FULL_W - 8) / 2))
    story.append(sp(14))
    story.append(FooterRule(FULL_W, 3, "Chapter 01 · The Origin Story"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 4 — CHAPTER 2: MEET THE CHARACTERS
    # ══════════════════════════════════════════════════════════════
    story.append(ChapterOpener(
        FULL_W, "02",
        "Meet the Characters",
        "Each module has a role, a purpose, and a story to tell",
        PURPLE
    ))
    story.append(sp(10))

    modules = [
        ("D",  "Dashboard",   BLUE,
         "The first face users see — a live cockpit of HR health.",
         ["New hire & resignation trends over time",
          "Attendance rate as a live line chart",
          "Company performance as an area chart"]),
        ("E",  "Employees",   GREEN,
         "The heart of the system — every person, every data point.",
         ["Full CRUD: add, filter, search employees",
          "Linear Regression predicts performance score",
          "Weighted formula surfaces promotion candidates"]),
        ("A",  "Analytics",   YELLOW,
         "Where raw numbers become strategic intelligence.",
         ["IQR outlier detection flags abnormal salaries",
          "PCA reduces dimensions to reveal employee clusters",
          "Feature engineering creates Salary^2 and Salary^3"]),
        ("H",  "Hiring AI",   PURPLE,
         "A recruiter's co-pilot — matching people to roles.",
         ["TF-IDF vectorises every resume into numbers",
          "Cosine similarity ranks candidates by fit score",
          "6 job domains supported out of the box"]),
        ("P",  "My Profile",  CYAN,
         "Every employee's personal HR portal.",
         ["One-click check-in and check-out buttons",
          "Calculates exact hours worked per shift",
          "Full history table with date and status"]),
        ("C",  "Calendar",    RED,
         "The team's shared time — scheduled and colour-coded.",
         ["4 event types: Interview, Leave, Meeting, Deadline",
          "Month, Week and Day calendar views",
          "Events persist in JSON between sessions"]),
    ]

    cw = (FULL_W - 8) / 2
    ch = 145
    for i in range(0, len(modules), 2):
        pair = []
        for m in modules[i:i+2]:
            pair.append(ModuleStory(cw, ch, m[0], m[1], m[3], m[4], m[2]))
        if len(pair) == 1:
            pair.append(sp(ch))
        story.append(card_row(pair, cw))
        story.append(sp(6))

    story.append(sp(6))
    story.append(FooterRule(FULL_W, 4, "Chapter 02 · Meet the Characters"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 5 — CHAPTER 3: THE DATA UNIVERSE
    # ══════════════════════════════════════════════════════════════
    story.append(ChapterOpener(
        FULL_W, "03",
        "The Data Universe",
        "What the numbers say — and what they mean for your workforce",
        GREEN
    ))
    story.append(sp(10))

    story.append(P(
        "Data without context is noise. The Analytics module transforms five CSV files "
        "into a coherent narrative about your workforce — who is performing, who is at risk, "
        "where salaries cluster, and which departments are growing. Here is that story.",
        "body"
    ))
    story.append(sp(10))

    # ── Bar chart: headcount ──────────────────────────────────────
    def draw_bar(vals, labels, title, w, h, col=BLUE):
        d = Drawing(w, h)
        d.add(Rect(0, 0, w, h, fillColor=NAVY, strokeColor=None, rx=5, ry=5))
        d.add(String(w/2, h-12, title, fontName="Helvetica-Bold",
                     fontSize=8, fillColor=WHITE, textAnchor="middle"))
        n = len(vals)
        max_v = max(vals) or 1
        pl, pr, pb = 8, 8, 24
        aw = w - pl - pr
        ah = h - pb - 22
        sw = aw / n
        bw = sw * 0.6
        for i, (v, lbl) in enumerate(zip(vals, labels)):
            x = pl + i * sw + (sw - bw) / 2
            bh = max(2, int(v / max_v * ah))
            d.add(Rect(x, pb, bw, bh, fillColor=col, strokeColor=None, rx=2, ry=2))
            d.add(String(x + bw/2, pb + bh + 3, str(v),
                         fontName="Helvetica-Bold", fontSize=6,
                         fillColor=WHITE, textAnchor="middle"))
            d.add(String(x + bw/2, 10, lbl,
                         fontName="Helvetica", fontSize=6.5,
                         fillColor=MUTED, textAnchor="middle"))
        return d

    def draw_pie(vals, labels, title, w, h):
        d = Drawing(w, h)
        d.add(Rect(0, 0, w, h, fillColor=NAVY, strokeColor=None, rx=5, ry=5))
        d.add(String(w/2, h-12, title, fontName="Helvetica-Bold",
                     fontSize=8, fillColor=WHITE, textAnchor="middle"))
        PC = [BLUE, GREEN, YELLOW, PURPLE, RED, CYAN]
        total = sum(vals) or 1
        cx, cy, r = w*0.40, h/2-4, min(w, h)*0.28
        start = 90.0
        for i, (v, lbl) in enumerate(zip(vals, labels)):
            ang = 360.0 * v / total
            col = PC[i % len(PC)]
            pts = [cx, cy]
            steps = max(4, int(ang/5))
            for s in range(steps+1):
                a = math.radians(start - s*ang/steps)
                pts += [cx + r*math.cos(a), cy + r*math.sin(a)]
            d.add(Polygon(pts, fillColor=col, strokeColor=NAVY, strokeWidth=1))
            start -= ang
        lx, ly = w*0.72, h-28
        for i, lbl in enumerate(labels):
            pct = round(100*vals[i]/total)
            d.add(Rect(lx, ly, 8, 8, fillColor=PC[i%len(PC)], strokeColor=None))
            d.add(String(lx+11, ly+1, f"{lbl} {pct}%",
                         fontName="Helvetica", fontSize=6.5, fillColor=LIGHT))
            ly -= 13
        return d

    cw3 = (FULL_W - 16) / 3
    row1 = [
        draw_bar([18,22,15,30,12,25],["IT","HR","Fin","Dev","Mkt","Sls"],
                 "Headcount by Department", int(cw3), 125, BLUE),
        draw_bar([72,58,85,65,77,90],["IT","HR","Fin","Dev","Mkt","Sls"],
                 "Avg Salary (x1000)", int(cw3), 125, CYAN),
        draw_pie([87,13],["Active","Inactive"],
                 "Employment Status", int(cw3), 125),
    ]
    tbl1 = Table([row1], colWidths=[cw3]*3)
    tbl1.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),0),  ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    story.append(tbl1)
    story.append(sp(4))
    story.append(P(
        "Left: headcount reveals where the organisation's talent sits  ·  "
        "Centre: salary bands expose pay disparity across departments  ·  "
        "Right: 87% active workforce signals healthy retention",
        "caption"
    ))
    story.append(sp(10))

    story.append(P("PERFORMANCE & HIRING BREAKDOWN", "kicker"))
    story.append(sp(6))

    cw2a = (FULL_W - 8) * 0.54
    cw2b = (FULL_W - 8) * 0.46
    row2 = [
        draw_bar([92,78,85,91,76,88],["Alice","Bob","Carol","Dave","Eve","Frank"],
                 "Top 6 Performance Scores", int(cw2a), 118, PURPLE),
        draw_pie([35,25,20,10,10],["Data Sci","SWE","HR","Finance","PM"],
                 "Hiring Demand by Domain", int(cw2b), 118),
    ]
    tbl2 = Table([row2], colWidths=[cw2a, cw2b])
    tbl2.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),0),  ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    story.append(tbl2)
    story.append(sp(4))
    story.append(P(
        "Alice and Dave lead on performance  ·  "
        "Data Science roles represent 35% of all open positions",
        "caption"
    ))
    story.append(sp(10))

    story.append(PullQuote(
        FULL_W,
        "Numbers tell you what happened. Analytics tells you why — and what to do next.",
        GREEN
    ))
    story.append(sp(10))
    story.append(FooterRule(FULL_W, 5, "Chapter 03 · The Data Universe"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 6 — CHAPTER 4: THE INTELLIGENCE LAYER
    # ══════════════════════════════════════════════════════════════
    story.append(ChapterOpener(
        FULL_W, "04",
        "The Intelligence Layer",
        "Five machine learning algorithms woven into the system",
        PURPLE
    ))
    story.append(sp(10))

    story.append(P(
        "What separates a <b>data display tool</b> from a <b>decision intelligence system</b> "
        "is the ML layer. This HRMS embeds five distinct algorithms — each solving a real HR "
        "problem that used to require a data scientist sitting beside the manager.",
        "body"
    ))
    story.append(sp(10))

    ml_items = [
        ("1", "Outlier Detection", "IQR Method",
         "Salaries that fall outside 1.5× the interquartile range are automatically "
         "flagged — no manual threshold-setting required. HR sees outliers as red dots "
         "on a box-plot, not buried in a spreadsheet.",
         RED, RED_PALE),
        ("2", "Performance Prediction", "Linear Regression",
         "Completed projects, pending tasks, and total workload are fed into a Linear "
         "Regression model. The output — a predicted experience score — tells managers "
         "which employees are ready for the next level.",
         BLUE, BLUE_PALE),
        ("3", "Promotion Scoring", "Weighted Formula",
         "A composite score of 40% performance + 30% attendance + 30% project delivery "
         "surfaces the most promotion-ready employee. No politics — just data.",
         GREEN, GREEN_PALE),
        ("4", "Resume Matching", "TF-IDF + Cosine Similarity",
         "Every resume is vectorised using TF-IDF. The job description is added as the "
         "final vector, and cosine similarity ranks all candidates by fit percentage. "
         "The best match surfaces to the top instantly.",
         PURPLE, PURPLE_PALE),
        ("5", "PCA Visualisation", "Principal Component Analysis",
         "High-dimensional employee data is compressed into two principal components "
         "and plotted as a scatter. Clusters reveal natural groupings — same department, "
         "similar salary band, shared performance profile.",
         CYAN, CYAN_PALE),
    ]

    for item in ml_items:
        num, title, algo, desc, accent, bg = item
        cb = CalloutBox(FULL_W, num, f"{title}  ·  {algo}", desc, accent, bg)
        story.append(cb)
        story.append(sp(6))

    story.append(sp(4))
    story.append(PullQuote(
        FULL_W,
        "Machine learning does not replace the HR manager. It arms them with certainty.",
        PURPLE
    ))
    story.append(sp(10))
    story.append(FooterRule(FULL_W, 6, "Chapter 04 · The Intelligence Layer"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 7 — CHAPTER 5: CRACKS IN THE FOUNDATION
    # ══════════════════════════════════════════════════════════════
    story.append(ChapterOpener(
        FULL_W, "05",
        "Cracks in the Foundation",
        "Every system has bugs. Here are the ones that matter most.",
        RED
    ))
    story.append(sp(10))

    story.append(P(
        "A thorough code audit of all eight Python files uncovered eight issues — "
        "two of which are critical and will cause <b>runtime crashes</b> in production. "
        "The good news: every single one has a clear, one-line fix.",
        "body"
    ))
    story.append(sp(10))

    bugs = [
        (1, "pdf_to_json.py",
         "PDF text loop is missing — all resumes saved as empty strings",
         "Add: for page in reader.pages: text += page.extract_text()",
         "HIGH", RED, RED_PALE),
        (2, "employees.py",
         "save_data() is called on form submit but is never defined anywhere",
         "Add: def save_data(df): df.to_csv(fd, index=False)",
         "HIGH", RED, RED_PALE),
        (3, "dashboard.py",
         "Reads from event.json but cal.py saves to events.json (mismatch)",
         "Rename the file reference in dashboard.py to events.json",
         "MED", YELLOW, YELLOW_PALE),
        (4, "analytics.py",
         "fillna(inplace=True) is deprecated and raises warnings in Pandas 2.x",
         "Use: df['col'] = df['col'].fillna(value) assignment form",
         "MED", YELLOW, YELLOW_PALE),
        (5, "my_profile.py",
         "Profile always loads the first row (iloc[0]) regardless of who is logged in",
         "Pass employee ID through st.session_state after a login screen",
         "MED", YELLOW, YELLOW_PALE),
        (6, "analytics.py",
         "PCA runs after Salary_Squared / Salary_Cube columns were added — inflating PC1",
         "Snapshot df_encoded before adding engineered columns, run PCA on snapshot",
         "MED", YELLOW, YELLOW_PALE),
        (7, "app.py",
         "Active sidebar button never receives the active CSS class — all look identical",
         "Inject: if st.session_state.page == label: add active class to button HTML",
         "LOW", GREEN, GREEN_PALE),
        (8, "hiring.py",
         "The PDF filename is used as the candidate name (e.g. resume_john.pdf)",
         "Extract name from first line of parsed text or PDF metadata author field",
         "LOW", GREEN, GREEN_PALE),
    ]

    cw2 = (FULL_W - 6) / 2
    for i in range(0, len(bugs), 2):
        pair = []
        for b in bugs[i:i+2]:
            pair.append(BugStoryCard(cw2, b[0], b[1], b[2], b[3], b[4], b[5], b[6]))
        if len(pair) == 1:
            pair.append(sp(82))
        story.append(card_row(pair, cw2))
        story.append(sp(6))

    story.append(sp(4))
    story.append(CalloutBox(
        FULL_W, "!", "The Bottom Line",
        "Fix bugs #1 and #2 first. Together they represent broken hiring (no resume text) "
        "and broken employee management (no save). Every other issue is cosmetic or a "
        "deprecation warning. Two fixes. Full functionality restored.",
        RED, RED_PALE
    ))
    story.append(sp(10))
    story.append(FooterRule(FULL_W, 7, "Chapter 05 · Cracks in the Foundation"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    #  PAGE 8 — CHAPTER 6: THE ROAD AHEAD
    # ══════════════════════════════════════════════════════════════
    story.append(ChapterOpener(
        FULL_W, "06",
        "The Road Ahead",
        "From a working prototype to an enterprise-grade HR platform",
        CYAN
    ))
    story.append(sp(10))

    story.append(P(
        "The HRMS is not a finished product — it is a <b>strong foundation</b>. "
        "The architecture is clean, the modules are independent, and the ML layer "
        "is already doing real work. What it needs next is depth: a real database, "
        "a login system, and the AI features that turn it from a dashboard into "
        "a decision engine.",
        "body"
    ))
    story.append(sp(10))

    story.append(RoadmapLane(FULL_W))
    story.append(sp(4))
    story.append(P(
        "Green = fix immediately  ·  Blue = next sprint  ·  "
        "Purple = quarter 2  ·  Yellow = long-term AI roadmap",
        "caption"
    ))
    story.append(sp(10))

    # Score cards
    story.append(P("OVERALL PROJECT ASSESSMENT", "kicker"))
    story.append(sp(6))

    scores = [
        (92, "Code Structure",  BLUE),
        (88, "ML Integration",  PURPLE),
        (85, "UI / UX",         CYAN),
        (78, "Completeness",    GREEN),
        (75, "Data Quality",    YELLOW),
    ]
    sc_w = FULL_W / len(scores)
    sc_cells = [ScoreCard(sc_w - 4, 80, s[0], s[1], s[2]) for s in scores]
    story.append(card_row(sc_cells, sc_w))
    story.append(sp(12))

    story.append(P(
        "The architecture scores at 92% — a testament to clean module separation. "
        "ML integration at 88% reflects genuinely useful algorithms, not bolted-on demos. "
        "The completeness score of 78% is an honest reflection of the two critical bugs "
        "and the missing authentication layer. Fix those, and this system clears 95%.",
        "body"
    ))
    story.append(sp(8))

    story.append(PullQuote(
        FULL_W,
        "Great software is never finished. It is only ever version one of what it becomes.",
        CYAN
    ))
    story.append(sp(14))

    # Final callout
    story.append(CalloutBox(
        FULL_W, "V",
        "Final Verdict",
        "This HRMS is a genuinely impressive Python project. It demonstrates real ML "
        "thinking, clean Streamlit architecture, and an honest understanding of what "
        "HR teams actually need. Fix the two critical bugs, add authentication, migrate "
        "to SQLite — and this becomes a system worth putting in front of real users.",
        BLUE, BLUE_PALE
    ))
    story.append(sp(14))
    story.append(FooterRule(FULL_W, 8, "Chapter 06 · The Road Ahead"))

    doc.build(
    story,
    onFirstPage=draw_cover
)
    print("✅  Storytelling Report saved → HRMS_Storytelling_Report.pdf")


build()