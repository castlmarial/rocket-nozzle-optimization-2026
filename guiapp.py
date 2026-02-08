import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from flight_sim import simulate_flight
from main import optimize_rocket_design
from grain_design import calculate_grain_geometry, plot_grain_geometry

# --- Streamlit App UI Configuration ---
st.set_page_config(page_title="KNSB Rocket Simulator & Designer", layout="wide")

st.title("🚀 KNSB Solid Fuel Rocket Design & Flight Simulator")
st.markdown("""
이 도구는 **PROPEP3**의 화학 평형 데이터와 **RK45 수치 해석**을 결합하여 고체 로켓의 성능을 예측합니다.
사이드바에서 파라미터를 입력하고 'Run Simulation'을 클릭하세요.
""")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("🛠️ Design Parameters")

    # 1. Propellant Thermochemistry (PROPEP3 기반 데이터)
    st.subheader("🧪 Propellant Properties (from PROPEP3)")
    st.info("PROPEP3 결과값과 실제 측정 밀도를 입력하세요.")
    
    # 실제 측정 밀도 (약 1.6g/cm^3 -> 1600kg/m^3)
    prop_rho = st.number_input(
        "Propellant Density (kg/m³)", 
        value=1600.0, 
        step=10.0, 
        help="실제 측정된 밀도를 권장합니다 (이론 밀도 대비 약 85~90%)."
    )
    
    # C* (PROPEP3 ft/s 단위를 m/s로 변환하여 입력)
    c_star_input = st.number_input(
        "Characteristic Velocity C* (m/s)", 
        value=910.0, 
        step=1.0, 
        help="PROPEP3의 ft/s 결과값에 0.3048을 곱해 m/s로 변환하세요."
    )

    st.subheader("🎯 Target Settings")
    h_target = st.number_input("Target Altitude (m)", value=295.0, format="%.1f")

    st.subheader("🚀 Rocket Specifications")
    m0 = st.number_input("Initial Total Mass (kg)", value=3.75, format="%.2f")
    mp = st.number_input("Propellant Mass (kg)", value=0.400, format="%.3f")
    CD_A = st.number_input("Drag Coefficient × Area (m²)", value=0.00264, format="%.5f")

    st.subheader("🔥 Engine/Nozzle Design")
    tb = st.number_input("Burn Time (s)", value=3.05, format="%.2f")
    k_gamma = st.number_input("Specific Heat Ratio (γ)", value=1.137, format="%.3f", help="PROPEP3의 Chamber CP/CV 값")
    epsilon = st.number_input("Nozzle Expansion Ratio (ε)", value=7.414, format="%.3f")
    P0 = st.number_input("Max Chamber Pressure (Pa)", value=3_000_000, step=100_000, format="%d")
    P_percentage = st.number_input("Average to Max Pressure Ratio (%)", value=61.5, step=0.1, format="%.1f") / 100.0

    st.subheader("📏 Grain Geometry Inputs")
    D_chamber_in = st.number_input("Chamber Inner Diameter (mm)", value=54.0, format="%.1f")
    t_liner_in = st.number_input("Liner/Tube Thickness (mm)", value=2.0, format="%.1f")

    st.markdown("---")
    run_button = st.button("Run Simulation & Design", use_container_width=True, type="primary")

