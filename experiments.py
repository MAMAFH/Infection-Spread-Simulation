"""
============================================================
  experiments.py — 4 Simulation Experiments
  Usage:  python experiments.py
============================================================

  Experiment 1: Vary infection rate (β)
  Experiment 2: Vary recovery rate (γ)
  Experiment 3: Effect of vaccination
  Experiment 4: Normal vs. social distancing (lower β)
"""

import matplotlib.pyplot as plt
from sir_model import simulate_sir, plot_sir, print_summary

# ──────────────────────────────────────────────────────────
#  SHARED BASE SETTINGS
# ──────────────────────────────────────────────────────────
N    = 10_000
I0   = 10
DAYS = 200

# ──────────────────────────────────────────────────────────
#  EXPERIMENT 1: Vary Infection Rate (β)
#  Expected: Higher β → faster spread, higher peak, earlier peak
# ──────────────────────────────────────────────────────────
print("\n=== Experiment 1: Varying β (infection rate) ===")

beta_values = [0.1, 0.2, 0.3, 0.5]
gamma_fixed  = 0.05

fig1, axes1 = plt.subplots(2, 2, figsize=(14, 8))
fig1.suptitle("Experiment 1: Effect of Infection Rate (β)", fontsize=14, fontweight="bold")

for ax, beta in zip(axes1.flatten(), beta_values):
    res = simulate_sir(N=N, I0=I0, beta=beta, gamma=gamma_fixed, days=DAYS)
    plot_sir(res, title=f"β = {beta}  |  R₀ = {res['R0']:.1f}", ax=ax)
    print_summary(res, label=f"β={beta}")

plt.tight_layout()
plt.savefig("exp1_beta.png", dpi=150)
plt.show()

# ──────────────────────────────────────────────────────────
#  EXPERIMENT 2: Vary Recovery Rate (γ)
#  Expected: Higher γ → faster recovery, lower peak
# ──────────────────────────────────────────────────────────
print("\n=== Experiment 2: Varying γ (recovery rate) ===")

beta_fixed   = 0.3
gamma_values = [0.02, 0.05, 0.10, 0.20]

fig2, axes2 = plt.subplots(2, 2, figsize=(14, 8))
fig2.suptitle("Experiment 2: Effect of Recovery Rate (γ)", fontsize=14, fontweight="bold")

for ax, gamma in zip(axes2.flatten(), gamma_values):
    res = simulate_sir(N=N, I0=I0, beta=beta_fixed, gamma=gamma, days=DAYS)
    plot_sir(res, title=f"γ = {gamma}  |  R₀ = {res['R0']:.1f}", ax=ax)
    print_summary(res, label=f"γ={gamma}")

plt.tight_layout()
plt.savefig("exp2_gamma.png", dpi=150)
plt.show()

# ──────────────────────────────────────────────────────────
#  EXPERIMENT 3: Vaccination Effect
#  Expected: Higher vaccination → fewer susceptibles → lower/no peak
# ──────────────────────────────────────────────────────────
print("\n=== Experiment 3: Vaccination Effect ===")

beta_v  = 0.3
gamma_v = 0.05
vax_levels = [0.0, 0.20, 0.40, 0.70]

fig3, axes3 = plt.subplots(2, 2, figsize=(14, 8))
fig3.suptitle("Experiment 3: Effect of Vaccination", fontsize=14, fontweight="bold")

for ax, vax in zip(axes3.flatten(), vax_levels):
    res = simulate_sir(N=N, I0=I0, beta=beta_v, gamma=gamma_v,
                       days=DAYS, vaccination_pct=vax)
    plot_sir(res, title=f"Vaccination = {int(vax*100)}%", ax=ax)
    print_summary(res, label=f"Vaccination={int(vax*100)}%")

plt.tight_layout()
plt.savefig("exp3_vaccination.png", dpi=150)
plt.show()

# ──────────────────────────────────────────────────────────
#  EXPERIMENT 4: Normal vs Social Distancing
#  Social distancing ≈ reducing β (fewer contacts per day)
#  Expected: Lower β significantly flattens the infection curve
# ──────────────────────────────────────────────────────────
print("\n=== Experiment 4: Normal vs. Social Distancing ===")

gamma_sd = 0.05
scenarios = {
    "No Measures (β=0.4)":       {"beta": 0.4, "color": "#ff006e"},
    "Mild Distancing (β=0.25)":  {"beta": 0.25, "color": "#fb8500"},
    "Strong Distancing (β=0.15)":{"beta": 0.15, "color": "#06d6a0"},
}

fig4, ax4 = plt.subplots(figsize=(11, 6))

for label, cfg in scenarios.items():
    res = simulate_sir(N=N, I0=I0, beta=cfg["beta"],
                       gamma=gamma_sd, days=DAYS)
    ax4.plot(res["time"], res["I"], label=label,
             color=cfg["color"], linewidth=2.5)
    print_summary(res, label=label)

ax4.set_title("Experiment 4: Normal vs. Social Distancing",
              fontsize=13, fontweight="bold")
ax4.set_xlabel("Days")
ax4.set_ylabel("Infected Population")
ax4.legend()
ax4.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("exp4_distancing.png", dpi=150)
plt.show()

print("\n✅ All experiments complete. Charts saved as PNG files.")
