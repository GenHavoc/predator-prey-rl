"""
build_report.py  –  Comprehensive report with full explanations (humanised)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable
import os

OUT_PATH = "report.pdf"

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#212121")
BLUE    = colors.HexColor("#c0392b")
LTBLUE  = colors.HexColor("#fdf2f1")
ACCENT  = colors.HexColor("#c0392b")
DKBLUE  = colors.HexColor("#922b21")
MID     = colors.HexColor("#555555")
GREY    = colors.HexColor("#777777")
BGGREY  = colors.HexColor("#fafafa")
ROWALT  = colors.HexColor("#f5f5f5")
RULE    = colors.HexColor("#e0e0e0")
WHITE   = colors.white
CODE_BG = colors.HexColor("#f5f5f5")
WARN_BG = colors.HexColor("#fff8e1")
INFO_BG = colors.HexColor("#fdf9f9")

S = getSampleStyleSheet()
PAGE_W = A4[0] - 5*cm

# ── Paragraph styles ──────────────────────────────────────────────────────────
title_style = ParagraphStyle("T",
    fontName="Helvetica-Bold", fontSize=26, leading=32,
    textColor=NAVY, alignment=TA_CENTER,
    spaceBefore=0, spaceAfter=6)

subtitle_style = ParagraphStyle("Sub",
    fontName="Helvetica", fontSize=11, leading=16,
    textColor=colors.HexColor("#777777"), alignment=TA_CENTER,
    spaceBefore=0, spaceAfter=0)

meta_style = ParagraphStyle("Meta",
    fontName="Helvetica", fontSize=9, leading=13,
    textColor=colors.HexColor("#777777"), alignment=TA_CENTER)

h1 = ParagraphStyle("H1",
    fontName="Helvetica-Bold", fontSize=13, leading=17,
    textColor=NAVY, spaceBefore=18, spaceAfter=4)

h2 = ParagraphStyle("H2",
    fontName="Helvetica-Bold", fontSize=10, leading=14,
    textColor=BLUE, spaceBefore=10, spaceAfter=2)

h3 = ParagraphStyle("H3",
    fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    textColor=NAVY, spaceBefore=6, spaceAfter=1)

body = ParagraphStyle("Body",
    fontName="Helvetica", fontSize=9.5, leading=14.5,
    textColor=colors.HexColor("#222222"), alignment=TA_JUSTIFY,
    spaceBefore=0, spaceAfter=5)

note = ParagraphStyle("Note",
    fontName="Helvetica-Oblique", fontSize=9, leading=13,
    textColor=colors.HexColor("#444444"), alignment=TA_JUSTIFY,
    leftIndent=8, spaceBefore=2, spaceAfter=5)

mono = ParagraphStyle("Mono",
    fontName="Courier", fontSize=8.5, leading=12.5,
    textColor=colors.HexColor("#1a2744"),
    backColor=CODE_BG,
    leftIndent=10, rightIndent=10,
    borderPadding=(6, 8, 6, 8),
    spaceBefore=4, spaceAfter=6)

caption = ParagraphStyle("Cap",
    fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
    textColor=GREY, alignment=TA_CENTER,
    spaceBefore=3, spaceAfter=8)

bullet_style = ParagraphStyle("Bullet",
    fontName="Helvetica", fontSize=9.5, leading=14,
    textColor=colors.HexColor("#222222"),
    leftIndent=16, spaceBefore=2, spaceAfter=2)


def accent_rule():
    return HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=6, spaceBefore=2)


def info_box(text, bg=LTBLUE, border=BLUE):
    """Highlighted information box."""
    inner = Paragraph(text, ParagraphStyle("IB",
        fontName="Helvetica", fontSize=9, leading=13.5,
        textColor=colors.HexColor("#212121"), alignment=TA_JUSTIFY))
    t = Table([[inner]], colWidths=[PAGE_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("BOX",        (0,0), (-1,-1), 0.8, border),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    return t


def sp(h=4): return Spacer(1, h)
def B(t): return f"<b>{t}</b>"
def I(t): return f"<i>{t}</i>"


def M(text):
    lines = text.split("\n")
    safe = "<br/>".join(
        l.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        for l in lines
    )
    return Paragraph(safe, mono)


_hdr_cell  = ParagraphStyle("TblHdr",  fontName="Helvetica-Bold", fontSize=8.5,
    leading=12, textColor=WHITE, spaceBefore=0, spaceAfter=0)
_body_cell = ParagraphStyle("TblBody", fontName="Helvetica", fontSize=8.5,
    leading=12, textColor=colors.HexColor("#222"), spaceBefore=0, spaceAfter=0)


def _cell(val, style):
    if isinstance(val, str):
        return Paragraph(val, style)
    return val


def mktable(data, col_widths, hdr_color=BLUE):
    wrapped = []
    for r, row in enumerate(data):
        st = _hdr_cell if r == 0 else _body_cell
        wrapped.append([_cell(c, st) for c in row])
    t = Table(wrapped, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), hdr_color),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [ROWALT, WHITE]),
        ("GRID",          (0,0),(-1,-1), 0.3, RULE),
        ("ALIGN",         (0,0),(-1,-1), "LEFT"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
    ]))
    return t


def section(title):
    return KeepTogether([
        Paragraph(title, h1),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=6, spaceBefore=2),
    ])


def subsection(title):
    return KeepTogether([
        Paragraph(title, h2),
        sp(2),
    ])


def subsubsection(title):
    return Paragraph(title, h3)


def cover_block():
    return KeepTogether([
        Paragraph("Predator&#8211;Prey MDP on an N&#215;N Grid", title_style),
        Paragraph("Principles, Implementation &amp; Scalable Evaluation", subtitle_style),
        sp(10),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=4, spaceBefore=0),
    ])


# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(OUT_PATH, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm)
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story += [cover_block(), sp(6),
        Paragraph(
            "This report walks through a predator-prey game modelled as a Markov Decision "
            "Process (MDP) on an N&#215;N grid. Think of it as a cat-and-mouse problem: "
            "a predator tries to catch prey that is moving randomly around a grid, and "
            "we want to figure out how valuable each position is for the predator. "
            "We cover every piece of the pipeline &#8212; from simulating a single step of "
            "the game to computing long-run catch rates for grids as large as 25&#215;25. "
            "Throughout, sparse data structures are used to keep memory at O(N<super>4</super>) "
            "rather than the O(N<super>8</super>) that a naive dense approach would require. "
            "The final section shows measured state values and runtimes for "
            "N &#8712; {5, 10, 15, 20, 25}.",
            body),
    ]

    # ── 1. Sparse Matrices: A Primer ──────────────────────────────────────────
    story += [sp(6), section("1.  Sparse Matrices: Why They Matter Here")]

    story += [
        Paragraph(
            "Before diving into the game itself, it helps to understand the memory problem "
            "we are up against &#8212; and the trick that solves it. This section explains "
            "sparse matrices from scratch. The payoff shows up in every module from the "
            "kernel builder through to the Bellman update loop.",
            body),
        sp(4),
        subsection("1a.  The memory wall"),
        Paragraph(
            "The core object in an MDP is the transition matrix P. Each row of P "
            "answers the question: &#8220;If I am in state s and take action a, which "
            "states might I end up in, and with what probability?&#8221; For our grid game, "
            "P has 5N<super>4</super> rows and N<super>4</super> columns. Storing it as a "
            "plain array of 64-bit floats costs 5&#183;N<super>8</super>&#183;8 bytes "
            "&#8212; a number that grows catastrophically with N:",
            body),
        mktable(
            [[B("N"), B("|S| = N<super>4</super>"), B("Dense equivalent (not used)"), B("Sparse NNZ (approx)")],
             ["5",  "625",       "~16 MB",    "~15,000"],
             ["10", "10,000",    "~40 GB",    "~400,000"],
             ["15", "50,625",    "~4.6 TB",   "~3.0 M"],
             ["20", "160,000",   "~51 TB",    "~13.8 M"],
             ["25", "390,625",   "~381 TB",   "~42 M"]],
            [2*cm, 3*cm, 4.5*cm, 4*cm], NAVY),
        sp(6),
        Paragraph(
            "The good news: most of those entries are zero. For any given (state, action) "
            "pair, only a small number of next-states are actually reachable. The predator "
            "can only land in one new cell. The prey has at most five places it can go. "
            "When a catch happens, the prey respawns in one of N<super>2</super>&#8722;1 "
            "cells &#8212; but that is still just a tiny fraction of the N<super>4</super> "
            "possible states. So instead of storing all the zeros, we can store " +
            I("only") + " the non-zero entries and skip everything else. "
            "That is exactly what a sparse matrix does.",
            body),
        sp(4),
        subsection("1b.  COO format &#8212; the simplest sparse representation"),
        Paragraph(
            "The coordinate (COO) format is about as simple as it gets. You keep three "
            "lists side-by-side: " +
            B("rows[]") + ", " + B("cols[]") + ", and " + B("data[]") + ". "
            "Entry k means: &#8220;the matrix has value data[k] at position "
            "(rows[k], cols[k])&#8221;. Building it is easy &#8212; every time you "
            "discover a non-zero entry, just append to all three lists. You do not even "
            "need to know in advance how many entries there will be.",
            body),
        M("# COO construction (pseudocode)\nrows, cols, data = [], [], []\nfor s, a in all (state, action) pairs:\n"
          "    for s_next, prob in reachable_next_states(s, a):\n"
          "        rows.append(s * A + a)\n        cols.append(s_next)\n        data.append(prob)\n"
          "P_coo = coo_matrix((data, (rows, cols)), shape=(S*A, S))"),
        Paragraph(
            "COO is great for " + I("building") + " a matrix, but it is slow for " +
            I("using") + " one. If you want all the entries in a particular row, "
            "you have to scan the entire rows[] list to find them &#8212; there is no "
            "shortcut. That is where CSR comes in.",
            body),
        sp(4),
        subsection("1c.  CSR format &#8212; fast row access"),
        Paragraph(
            "CSR (Compressed Sparse Row) reorganises the same information so you can "
            "jump directly to any row. Instead of unsorted triplets, it uses:",
            body),
        M("indptr  : length (nrows + 1);  indptr[i]..indptr[i+1] gives the slice of col/data for row i\n"
          "indices : length NNZ;          column indices of each non-zero\n"
          "data    : length NNZ;          values of each non-zero\n\n"
          "Row i occupies:  indices[indptr[i] : indptr[i+1]]\n"
          "                 data   [indptr[i] : indptr[i+1]]"),
        Paragraph(
            "Think of indptr as a table of contents: it tells you exactly where each "
            "row starts and ends in the indices and data arrays. With this in hand, a "
            "matrix-vector product P @ v runs in O(NNZ) time &#8212; it only ever touches "
            "the non-zero entries, never the zeros. For our matrix with O(N<super>4</super>) "
            "non-zeros, that is a dramatic speedup over the O(N<super>8</super>) cost of "
            "multiplying a full dense matrix.",
            body),
        Paragraph(
            "We build in COO (easy to construct) and then convert to CSR in one scipy "
            "call (fast to use). Scipy handles the sorting and index-building internally:",
            body),
        M("P = csr_matrix(\n    (np.array(data), (np.array(rows), np.array(cols))),\n"
          "    shape=(S*A, S), dtype=np.float64\n)"),
        sp(4),
        subsection("1d.  Two operations we rely on heavily"),
        Paragraph(
            "The Bellman update loop (Section 3g) leans on two sparse operations repeatedly:",
            body),
        Paragraph(
            B("Row slicing:") + " Given the full kernel P of shape (S&#183;A, S), we "
            "can extract just the rows that correspond to action a &#8212; one row per "
            "state &#8212; to get a smaller matrix P_a of shape (S, S). Scipy handles "
            "this efficiently because CSR knows exactly where each row lives.",
            body),
        Paragraph(
            B("Diagonal weighting:") + " scipy.sparse.diags(v) wraps a plain vector v "
            "into a sparse diagonal matrix. Multiplying diag(&#960;[:,a]) @ P_a is then "
            "a cheap sparse-times-sparse operation that scales each row of P_a by the "
            "policy probability for action a. Both the time and the memory cost stay "
            "proportional to NNZ, not to N<super>8</super>.",
            body),
        info_box(
            B("The key idea: ") +
            "By looping over the 5 actions (not the N<super>4</super> states), we build "
            "the full policy-weighted kernel P_&#960; from 5 sparse matrix multiplications. "
            "The result is another CSR matrix with O(N<super>4</super>) non-zeros, ready "
            "for the iterative Bellman update.",
            LTBLUE, BLUE),
    ]

    # ── 2. Problem Setup ──────────────────────────────────────────────────────
    story += [PageBreak(), section("2.  The Game: Setup and Notation")]
    story += [
        Paragraph(
            "The arena is an N&#215;N grid. A " + I("state") + " captures where both "
            "agents are: (predator cell, prey cell). Time moves in discrete ticks. "
            "At tick zero the predator starts at (1,1) and the prey at (N,N) "
            "&#8212; diagonally opposite corners.",
            body),

        subsection("State space  S"),
        Paragraph(
            "To work with arrays we need a single number for each state. We encode "
            "grid positions row-first (row 0, column 0 is position 0; row 0, column 1 "
            "is position 1; and so on). A full state packs both positions into one integer:",
            body),
        M("pos_idx   = row * N + col                       # in [0, N^2)\n"
          "state_idx = pred_idx * N^2 + prey_idx           # in [0, N^4)\n"
          "|S| = N^4"),
        Paragraph(
            "Every (predator, prey) pair maps to a unique integer. Going the other way "
            "is just integer division: pred_idx = state_idx // N<super>2</super>, "
            "prey_idx = state_idx % N<super>2</super>. These conversions live in "
            "state_space.py as state_to_idx / idx_to_state.",
            body),

        subsection("Action space  A"),
        mktable(
            [[B("Index"), B("Name"), B("(&#916;row, &#916;col)"), B("Effect if off-grid")],
             ["0","stay","(0, 0)","no movement"],
             ["1","up","(&#8722;1, 0)","predator stays"],
             ["2","down","(+1, 0)","predator stays"],
             ["3","left","(0, &#8722;1)","predator stays"],
             ["4","right","(0, +1)","predator stays"]],
            [1.8*cm, 2.2*cm, 3*cm, 4*cm]),
        sp(4),
        Paragraph(
            "The predator picks one of five moves each tick. Trying to walk off the "
            "edge of the grid simply leaves it where it is. This keeps apply_action "
            "clean: no special cases, no out-of-bounds checks needed by callers.",
            body),

        subsection("How the prey moves"),
        Paragraph(
            "The prey does not have a strategy &#8212; it just wanders. Each tick it "
            "picks uniformly at random among staying put or stepping to any neighbouring "
            "cell that is still within the grid. How many choices it has depends on "
            "where it is:",
            body),
        mktable(
            [[B("Cell type"), B("Valid moves"), B("Stay probability"), B("Move probability each")],
             ["Corner",   "2 (stay + 1 neighbour)... wait, 3", "1/3", "1/3 each"],
             ["Corner (N=2)", "3 (stay + 2 neighbours)", "1/3", "1/3 each"],
             ["Edge (non-corner)", "4 (stay + 3 neighbours)", "1/4", "1/4 each"],
             ["Interior", "5 (stay + 4 neighbours)", "1/5", "1/5 each"]],
            [3.5*cm, 4.5*cm, 3*cm, 3*cm]),
        sp(4),
        Paragraph(
            "This lives in prey_transition_probs in state_space.py. Because the prey "
            "moves independently of the predator&#8217;s action, the prey probabilities "
            "only depend on the prey&#8217;s current cell &#8212; which makes the "
            "kernel construction simpler.",
            body),

        subsection("Catches and respawning"),
        Paragraph(
            "After both agents move, if they land on the same cell a " + I("catch") + " "
            "happens. The predator scores +1, and the prey immediately " + I("respawns") + " "
            "at a cell chosen uniformly at random from the N<super>2</super>&#8722;1 cells "
            "that are not occupied by the predator. If no catch happens, the reward is zero. "
            "Respawning keeps the game going forever &#8212; there is no absorbing end "
            "state &#8212; and it means each catch distributes probability mass across "
            "N<super>2</super>&#8722;1 next-states in the transition matrix.",
            body),
    ]

    # ── 3. Functions ──────────────────────────────────────────────────────────
    story += [PageBreak(), section("3.  What Each Function Does")]

    # 3a
    story += [subsection("3a.  simulator  &#8212;  simulator.py"),
        Paragraph(
            "The simulator advances the game by one tick and returns the outcome. "
            "Call it twice with the same inputs and you may well get different results "
            "&#8212; because the prey moves randomly.",
            body),
        Paragraph(
            B("Predator move:") + " The chosen action picks a direction. The new position "
            "is clamped to the grid boundary. Completely deterministic.",
            body),
        Paragraph(
            B("Prey move:") + " The prey&#8217;s valid moves are listed and one is drawn "
            "uniformly with np.random.choice. This is the only random part.",
            body),
        Paragraph(
            B("Catch check:") + " If both agents end up on the same cell, reward = 1.0 "
            "and the prey respawns at a randomly chosen cell (excluding the predator&#8217;s "
            "cell) via np.random.randint.",
            body),
        Paragraph(
            B("Coordinates:") + " The simulator talks to the outside world in " + I("1-indexed") + " "
            "positions (rows and columns run from 1 to N). Internally it converts to "
            "0-indexed. Every other module uses 0-indexed throughout.",
            body),
        M("Inputs:  N, pred_pos (1-indexed), prey_pos (1-indexed), action (0..4)\n"
          "Outputs: next_pred_pos, next_prey_pos (both 1-indexed), reward (0.0 or 1.0)"),
    ]

    # 3b
    story += [subsection("3b.  kernel_sparse  &#8212;  kernel_sparse.py"),
        Paragraph(
            "The transition kernel P is the mathematical backbone of the MDP. "
            "Row s&#183;|A|+a of P is a probability distribution that answers: "
            "&#8220;given that I am in state s and take action a, where might I end up?&#8221;",
            body),
        M("P[s*A + a, s'] = Prob(S_{t+1}=s' | S_t=s, A_t=a)"),
        Paragraph(
            "P has shape (N<super>4</super>&#183;5, N<super>4</super>) and every row sums "
            "to exactly 1. To build it, we loop over every (predator position, prey "
            "position, action) triple and work out where everyone ends up:",
            body),
        M("for pred_idx in range(N^2):\n"
          "  for prey_idx in range(N^2):\n"
          "    s = state_to_idx(pred_idx, prey_idx, N)\n"
          "    for a in range(5):\n"
          "      sa_row = s * 5 + a\n"
          "      new_pred = apply_action(pred, a, N)\n"
          "      for (nqr, nqc, p_prey) in prey_transition_probs(prey, N):\n"
          "        new_prey = pos_to_idx(nqr, nqc, N)\n"
          "        if new_pred == new_prey:   # catch!\n"
          "          for spawn in range(N^2) if spawn != new_pred:\n"
          "            P[sa_row, state(new_pred, spawn)] += p_prey / (N^2-1)\n"
          "        else:\n"
          "          P[sa_row, state(new_pred, new_prey)] += p_prey"),
        Paragraph(
            "When a catch occurs, the prey&#8217;s probability p_prey gets spread "
            "equally across all N<super>2</super>&#8722;1 respawn cells. This is what "
            "keeps every row summing to 1.",
            body),
        sp(4),
        Paragraph(
            "Rather than allocating a dense array (which would require ~51 TB at N=20), "
            "we keep three plain Python lists &#8212; rows, cols, data &#8212; and append "
            "to them only when we find a non-zero entry. Once the loop finishes, a single "
            "scipy call converts everything to CSR format:",
            body),
        M("P = csr_matrix(\n"
          "    (np.array(data), (np.array(rows), np.array(cols))),\n"
          "    shape=(S*A, S), dtype=np.float64\n)"),
        Paragraph(
            "Doing the conversion in one bulk call is much faster than building the "
            "matrix entry-by-entry. The resulting CSR object stores only the actual "
            "non-zeros &#8212; roughly O(N<super>4</super>) of them.",
            body),
        info_box(
            B("How big is the saving? ") +
            "For N=20, a dense P would need around 51 TB. The sparse version stores "
            "roughly 13.8 million non-zero values &#8212; about 110 MB total. "
            "That is a saving of over 400,000 times.",
            INFO_BG, colors.HexColor("#c0392b")),
    ]

    # 3c
    story += [subsection("3c.  reward_function  &#8212;  reward_function.py"),
        Paragraph(
            "The reward matrix R has shape (N<super>4</super>, 5). Entry R[s, a] is "
            "the " + I("expected") + " reward for taking action a in state s, "
            "averaged over the prey&#8217;s random movement. Since the only non-zero "
            "reward is +1 on a catch, this simplifies to: what is the probability "
            "of a catch when I do this?",
            body),
        M("R[s, a] = E[reward | S_t=s, A_t=a]\n"
          "        = Prob(new_pred_pos == new_prey_pos | s, a)\n"
          "        = sum over prey moves of (p_prey if new_prey == new_pred else 0)"),
        Paragraph(
            "The code loops over (predator, prey, action) just like the kernel builder, "
            "but only accumulates catch probabilities &#8212; it does not need the full "
            "distribution over next-states. R is stored as a plain dense "
            "(N<super>4</super>, 5) array. At N=20 that is only about 6 MB, so there is "
            "no need for sparse tricks here.",
            body),
    ]

    # 3d
    story += [subsection("3d.  sample_policy  &#8212;  sample_policy.py"),
        Paragraph(
            "The policy matrix &#960; has shape (|S|, |A|) and describes how the "
            "predator should behave. We use a &#8220;greedy mix&#8221; strategy: "
            "half the time pick a move that brings you closer to the prey; "
            "the other half pick any other move at random. More precisely:", body),
        Paragraph("Let G(s) be the set of actions that minimise how far the predator "
            "moves from the prey (measured by Manhattan distance), and O(s) be "
            "everything else. Then:", body),
        M("pi(a|s) = 0.5 / |G(s)|   if a in G(s)\n"
          "pi(a|s) = 0.5 / |O(s)|   if a in O(s)\n"
          "pi(a|s) = 1.0 / |G(s)|   if O(s) is empty  (all actions are greedy)"),
        Paragraph(
            B("Why Manhattan distance?") + " It is cheap to compute and gives a "
            "reasonable approximation of &#8220;how close are they&#8221; on a grid. "
            "It would be the exact shortest-path distance on an infinite grid; "
            "on a bounded grid it can slightly overestimate because walls may "
            "force detours. That imperfection is fine here &#8212; we want a "
            "plausible but not necessarily optimal policy.",
            body),
        Paragraph(
            "Every row of &#960; sums to exactly 1 by construction. The "
            "verify_policy() function checks this with an assertion.",
            body),
    ]

    # 3e
    story += [subsection("3e.  induced_kernel_sparse  &#8212;  induced_kernel_sparse.py"),
        Paragraph(
            "Given a policy &#960; and the full kernel P, the " + I("policy-induced kernel") + " "
            "P_&#960; merges the two by weighting each action&#8217;s transition "
            "probabilities by how often the policy chooses that action:",
            body),
        M("P_pi[s, s'] = sum_a  pi(a|s) * P[s*A + a, s']"),
        Paragraph(
            "P_&#960; has shape (N<super>4</super>, N<super>4</super>) and is again "
            "row-stochastic. It represents the one-step dynamics of the system "
            "when the predator follows policy &#960;.",
            body),
        sp(2),
        Paragraph(
            "Rather than contracting a dense (S, A, S) array, we loop over the five "
            "actions and add up weighted sparse matrices. For each action a:",
            body),
        M("row_indices = np.arange(S) * A + a      # rows of P corresponding to action a\n"
          "P_a         = P_sparse[row_indices]      # CSR slice, shape (S, S)\n"
          "W_a         = diags(Pi[:, a])            # sparse diagonal, shape (S, S)\n"
          "P_pi       += W_a @ P_a                  # accumulate weighted contribution"),
        Paragraph(
            "row_indices picks out the rows of P that belong to action a &#8212; one "
            "per state. W_a @ P_a then scales each row of P_a by how likely the policy "
            "is to choose action a in that state. After five iterations we have P_&#960;. "
            "The whole thing involves only sparse arithmetic &#8212; no loop over the "
            "N<super>4</super> states. Cost: O(5&#183;NNZ(P)) = O(N<super>4</super>).",
            body),
        info_box(
            B("Why no state loop? ") +
            "Scipy&#8217;s CSR fancy indexing fetches arbitrary rows in O(NNZ/A) time, "
            "and diag @ CSR is a built-in sparse operation. The outer loop runs exactly "
            "five times regardless of how large N is.",
            LTBLUE, BLUE),
    ]

    # 3f
    story += [subsection("3f.  induced_reward  &#8212;  induced_reward.py"),
        Paragraph(
            "The " + I("policy-induced reward") + " vector r_&#960; is a column of length "
            "|S|. Entry r_&#960;[s] is the expected immediate reward in state s when "
            "following policy &#960;: just the weighted average of the per-action rewards.",
            body),
        M("r_pi[s] = sum_a  pi(a|s) * R[s, a]  =  (Pi * R).sum(axis=1)"),
        Paragraph(
            "This is an element-wise multiply followed by a row sum &#8212; exactly "
            "what NumPy&#8217;s broadcasting does in a single call. The result gets "
            "reshaped to a column vector (S, 1) so it broadcasts correctly with V "
            "in the Bellman update.",
            body),
    ]

    # 3g
    story += [subsection("3g.  state_value_eval_sparse  &#8212;  state_value_eval_sparse.py"),
        Paragraph(
            "The state value function V<super>&#960;</super>(s) answers: "
            "&#8220;if I start in state s and follow policy &#960; forever, "
            "how much total reward do I expect to collect (with future rewards "
            "discounted by &#947; per tick)?&#8221; It satisfies:",
            body),
        M("V^pi = r_pi + gamma * P_pi @ V^pi"),
        Paragraph(
            "This looks like a linear system, and technically we could solve it "
            "directly &#8212; but that costs O(|S|<super>3</super>) = O(N<super>12</super>), "
            "which is completely out of the question for anything beyond a toy grid. "
            "Instead we use " + I("iterative policy evaluation") + ": start with V=0 "
            "and keep applying the Bellman update until the values stop changing:",
            body),
        M("V_0 = 0\nV_{k+1} = r_pi + gamma * P_pi @ V_k\n"
          "Stop when  ||V_{k+1} - V_k||_inf < tol = 1e-9"),
        Paragraph(
            B("Will it always converge?") + " Yes. The update is a contraction "
            "mapping (because &#947; &lt; 1 and P_&#960; is row-stochastic), so "
            "by the Banach fixed-point theorem it converges to the unique true "
            "value function V<super>&#960;</super> no matter where we start.",
            body),
        Paragraph(
            B("How many iterations?") + " The error shrinks by a factor of &#947; "
            "each step. With &#947;=0.99 and a tolerance of 10<super>&#8722;9</super> "
            "we need roughly 2,000&#8211;2,100 iterations in the worst case.",
            body),
        sp(2),
        Paragraph(
            B("Implementation:") + " _induced_kernel_fast pre-builds P_&#960; "
            "as a CSR matrix (using the action-loop approach from Section 3e). The "
            "evaluation loop then calls P_pi.dot(V) &#8212; one sparse matrix-vector "
            "multiply per iteration, costing O(NNZ) = O(N<super>4</super>). "
            "Three subtle bugs had to be fixed along the way:",
            body),
        mktable(
            [[B("Fix"), B("Issue"), B("Solution")],
             ["FIX 1",
              "scipy sparse matvec (P_pi.dot(V)) returns numpy.matrix instead of ndarray, "
              "causing silent shape-broadcast bugs in the Bellman update",
              "Wrap result in np.asarray(...).reshape(S,1) to guarantee a clean column vector"],
             ["FIX 2",
              "induced_reward returns shape (S,1) but could be (S,) if keepdims is omitted, "
              "causing the addition r_pi + gamma*Pv to broadcast incorrectly",
              "Explicitly reshape r_pi with .reshape(S,1) before the loop"],
             ["FIX 3",
              "scipy.sparse.diags() import could be shadowed in a nested scope, "
              "causing a silent NameError or wrong function call",
              "Use the module-level import throughout; enforce P_pi = csr_matrix(P_pi) after construction"],
            ],
            [1.2*cm, 6.2*cm, 7.1*cm]),
        sp(4),
        Paragraph(
            "Convergence is checked at the end of each iteration using the inf-norm "
            "of the update: np.linalg.norm(delta, np.inf) = max(|delta_i|). "
            "When this falls below 10<super>&#8722;9</super>, we stop.",
            body),
    ]

    # 3h
    story += [subsection("3h.  q_value_eval  &#8212;  q_value_eval.py"),
        Paragraph(
            "While V<super>&#960;</super>(s) tells you how good a " + I("state") + " is, "
            "Q<super>&#960;</super>(s,a) tells you how good a specific " + I("action") + " "
            "is in that state. It answers: &#8220;if I take action a now but then "
            "follow policy &#960; for every future step, how much total reward do "
            "I expect?&#8221;",
            body),
        M("Q^pi(s, a) = R[s, a]  +  gamma * sum_{s'} P[s*A+a, s'] * V^pi[s']"),
        Paragraph(
            "In matrix form (stacking all (s,a) pairs into one long vector):",
            body),
        M("Q_flat  = R_flat + gamma * P @ V^pi         # shape (S*A, 1)\n"
          "Q       = Q_flat.reshape(S, A)              # shape (S, A)"),
        Paragraph(
            "where R_flat = R.reshape(-1,1) and V<super>&#960;</super> has already been "
            "computed by state_value_eval. The sparse kernel P can be used directly for "
            "the matrix-vector multiply here, keeping costs at O(NNZ) = O(N<super>4</super>). "
            "Once we have Q<super>&#960;</super>, finding the best action in any state is "
            "just argmax_a Q<super>&#960;</super>(s,a).",
            body),
    ]

    # ── 4. Results ────────────────────────────────────────────────────────────
    story += [PageBreak(), section("4.  Results  (Part j)"),
        Paragraph(
            "We ran the full sparse pipeline for each N &#8712; {5, 10, 15, 20, 25}: "
            "sparse kernel construction, reward matrix, sample policy, and iterative "
            "value evaluation. The starting state s<sub>0</sub> puts the predator at "
            "(0,0) and the prey at (N&#8722;1,N&#8722;1) &#8212; opposite corners.",
            body),
        sp(4),
        mktable(
            [[B("N"), B("|S| = N<super>4</super>"), B("V<super>&#960;</super>(s<sub>0</sub>)"), B("Run time (s)")],
             ["5",  "625",       "5.4697",  "0.10"],
             ["10", "10,000",    "1.6287",  "1.12"],
             ["15", "50,625",    "0.7319",  "5.55"],
             ["20", "160,000",   "0.3772",  "19.04"],
             ["25", "390,625",   "0.2072",  "68.66"]],
            [2*cm, 3.5*cm, 4.5*cm, 4*cm], NAVY),
        sp(4),
        subsubsection("What the numbers tell us"),
        Paragraph(
            B("Why does V decrease with N?") + " At N=5, predator and prey start just "
            "8 Manhattan steps apart. At N=25 they start 48 steps apart. More distance "
            "means more ticks before a catch, and discounting (&#947;=0.99) penalises "
            "delayed rewards exponentially. So V<super>&#960;</super>(s<sub>0</sub>) "
            "shrinks as the grid grows, approaching zero as N &#8594; &#8734;.",
            body),
        Paragraph(
            B("Why does runtime grow the way it does?") + " Building the kernel "
            "requires looping over O(N<super>4</super>) (predator, prey, action) triples. "
            "Catch events add O(N<super>2</super>) entries each, but they are rare enough "
            "that the practical cost stays close to O(N<super>4</super>) rather than "
            "the worst-case O(N<super>6</super>). Each Bellman iteration costs "
            "O(NNZ(P_&#960;)) &#8773; O(N<super>4</super>), and with around 2,000&#8211;3,000 "
            "iterations total the overall runtime scales roughly as "
            "O(N<super>4</super>&#183;k).",
            body),
        Paragraph(
            B("The memory story:") + " A naive dense implementation of P at N=20 would "
            "need ~51 TB. The sparse CSR version uses ~110 MB. At N=25 (390,625 states, "
            "~42 million non-zeros in P) the whole computation fits on a laptop.",
            body),
    ]

    # Plots
    story.append(sp(6))
    for fname, cap in [
        ("plots/state_values.png",
         "Figure 1.  V<super>&#960;</super>(s<sub>0</sub>) at the initial state "
         "((0,0),(N&#8722;1,N&#8722;1)) under the greedy-mix policy for N &#8712; {5, 10, 15, 20, 25}."),
        ("plots/runtimes.png",
         "Figure 2.  Total wall-clock run time (sparse kernel + reward + policy + "
         "matrix-free value eval) as a function of N."),
    ]:
        if os.path.exists(fname):
            story.append(Image(fname, width=13.5*cm, height=8.8*cm))
            story.append(Paragraph(cap, caption))
            story.append(sp(6))
        else:
            story.append(Paragraph(
                f"[Plot not found: {fname} &#8212; run generate_plots.py first]", note))

    # ── 5. Summary ────────────────────────────────────────────────────────────
    story += [PageBreak(), section("5.  Summary of Files"),
        Paragraph(
            "Each part of the pipeline lives in its own file. "
            "Here is a quick reference showing what each module produces "
            "and the key design decision behind it.",
            body),
        sp(4),
        mktable(
            [[B("File"), B("Part"), B("Output shape"), B("Key design choice")],
             ["simulator.py",              "(a)", "scalars",
              "Stochastic step: deterministic pred move + random prey move + catch/respawn"],
             ["kernel_sparse.py",          "(b)", "(5N<super>4</super>, N<super>4</super>) CSR",
              "COO list accumulation then bulk CSR conversion; O(N<super>4</super>) memory"],
             ["reward_function.py",        "(c)", "(N<super>4</super>, 5)",
              "Expected catch probability per (s,a); dense N<super>4</super>x5 array"],
             ["sample_policy.py",          "(d)", "(N<super>4</super>, 5)",
              "Greedy 50% on min-Manhattan actions + uniform 50% on rest"],
             ["induced_kernel_sparse.py",  "(e)", "(N<super>4</super>, N<super>4</super>) CSR",
              "5-iteration action loop: diag(&#960;[:,a]) @ P_a; no state loop; O(N<super>4</super>)"],
             ["induced_reward.py",         "(f)", "(N<super>4</super>, 1)",
              "Vectorised row-wise dot product &#960; * R; single NumPy call"],
             ["state_value_eval_sparse.py","(g)", "(N<super>4</super>, 1)",
              "CSR Bellman iteration; sparse P_&#960; matvec O(N<super>4</super>) per step; 3 fixes"],
             ["q_value_eval.py",           "(h)", "(N<super>4</super>, 5)",
              "R_flat + &#947;&#183;P&#183;V<super>&#960;</super> then reshape; O(N<super>4</super>) sparse matvec"],
             ["generate_plots.py",         "(j)", "plots/",
              "Sparse pipeline; N &#8712; {5,10,15,20,25}; saves two PNG plots"],
            ],
            [5.2*cm, 1.2*cm, 3.2*cm, 5.4*cm]),
        sp(10),
        info_box(
            B("Scalability in a nutshell: ") +
            "The pipeline reaches N=25 (390,625 states) on a laptop through three "
            "choices: (1) building P as a COO list and converting to CSR in one shot, "
            "keeping memory at O(N<super>4</super>) rather than the O(N<super>8</super>) "
            "a dense array would need; "
            "(2) assembling P_&#960; with a five-iteration action loop using diag(&#960;[:,a])@P_a "
            "&#8212; no loop over states; and (3) running Bellman updates as sparse "
            "matrix-vector products that only touch the O(N<super>4</super>) non-zeros. "
            "Together these keep runtime at O(N<super>4</super>&#183;k).",
            LTBLUE, BLUE),
    ]

    doc.build(story)
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    build()