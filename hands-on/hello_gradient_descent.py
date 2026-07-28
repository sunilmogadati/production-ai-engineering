"""Hello, gradient descent: watch a model actually learn, one step at a time.

Why this file: hello_linear.py calls .fit() and a best-fit line appears. That's
the magic trick. This file is the trick explained - the same answer, but every
step done by hand so you can see the loop, the two knobs moving together, and
the exact moment it decides it's finished.

No numpy, no scikit-learn. Just arithmetic you could do on paper.
Pairs with study-docs/ML_Study_01 (sections 3.4 - 3.7).

Run it:      python3 hello_gradient_descent.py
Debug it:    press F5 in VS Code (see DEMO_gradient_descent.md)
"""

# ============================================================================
# THE DATA - four weeks of a small business
# ============================================================================

# What we spent on advertising each week, in thousands of dollars.
# So "1" means we spent $1,000 that week. This is the thing we KNOW (the input).
ad_spend = [1, 2, 3, 4]

# What we sold each week, in thousands of dollars.
# "5" means $5,000 of sales. This is the thing we want to PREDICT (the answer).
sales = [5, 7, 8, 11]

# How many weeks of data we have (here: 4).
# "m" is just the traditional letter for "how many examples do we have".
m = len(ad_spend)


# ============================================================================
# THE SETTINGS - the few numbers we choose ourselves
# ============================================================================

# Our starting guess for the two knobs, both set to zero.
# That means our first "model" is a flat line predicting zero sales forever.
# We start deliberately wrong to prove the math can dig itself out.
THETA0_START = 0.0   # the starting height of the line (sales at zero ad spend)
THETA1_START = 0.0   # the steepness of the line (extra sales per $1,000 spent)

# How big a step we take downhill each time we learn something.
# Too big and we leap over the answer; too small and we crawl. 0.05 is "just right" here.
ALPHA = 0.05

# A safety cap: never loop more than this many times, no matter what.
# Without it, a bad ALPHA could spin forever.
MAX_ITERS = 3000

# "Close enough to stop." If one whole round improves our score by less than
# this hair-thin amount, more rounds are pointless - so we quit.
TOLERANCE = 1e-9


# ============================================================================
# THE MODEL - three tiny functions, and that's the entire "AI"
# ============================================================================

def predict(theta0, theta1, x):
    """Our whole model: given ad spend, guess the sales."""
    # Start at theta0, then add theta1 for every $1,000 of ad spend.
    # That's it. That's the model. One line of arithmetic.
    return theta0 + theta1 * x


def cost(theta0, theta1):
    """The 'badness score' for a line. Lower = better. Like a golf score."""
    # We'll add up how badly we missed on every week.
    total = 0.0

    # Walk through the weeks one at a time, pairing each spend with its real sales.
    for x, y in zip(ad_spend, sales):
        # How far off were we this week? (our guess) minus (what really happened).
        # Negative means we guessed too low; positive means we guessed too high.
        error = predict(theta0, theta1, x) - y

        # Square it. Two reasons: it kills the minus signs (so a -3 miss and a +3
        # miss don't cancel out to "perfect"), and it punishes big misses harder.
        total += error ** 2

    # Divide by 2m to get an average (the "2" is a math convenience that makes
    # the slope formulas below come out clean - see the study doc, section 3.3).
    return total / (2 * m)


def slopes(theta0, theta1):
    """Which way is UPHILL for each knob? Both measured from the same spot."""
    # Slope for the height knob = simply the average error across all weeks.
    # If our line sits too low, this comes out negative.
    slope0 = sum(predict(theta0, theta1, x) - y for x, y in zip(ad_spend, sales)) / m

    # Slope for the steepness knob = the average error, but weighted by ad spend.
    # Weeks with bigger spend pull harder on the steepness - which makes sense,
    # because steepness affects those far-right points the most.
    slope1 = sum((predict(theta0, theta1, x) - y) * x for x, y in zip(ad_spend, sales)) / m

    # Hand back both numbers together. This pair IS "the gradient".
    return slope0, slope1


# ============================================================================
# THE LOOP - this is training. There is nothing else.
# ============================================================================

