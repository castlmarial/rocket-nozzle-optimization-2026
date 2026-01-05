🚀 KNSB Solid Fuel Rocket Simulator & Designer. 

A comprehensive simulation tool for optimizing the design and predicting the flight performance of KNSB (Potassium Nitrate-Sorbitol) solid-fuel rockets. Users can input the target altitude and rocket specifications, and the tool reverse-engineers the necessary thrust and nozzle dimensions (Throat/Exit) while visualizing the actual flight trajectory using RK45 (Runge-Kutta) numerical analysis.

Installation & Usage
1. Clone the Repository: git clone https://github.com/your-username/rocket-sim-2026.git
2. cd rocket-sim-2026
3. Install DependenciesBashpip install -r requirements.txt
4. Run the Application: streamlit run guiapp.py
   
The simulator will launch automatically in your default web browser.
📂 File Structure📦 rocket-sim-2026
 ┣ 📜 guiapp.py          # [Main] Streamlit GUI and result reporting
 ┣ 📜 flight_sim.py      # [Physics] RK45-based rocket EOM solver
 ┣ 📜 main.py            # [Logic] Thrust optimization algorithm for target altitude
 ┣ 📜 rocket_utils.py    # [Math] Modules for ISA atmosphere, nozzle calc, and Mach number
 ┗ 📜 requirements.txt   # List of required libraries

Developer: PARK SEONGJAE RocketDan2026 Engine Team LeaderGitHub: @castl_marial
