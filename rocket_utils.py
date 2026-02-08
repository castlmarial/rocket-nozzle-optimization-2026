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
    """Calculate Mach number from area ratio and specific heat ratio"""
    def equation(Ma):
        if Ma <= 0: return 999 
        term1 = 1.0 / Ma
        term2 = (2 / (k + 1)) * (1 + (k - 1) / 2 * Ma**2)
        exponent = (k + 1) / (2 * (k - 1))
        return term1 * (term2 ** exponent) - epsilon

    # initial guess with supersonic condition
    Ma_sol = fsolve(equation, 2.0)[0]
    return Ma_sol

def calculate_nozzle_dimensions(F_req, P0, P_percentage, epsilon, k, c_star):
    """
    PROPEP3의 C*를 입력받아 물리적 Isp와 노즐 치수를 계산합니다.
    """
    Ma = calculate_Ma(epsilon, k)
    Pe_ratio = (1 + (k - 1) / 2 * Ma**2)**(-k / (k - 1))
    Pa_SL = 101325
    g0 = 9.80665 # 표준 중력 가속도
    
    # 1. Thrust Coefficient (CF) 계산
    term1 = (2 * k**2 / (k - 1))
    term2 = (2 / (k + 1))**((k + 1) / (k - 1))
    term3 = (1 - Pe_ratio**((k - 1) / k))
    
    CF_SL = np.sqrt(term1 * term2 * term3) + (Pe_ratio - Pa_SL / P0) * epsilon
    
    # 2. 물리적 비추력 (Isp) 도출: Isp = (C* * CF) / g0
    # PROPEP3의 화학 성능(C*)과 노즐의 기계적 성능(CF)을 결합
    isp_phys = (c_star * CF_SL) / g0
    
    # 3. 노즐 치수 역산 (F = CF * P_avg * At)
    P_avg = P_percentage * P0
    At_req = F_req / (CF_SL * P_avg)
    
    dt_req = np.sqrt(4 * At_req / np.pi)
    Ae_req = At_req * epsilon
    de_req = np.sqrt(4 * Ae_req / np.pi)
    
    return At_req, dt_req, Ae_req, de_req, CF_SL, isp_phys
