# 🚀 KNSB Solid Fuel Rocket Simulator & Designer

A comprehensive inverse-design simulation tool for optimizing **KNSB
(Potassium Nitrate--Sorbitol)** solid rocket motors and predicting
real-flight performance using high-accuracy numerical integration.

This simulator automatically determines the **required thrust, nozzle
dimensions (Throat/Exit), and grain geometry** to reach a target
altitude --- while visualizing the full flight trajectory using RK45
(Runge--Kutta) integration.

------------------------------------------------------------------------

## 📌 Overview

This project implements a full-stack rocket design workflow:

-   🎯 Target altitude input\
-   🔍 Required thrust optimization (Binary Search)\
-   🔥 Internal ballistics simulation\
-   🚀 Nozzle dimension calculation\
-   📈 RK45-based flight trajectory analysis\
-   🖥 Interactive Streamlit GUI

The system performs **inverse rocket motor design**, meaning it starts
from mission requirements and derives the physical engine configuration
needed to achieve them.

------------------------------------------------------------------------

## ✨ Key Features

### 🚀 Trajectory Optimization

Automatically determines the optimal average thrust required to reach
the target altitude.

### 🔥 Internal Ballistics Simulation

Simulates chamber pressure variation and thrust profile during
combustion.

### 📐 Nozzle Design

Computes: - Throat area (Aₜ) - Exit area (Aₑ) - Exit Mach number (Mₑ) -
Expansion ratio\
Including efficiency corrections for realistic performance.

### 🔵 BATES Grain Geometry Optimization

Determines: - Core diameter\
- Grain length\
- Required propellant mass

Based on burn-time constraints and chamber pressure evolution.

### 📊 Interactive Visualization

Streamlit-based interface with: - Altitude / Velocity plots\
- Drag profile\
- Chamber pressure curve\
- Grain cross-section visualization

------------------------------------------------------------------------

## 🛠 Tech Stack

  Category               Technology
  ---------------------- -------------------------------
  Language               Python 3.x
  Numerical Methods      SciPy (`solve_ivp`, `fsolve`)
  Scientific Computing   NumPy
  Visualization          Matplotlib
  UI Framework           Streamlit

------------------------------------------------------------------------

## 📂 Project Structure

    📦 rocket-sim-2026
     ┣ 📜 guiapp.py          # [Main] Streamlit GUI & result reporting
     ┣ 📜 flight_sim.py      # [Physics] RK45-based EOM solver
     ┣ 📜 main.py            # [Logic] Thrust optimization algorithm
     ┣ 📜 rocket_utils.py    # [Math] ISA atmosphere, nozzle, Mach calc
     ┣ 📜 grain_design.py    # [Math] BATES grain optimization
     ┗ 📜 requirements.txt   # Dependencies

------------------------------------------------------------------------

## 🚀 Installation & Usage

### 1️⃣ Clone Repository

``` bash
git clone https://github.com/your-username/rocket-sim-2026.git
cd rocket-sim-2026
```

### 2️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```

### 3️⃣ Run Application

``` bash
streamlit run guiapp.py
```

The simulator will automatically open in your default browser.

------------------------------------------------------------------------

## 🌐 Streamlit Cloud Version

https://rocket-nozzle-optimization-2026-kvkgsfa3gmgqz3uyopn9bs.streamlit.app/

------------------------------------------------------------------------

# 📐 Mathematical Framework

## Equation of Motion

F_net = F_thrust - D - mg

## Nozzle Performance Equation

F = P_c A_t C_F η

## Atmospheric Model

Based on ISA (International Standard Atmosphere)\
Altitude-dependent density and pressure variation included in drag
computation.

------------------------------------------------------------------------

# 🧠 Simulation Workflow

## Step 1: Required Thrust Optimization

-   Binary Search algorithm
-   RK45 numerical integration
-   Includes drag, gravity, and mass depletion

## Step 2: Nozzle Dimensioning

-   Exit Mach number calculation
-   Expansion ratio derivation
-   Throat & exit area computation

## Step 3: Internal Ballistics & Grain Design

-   Time-varying burn area
-   Chamber pressure update per timestep
-   BATES grain geometry optimization

## Step 4: Visualization

-   Altitude vs Time
-   Velocity vs Time
-   Drag vs Time
-   Chamber pressure vs Time
-   Grain geometry cross-section

------------------------------------------------------------------------

# 👨‍🚀 Developer

PARK SEONGJAE\
RocketDan2026 Engine Team Leader\
GitHub: @castl_marial

------------------------------------------------------------------------

# 📜 License

This project is intended for educational and simulation purposes.
