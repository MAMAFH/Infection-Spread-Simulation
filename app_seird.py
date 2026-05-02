"""
============================================================
  app_seird.py — Streamlit Interactive UI for SEIR-D Model
  Usage: py -m streamlit run app_seird.py
============================================================
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from seir_model import simulate_seird, simulate_multiple_stochastic, plot_stochastic_comparison, COLOURS

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Infection Spread Simulation",
    page_icon="🦠",
    layout="wide",
)

st.title("🦠 Infection Spread Simulation")
st.markdown(
    "Model disease spread with **Exposed** and **Death** compartments, "
    "time-varying infection rate, and ongoing vaccination."
)

# ── Sidebar Parameters ─────────────────────────────────────
st.sidebar.header("⚙️ Population & Time")
N    = st.sidebar.number_input("Population (N)",  100, 1_000_000, 10_000, 100)
E0   = st.sidebar.number_input("Initially Exposed (E₀)", 0, 10_000, 50)
I0   = st.sidebar.number_input("Initially Infected (I₀)", 1, 10_000, 10)
DAYS = st.sidebar.slider("Duration (days)", 30, 730, 200, 10)

st.sidebar.header("🔬 Disease Parameters")
IR    = st.sidebar.slider("Infection Rate (IR)",       0.01, 1.0,  0.30, 0.01,
                           help="Daily transmission probability per contact")
RR    = st.sidebar.slider("Recovery Rate (RR)",        0.01, 0.50, 0.07, 0.01,
                           help="Fraction of infected who recover per day")
DR    = st.sidebar.slider("Death Rate (DR)",           0.00, 0.20, 0.01, 0.005,
                           help="Fraction of infected who die per day")
SIGMA = st.sidebar.slider("Incubation Rate (σ)",       0.01, 1.0,  0.20, 0.01,
                           help="Fraction of exposed who become infectious per day (1/σ = avg incubation days)")

if RR + DR >= 1.0:
    st.sidebar.error(f"⚠ RR + DR = {RR+DR:.2f} ≥ 1. Please reduce values.")
    st.stop()

st.sidebar.header("💉 Vaccination")
VAX_RATE = st.sidebar.slider("Daily Vaccination Rate (% of S)",
                               0, 5, 0, step=1,
                               help="Percentage of susceptibles vaccinated each day") / 100.0

st.sidebar.header("🚦 Intervention (Reduce IR)")
use_intervention = st.sidebar.checkbox("Enable Social Distancing / Intervention")
INT_DAY    = None
IR_REDUCED = None
if use_intervention:
    INT_DAY    = st.sidebar.slider("Intervention Day", 1, DAYS - 1, 30)
    IR_REDUCED = st.sidebar.slider("Reduced IR after Intervention", 0.01, IR, min(0.10, IR), 0.01)

st.sidebar.header("🎲 Simulation Mode")
SIM_MODE = st.sidebar.radio("Select Mode", ["Deterministic", "Stochastic"])
NUM_RUNS = 1
if SIM_MODE == "Stochastic":
    NUM_RUNS = st.sidebar.slider("Number of Stochastic Runs", 1, 20, 5)

# ── Run Simulation ─────────────────────────────────────────
result_det = simulate_seird(
    N=N, E0=E0, I0=I0,
    IR=IR, RR=RR, DR=DR, sigma=SIGMA,
    days=DAYS,
    intervention_day=INT_DAY,
    IR_reduced=IR_REDUCED,
    vaccination_rate=VAX_RATE,
    mode="deterministic"
)

stoch_results = []
if SIM_MODE == "Stochastic":
    stoch_results = simulate_multiple_stochastic(
        N=N, E0=E0, I0=I0,
        IR=IR, RR=RR, DR=DR, sigma=SIGMA,
        days=DAYS,
        intervention_day=INT_DAY,
        IR_reduced=IR_REDUCED,
        vaccination_rate=VAX_RATE,
        num_runs=NUM_RUNS
    )

# ── Metrics Row ────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("R₀", f"{result_det['R0']:.2f}")

if SIM_MODE == "Deterministic":
    c2.metric("Peak Infected",  f"{result_det['peak_infected']:,.0f}")
    c3.metric("Peak Day",       str(result_det["peak_day"]))
    c4.metric("Total Recovered",f"{result_det['total_recovered']:,.0f}")
    c5.metric("Total Deaths",   f"{result_det['total_dead']:,.0f}")
else:
    avg_peak = sum(r['peak_infected'] for r in stoch_results) / len(stoch_results)
    avg_peak_day = sum(r['peak_day'] for r in stoch_results) / len(stoch_results)
    avg_rec = sum(r['total_recovered'] for r in stoch_results) / len(stoch_results)
    avg_deaths = sum(r['total_dead'] for r in stoch_results) / len(stoch_results)
    
    c2.metric("Avg Peak Infected",  f"{avg_peak:,.0f}")
    c3.metric("Avg Peak Day",       f"{avg_peak_day:.1f}")
    c4.metric("Avg Total Recovered",f"{avg_rec:,.0f}")
    c5.metric("Avg Total Deaths",   f"{avg_deaths:,.0f}")

# ── Full SEIRD Chart ───────────────────────────────────────
if SIM_MODE == "Deterministic":
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    for key in ("S", "E", "I", "R", "D"):
        ax.plot(result_det["time"], result_det[key],
                label=key, color=COLOURS[key], linewidth=2)

    ax.axvline(x=result_det["peak_day"], color=COLOURS["I"],
               linestyle="--", alpha=0.5)

    if use_intervention and INT_DAY:
        ax.axvline(x=INT_DAY, color="grey", linestyle=":",
                   linewidth=1.5, label=f"Intervention Day {INT_DAY}")

    ax.set_title(f"SEIR-D (Deterministic) | IR={IR}, RR={RR}, DR={DR}, σ={SIGMA}, N={N:,}",
                 fontweight="bold")
    ax.set_xlabel("Days")
    ax.set_ylabel("Population")
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
else:
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    plot_stochastic_comparison(result_det, stoch_results, 
                               title=f"SEIR-D (Deterministic vs Stochastic - {NUM_RUNS} runs)", ax=ax)
    if use_intervention and INT_DAY:
        ax.axvline(x=INT_DAY, color="grey", linestyle=":",
                   linewidth=1.5, label=f"Intervention Day {INT_DAY}")
        ax.legend()
    st.pyplot(fig)

# ── Interpretation ─────────────────────────────────────────
st.subheader("📊 Interpretation")
r0 = result_det["R0"]
if r0 > 1:
    st.warning(f"**R₀ = {r0:.2f} > 1** — The epidemic is growing. "
               "Each infected person infects more than one other on average.")
else:
    st.success(f"**R₀ = {r0:.2f} ≤ 1** — The epidemic is under control.")

# ── Parameter Reference ────────────────────────────────────
with st.expander("📖 Parameter Reference"):
    st.markdown("""
| Parameter | Meaning                                                  |
|-----------|----------------------------------------------------------|
| **IR**    | Daily probability infected person transmits to susceptible |
| **RR**    | Fraction of Infected who recover each day                |
| **DR**    | Fraction of Infected who die each day                    |
| **σ**     | Fraction of Exposed who become Infected each day         |
| **R₀**    | IR / (RR + DR) — epidemic threshold (>1 = spreads)      |
| **Vax Rate** | % of remaining Susceptibles vaccinated per day        |
    """)

# ── Daily Data Table ───────────────────────────────────────
with st.expander("🔢 Daily Data (All Days) - Deterministic"):
    df = pd.DataFrame({
        "Day":         result_det["time"],
        "Susceptible": [round(v) for v in result_det["S"]],
        "Exposed":     [round(v) for v in result_det["E"]],
        "Infected":    [round(v) for v in result_det["I"]],
        "Recovered":   [round(v) for v in result_det["R"]],
        "Dead":        [round(v) for v in result_det["D"]],
    })
    st.dataframe(df, use_container_width=True)
