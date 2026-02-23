import numpy as np
from scipy.optimize import fsolve

def isa_atmosphere(h):
    """ISA standard atmosphere model"""
    if 0 <= h < 11000:
        T = 288.15 - 0.0065 * h
        Pa = 101325 * (T / 288.15)**5.2561
        rho = Pa / (287.05 * T)
    elif h >= 11000:
        T_11km = 216.65
        Pa_11km = 22632
        rho = Pa_11km / (287.05 * T_11km) * np.exp(-9.80665 * (h - 11000) / (287.05 * T_11km))
    else:
        rho = 1.225
        Pa = 101325
    return rho, Pa

def calculate_Ma(epsilon, k):
    """Calculate Mach number from area ratio"""
    def equation(Ma):
        if Ma <= 0: return 999 
        term1 = 1.0 / Ma
        term2 = (2 / (k + 1)) * (1 + (k - 1) / 2 * Ma**2)
        exponent = (k + 1) / (2 * (k - 1))
        return term1 * (term2 ** exponent) - epsilon

    Ma_sol = fsolve(equation, 2.0)[0]
    return Ma_sol

def calculate_nozzle_dimensions(F_req, P0, P_percentage, epsilon, k, c_star, efficiency=0.92):
    """
    효율 계수(efficiency)를 반영하여 노즐을 설계합니다.
    efficiency: 총 효율 (기본값 0.92 권장)
    """
    # 1. 출구 마하수 계산
    Ma = calculate_Ma(epsilon, k)
    
    # 2. 압력비
    Pe_ratio = (1 + (k - 1) / 2 * Ma**2)**(-k / (k - 1))
    
    Pa_SL = 101325
    Pc = P0 * P_percentage
    
    # 3. 이상적인 CF 계산
    term1 = (2 * k**2 / (k - 1))
    term2 = (2 / (k + 1))**((k + 1) / (k - 1))
    term3 = (1 - Pe_ratio**((k - 1) / k))
    
    CF_ideal_momentum = np.sqrt(term1 * term2 * term3)
    CF_ideal_pressure = (Pe_ratio - Pa_SL / Pc) * epsilon
    
    # [핵심 수정] 실제 CF = 이상적 CF * 효율
    CF_ideal = CF_ideal_momentum + CF_ideal_pressure
    CF_real = CF_ideal * efficiency
    
    # 4. 노즐 목 설계 (실제 효율이 반영된 CF 사용)
    # F = Pc * At * CF_real  ->  At = F / (Pc * CF_real)
    # 효율이 낮을수록 At는 더 커져야 함
    At = F_req / (Pc * CF_real)
    Dt = np.sqrt(4 * At / np.pi)
    
    # 5. 출구 설계
    Ae = At * epsilon
    De = np.sqrt(4 * Ae / np.pi)
    
    return {
        "At": At,
        "Dt": Dt,
        "Ae": Ae,
        "De": De,
        "CF": CF_real,      # 실제 CF 반환
        "CF_ideal": CF_ideal,
        "Ma_exit": Ma,
        "Pc_avg": Pc
    }
