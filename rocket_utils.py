import numpy as np
from scipy.optimize import fsolve

def isa_atmosphere(h):
    """ISA 표준 대기 모델"""
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
    """면적비(epsilon)로 출구 마하수(Me) 계산"""
    # f(Ma) = Area_Ratio_Eq - epsilon = 0
    def equation(Ma):
        if Ma <= 0: return 999 # 양수여야 함
        term1 = 1.0 / Ma
        term2 = (2 / (k + 1)) * (1 + (k - 1) / 2 * Ma**2)
        exponent = (k + 1) / (2 * (k - 1))
        return term1 * (term2 ** exponent) - epsilon

    # 초기 추정값 2.0 (초음속 가정)
    Ma_sol = fsolve(equation, 2.0)[0]
    return Ma_sol

def calculate_nozzle_dimensions(F_req, P0, P_percentage, epsilon, k):
    """목표 추력을 위한 노즐 치수 역산"""
    # 1. 마하수 및 추력 계수 계산
    Ma = calculate_Ma(epsilon, k)
    Pe_ratio = (1 + (k - 1) / 2 * Ma**2)**(-k / (k - 1))
    Pa_SL = 101325
    
    term1 = (2 * k**2 / (k - 1))
    term2 = (2 / (k + 1))**((k + 1) / (k - 1))
    term3 = (1 - Pe_ratio**((k - 1) / k))
    
    CF_SL = np.sqrt(term1 * term2 * term3) + (Pe_ratio - Pa_SL / P0) * epsilon
    
    # 2. 목 면적(At) 역산: F = CF * P_avg * At
    P_avg = P_percentage * P0
    At_req = F_req / (CF_SL * P_avg)
    
    # 3. 치수 계산
    dt_req = np.sqrt(4 * At_req / np.pi)
    Ae_req = At_req * epsilon
    de_req = np.sqrt(4 * Ae_req / np.pi)
    
    return At_req, dt_req, Ae_req, de_req, CF_SL