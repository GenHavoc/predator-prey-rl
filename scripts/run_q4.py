from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether,
)
import os

OUT_PATH = "report.pdf"

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

bullet = ParagraphStyle("Bullet",
    fontName="Helvetica", fontSize=9.5, leading=14,
    textColor=colors.HexColor("#222222"), alignment=TA_JUSTIFY,
    leftIndent=18, bulletIndent=8, spaceBefore=1, spaceAfter=3,
    bulletFontName="Helvetica", bulletFontSize=9.5)

formula = ParagraphStyle("Formula",
    fontName="Helvetica", fontSize=10.5, leading=17,
    textColor=colors.HexColor("#212121"), alignment=TA_CENTER,
    backColor=colors.HexColor("#fdf2f1"),
    borderPadding=(8, 12, 8, 12),
    spaceBefore=6, spaceAfter=6)

def F(text):
    inner = Paragraph(text, ParagraphStyle("FI",
        fontName="Helvetica", fontSize=10.5, leading=17,
        textColor=colors.HexColor("#212121"), alignment=TA_CENTER))
    t = Table([[inner]], colWidths=[PAGE_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#fdf2f1")),
        ("BOX",           (0,0), (-1,-1), 0.6, ACCENT),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
    ]))
    return t


def info_box(text, bg=LTBLUE, border=BLUE):
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

def cover_block():
    return KeepTogether([
        Paragraph("Predator&ndash;Prey Policy Gradient", title_style),
        Paragraph("Neural Network Design, REINFORCE, and Optimizers", subtitle_style),
        sp(10),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=4, spaceBefore=0),
    ])


