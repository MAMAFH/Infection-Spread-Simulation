"""
============================================================
  scenarios.py — Multi-Scenario Comparison
  Usage: py scenarios.py
============================================================

  Three scenarios run against the same base parameters:
  1) No intervention       (baseline)
  2) Vaccination campaign  (daily vaccination rate)
  3) Social distancing     (reduced IR after intervention day)

  All results plotted on the same chart for easy comparison.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from seir_model import simulate_seird, plot_seird, print_metrics

# ──────────────────────────────────────────────────────────
#  SHARED BASE PARAMETERS
# ──────────────────────────────────────────────────────────
N     = 10_000
E0    = 50
I0    = 10
DAYS  = 200

IR    = 0.30
RR    = 0.07
DR    = 0.01
SIGMA = 0.20

# ──────────────────────────────────────────────────────────
#  SCENARIO 1 — No Intervention (baseline)
# ──────────────────────────────────────────────────────────
res_baseline = simulate_seird(
    N=N, E0=E0, I0=I0,
    IR=IR, RR=RR, DR=DR, sigma=SIGMA,
    days=DAYS,
)
print_metrics(res_baseline, label="Scenario 1 — No Intervention")

# ──────────────────────────────────────────────────────────
#  SCENARIO 2 — Daily Vaccination (0.8% of S vaccinated/day)
#  Vaccination moves S → R each day, shrinking the
#  susceptible pool and slowing / stopping the epidemic.
# ──────────────────────────────────────────────────────────
VACC_RATE = 0.008   # 0.8% of remaining S vaccinated per day

res_vaccination = simulate_seird(
    N=N, E0=E0, I0=I0,
    IR=IR, RR=RR, DR=DR, sigma=SIGMA,
    days=DAYS,
    vaccination_rate=VACC_RATE,
)
print_metrics(res_vaccination, label="Scenario 2 — Vaccination (0.8%/day)")

# ──────────────────────────────────────────────────────────
#  SCENARIO 3 — Social Distancing (IR reduced on day 30)
#  Reducing IR models mask mandates, school closures, etc.
#  The infection curve flattens ("flattening the curve").
# ──────────────────────────────────────────────────────────
INTERVENTION_DAY = 30   # day distancing starts
IR_REDUCED       = 0.10 # IR drops from 0.30 to 0.10

res_distancing = simulate_seird(
    N=N, E0=E0, I0=I0,
    IR=IR, RR=RR, DR=DR, sigma=SIGMA,
    days=DAYS,
    intervention_day=INTERVENTION_DAY,
    IR_reduced=IR_REDUCED,
)
print_metrics(res_distancing, label=f"Scenario 3 — Social Distancing from Day {INTERVENTION_DAY}")

# ──────────────────────────────────────────────────────────
#  FULL SEIRD CHARTS FOR EACH SCENARIO
# ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("SEIR-D Multi-Scenario Comparison", fontsize=14, fontweight="bold")

plot_seird(res_baseline,   title="Scenario 1 — No Intervention",       ax=axes[0])
plot_seird(res_vaccination, title="Scenario 2 — Vaccination (0.8%/day)", ax=axes[1])
plot_seird(res_distancing, title=f"Scenario 3 — Social Distancing (Day {INTERVENTION_DAY})", ax=axes[2])

plt.tight_layout()
plt.savefig("scenarios_full.png", dpi=150)
plt.show()

# ──────────────────────────────────────────────────────────
#  OVERLAY: Infected (I) curve — all 3 on one chart
# ──────────────────────────────────────────────────────────
palette = ["#ff006e", "#3a86ff", "#06d6a0"]
labels  = [
    "No Intervention",
    "Vaccination (0.8%/day)",
    f"Social Distancing (Day {INTERVENTION_DAY})",
]
results = [res_baseline, res_vaccination, res_distancing]

fig2, ax2 = plt.subplots(figsize=(11, 6))
for res, label, colour in zip(results, labels, palette):
    ax2.plot(res["time"], res["I"], label=label, color=colour, linewidth=2.5)

# Mark intervention day as vertical line
ax2.axvline(x=INTERVENTION_DAY, color="grey",
            linestyle=":", linewidth=1.5, label=f"Intervention Day {INTERVENTION_DAY}")

ax2.set_title("Infected (I) Over Time — All Scenarios", fontsize=13, fontweight="bold")
ax2.set_xlabel("Days")
ax2.set_ylabel("Infected Count")
ax2.legend()
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax2.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("scenarios_infected_overlay.png", dpi=150)
plt.show()

# ──────────────────────────────────────────────────────────
#  SUMMARY TABLE
# ──────────────────────────────────────────────────────────
print("\n" + "═" * 65)
print(f"  {'Scenario':<32} {'Peak I':>10} {'Day':>5} {'Deaths':>10}")
print("═" * 65)
for res, label in zip(results, labels):
    print(f"  {label:<32} {res['peak_infected']:>10,.0f} "
          f"{res['peak_day']:>5}  {res['total_dead']:>10,.0f}")
print("═" * 65)
print("\n✅ Charts saved: scenarios_full.png, scenarios_infected_overlay.png")
