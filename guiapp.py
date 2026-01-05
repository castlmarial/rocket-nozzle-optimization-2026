import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from flight_sim import simulate_flight
from main import optimize_rocket_design
from main import optimize_rocket_design
from grain_design import calculate_grain_geometry

# --- Streamlit App UI ---

st.set_page_config(page_title="KNSB Rocket Simulator", layout="wide")

st.title("🚀 KNSB Solid Fuel Rocket Design & Flight Simulator")
st.markdown("Use the sidebar to input your rocket's design parameters. The app will calculate engine performance and simulate the flight to predict the apogee.")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("Design Parameters")

    st.subheader("Target Settings")
    h_target = st.number_input("Target Altitude (m)", value=295.0, format="%.1f")

    st.subheader("Rocket Specifications")
    m0 = st.number_input("Initial Total Mass (kg)", value=3.75, format="%.2f")
    mp = st.number_input("Propellant Mass (kg)", value=0.400, format="%.3f")
    CD_A = st.number_input("Drag Coefficient × Area (m²)", value=0.00264, format="%.5f")

    st.subheader("Engine/Nozzle Design")
    tb = st.number_input("Burn Time (s)", value=3.05, format="%.2f")
    k = st.number_input("Specific Heat Ratio (k)", value=1.226, format="%.3f")
    epsilon = st.number_input("Nozzle Expansion Ratio (ε)", value=7.414, format="%.3f")
    P0 = st.number_input("Max Chamber Pressure (Pa)", value=3_000_000, step=100_000, format="%d")
    P_percentage = st.number_input("Average to Max Pressure Ratio (%)", value=61.5, step=0.1, format="%.1f") / 100.0

    st.subheader("Grain Geometry Inputs")
    D_chamber_in = st.number_input("Chamber Inner Diameter (mm)", value=54.0, format="%.1f")
    t_liner_in = st.number_input("Liner/Tube Thickness (mm)", value=2.0, format="%.1f")

    st.markdown("---")
    run_button = st.button("Run Simulation", use_container_width=True)

# --- Main Panel for Results ---

if run_button:
    # Calculate performance based on inputs
    try:
        # Use optimization logic from main.py to find required thrust for target altitude
        results = optimize_rocket_design(h_target, m0, mp, CD_A, tb, k, epsilon, P0, P_percentage)
        
        F_avg = results["F_req"]
        h_max = results["h_max"]
        dt = results["dt"]
        de = results["de"]
        total_impulse = results["Total Impulse"]
        CF = results["CF"]
        
        # Run flight simulation for plotting (using the optimized thrust)
        t_sim, y_sim = simulate_flight(F_avg, tb, m0, mp, CD_A)
        
        # Recalculate other metrics for display
        v_max = np.max(y_sim[1])
        apogee_error = h_max - h_target
        P_avg = P0 * P_percentage
        m_dot = mp / tb
        I_sp = F_avg / (m_dot * 9.81)
        At = results["At"]
        grain_res = calculate_grain_geometry(
            grain_type="BATES",
            D_chamber_mm=D_chamber_in,
            t_liner_mm=t_liner_in,
            m_prop=mp,
            At=At,
            tb=tb,
            P_avg_pa=P0*P_percentage
        )

        # --- Display Results ---
        st.header("Simulation Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Predicted Apogee", f"{h_max:.1f} m", f"{apogee_error:+.1f} m vs Target")
        col2.metric("Max Velocity", f"{v_max:.1f} m/s")
        col3.metric("Average Thrust", f"{F_avg:.1f} N")

        # --- Plotting ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 1. altitude graph (left)
        ax1.plot(t_sim, y_sim[0], label='Altitude', color='dodgerblue')
        ax1.axhline(h_max, ls='--', color='gray', label=f'Apogee: {h_max:.1f} m')
        ax1.set_xlabel('Time (s)') 
        ax1.set_ylabel('Altitude (m)')
        ax1.set_title('Altitude Profile')
        ax1.grid(True)
        ax1.legend()

        # 2. velocity graph (right)
        ax2.plot(t_sim, y_sim[1], label='Velocity', color='orangered')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Velocity (m/s)')
        ax2.set_title('Velocity Profile')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig)

        # --- Detailed Performance Data ---
        st.subheader("Calculated Performance Metrics")
            
        # Display in two columns for better layout
        col_a, col_b = st.columns(2)
            
        # Left Column
        col_a.markdown(f"**Average Thrust:** `{F_avg:.2f} N`")
        col_a.markdown(f"**Total Impulse:** `{total_impulse:.2f} Ns`")
        col_a.markdown(f"**Specific Impulse:** `{I_sp:.2f} s`")
        col_a.markdown(f"**Thrust Coefficient:** `{CF:.3f}`")

        # Right Column
        col_b.markdown(f"**Avg. Chamber Pressure:** `{P_avg/1e6:.2f} MPa`")
        col_b.markdown(f"**Mass Flow Rate:** `{m_dot:.3f} kg/s`")
        col_b.markdown(f"**Nozzle Throat Diameter:** `{dt*1000:.2f} mm`")
        col_b.markdown(f"**Nozzle Exit Diameter:** `{de*1000:.2f} mm`")

        # --- Grain Geometry Results ---
        st.markdown("---")
        st.subheader("Grain Geometry Design")
        
        if "error" in grain_res:
            st.error(grain_res["error"])
        else:
            g_col1, g_col2, g_col3, g_col4 = st.columns(4)
            
            g_col1.metric("Grain Type", grain_res['Grain_Type'])
            g_col1.markdown(f"*{grain_res['Grain_Type']}*")

            g_col2.metric("Grain Outer Diameter", f"{grain_res['D_grain_mm']:.1f} mm")
            g_col2.markdown(f"*(Chamber {D_chamber_in}mm - 2x{t_liner_in}mm)*")
            
            g_col3.metric("Core Diameter", f"{grain_res['d_core_mm']:.1f} mm")
            g_col3.markdown(f"*Port Ratio: {grain_res['Port_Ratio']:.2f}*")
            
            g_col4.metric("Total Grain Length", f"{grain_res['L_grain_mm']:.1f} mm")
            g_col4.markdown(f"*L/D Ratio: {grain_res['L_over_D']:.2f}*")
            
            # errors/warnings
            st.info(f"Calculated Burn Rate: **{grain_res['r_mm_s']:.2f} mm/s** (@ {P0*P_percentage/1e6:.1f} MPa)")
            
            if grain_res['is_erosive_risk']:
                st.warning("High L/D Ratio (>6). Port Ratio has been increased to >3.0 to minimize erosive burning risks.")
            
            st.markdown(f"""
            > **Design Check:**
            > Required Burning Area ($A_b$): `{grain_res['Ab_req_m2']*10000:.2f} cm²`
            """)

    except Exception as e:
        st.error(f"An error occurred during calculation or simulation: {e}")
        st.warning("Please check your input parameters. Division by zero or invalid values can cause errors.")
else:
    st.info("Adjust the parameters in the sidebar and click **Run Simulation & Design** to see the results.")

st.markdown("---")
st.markdown(
    "Developed by PARK SEONGJAE / @castl_marial <span style='color: #FF4B4B; font-weight: bold;'>RocketDan2026 Engine Team</span> Leader", 
    unsafe_allow_html=True
)