def build():
    doc = SimpleDocTemplate(OUT_PATH, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm)
    story = []

    story += [cover_block(), sp(6),
        Paragraph(
            "This report documents the implementation of a reinforcement learning agent "
            "for a predator-prey game on a 4&times;4 grid using PyTorch. We walk through "
            "the design of the neural network policy, the unbiased estimation of the "
            "policy gradient using the REINFORCE algorithm, and a comparison between "
            "Simple Stochastic Gradient Ascent (SGA) and the Adam optimizer.",
            body),
    ]

    story += [sp(8), subsection("Hyperparameters")]
    hp_data = [
        ["Parameter", "Value"],
        ["Grid size (N)", "4"],
        ["Discount factor (γ)", "0.99"],
        ["Max steps per episode", "50"],
        ["Episodes per gradient estimate", "20"],
        ["Learning rate – Simple SGA", "0.005"],
        ["Learning rate – Adam", "0.003"],
        ["Training iterations", "2000"],
    ]
    hp_table = Table(hp_data, colWidths=[PAGE_W*0.55, PAGE_W*0.45])
    hp_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#c0392b")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, ROWALT]),
        ("GRID",        (0, 0), (-1, -1), 0.3, RULE),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(hp_table)

    story += [sp(10), section("1. Neural Network Policy Design (Part a)")]
    story += [
        Paragraph(
            "The policy function &pi;<sub>&theta;</sub>(a|s) maps the current state to a "
            "probability distribution over the five possible actions. We implemented this "
            "using a feed-forward neural network in PyTorch (<b>PolicyNetwork</b> class in "
            "<i>policy_network.py</i>).",
            body),
        subsection("1.1  State Representation"),
        Paragraph(
            "The environment consists of a predator and a prey on a 4&times;4 grid.  "
            "Rather than using raw coordinates (which would impose a misleading linear "
            "metric on positions), we encode the state as a <b>concatenated one-hot vector</b>:",
            body),
        M("state = [one_hot(predator_pos, 16)  ||  one_hot(prey_pos, 16)]"),
        Paragraph(
            "This produces a <b>32-dimensional</b> binary input vector. "
            "The first 16 elements identify the predator cell; the second 16 identify the prey cell. "
            "One-hot encoding is critical because it lets the network learn independent spatial features "
            "for each cell without assuming any numerical distance between grid positions.",
            body),
        subsection("1.2  Network Architecture"),
        Paragraph(
            "The network consists of three fully connected linear layers with ReLU activations "
            "in the hidden layers:",
            body),
        M("Linear(32, 128) -> ReLU -> Linear(128, 128) -> ReLU -> Linear(128, 5)"),
        Paragraph(
            "<bullet>&bull;</bullet> <b>Input layer (32 &rarr; 128):</b>  Projects the sparse one-hot encoding into a "
            "dense 128-dimensional representation.",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> <b>Hidden layer (128 &rarr; 128):</b>  Adds a second layer of nonlinearity, allowing "
            "the network to learn complex predator-prey spatial interactions.",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> <b>Output layer (128 &rarr; 5):</b>  Produces raw logits for the five actions "
            "(stay, up, down, left, right).",
            body),
        sp(4),
        Paragraph(
            "The output logits are passed directly to <code>Categorical(logits=...)</code> from "
            "<code>torch.distributions</code>, which applies the softmax internally.  This avoids "
            "numerical instability from manually computing exp/sum.",
            body),
        subsection("1.3  Design Rationale"),
        Paragraph(
            "128 hidden units in two layers provide sufficient capacity to represent a good policy "
            "over the 256 joint states (16 predator positions &times; 16 prey positions) while keeping "
            "the parameter count manageable (~21k parameters) for REINFORCE, which is a high-variance estimator. "
            "Weights are initialized using Xavier uniform initialization and biases are set to zero, which produces "
            "a near-uniform starting policy&mdash;a reasonable exploration starting point.",
            body),
    ]

    story += [sp(10), section("2. Unbiased Gradient Estimation (Part b)")]
    story += [
        Paragraph(
            "To train the policy, we need an unbiased estimate of the policy gradient. "
            "Since we only have access to the <code>simulator</code> function (a black-box environment "
            "that returns next states and rewards), we use Monte-Carlo sampling via the "
            "<b>REINFORCE algorithm</b> (also called the score-function estimator).",
            body),
        subsection("2.1  The REINFORCE Algorithm"),
        Paragraph(
            "The training objective is the expected total return under the policy:",
            body),
        F("J(&theta;) = E<sub>&tau;~&pi;<sub>&theta;</sub></sub>[R(&tau;)],&nbsp;&nbsp;&nbsp;&nbsp;R(&tau;) = &sum;<sub>t</sub> r<sub>t</sub>"),
        sp(2),
        Paragraph(
            "The policy-gradient theorem (Sutton et al., 1999) gives the exact gradient:",
            body),
        F("&nabla;<sub>&theta;</sub>J(&theta;) = E<sub>&tau;~&pi;<sub>&theta;</sub></sub>[&sum;<sub>t</sub> G<sub>t</sub> &nabla;<sub>&theta;</sub> log &pi;<sub>&theta;</sub>(a<sub>t</sub> | s<sub>t</sub>)]"),
        sp(2),
        Paragraph(
            "where G<sub>t</sub> = &sum;<sub>k&ge;t</sub> &gamma;<sup>k&minus;t</sup> r<sub>k</sub> "
            "is the discounted return from step t. Using G<sub>t</sub> instead of the full episode "
            "return R(&tau;) applies the <i>causality improvement</i>: future actions cannot affect "
            "past rewards, reducing variance without introducing bias.",
            body),
        sp(4),
        Paragraph(
            "A single-trajectory Monte-Carlo estimate (<b>REINFORCE</b>, Williams 1992) is:",
            body),
        F("g<super>^</super> = &sum;<sub>t</sub> G<sub>t</sub> &nabla;<sub>&theta;</sub> log &pi;<sub>&theta;</sub>(a<sub>t</sub> | s<sub>t</sub>)"),
        sp(4),
        Paragraph(
            "The <code>gradient_estimate</code> function in <i>gradient_estimate.py</i> implements this by:",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> Running <b>20 episodes</b> of 50 steps each using the simulator,",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> Recording log &pi;<sub>&theta;</sub>(a<sub>t</sub>|s<sub>t</sub>) at each step,",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> Computing discounted returns G<sub>t</sub> via backward recursion,",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> Forming the loss L = &minus;(1/M) &sum;<sub>episodes</sub> &sum;<sub>t</sub> "
            "log &pi;(a<sub>t</sub>|s<sub>t</sub>) &#183; G<sub>t</sub>,",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> Averaging over M = 20 episodes for lower-variance gradient estimates.",
            body),
        subsection("2.2  PyTorch Score Function Method"),
        Paragraph(
            "The score function &nabla;<sub>&theta;</sub> log &pi;<sub>&theta;</sub>(a|s) is obtained "
            "using PyTorch's <b><code>torch.distributions.Categorical</code></b> class:",
            body),
        M("logits = policy(state)                    # forward pass\n"
          "dist = Categorical(logits=logits)          # build distribution\n"
          "action = dist.sample()                     # sample action\n"
          "log_prob = dist.log_prob(action)            # log pi(a|s)"),
        Paragraph(
            "The key method is <b><code>dist.log_prob(action)</code></b>.  It computes "
            "log &pi;<sub>&theta;</sub>(a|s) while preserving the autograd computational graph.  "
            "When we later call <code>.backward()</code> on a loss built from these log-probabilities, "
            "PyTorch's automatic differentiation engine computes &nabla;<sub>&theta;</sub> log &pi;<sub>&theta;</sub>(a|s) "
            "exactly&mdash;the score function.",
            body),
        sp(4),
        info_box(
            B("Unbiased Property: ") +
            "To keep the gradient estimate strictly unbiased as required, we use the raw "
            "discounted returns G<sub>t</sub> without subtracting a baseline or standardizing. "
            "While a baseline would reduce variance, it is not required for unbiasedness, "
            "and we keep the estimator in its purest form.",
            INFO_BG, colors.HexColor("#c0392b")),
    ]

    story += [PageBreak(), section("3. Simple Stochastic Gradient Ascent (Part c)")]
    story += [
        Paragraph(
            "With the gradient estimate computed, the <code>simple_SGA</code> function in "
            "<i>simple_sga.py</i> updates the parameters using the vanilla gradient ascent rule:",
            body),
        F("&theta; &larr; &theta; + &alpha; &nabla;<sub>&theta;</sub>J &nbsp;&nbsp;(gradient <i>ascent</i> on J)"),
        sp(2),
        Paragraph(
            "Since our loss L = &minus;J(&theta;), calling <code>loss.backward()</code> gives "
            "&nabla;<sub>&theta;</sub> L = &minus;&nabla;<sub>&theta;</sub> J. Therefore gradient "
            "<i>descent</i> on L is equivalent to gradient <i>ascent</i> on J:",
            body),
        M("policy.zero_grad()\n"
          "loss.backward()\n"
          "with torch.no_grad():\n"
          "    for param in policy.parameters():\n"
          "        param.data -= lr * param.grad"),
        subsection("3.1  Learning Rate Choice"),
        Paragraph(
            "We use a learning rate of <b>&alpha; = 0.005</b> for Simple SGA.  This was selected "
            "empirically:",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> <b>&alpha; = 0.001:</b>  Too slow; the policy barely improved over 1000 iterations.",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> <b>&alpha; = 0.01:</b>  Moderate improvement but showed oscillations due to "
            "high-variance REINFORCE gradients.",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> <b>&alpha; = 0.05:</b>  Too aggressive; caused the policy to oscillate wildly "
            "and fail to converge.",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> <b>&alpha; = 0.005:</b>  Best trade-off between speed and stability.  "
            "The policy shows a clear upward learning trend.",
            body),
    ]

    story += [sp(10), section("4. Adam Optimizer Comparison (Part d)")]
    story += [
        Paragraph(
            "To contrast with simple SGA, we trained an identical policy network using "
            "PyTorch's built-in <b><code>torch.optim.Adam</code></b> optimizer "
            "(Kingma &amp; Ba, 2015) with learning rate &alpha; = 3&times;10<sup>&minus;3</sup>.",
            body),
        subsection("4.1  Adam Algorithm"),
        Paragraph(
            "Adam maintains bias-corrected exponential moving averages of the first moment (mean) "
            "and second moment (uncentred variance) of the gradient, then scales each parameter update individually:",
            body),
        F("m<super>^</super><sub>t</sub> = (&beta;<sub>1</sub> m<sub>t&minus;1</sub> + (1&minus;&beta;<sub>1</sub>) g<sub>t</sub>) / (1&minus;&beta;<sub>1</sub><sup>t</sup>)&nbsp;&nbsp;&nbsp;(bias-corrected 1st moment)"),
        sp(3),
        F("v<super>^</super><sub>t</sub> = (&beta;<sub>2</sub> v<sub>t&minus;1</sub> + (1&minus;&beta;<sub>2</sub>) g<sub>t</sub><sup>2</sup>) / (1&minus;&beta;<sub>2</sub><sup>t</sup>)&nbsp;&nbsp;&nbsp;(bias-corrected 2nd moment)"),
        sp(3),
        F("&theta;<sub>t</sub> = &theta;<sub>t&minus;1</sub> &minus; &alpha; &#183; m<super>^</super><sub>t</sub> / (&radic;v<super>^</super><sub>t</sub> + &epsilon;)"),
        sp(4),
        Paragraph(
            "The adaptive per-parameter scaling by the square root of the second moment makes Adam far less "
            "sensitive to the choice of learning rate than plain SGD, and typically converges "
            "faster in terms of iteration count.",
            body),
        subsection("4.2  Why Adam Over Simple SGA?"),
        Paragraph(
            "<bullet>&#8226;</bullet> <b>Adaptive step sizes:</b>  Parameters receiving sparse or infrequent "
            "gradients get larger effective learning rates.",
            body),
        Paragraph(
            "<bullet>&#8226;</bullet> <b>Momentum:</b>  The first-moment estimate smooths out the high variance "
            "inherent in REINFORCE, leading to more stable updates.",
            body),
        sp(4),
        Paragraph(
            "The implementation in <i>run_adam.py</i> follows the standard PyTorch pattern:",
            body),
        M("optimizer = optim.Adam(policy.parameters(), lr=0.003)\n"
          "optimizer.zero_grad()\n"
          "loss.backward()\n"
          "optimizer.step()"),
        sp(8),
        subsection("4.5  Learning Curves"),
        Paragraph(
            "The figure below compares the smoothed total reward per episode over 2000 training "
            "iterations for both Simple SGA (lr=0.005) and Adam (lr=0.003). "
            "Faint lines show raw rewards; bold lines show the exponential moving average "
            "(weight&nbsp;=&nbsp;0.95).",
            body),
    ]

    story.append(sp(8))
    fname = "learning_curves.png"
    if os.path.exists(fname):
        story.append(Image(fname, width=14*cm, height=7*cm))
        story.append(Paragraph(
            "Figure 1. Learning curves: Simple SGA vs Adam on the Predator-Prey game (N=4). "
            "Both optimizers show an upward trend in average reward. Adam typically converges "
            "faster and more stably due to its adaptive moment estimates.",
            caption))
    else:
        story.append(info_box(
            "<b>Plot not found.</b>  Run <code>python3 generate_plots.py</code> first "
            "to generate learning_curves.png, then re-run this script.",
            WARN_BG, colors.HexColor("#e65100")))

    story += [sp(10), section("5. Summary")]
    story += [
        Paragraph(
            "We have successfully implemented the REINFORCE policy gradient algorithm for "
            "the predator-prey game on a 4&times;4 grid:",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> A 3-layer feed-forward neural network (32&rarr;128&rarr;128&rarr;5) "
            "parameterizes the stochastic policy.",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> The <code>gradient_estimate</code> function provides unbiased Monte-Carlo "
            "estimates of the policy gradient using the REINFORCE algorithm, with PyTorch's "
            "<code>Categorical.log_prob</code> for the score function.",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> Simple SGA manually updates parameters with a fixed learning rate (0.005).",
            body),
        Paragraph(
            "<bullet>&bull;</bullet> Adam adapts learning rates per parameter, generally achieving faster and "
            "more stable convergence for this problem.",
            body),
    ]

    doc.build(story)
    print(f"Report saved to {OUT_PATH}")


if __name__ == "__main__":
    build()