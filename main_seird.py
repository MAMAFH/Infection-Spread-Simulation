"""
============================================================
  main_seird.py — Run a single SEIR-D base simulation
  Usage:  py main_seird.py
============================================================
"""

from seir_model import simulate_seird, plot_seird, print_metrics

# ──────────────────────────────────────────────────────────
#  PARAMETERS  ← edit these to explore the model
# ──────────────────────────────────────────────────────────
N     = 10_000   # Total population
E0    = 50       # Initially exposed (incubating)
I0    = 10       # Initially infectious
DAYS  = 200      # Simulation length (days)

IR    = 0.30     # Infection rate  (S → E per contact per day)
RR    = 0.07     # Recovery rate   (fraction of I who recover per day)
DR    = 0.01     # Death rate      (fraction of I who die per day)
#                  ⚠ RR + DR must be < 1
SIGMA = 0.20     # Incubation rate (fraction of E who become I per day)
#                  1/sigma = average incubation period = 5 days

# ── Optional: intervention (IR drops after a given day) ───
INTERVENTION_DAY = None   # e.g. 40 — set to None to disable
IR_REDUCED       = None   # e.g. 0.10

# ── Optional: daily vaccination ───────────────────────────
VACCINATION_RATE = 0.0    # e.g. 0.005 → 0.5% of S vaccinated per day

# ──────────────────────────────────────────────────────────
#  RUN
# ──────────────────────────────────────────────────────────
result = simulate_seird(
    N=N, E0=E0, I0=I0,
    IR=IR, RR=RR, DR=DR, sigma=SIGMA,
    days=DAYS,
    intervention_day=INTERVENTION_DAY,
    IR_reduced=IR_REDUCED,
    vaccination_rate=VACCINATION_RATE,
)

print_metrics(result, label="SEIR-D Base Simulation")

plot_seird(
    result,
    title=f"SEIR-D Base  |  IR={IR}, RR={RR}, DR={DR}, σ={SIGMA}, N={N:,}",
)
