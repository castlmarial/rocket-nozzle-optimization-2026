import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import traceback

# 모듈 임포트 (파일 이름이 정확해야 합니다)
from flight_sim import simulate_flight
from main import optimize_rocket_design
from grain_design import calculate_grain_geometry, plot_grain_geometry
from rocket_utils import isa_atmosphere

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

    # 1. Propellant Thermochemistry
    st.subheader("🧪 Propellant Properties")
    st.info("PROPEP3 결과값과 실제 측정 밀도를 입력하세요.")
    
    prop_rho = st.number_input(
        "Propellant Density (kg/m³)", 
        value=1700.0, 
        step=10.0, 
        help="실제 측정된 밀도를 권장합니다 (이론 밀도 대비 약 85~90%)."
    )
    
    c_star_input = st.number_input(
        "Characteristic Velocity C* (m/s)", 
        value=910.0, 
        step=1.0, 
        help="PROPEP3의 ft/s 결과값에 0.3048을 곱해 m/s로 변환하세요."
    )

    st.subheader("🎯 Target Settings")
    h_target = st.number_input("Target Altitude (m)", value=280.0, format="%.1f")

    st.subheader("🚀 Rocket Specifications")
    m0 = st.number_input("Initial Total Mass (kg)", value=6.00, format="%.2f")
    mp = st.number_input("Propellant Mass (kg)", value=0.400, format="%.3f")
    CD_A = st.number_input("Drag Coefficient × Area (m²)", value=0.00264, format="%.5f")

    st.subheader("🔥 Engine/Nozzle Design")
    tb = st.number_input("Burn Time (s)", value=1.5, format="%.2f")
    k_gamma = st.number_input("Specific Heat Ratio (γ)", value=1.137, format="%.3f")
    epsilon = st.number_input("Nozzle Expansion Ratio (ε)", value=5.000, format="%.3f")
    P0 = st.number_input("Max Chamber Pressure (Pa)", value=3_000_000, step=100_000, format="%d")
    P_percentage = st.number_input("Average to Max Pressure Ratio (%)", value=61.5, step=0.1, format="%.1f") / 100.0

    # [추가됨] 효율 계수 슬라이더
    st.markdown("**Efficiency Factor**")
    efficiency_factor = st.slider(
        "Total Efficiency (η)", 
        min_value=0.5, 
        max_value=1.0, 
        value=0.92, 
        step=0.01,
        help="이론 대비 실제 성능 비율입니다. (연소 효율 + 노즐 효율 + 발산 손실). 보통 0.85~0.95 사이입니다."
    )

    st.subheader("📏 Grain Geometry Inputs")
    D_chamber_in = st.number_input("Chamber Inner Diameter (mm)", value=54.0, format="%.1f")
    t_liner_in = st.number_input("Liner/Tube Thickness (mm)", value=2.0, format="%.1f")

    st.markdown("---")
    run_button = st.button("Run Simulation & Design", use_container_width=True, type="primary")

