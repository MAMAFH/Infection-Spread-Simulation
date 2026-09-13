# 🦠 SEIR-D Infection Spread Simulation

An interactive epidemiological simulation engine and Streamlit web application for modeling disease transmission, public health interventions (social distancing/lockdowns), ongoing vaccination campaigns, and mortality using the **SEIR-D** (Susceptible-Exposed-Infected-Recovered-Deceased) compartmental model.

For full mathematical models and technical architecture, see [PROJECT_DESCRIPTION.md]

---

## 📋 Prerequisites

Before installing the project, ensure you have the following installed on your system:

- **Python**: Version 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- **Git**: (Optional) For cloning the repository ([Download Git](https://git-scm.com/))
- **pip**: Python package manager (included with standard Python installations)

---

## 📥 Installation Guide

Follow these step-by-step instructions to get the project running locally on **Windows**, **macOS**, or **Linux**.

### Step 1: Obtain the Project

**Using Git:**
```bash
git clone https://github.com/MAMAFH/Infection-Spread-Simulation.git
cd Infection-Spread-Simulation
```

*Or download and extract the ZIP archive from GitHub and navigate into the extracted folder in your terminal.*

---

### Step 2: Set Up a Virtual Environment (Recommended)

Creating a virtual environment prevents dependency conflicts with other Python projects.

#### On Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Required Packages

Install all core dependencies (`matplotlib`, `numpy`, `streamlit`, `pandas`) using `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 🖥️ How to Run the Application

### 1. Launch the Interactive Web Dashboard (Streamlit)

To launch the web interface in your default browser:

```bash
streamlit run app_seird.py
```

*If `streamlit` is not recognized directly in your PATH, run:*
```bash
python -m streamlit run app_seird.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

### 2. Run Command-Line Simulation & Benchmark Scripts

- **Run Single Baseline Simulation (SEIR-D):**
  ```bash
  python main_seird.py
  ```
  *(Displays simulation metrics in terminal and opens interactive Matplotlib plots)*

- **Run Multi-Scenario Comparative Analysis:**
  ```bash
  python scenarios.py
  ```
  *(Compares Baseline vs. Daily Vaccination vs. Social Distancing and saves chart images `scenarios_full.png` and `scenarios_infected_overlay.png`)*

- **Run Sensitivity Experiments:**
  ```bash
  python experiments.py
  ```
  *(Runs sensitivity sweeps across infection rates, recovery rates, and vaccination levels)*

---

## 🛠️ Troubleshooting & FAQs

<details>
<summary><b>1. "streamlit: command not found" or "python is not recognized"</b></summary>

- Make sure your virtual environment is activated (`venv\Scripts\activate` on Windows or `source venv/bin/activate` on macOS/Linux).
- Alternatively, launch Streamlit via Python directly: `python -m streamlit run app_seird.py`.
</details>

<details>
<summary><b>2. "RR + DR must be < 1" Error</b></summary>

- The model enforces that Recovery Rate ($RR$) + Death Rate ($DR$) must sum to less than $1.0$ so that the total exit rate from the Infected compartment remains physically valid ($RR + DR < 1$). Reduce either rate if adjusting sliders.
</details>

---

## ✨ Key Features

- **SEIR-D Compartmental Engine**: Simulates Susceptible ($S$), Exposed ($E$), Infected ($I$), Recovered ($R$), and Deceased ($D$) dynamics.
- **Dual Modes**: **Deterministic** differential equations & **Stochastic** (Binomial Monte Carlo) multi-run ensembles.
- **Dynamic Interventions**: Simulates transmission drops ($IR$) starting at specified intervention days (e.g. social distancing / lockdowns).
- **Daily Vaccination Campaigns**: Models ongoing vaccination moving $S \rightarrow R$ daily.
- **Interactive Metrics & Plots**: Live $R_0$ calculation, peak infected day tracking, and daily data tables exportable to CSV/DataFrames.

---

## 📁 Project Structure

- [`app_seird.py`] — Streamlit Interactive Web Application
- [`seir_model.py`] — Core SEIR-D Simulation Engine
- [`main_seird.py`] — Command-Line Baseline Script
- [`scenarios.py`] — Multi-Scenario Comparison Script
- [`experiments.py`] — Sensitivity Analysis Benchmark Suite
- [`requirements.txt`] — Project Dependencies
- [`PROJECT_DESCRIPTION.md`] — Comprehensive Technical Documentation

---

## 📜 License

Distributed under the [Apache License 2.0].