# --- Main Panel for Results ---
if run_button:
    try:
        # 1. 최적화 알고리즘 실행 (필요 추력 및 노즐 목 계산)
        # k_gamma를 k 인자로 전달
        results = optimize_rocket_design(h_target, m0, mp, CD_A, tb, k_gamma, epsilon, P0, P_percentage)
        
        F_avg = results["F_req"]
        h_max = results["h_max"]
        dt = results["dt"]
        de = results["de"]
        total_impulse = results["Total Impulse"]
        CF = results["CF"]
        At = results["At"]

        # 2. RK45 기반 비행 시뮬레이션 수행
        t_sim, y_sim = simulate_flight(F_avg, tb, m0, mp, CD_A)
        
        # 도달 시간 계산
        if len(t_sim) > 0:
            idx_ap = int(np.nanargmax(y_sim[0]))
            t_apogee = float(t_sim[idx_ap])
            v_max = np.max(y_sim[1])
        else:
            t_apogee, v_max = 0.0, 0.0
        
        # 3. 그레인 형상 설계 계산 (수정된 밀도 및 C* 반영)
        grain_res = calculate_grain_geometry(
            D_chamber_mm=D_chamber_in,
            t_liner_mm=t_liner_in,
            m_prop=mp,
            At=At,
            tb=tb,
            P_avg_pa=P0 * P_percentage,
            prop_density=prop_rho,
            c_star=c_star_input,
            grain_type="BATES"
        )

        # --- Display Summary Metrics ---
        st.header("📊 Simulation Results Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Predicted Apogee", f"{h_max:.1f} m", f"{h_max - h_target:+.1f} m vs Target")
        col2.metric("Max Velocity", f"{v_max:.1f} m/s")
        col3.metric("Average Thrust", f"{F_avg:.1f} N")

        # --- Plotting Flight Profiles ---
        from rocket_utils import isa_atmosphere
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Altitude
        axes[0,0].plot(t_sim, y_sim[0], color='dodgerblue', lw=2)
        axes[0,0].set_title('Altitude Profile (m)')
        axes[0,0].grid(True, alpha=0.3)
        
        # Velocity
        axes[0,1].plot(t_sim, y_sim[1], color='orangered', lw=2)
        axes[0,1].set_title('Velocity Profile (m/s)')
        axes[0,1].grid(True, alpha=0.3)
        
        # Mass Flow
        mdot_array = np.where(t_sim <= tb, mp / tb, 0.0)
        axes[1,0].plot(t_sim, mdot_array, color='seagreen', lw=2)
        axes[1,0].set_title('Mass Flow Rate (kg/s)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Drag
        rho_arr = np.array([isa_atmosphere(max(0.0, float(h)))[0] for h in y_sim[0]])
        drag_array = 0.5 * rho_arr * CD_A * (y_sim[1] ** 2)
        axes[1,1].plot(t_sim, drag_array, color='purple', lw=2)
        axes[1,1].set_title('Drag Force (N)')
        axes[1,1].grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)

        # --- Detailed Performance Data ---
        st.subheader("📋 Motor & Nozzle Performance")
        c_a, c_b = st.columns(2)
        with c_a:
            st.write(f"**Total Impulse:** `{total_impulse:.2f} Ns`")
            st.write(f"**Specific Impulse (Isp):** `{F_avg / ( (mp/tb) * 9.81 ):.2f} s`")
            st.write(f"**Thrust Coefficient (CF):** `{CF:.3f}`")
        with c_b:
            st.write(f"**Throat Diameter:** `{dt*1000:.2f} mm` (Graphite Insert)")
            st.write(f"**Exit Diameter:** `{de*1000:.2f} mm` (Al6061 Housing)")
            st.write(f"**Characteristic Velocity (C*):** `{c_star_input:.1f} m/s` (Input)")

        # --- Grain Geometry Visualization ---
        st.markdown("---")
        st.subheader("📐 Grain Geometry Design (BATES)")
        
        if "error" in grain_res:
            st.error(grain_res["error"])
        else:
            g1, g2, g3 = st.columns(3)
            g1.metric("Grain OD", f"{grain_res['D_grain_mm']:.1f} mm")
            g2.metric("Core Diameter", f"{grain_res['d_core_mm']:.1f} mm")
            g3.metric("Length", f"{grain_res['L_grain_mm']:.1f} mm")

            st.info(f"**Design Note:** 사용된 밀도 {grain_res['rho_used']}kg/m³ 기준, 목표 압력 유지를 위한 연소율은 **{grain_res['r_mm_s']:.2f} mm/s** 입니다.")
            
            if grain_res['is_erosive_risk']:
                st.warning("⚠️ L/D 비율이 6을 초과하여 침식 연소 위험이 있습니다. Port Ratio가 3.0으로 상향 조정되었습니다.")

            # Grain Plot
            fig_grain = plot_grain_geometry(grain_res)
            st.pyplot(fig_grain)

    except Exception as e:
        st.error(f"시뮬레이션 중 오류가 발생했습니다: {e}")

st.markdown("---")
st.caption(f"Developed by **{st.get_option('server.baseUrlPath') or 'PARK SEONGJAE'}** | RocketDan2026 Engine Team Leader")
