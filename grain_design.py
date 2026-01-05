import numpy as np

# --- KNSB Propellant Properties (Typical Values) ---
# 출처: Richard Nakka's Experimental Rocketry (KNSB)
KNSB_PROPS = {
    'density': 1641.0,      # [kg/m^3] 밀도 
    'c_star': 895.0,        # [m/s] 특성배기속도
    'a': 8.26e-3,           # [m/s per MPa^n] 연소속도 계수 (a) - 주의: 단위 변환됨
    'n': 0.319              # [] 연소속도 지수 (n)
}

def calculate_grain_geometry(D_chamber_mm, t_liner_mm, m_prop, At, tb, P_avg_pa, grain_type="BATES"):
    """
    사용자의 알고리즘에 따라 그레인 형상(BATES)을 설계하는 함수
    
    :param D_chamber_mm: 챔버 내경 (mm)
    :param t_liner_mm: 지관(라이너) 두께 (mm)
    :param m_prop: 추진제 질량 (kg) - main.py 최적화 결과
    :param At: 노즐 목 단면적 (m^2) - main.py 최적화 결과
    :param tb: 연소 시간 (s)
    :param P_avg_pa: 평균 챔버 압력 (Pa)
    """
    
    # 단위 변환 (mm -> m)
    D_chamber = D_chamber_mm / 1000.0
    t_liner = t_liner_mm / 1000.0
    
    # -----------------------------------------------------------
    # 1) & 2) 평균 질량 유량 계산 (Mass Flow Rate)
    # mdot = m_prop / t_burn
    # -----------------------------------------------------------
    mdot = m_prop / tb
    
    # -----------------------------------------------------------
    # 3) 연소실 압력 및 특성배기속도 확인
    # P_c = (mdot * c*) / At
    # 입력받은 P_avg_pa가 있지만, 물리적 정합성을 위해 KNSB c*로 역산하여 검증하거나 사용
    # 여기서는 KNSB 표준 c*를 사용해 이론적 요구 압력을 계산해봄 (참고용)
    # -----------------------------------------------------------
    c_star = KNSB_PROPS['c_star']
    Pc_calc = (mdot * c_star) / At
    
    # 설계 기준 압력은 사용자가 입력/설정한 P_avg_pa를 우선하되, 
    # 연소속도 계산 시에는 실제 물리 현상을 반영하기 위해 P_avg_pa(설계치)를 사용합니다.
    
    # -----------------------------------------------------------
    # 4) 연소속도 r 계산 (Vielle's Law)
    # r = a * P^n
    # -----------------------------------------------------------
    a = KNSB_PROPS['a'] # 단위: m/s per MPa^n
    n = KNSB_PROPS['n']
    
    # 압력 단위를 MPa로 변환하여 적용
    P_mpa = P_avg_pa / 1e6
    r = a * (P_mpa ** n) # [m/s]
    
    # -----------------------------------------------------------
    # 5) 필요 연소면적 Ab 계산
    # Ab = mdot / (density * r)
    # -----------------------------------------------------------
    rho = KNSB_PROPS['density']
    Ab_req = mdot / (rho * r)
    
    # -----------------------------------------------------------
    # 6) 형상 치수 결정 (BATES Grain)
    # -----------------------------------------------------------
    
    # 6-1. 그레인 외경 (D_grain)
    D_grain = D_chamber - (2 * t_liner)
    if D_grain <= 0:
        return {"error": "지관 두께가 챔버 내경보다 큽니다."}

    # 6-2. 포트 비율(Port Ratio) 고려한 코어 지름(d_core) 설정
    # Port Ratio = A_port / At >= 2.0
    # A_port = pi * d_core^2 / 4
    # 즉, d_core >= sqrt( (2.0 * At * 4) / pi )
    
    min_port_ratio = 2.0
    d_core_min = np.sqrt((min_port_ratio * At * 4) / np.pi)
    
    # 초기 설정: 최소 포트 비율에 딱 맞춤
    d_core = d_core_min
    
    # 6-3. 질량 보존 법칙으로 그레인 길이(L) 역산
    # m_prop = rho * V_prop
    # V_prop = Area_cross * L = (pi/4 * (D_grain^2 - d_core^2)) * L
    # L = m_prop / (rho * pi/4 * (D_grain^2 - d_core^2))
    
    A_cross = (np.pi / 4) * (D_grain**2 - d_core**2)
    L_grain = m_prop / (rho * A_cross)
    
    # 6-4. L/D 비율 체크 및 침식 연소(Erosive Burning) 고려 보정
    # 조건: L/D > 6 이면, Port Ratio는 2보다 더 커야 함 (안전을 위해 3.0으로 상향 조정 로직 예시)
    L_over_D = L_grain / D_grain
    
    is_erosive_risk = False
    if L_over_D > 6.0:
        is_erosive_risk = True
        # 침식 연소 방지를 위해 포트 비율을 2.0 -> 3.0으로 증가시켜 재계산
        target_port_ratio = 3.0
        d_core_erosive = np.sqrt((target_port_ratio * At * 4) / np.pi)
        
        # 코어가 커지면 부피가 줄어드므로 길이는 더 길어져야 함 (반복 계산 필요 없음, 수식 대입)
        d_core = d_core_erosive
        A_cross = (np.pi / 4) * (D_grain**2 - d_core**2)
        L_grain = m_prop / (rho * A_cross)
        
        # 재계산된 L/D 업데이트
        L_over_D = L_grain / D_grain

    # 최종 포트 비율 계산
    A_port = (np.pi / 4) * (d_core**2)
    final_port_ratio = A_port / At

    # -----------------------------------------------------------
    # 결과 반환
    # -----------------------------------------------------------
    return {
        "Grain_Type": grain_type,
        "D_grain_mm": D_grain * 1000,
        "d_core_mm": d_core * 1000,
        "L_grain_mm": L_grain * 1000,
        "L_over_D": L_over_D,
        "Port_Ratio": final_port_ratio,
        "Ab_req_m2": Ab_req,
        "r_mm_s": r * 1000,
        "mdot_kg_s": mdot,
        "is_erosive_risk": is_erosive_risk,
        "density_used": rho
    }