def train():
    """Walk downhill until the score stops improving."""
    # Put both knobs at their starting (deliberately terrible) values.
    theta0, theta1 = THETA0_START, THETA1_START

    # Remember last round's score so we can tell whether we're still improving.
    previous_cost = cost(theta0, theta1)

    # We won't print all 1000+ rounds - just these interesting ones.
    show_at = {0, 1, 2, 3, 5, 10, 30, 100, 500, 3000}

    # Print a table header so the numbers line up nicely.
    print(f"{'iter':>5} {'theta0':>8} {'theta1':>8} {'cost J':>10}   what's happening")
    print("-" * 78)

    # Show where we're starting from: a flat line, and a horrible score.
    print(f"{0:>5} {theta0:>8.2f} {theta1:>8.2f} {previous_cost:>10.4f}   "
          f"flat line at 0 - terrible, as intended")

    # Go around the loop up to MAX_ITERS times. Each trip = one "iteration".
    for i in range(1, MAX_ITERS + 1):

        # STEP 1: Stand still and feel which way the ground tilts, for BOTH knobs.
        # Crucially, both readings are taken from where we are RIGHT NOW.
        slope0, slope1 = slopes(theta0, theta1)

        # STEP 2: Work out where each knob should move to - but don't move yet.
        # We subtract the slope because the slope points UPHILL and we want DOWN.
        # (If the slope is negative, subtracting it makes the knob go UP. Nice trick.)
        temp0 = theta0 - ALPHA * slope0
        temp1 = theta1 - ALPHA * slope1

        # STEP 3: NOW move both knobs, at the same instant.
        # This is the "simultaneous update". We used temp0/temp1 so that theta1's
        # step was decided BEFORE theta0 moved - both from the same starting spot.
        theta0, theta1 = temp0, temp1

        # EXIT 0 (the panic button): are the knobs flying off to silly numbers?
        # That means our steps are so big we're leaping OVER the valley and landing
        # higher up the far wall each time - the "too large" picture from section 3.6.
        # We check here, before scoring, because squaring a huge number would crash.
        if abs(theta0) > 1e6 or abs(theta1) > 1e6:
            print(f"{i:>5} {theta0:>8.1e} {theta1:>8.1e} {'exploding':>10}   "
                  f"STOP: knobs flying off - ALPHA is too big (section 3.6, live)")
            break

        # Score our brand-new line. This number should drop every single round.
        current_cost = cost(theta0, theta1)

        # EXIT 1: the ground went flat. Flat only happens at the bottom - we're done.
        if abs(slope0) < 1e-7 and abs(slope1) < 1e-7:
            print(f"{i:>5} {theta0:>8.2f} {theta1:>8.2f} {current_cost:>10.4f}   "
                  f"STOP: both slopes ~ 0, we're on flat ground")
            break

        # EXIT 2: the score barely moved this round, so more rounds won't help.
        # This is the one that actually fires for our data.
        if abs(previous_cost - current_cost) < TOLERANCE:
            print(f"{i:>5} {theta0:>8.2f} {theta1:>8.2f} {current_cost:>10.4f}   "
                  f"STOP: cost stopped dropping (converged)")
            break

        # Print this round only if it's one of the interesting ones.
        if i in show_at:
            note = ""  # a plain-English aside for the rows worth pausing on

            # These asides describe what happens with the DEFAULT settings. If you've
            # changed ALPHA or the starting knobs to experiment, they'd be lies - so
            # we only show them when the settings are untouched.
            if ALPHA == 0.05 and THETA1_START == 0.0:
                if i == 10:
                    note = "<- theta1 overshoots to its peak..."
                elif i == 30:
                    note = "<- ...and now eases back down as theta0 catches up"
                elif i == 500:
                    note = "<- basically there; the remaining steps barely move it"
            print(f"{i:>5} {theta0:>8.2f} {theta1:>8.2f} {current_cost:>10.4f}   {note}")

        # Carry this round's score forward, to compare against next round's.
        previous_cost = current_cost

    else:
        # This runs ONLY if the loop finished all 3000 rounds without breaking out,
        # i.e. it never converged. Our safety cap caught it.
        i = MAX_ITERS
        print(f"{i:>5} {theta0:>8.2f} {theta1:>8.2f} {cost(theta0, theta1):>10.4f}   "
              f"STOP: hit MAX_ITERS (the safety cap)")

    # Hand back the two learned knobs, plus how many rounds it actually took.
    return theta0, theta1, i


# ============================================================================
# THE ANSWER KEY - because linear regression is simple enough to cheat on
# ============================================================================

