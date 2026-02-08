import numpy as np
import matplotlib.pyplot as plt
from rocket_utils import calculate_nozzle_dimensions
from flight_sim import simulate_flight

def optimize_rocket_design(h_target, m0, mp, CD_A, tb, k, epsilon, P0, P_percentage, c_star, verbose=False):
    """
    목표 고도 달성을 위해 필요한 추력을 찾고, 물리적 Isp 기반 노즐 설계를 수행합니다.
    """
    if verbose:
        print(f"목표 고도 {h_target}m 도달을 위한 추력 탐색 시작 (C*: {c_star} m/s)...")

    # 1. 목표 고도를 위한 필요 추력(F_req) 최적화 (이분법)
    F_min, F_max = 10.0, 500.0
    tol = 0.01 
    iter_count = 0
    max_iter = 100
    
    F_req = 0
    h_max = 0
    
    while (F_max - F_min) > 1e-4 and iter_count < max_iter:
        iter_count += 1
        F_test = (F_min + F_max) / 2
        
        # 시뮬레이션 실행 (flight_sim.py 내부 시뮬레이션 로직 사용)
        t, y = simulate_flight(F_test, tb, m0, mp, CD_A)
        h_max = np.max(y[0]) 
        
        if h_max > h_target:
            F_max = F_test
        else:
            F_min = F_test
            
        if abs(h_max - h_target) < tol:
            break
            
    F_req = (F_min + F_max) / 2
    
    # 2. 노즐 치수 및 물리적 Isp 역산
    At, dt, Ae, de, CF, isp_phys = calculate_nozzle_dimensions(F_req, P0, P_percentage, epsilon, k, c_star)
    
    return {
        "F_req": F_req,
        "Total Impulse": F_req * tb,
        "h_max": h_max,
        "dt": dt,
        "de": de,
        "At": At,
        "Ae": Ae,
        "CF": CF,
        "Isp_phys": isp_phys
    }

def main():
    print("--- [RocketDan2026] 로켓 노즐 설계 최적화 프로그램 ---")
    
    # 설계 목표 및 제약 조건
    h_target = 295.0     # [m] 목표 고도
    m0 = 3.75            # [kg] 초기 질량
    mp = 0.400           # [kg] 추진제 질량
    CD_A = 0.00264       # [m^2] 항력 계수 * 단면적
    tb = 3.05            # [s] 연소 시간
    
    # PROPEP3 기반 파라미터 적용
    c_star = 909.8       # [m/s] 특성 속도 (2984.9 ft/s 변환값)
    k = 1.1376           # 비열비 (Chamber CP/CV)
    epsilon = 7.414      # 노즐 팽창비
    P0 = 3e6             # [Pa] 최대 압력 (3MPa)
    P_percentage = 0.615 # 평균 압력 비율
    
    results = optimize_rocket_design(h_target, m0, mp, CD_A, tb, k, epsilon, P0, P_percentage, c_star, verbose=True)
    
    # 결과 출력
    print("\n--- [설계 결과 리포트] ---")
    print(f"1. 목표 고도 도달: {results['h_max']:.2f} m")
    print(f"2. 필요 평균 추력: {results['F_req']:.2f} N")
    print(f"3. 물리적 비추력 (Isp): {results['Isp_phys']:.2f} s")
    print(f"4. 노즐 목 직경 (dt): {results['dt']*1000:.2f} mm (그래파이트 인서트)")
    print(f"5. 노즐 출구 직경 (de): {results['de']*1000:.2f} mm (Al6061 하우징)")
    
    # 결과 그래프 출력 (최종 스펙 시뮬레이션)
    t_final, y_final = simulate_flight(results["F_req"], tb, m0, mp, CD_A)
    
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t_final, y_final[0], label='Altitude')
    plt.ylabel('Altitude (m)')
    plt.title(f'Flight Simulation (Apogee: {np.max(y_final[0]):.1f}m)')
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(t_final, y_final[1], color='orange', label='Velocity')
    plt.ylabel('Velocity (m/s)')
    plt.xlabel('Time (s)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