# --- Main Panel for Results ---
if run_button:
    try:
        # 1. 최적화 알고리즘 실행 (Efficiency 인자 전달)
        results = optimize_rocket_design(
            h_target, m0, mp, CD_A, tb, k_gamma, epsilon, P0, P_percentage, c_star_input, 
            efficiency=efficiency_factor # 효율 반영
        )
        
        # Dictionary Key 매핑 (대소문자 주의)
        F_avg = results["F_req"]
        h_max = results["h_max"]
        dt = results["Dt"]    # Nozzle Throat Diameter
        de = results["De"]    # Nozzle Exit Diameter
        CF = results["CF"]
        At = results["At"]
        
        # Total Impulse 직접 계산 (Target)
        target_total_impulse = F_avg * tb 

        # 2. 비행 시뮬레이션 수행
        t_sim, y_sim = simulate_flight(F_avg, tb, m0, mp, CD_A)
        
        if len(t_sim) > 0:
            idx_ap = int(np.nanargmax(y_sim[0]))
            t_apogee = float(t_sim[idx_ap])
            v_max = np.max(y_sim[1])
        else:
            t_apogee, v_max = 0.0, 0.0
        
        # 3. 그레인 형상 설계 (OpenMotor 방식 시뮬레이션 포함)
        grain_res = calculate_grain_geometry(
            D_chamber_mm=D_chamber_in,
            t_liner_mm=t_liner_in,
            m_prop=mp,
            At=At,
            tb_target=tb,
            P_avg_pa=P0 * P_percentage,
            prop_density=prop_rho,
            c_star=c_star_input,
            efficiency=efficiency_factor, # ★★★ [수정] 이 줄을 꼭 추가해주세요!
            grain_type="BATES"
        )

        # --- Display Summary Metrics ---
        st.header("📊 Simulation Results Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Predicted Apogee", f"{h_max:.1f} m", f"{h_max - h_target:+.1f} m vs Target")
        col2.metric("Max Velocity", f"{v_max:.1f} m/s")
        col3.metric("Average Thrust", f"{F_avg:.1f} N")

        # --- Plotting Flight Profiles ---
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Altitude
        axes[0,0].plot(t_sim, y_sim[0], color='dodgerblue', lw=2)
        axes[0,0].set_title('Altitude Profile (m)')
        axes[0,0].set_ylabel('Altitude (m)')
        axes[0,0].grid(True, alpha=0.3)
        
        # Velocity
        axes[0,1].plot(t_sim, y_sim[1], color='orangered', lw=2)
        axes[0,1].set_title('Velocity Profile (m/s)')
        axes[0,1].set_ylabel('Velocity (m/s)')
        axes[0,1].grid(True, alpha=0.3)
        
        # Mass Flow
        mdot_array = np.where(t_sim <= tb, mp / tb, 0.0)
        axes[1,0].plot(t_sim, mdot_array, color='seagreen', lw=2)
        axes[1,0].set_title('Mass Flow Rate (kg/s)')
        axes[1,0].set_ylabel('Mass Flow (kg/s)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Drag
        rho_arr = np.array([isa_atmosphere(max(0.0, float(h)))[0] for h in y_sim[0]])
        drag_array = 0.5 * rho_arr * CD_A * (y_sim[1] ** 2)
        axes[1,1].plot(t_sim, drag_array, color='purple', lw=2)
        axes[1,1].set_title('Drag Force (N)')
        axes[1,1].set_ylabel('Drag (N)')
        axes[1,1].grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)

        # --- Detailed Performance Data ---
        st.subheader("📋 Motor Performance Comparison")
        st.markdown("OpenMotor 등 외부 시뮬레이터와 비교할 때 아래 **Simulation Prediction** 값을 참고하세요.")
        
        c1, c2, c3 = st.columns(3)
        
        # 1. 이론적 요구사항 (Target)
        c1.markdown("#### 🎯 Requirement (Target)")
        c1.write(f"**Avg Thrust:** `{F_avg:.1f} N`")
        c1.write(f"**Total Impulse:** `{target_total_impulse:.1f} Ns`")
        c1.write(f"**Target Isp:** `{results['Isp_phys']:.1f} s`")
        
        # 2. 시뮬레이션 예측값 (Real Physics with Grain)
        c2.markdown("#### 🧪 Simulation Prediction")
        
        # grain_res에서 시뮬레이션된 실제 임펄스 가져오기
        sim_impulse = grain_res.get('sim_total_impulse', 0)
        sim_burn_time = grain_res.get('sim_burn_time', tb)
        sim_avg_thrust = sim_impulse / sim_burn_time if sim_burn_time > 0 else 0
        sim_isp = sim_impulse / (mp * 9.80665)
        
        c2.write(f"**Sim Thrust:** `{sim_avg_thrust:.1f} N`")
        c2.write(f"**Sim Impulse:** `{sim_impulse:.1f} Ns`")
        c2.write(f"**Sim Isp:** `{sim_isp:.1f} s`")

        # 3. 설계 치수 및 효율
        c3.markdown("#### 📐 Geometry & Efficiency")
        c3.write(f"**Throat (Dt):** `{dt*1000:.2f} mm`")
        c3.write(f"**Exit (De):** `{de*1000:.2f} mm`")
        c3.write(f"**Efficiency (η):** `{efficiency_factor*100:.0f}%`")
        
        # 오차 경고
        if abs(target_total_impulse - sim_impulse) > 20:
             st.warning(f"⚠️ **주의:** 설계 요구 임펄스({target_total_impulse:.0f}Ns)와 그레인 시뮬레이션 결과({sim_impulse:.0f}Ns)의 차이가 큽니다.\n"
                        f"효율 계수(Efficiency Factor)를 조절하여 두 값을 비슷하게 맞추면 더 정확한 설계를 얻을 수 있습니다.")

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

            st.info(f"**Design Note:** 목표 연소 시간({tb}s)을 맞추기 위해 시뮬레이션된 BATES 그레인의 코어 직경은 **{grain_res['d_core_mm']:.1f}mm** 입니다.")
            
            # Grain Plot (컨테이너 전달)
            plot_grain_geometry(grain_res, container=st)

    except Exception as e:
        st.error("시뮬레이션 중 오류가 발생했습니다.")
        st.code(traceback.format_exc())

st.markdown("---")
st.caption("Developed by **RocketDan2026 Engine Team Leader** | Powered by Streamlit & Python")
