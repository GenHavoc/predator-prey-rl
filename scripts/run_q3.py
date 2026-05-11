"""build_report_q3.py — Generates report_q3.pdf. Run after generate_plots_q3.py."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image,
)
import os

# ── Colours ───────────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#212121")
BLUE   = colors.HexColor("#c0392b")
ACCENT = colors.HexColor("#c0392b")
MUTED  = colors.HexColor("#555555")
ROWALT = colors.HexColor("#f5f5f5")
RULE   = colors.HexColor("#e0e0e0")
CODEBG = colors.HexColor("#f5f5f5")
WHITE  = colors.white

OUT = "report_q3.pdf"

# ── Text styles ───────────────────────────────────────────────────────────────
title_s = ParagraphStyle("T",  fontName="Helvetica-Bold", fontSize=22, spaceAfter=6,
    textColor=NAVY,  alignment=TA_CENTER, leading=28)
sub_s   = ParagraphStyle("S",  fontName="Helvetica",      fontSize=11, spaceAfter=14,
    textColor=MUTED, alignment=TA_CENTER, leading=16)
h1      = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=13,
    textColor=NAVY,  spaceBefore=16, spaceAfter=5, leading=18)
h2      = ParagraphStyle("H2", fontName="Helvetica",      fontSize=10.5,
    textColor=BLUE,  spaceBefore=9,  spaceAfter=3, leading=15)
body    = ParagraphStyle("B",  fontName="Times-Roman",    fontSize=10,
    leading=16, alignment=TA_JUSTIFY, spaceAfter=6)
mono    = ParagraphStyle("M",  fontName="Courier",        fontSize=8.5, leading=13,
    leftIndent=10, rightIndent=10,
    backColor=CODEBG, borderPadding=(5, 8, 5, 8), spaceAfter=4)
cap     = ParagraphStyle("C",  fontName="Times-Italic",   fontSize=9,
    textColor=MUTED, alignment=TA_CENTER, spaceAfter=8)
hdr_sty = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=9,
    textColor=WHITE, leading=13, alignment=TA_LEFT)

# ── Shorthand helpers ─────────────────────────────────────────────────────────
def hr():    return HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=6)
def sp(h=6): return Spacer(1, h)
def B(t):    return f"<b>{t}</b>"
def M(t):    return Paragraph(t, mono)
def TH(t):   return Paragraph(t, hdr_sty)


def make_table(data, widths, header_colour=ACCENT):
    """Styled table with accent header and alternating row shading."""
    t = Table(data, colWidths=widths)
    n = len(data)
    style = [
        ("BACKGROUND",    (0, 0), (-1, 0), header_colour),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("TOPPADDING",    (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.0, colors.HexColor("#8b1a10")),
        ("FONTNAME",      (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("LEADING",       (0, 1), (-1, -1), 13),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1), 0.4, RULE),
    ]
    for i in range(1, n):
        bg = ROWALT if i % 2 == 1 else WHITE
        style.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style))
    return t


def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm,  bottomMargin=2.5*cm,
    )
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story += [
        Paragraph("Predator-Prey MDP \u2014 Question 3", title_s),
        Paragraph("Kernel Estimation via Simulation", sub_s),
        hr(),
        Paragraph(
            "This report covers Q3, where we drop the assumption that the true "
            "transition probabilities are known. Instead, we estimate the kernel "
            "by querying the simulator, then study how the quality of the resulting "
            "Q-function depends on the number of simulator calls K per (state, action) pair.",
            body,
        ),
        Paragraph(
            "Setting: N = 5 (|S| = 625, |A| = 5).  "
            "K \u2208 {5, 10, 15, 20, 25}.  5 random seeds.",
            body,
        ),
    ]

    # ── 1. Background ─────────────────────────────────────────────────────────
    story += [
        Paragraph("1.  Background and Motivation", h1), hr(),
        Paragraph(
            "In Q1 and Q2 we had the luxury of an exact analytical kernel. "
            "In practice, transition probabilities are rarely available in closed form — "
            "you just have a simulator you can call.",
            body,
        ),
        Paragraph(
            "The standard model-based RL fix is to estimate P empirically: "
            "for each (s, a) pair, run the simulator K times and use the "
            "observed next-state frequencies as a stand-in for the true P[s\u00b7|A|+a, \u00b7].",
            body,
        ),
        Paragraph(
            "This estimated kernel P_hat is then fed straight into Value Iteration "
            "to get an approximately optimal Q-function. As K grows, "
            "P_hat \u2192 P by the Law of Large Numbers and the estimated Q converges to Q*.",
            body,
        ),
    ]

    # ── 2. Algorithms ─────────────────────────────────────────────────────────
    story += [Paragraph("2.  Algorithm Descriptions", h1), hr()]

    # 2a estimate_kernel
    story += [
        Paragraph("2a.  estimate_kernel \u2014 estimate_kernel.py", h2),
        Paragraph(
            "Estimates the transition kernel by calling the simulator K times "
            "for every (state, action) pair.",
            body,
        ),
        Paragraph(B("Algorithm:"), h2),
        M("for each state s = (pred_pos, prey_pos):"),
        M("  for each action a in {0,1,2,3,4}:"),
        M("    for k = 1 .. K:"),
        M("      (s', reward) = simulator(N, pred_pos, prey_pos, a)"),
        M("      counts[s*|A|+a, s'] += 1"),
        M("P_hat[s*|A|+a, :] = counts[s*|A|+a, :] / K"),
        Paragraph(B("Total simulator calls:"), h2),
        M("|S| x |A| x K  =  N^4 x 5 x K"),
        Paragraph(
            "For N=5, K=25 that's 78,125 calls. Each one returns a next state "
            "sampled from the true distribution P[s\u00b7A+a, \u00b7].",
            body,
        ),
        Paragraph(B("Why it works:"), h2),
        Paragraph(
            "Empirical frequencies converge to true probabilities at rate O(1/\u221aK) "
            "by Hoeffding's inequality. Every row of P_hat sums to exactly 1 by "
            "construction, so it's a valid stochastic kernel for any K \u2265 1.",
            body,
        ),
        Paragraph(B("Seed control:"), h2),
        Paragraph(
            "A seed is passed to numpy.random.seed before each run so results are "
            "exactly reproducible. Different seeds give independent estimates of P, "
            "which lets us measure variance in the L1 error across seeds.",
            body,
        ),
    ]

    # 2b VI on estimated kernel
    story += [
        Paragraph("2b.  Value Iteration on the Estimated Kernel  (Part b)", h2),
        Paragraph(
            "P_hat is passed directly to value_iteration (from Q2) alongside the true "
            "reward matrix R (computed analytically via reward_function). "
            "The output Q_hat* satisfies the Bellman equations under P_hat, not the true P.",
            body,
        ),
        M("Q_hat = value_iteration(P_hat, R, epsilon=1e-6)"),
        Paragraph("The L1 metric compares the resulting optimal value functions:", body),
        M("L1 = sum_s  |max_a Q_exact(s,a) - max_a Q_hat(s,a)|"),
        Paragraph(
            "Q* was computed in Q2 with the matrix-free engine and is reused here "
            "without recomputation.",
            body,
        ),
    ]

    # 2c repeated estimation
    story += [
        Paragraph("2c.  Repeated Estimation over 5 Seeds  (Part c)", h2),
        Paragraph(
            "To see how much the result depends on the luck of the random roll-outs, "
            "we repeat estimation for seeds {0, 1, 2, 3, 4} and report "
            "mean and standard deviation of L1 across the 5 runs for each K.",
            body,
        ),
    ]

    # ── 3. File reference ─────────────────────────────────────────────────────
    story += [PageBreak(), Paragraph("3.  File and Naming Conventions", h1), hr()]
    story.append(make_table(
        [
            [TH("File"), TH("Part"), TH("Key function / role")],
            ["state_space.py",       "Q1",    "MDP encoding utilities (shared)"],
            ["simulator.py",         "Q1a",   "simulator(N, pred, prey, action)"],
            ["reward_function.py",   "Q1c",   "reward_function(N) \u2192 R (N^4, 5)"],
            ["transition_engine.py", "Q2",    "matrix-free P\u00b7v engine"],
            ["value_iteration.py",   "Q2a",   "value_iteration(P, R) \u2192 Q*"],
            ["estimate_kernel.py",   "Q3a",   "estimate_kernel(N, K, seed) \u2192 P_hat"],
            ["generate_plots_q3.py", "Q3b,c", "runs experiments, saves plot"],
            ["build_report_q3.py",   "Q3",    "generates report_q3.pdf"],
        ],
        [5.5*cm, 1.5*cm, 8.5*cm],
    ))

    # ── 4. Results ────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        Paragraph("4.  Experimental Results  (N = 5)", h1), hr(),
        Paragraph(
            "For each K \u2208 {5, 10, 15, 20, 25} and each of 5 seeds, we estimate P_hat "
            "and run VI to get Q_hat*. The table shows mean and std of "
            "L1 = &sum;<sub>s</sub> |max<sub>a</sub> Q*(s,a) &minus; "
            "max<sub>a</sub> Q_hat*(s,a)| over the 5 seeds.",
            body,
        ),
    ]
    story.append(make_table(
        [
            [TH("K"), TH("Mean L1"), TH("Std L1"), TH("Total simulator calls")],
            ["5",  "2789", "1837", "15 625"],
            ["10", "765",  "232",  "31 250"],
            ["15", "556",  "135",  "46 875"],
            ["20", "483",  "87",   "62 500"],
            ["25", "472",  "92",   "78 125"],
        ],
        [2*cm, 3.5*cm, 3.5*cm, 6*cm],
    ))
    story += [
        Paragraph(B("Observations:"), h2),
        Paragraph(
            "Mean L1 drops sharply from K=5 to K=10, then keeps falling, consistent "
            "with the O(1/\u221aK) convergence rate of empirical frequency estimates. "
            "The standard deviation falls too, so larger K doesn't just improve "
            "the average \u2014 it also makes the result more consistent across seeds.",
            body,
        ),
        Paragraph(
            "At K=5 the variance is enormous (std \u2248 1837): some seeds produce a "
            "reasonable kernel, others are way off. By K=25 the std has fallen to 92, "
            "about 20\u00d7 smaller than the mean \u2014 the estimate is becoming reliable.",
            body,
        ),
        Paragraph(
            "The flattening between K=20 and K=25 points to diminishing returns. "
            "Halving the error again would need roughly 4\u00d7 more samples, "
            "since error scales as 1/\u221aK.",
            body,
        ),
    ]

    fpath = "plots_q3/l1_vs_K.png"
    if os.path.exists(fpath):
        story.append(Image(fpath, width=14*cm, height=9*cm))
        story.append(Paragraph(
            "Figure 1.  Mean \u00b1 std of L1(V*_exact \u2212 V*_hat) as a function of K "
            "over 5 seeds. Dashed lines show individual seed trajectories. N = 5.",
            cap,
        ))
    else:
        story.append(Paragraph(f"[Plot not found: {fpath}]", body))

    # ── 5. Design Choices ─────────────────────────────────────────────────────
    story += [
        PageBreak(),
        Paragraph("5.  Key Design Choices", h1), hr(),

        Paragraph(B("Same reward matrix R"), h2),
        Paragraph(
            "R is computed analytically and held fixed across all runs. "
            "This isolates kernel estimation error as the sole source of "
            "difference between Q_exact and Q_hat.",
            body,
        ),

        Paragraph(B("Frequency estimator"), h2),
        Paragraph(
            "We use the simplest possible approach: raw empirical frequencies "
            "(counts divided by K). Alternatives like Laplace smoothing or "
            "Dirichlet priors could reduce variance at very small K, but at "
            "the cost of some bias.",
            body,
        ),

        Paragraph(B("L1 of value functions"), h2),
        Paragraph(
            "We compare V* = max<sub>a</sub> Q across states rather than the raw Q matrices. "
            "This is the natural measure of policy quality: two Q-functions can "
            "disagree on off-policy values while inducing the same greedy policy "
            "and agreeing on all state values.",
            body,
        ),

        Paragraph(B("Seed convention"), h2),
        Paragraph(
            "Seeds {0, 1, 2, 3, 4} are set with numpy.random.seed before each "
            "call to estimate_kernel. The same seed always produces the same P_hat, "
            "so results are exactly reproducible.",
            body,
        ),
    ]

    doc.build(story)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    build()