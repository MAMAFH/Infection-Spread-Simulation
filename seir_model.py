"""
============================================================
  seir_model.py — SEIR-D Epidemic Simulation Engine
  Compartments: Susceptible, Exposed, Infected, Recovered, Dead
  Course: System Modeling and Simulation
============================================================

  Discrete-time transitions each day:
  ─────────────────────────────────────────────────────────
    new_exposed    = IR  × (I/N) × S       [S → E]
    new_infectious = sigma × E             [E → I]
    new_recoveries = RR  × I               [I → R]
    new_deaths     = DR  × I               [I → D]
  ─────────────────────────────────────────────────────────

  KEY MODELING RULE — No Double Counting:
    Infected leave the I compartment via TWO paths:
      → recovery  (rate RR per day)
      → death     (rate DR per day)
    Total leaving I = (RR + DR) × I
    We subtract BOTH from I, so RR and DR must sum to < 1.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


# ──────────────────────────────────────────────────────────
#  CORE SEIR-D SIMULATION FUNCTION
# ──────────────────────────────────────────────────────────

def simulate_seird(
    N: int,
    E0: int,
    I0: int,
    IR: float,
    RR: float,
    DR: float,
    sigma: float,
    days: int,
    # --- Time-varying infection rate ---
    intervention_day: int   = None,   # day on which IR drops
    IR_reduced: float       = None,   # IR value after intervention
    # --- Ongoing vaccination ---
    vaccination_rate: float = 0.0,    # fraction of S vaccinated per day
    # --- Simulation mode ---
    mode: str = "deterministic",      # "deterministic" or "stochastic"
) -> dict:
    """
    Run a discrete-time SEIR-D simulation.

    Parameters
    ----------
    N                : Total population
    E0               : Initially exposed (not yet infectious)
    I0               : Initially infectious
    IR               : Infection rate — daily probability of S→E per contact
    RR               : Recovery rate  — fraction of I who recover per day
    DR               : Death rate     — fraction of I who die per day
                       ⚠ RR + DR must be < 1 to be physically meaningful
    sigma            : Incubation rate — fraction of E who become I per day
                       (1/sigma = average incubation period in days)
    days             : Simulation length in days
    intervention_day : Day when IR changes (None = no intervention)
    IR_reduced       : IR value after intervention_day
    vaccination_rate : Fraction of remaining S vaccinated per day (0–1)

    Returns
    -------
    dict with time-series lists S, E, I, R, D, time
    and scalar metrics: peak_infected, peak_day,
                        total_recovered, total_dead, R0
    """

    # ── Validate rates ──────────────────────────────────────
    if RR + DR >= 1.0:
        raise ValueError(
            f"RR ({RR}) + DR ({DR}) = {RR+DR:.2f} must be < 1. "
            "Reduce recovery or death rate."
        )

    # ── Initial conditions ──────────────────────────────────
    S0 = max(N - E0 - I0, 0)
    R0_init = 0
    D0 = 0

    S_list = [float(S0)]
    E_list = [float(E0)]
    I_list = [float(I0)]
    R_list = [float(R0_init)]
    D_list = [float(D0)]
    time   = list(range(days + 1))
    
    # Random number generator for stochastic mode
    rng = np.random.default_rng()

    # ── Daily simulation loop ───────────────────────────────
    for day in range(days):

        S = S_list[-1]
        E = E_list[-1]
        I = I_list[-1]
        R = R_list[-1]
        D = D_list[-1]

        # ── Time-varying IR (intervention) ──────────────────
        current_IR = IR
        if intervention_day is not None and IR_reduced is not None:
            if day >= intervention_day:
                current_IR = IR_reduced

        if mode == "deterministic":
            # ── Daily vaccination: moves S → R ──────────────────
            vaccinated_today = vaccination_rate * S
            vaccinated_today = min(vaccinated_today, S)   # can't vaccinate more than S

            # ── Transitions ─────────────────────────────────────
            #   [S → E]  new exposures
            new_exposed    = current_IR * (I / N) * S

            #   [E → I]  end of incubation
            new_infectious = sigma * E

            #   [I → R]  recovery
            new_recoveries = RR * I

            #   [I → D]  death
            #   ⚠ Both new_recoveries AND new_deaths are subtracted from I.
            #     This is intentional — they represent two separate exit paths.
            new_deaths     = DR * I
            
        elif mode == "stochastic":
            # ── Daily vaccination: moves S → R ──────────────────
            vaccinated_today = rng.binomial(int(S), min(vaccination_rate, 1.0))
            
            # ── Transitions ─────────────────────────────────────
            #   [S → E]  new exposures
            infection_probability = current_IR * (I / N)
            infection_probability = min(max(infection_probability, 0.0), 1.0)
            # Sample from the S pool that wasn't just vaccinated
            new_exposed = rng.binomial(max(int(S) - vaccinated_today, 0), infection_probability)
            
            #   [E → I]  end of incubation
            new_infectious = rng.binomial(int(E), min(sigma, 1.0))
            
            #   [I → R]  recovery
            new_recoveries = rng.binomial(int(I), min(RR, 1.0))
            
            #   [I → D]  death
            # Deaths are sampled from those who did not recover today
            new_deaths = rng.binomial(max(int(I) - new_recoveries, 0), min(DR, 1.0))
        else:
            raise ValueError("mode must be 'deterministic' or 'stochastic'")

        # ── Update compartments ─────────────────────────────
        S_new = S - new_exposed - vaccinated_today
        E_new = E + new_exposed - new_infectious
        I_new = I + new_infectious - new_recoveries - new_deaths
        R_new = R + new_recoveries + vaccinated_today
        D_new = D + new_deaths

        # Clamp to avoid floating-point drift below zero
        S_new = max(S_new, 0.0)
        E_new = max(E_new, 0.0)
        I_new = max(I_new, 0.0)
        R_new = max(R_new, 0.0)

        S_list.append(S_new)
        E_list.append(E_new)
        I_list.append(I_new)
        R_list.append(R_new)
        D_list.append(D_new)

    # ── Compute metrics ─────────────────────────────────────
    peak_infected   = max(I_list)
    peak_day        = I_list.index(peak_infected)
    total_recovered = R_list[-1]
    total_dead      = D_list[-1]

    # Basic reproduction number (without time-varying adjustment)
    R0 = IR / (RR + DR)

    return {
        "S":              S_list,
        "E":              E_list,
        "I":              I_list,
        "R":              R_list,
        "D":              D_list,
        "time":           time,
        "peak_infected":  peak_infected,
        "peak_day":       peak_day,
        "total_recovered":total_recovered,
        "total_dead":     total_dead,
        "R0":             R0,
        "N":              N,
    }


# ──────────────────────────────────────────────────────────
#  PLOTTING HELPER
# ──────────────────────────────────────────────────────────

# Colour palette — consistent across all plots
COLOURS = {
    "S": "#3a86ff",   # blue
    "E": "#fb8500",   # orange
    "I": "#ff006e",   # red/pink
    "R": "#06d6a0",   # teal
    "D": "#8338ec",   # purple
}


def plot_seird(result: dict, title: str = "SEIR-D Simulation", ax=None):
    """
    Plot S, E, I, R, D curves.

    Parameters
    ----------
    result     : dict returned by simulate_seird()
    title      : chart title
    ax         : matplotlib Axes (optional; creates figure if None)
    """
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(11, 5))

    for key in ("S", "E", "I", "R", "D"):
        ax.plot(result["time"], result[key],
                label=key, color=COLOURS[key], linewidth=2)

    # Mark peak infection
    ax.axvline(x=result["peak_day"], color=COLOURS["I"],
               linestyle="--", alpha=0.5, linewidth=1.2)
    ax.annotate(
        f"Peak {result['peak_infected']:,.0f}\n(Day {result['peak_day']})",
        xy=(result["peak_day"], result["peak_infected"]),
        xytext=(result["peak_day"] + 2, result["peak_infected"] * 0.92),
        fontsize=8, color=COLOURS["I"],
    )

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Days")
    ax.set_ylabel("Population")
    ax.legend(loc="upper right")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(alpha=0.3)

    if standalone:
        plt.tight_layout()
        plt.show()


def plot_infected_comparison(scenarios: dict, title: str = "Scenario Comparison"):
    """
    Overlay the Infected (I) curve from multiple scenarios on one chart.

    Parameters
    ----------
    scenarios : dict of {label: result_dict}
    title     : chart title
    """
    palette = ["#ff006e", "#3a86ff", "#06d6a0", "#fb8500", "#8338ec"]

    fig, ax = plt.subplots(figsize=(11, 6))
    for (label, result), colour in zip(scenarios.items(), palette):
        ax.plot(result["time"], result["I"],
                label=label, color=colour, linewidth=2.5)

    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Days")
    ax.set_ylabel("Infected Population")
    ax.legend()
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


# ──────────────────────────────────────────────────────────
#  METRICS PRINTER
# ──────────────────────────────────────────────────────────

def print_metrics(result: dict, label: str = ""):
    """Print a formatted summary of key simulation metrics."""
    sep = "─" * 50
    print(f"\n{sep}")
    if label:
        print(f"  Scenario        : {label}")
    print(f"  Population (N)  : {result['N']:,}")
    print(f"  Basic R₀        : {result['R0']:.2f}  (>1 = epidemic grows)")
    print(f"  Peak Infected   : {result['peak_infected']:>12,.0f}  (Day {result['peak_day']})")
    print(f"  Total Recovered : {result['total_recovered']:>12,.0f}")
    print(f"  Total Deaths    : {result['total_dead']:>12,.0f}")

    # Population conservation check
    last_total = (result['S'][-1] + result['E'][-1] +
                  result['I'][-1] + result['R'][-1] + result['D'][-1])
    conservation_ok = abs(last_total - result['N']) < 1.0
    print(f"  Conservation    : {'✓ OK' if conservation_ok else '✗ ERROR'}")
    print(sep)

# ──────────────────────────────────────────────────────────
#  STOCHASTIC HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────

def simulate_multiple_stochastic(
    N: int, E0: int, I0: int, IR: float, RR: float, DR: float, sigma: float,
    days: int, intervention_day: int = None, IR_reduced: float = None,
    vaccination_rate: float = 0.0, num_runs: int = 5
) -> list:
    """Run the stochastic simulation multiple times."""
    runs = []
    for _ in range(num_runs):
        runs.append(simulate_seird(N, E0, I0, IR, RR, DR, sigma, days,
                                   intervention_day, IR_reduced, vaccination_rate,
                                   mode="stochastic"))
    return runs

def plot_stochastic_comparison(det_result: dict, stoch_results: list, title: str = "Deterministic vs Stochastic SEIR-D", ax=None):
    """Plot deterministic result as a smooth curve and multiple stochastic runs on the same graph."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(11, 6))

    # Plot deterministic
    for key in ("S", "E", "I", "R", "D"):
        ax.plot(det_result["time"], det_result[key],
                label=f"{key} (Det)", color=COLOURS[key], linewidth=3.5, zorder=10)

    # Plot stochastic
    for i, res in enumerate(stoch_results):
        for key in ("S", "E", "I", "R", "D"):
            # Only label the first stochastic run to avoid cluttering the legend
            lbl = f"{key} (Stoch)" if i == 0 else ""
            ax.plot(res["time"], res[key],
                    color=COLOURS[key], alpha=0.35, linewidth=1.5, label=lbl)

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Days")
    ax.set_ylabel("Population")
    
    # Simplify legend to avoid duplicates
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper right")
    
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(alpha=0.3)

    if standalone:
        plt.tight_layout()
        plt.show()
