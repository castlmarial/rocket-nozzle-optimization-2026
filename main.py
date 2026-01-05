import numpy as np
import matplotlib.pyplot as plt
from rocket_utils import calculate_nozzle_dimensions
from flight_sim import simulate_flight

import numpy as np
import matplotlib.pyplot as plt
from rocket_utils import calculate_nozzle_dimensions
from flight_sim import simulate_flight

def optimize_rocket_design(h_target, m0, mp, CD_A, tb, k, epsilon, P0, P_percentage, verbose=False):
    """
    Optimizes the rocket design to achieve a target altitude.
    Returns a dictionary of design parameters and performance metrics.
    """
    if verbose:
        print(f"목표 고도 {h_target}m 도달을 위한 추력 탐색 시작...")
        print(f"연소 시간 {tb}s, 초기 질량 {m0}kg, 추진제 질량 {mp}kg 가정")
        print("\n--- [계산 결과] ---")
        print("-----------------------------------------------------")

    # 2. 목표 고도를 위한 필요 추력(F_req) 최적화 (이분법)
    F_min, F_max = 10.0, 300.0
    tol = 0.01 # 허용 오차
    iter_count = 0
    max_iter = 100
    
    F_req = 0
    h_max = 0
    
    while (F_max - F_min) > 1e-4 and iter_count < max_iter:
        iter_count += 1
        F_test = (F_min + F_max) / 2
        
        # 시뮬레이션 실행
        t, y = simulate_flight(F_test, tb, m0, mp, CD_A)
        h_max = np.max(y[0]) # 최고 고도
        
        if verbose:
            print(f"반복 {iter_count}: 테스트 추력 = {F_test:.2f} N, 도달 고도 = {h_max:.2f} m")

        if h_max > h_target:
            F_max = F_test
        else:
            F_min = F_test
            
        if abs(h_max - h_target) < tol:
            break
            
    F_req = (F_min + F_max) / 2
    
    if verbose:
        print("-----------------------------------------------------")
        print(f"도달 고도: {h_max:.2f} m")
        print(f"최적화 완료! 필요 평균 추력: {F_req:.2f} N")
        print(f"필요 총 충격량: {F_req * tb:.2f} Ns")
    
    # 3. 노즐 치수 역산
    At, dt, Ae, de, CF = calculate_nozzle_dimensions(F_req, P0, P_percentage, epsilon, k)
    
    return {
        "F_req": F_req,
        "Total Impulse": F_req * tb,
        "h_max": h_max,
        "dt": dt,
        "de": de,
        "At": At,
        "Ae": Ae,
        "CF": CF
    }

def main():
    print("--- 로켓 노즐 설계 최적화 프로그램 ---")
    
    # 1. 설계 목표 및 제약 조건
    h_target = 295.0     # [m] 목표 고도
    m0 = 3.75            # [kg] 초기 질량
    mp = 0.400           # [kg] 추진제 질량
    CD_A = 0.00264       # [m^2] 항력 계수 * 단면적
    tb = 3.05            # [s] 연소 시간
    
    # 노즐/추진제 파라미터
    k = 1.226            # 비열비    
    epsilon = 7.414      # 노즐 팽창비
    P0 = 3e6             # [Pa] 최대 압력
    P_percentage = 0.615 # 평균 압력 비율
    
    results = optimize_rocket_design(h_target, m0, mp, CD_A, tb, k, epsilon, P0, P_percentage, verbose=True)
    
    F_req = results["F_req"]
    dt = results["dt"]
    de = results["de"]
    
    print("\n--- [설계 결과] ---")
    print(f"노즐 목 직경 (dt): {dt*1000:.3f} mm")
    print(f"노즐 출구 직경 (de): {de*1000:.3f} mm")
    
    # 4. 결과 그래프 출력
    # 최종 스펙으로 시뮬레이션 한 번 더 실행
    t_final, y_final = simulate_flight(F_req, tb, m0, mp, CD_A)
    
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t_final, y_final[0], label='Altitude')
    plt.xlabel('Time (s)')
    plt.ylabel('Altitude (m)')
    plt.title(f'Flight Simulation (Max Alt: {np.max(y_final[0]):.1f}m)')
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(t_final, y_final[1], color='orange', label='Velocity')
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m/s)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()