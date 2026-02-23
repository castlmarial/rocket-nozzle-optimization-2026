import numpy as np
import matplotlib.pyplot as plt
from rocket_utils import calculate_nozzle_dimensions
from flight_sim import simulate_flight

def optimize_rocket_design(h_target, m0, mp, CD_A, tb, k, epsilon, P0, P_percentage, c_star, efficiency=0.92, verbose=False):
    """
    efficiency 인자 추가: 노즐 및 연소 효율 (0.0 ~ 1.0)
    """
    if verbose:
        print(f"목표 고도 {h_target}m 도달을 위한 추력 탐색 시작 (Eff: {efficiency})...")

    # 1. 목표 고도를 위한 필요 추력(F_req) 최적화
    # 주의: 여기서 F_test는 '실제 발휘해야 하는 추력'입니다.
    # 시뮬레이션은 F_test 물리량을 그대로 쓰므로 여기선 수정 불필요
    F_min, F_max = 10.0, 1000.0
    F_req = 0
    h_max = 0
    iter_count = 0
    
    while iter_count < 50:
        iter_count += 1
        F_test = (F_min + F_max) / 2
        
        t, y = simulate_flight(F_test, tb, m0, mp, CD_A)
        h_current = np.max(y[0])
        
        if abs(h_current - h_target) < 1.0:
            F_req = F_test
            h_max = h_current
            break
        
        if h_current < h_target:
            F_min = F_test
        else:
            F_max = F_test
            
    F_req = (F_min + F_max) / 2
    
    # 2. 노즐 설계 치수 계산 (효율 반영)
    # F_req를 내기 위해, 효율이 낮으면 노즐 목(At)을 키웁니다.
    nozzle_dim = calculate_nozzle_dimensions(F_req, P0, P_percentage, epsilon, k, c_star, efficiency)
    
    # 3. Isp 계산 (실제 출력 기준)
    g0 = 9.80665
    m_dot = mp / tb
    Isp_phys = F_req / (m_dot * g0)

    results = {
        "F_req": F_req,
        "h_max": h_max,
        "Isp_phys": Isp_phys,
        "At": nozzle_dim['At'],
        "Dt": nozzle_dim['Dt'],
        "Ae": nozzle_dim['Ae'],
        "De": nozzle_dim['De'],
        "CF": nozzle_dim['CF'],
        "m_dot": m_dot
    }
    
    return results
