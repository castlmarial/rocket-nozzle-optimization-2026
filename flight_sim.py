import numpy as np
from scipy.integrate import solve_ivp
from rocket_utils import isa_atmosphere

def rocket_eom(t, X, params):
    """운동 방정식 (EOM)"""
    h, v = X
    
    # 파라미터 언패킹
    F_avg = params['F_avg']
    tb = params['tb']
    m0 = params['m0']
    mp = params['mp']
    CD_A = params['CD_A']
    
    g0 = 9.80665
    
    # 지면 아래로 떨어지면 물리 계산 중지 (속도, 가속도 0)
    if h < 0:
        return [0, 0]

    rho, _ = isa_atmosphere(h)
    
    # 질량 및 추력 업데이트
    mdot = mp / tb
    if t <= tb:
        m = m0 - mdot * t
        F = F_avg
    else:
        m = m0 - mp
        F = 0
        
    # 항력 및 가속도 (v의 부호에 따라 항력 방향 결정)
    D = 0.5 * rho * CD_A * (v**2) * np.sign(v)
    
    # 운동방정식: F_net = Thrust - Drag - Gravity
    F_net = F - D - m * g0
    vdot = F_net / m
    
    return [v, vdot]

def simulate_flight(F_avg, tb, m0, mp, CD_A):
    """비행 시뮬레이션 실행"""
    params = {'F_avg': F_avg, 'tb': tb, 'm0': m0, 'mp': mp, 'CD_A': CD_A}
    
    # [변경점 1] 이벤트 함수: 정점이 아니라 '지면 도달(h=0)' 시 종료
    def hit_ground(t, y):
        return y[0] # 고도(h)가 0이 될 때
    hit_ground.terminal = True
    hit_ground.direction = -1 # 위에서 아래로(-1) 떨어질 때만 감지

    # 시뮬레이션 시간 설정 (충분히 길게)
    t_span = [0, 300] 
    y0 = [0, 0] # [고도, 속도]
    
    # [변경점 2] t_eval: 그래프 해상도를 높이기 위해 0.05초 간격으로 강제 설정
    # 이것이 없으면 solver가 점을 듬성듬성 찍어서 그래프가 각져 보임
    t_eval = np.arange(0, 300, 0.05)
    
    sol = solve_ivp(
        fun=lambda t, y: rocket_eom(t, y, params),
        t_span=t_span,
        y0=y0,
        events=hit_ground, # 지면에 닿으면 종료
        t_eval=t_eval,     # <--- 핵심: 고해상도 플 plotting을 위한 설정
        rtol=1e-6, atol=1e-9
    )
    
    return sol.t, sol.y