def closed_form():
    """Solve it exactly with algebra, so we can grade our loop's homework."""
    # The average ad spend across the four weeks (2.5).
    x_bar = sum(ad_spend) / m

    # The average sales across the four weeks (7.75).
    y_bar = sum(sales) / m

    # Top of the fraction: do spend and sales move together, and how strongly?
    numerator = sum((x - x_bar) * (y - y_bar) for x, y in zip(ad_spend, sales))

    # Bottom of the fraction: how spread out is the ad spend on its own?
    denominator = sum((x - x_bar) ** 2 for x in ad_spend)

    # Divide them and you get the perfect steepness. For us: 9.5 / 5.0 = 1.9.
    theta1 = numerator / denominator

    # Then the height is whatever makes the line pass through the average point.
    theta0 = y_bar - theta1 * x_bar

    # These two numbers are the TRUTH. Our loop should crawl to roughly here.
    return theta0, theta1


# ============================================================================
# THE TEMPTING SHORTCUT - moving one knob at a time
# ============================================================================

def train_sequentially():
    """Move theta0, THEN read theta1's slope from the new spot. Not the same thing."""
    # Same terrible starting point as before, so it's a fair race.
    theta0, theta1 = THETA0_START, THETA1_START

    # No printing, no early exit - just run it out and see where it lands.
    for _ in range(MAX_ITERS):
        # Read ONLY the height knob's slope, and move it immediately.
        slope0, _ = slopes(theta0, theta1)
        theta0 = theta0 - ALPHA * slope0

        # Now read the steepness slope - but we're standing somewhere new, because
        # theta0 already moved. This reading comes from a different spot on the hill.
        _, slope1 = slopes(theta0, theta1)
        theta1 = theta1 - ALPHA * slope1

    # Where did this different recipe end up? (The surprise is below.)
    return theta0, theta1


# ============================================================================
# RUN IT ALL AND EXPLAIN WHAT HAPPENED
# ============================================================================

# Reprint the file's own summary at the top, minus the "how to run" bit.
print(__doc__.split("Run it:")[0].strip())

print("\n" + "=" * 78)
print("TRAINING: walk downhill until the score stops improving")
print("=" * 78)

# Do the actual learning. This one line runs the whole loop above.
learned0, learned1, iters_used = train()

print("\n" + "=" * 78)
print("DID IT WORK? Grade the loop against the exact formula")
print("=" * 78)

# Get the algebraically perfect answer to compare against.
true0, true1 = closed_form()

# Show what the blindfolded walk found...
print(f"  gradient descent found : sales = {learned0:.4f} + {learned1:.4f} * spend")

# ...versus what algebra proves is exactly right.
print(f"  exact formula says     : sales = {true0:.4f} + {true1:.4f} * spend")

# And how tiny the gap is (a rounding crumb).
print(f"  difference             : {abs(learned0 - true0):.2e} and {abs(learned1 - true1):.2e}")
print("\n  It walked, blindfolded, to the same answer algebra proves. That's the point.")

print("\n" + "=" * 78)
print("BONUS: what if we moved the knobs one at a time instead?")
print("=" * 78)

# Run the "shortcut" version to see where it ends up.
seq0, seq1 = train_sequentially()

print(f"  simultaneous (real gradient descent) : theta0={learned0:.4f}  theta1={learned1:.4f}")
print(f"  sequential   (NOT gradient descent)  : theta0={seq0:.4f}  theta1={seq1:.4f}")
print()
print("  Surprise: on a convex bowl, BOTH land on the same answer. The stopping")
print("  point is wherever every slope vanishes, and that's the same place either")
print("  way - they just take different routes there.")
print()
print("  So why insist on simultaneous? Because the gradient MEANS 'all the slopes")
print("  measured at the same point'. Mix in a slope taken after theta0 already")
print("  moved and your step is no longer along the gradient - every guarantee you")
print("  reasoned about (steepest descent, the learning-rate rules) assumed it was.")
print("  Real code sidesteps this by construction: theta := theta - alpha * grad(theta)")
print("  updates every knob at once, as one vector.")

print("\n" + "=" * 78)
print("THE TAKEAWAY")
print("=" * 78)
print("  1. Training is a LOOP: predict -> measure error -> nudge downhill -> repeat.")
print("  2. Both knobs move on EVERY pass. You never finish theta0 then start theta1.")
print("  3. It exits when the slopes flatten, the cost stops dropping, or it hits the cap.")
print("  4. Sign does the steering: line too low -> negative slope -> subtracting it")
print("     RAISES the line. The slope always points away from where you want to go.")
print(f"  5. A model 'learning' is just this: {iters_used} rounds of arithmetic, no magic.")
print(f"     (It never reached the {MAX_ITERS} cap - exit condition 2 fired first.)")
