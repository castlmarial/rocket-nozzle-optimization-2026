import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- KNSB Propellant Properties (Typical Values) ---
KNSB_PROPS = {
    'density': 1841.0,      # [kg/m^3] 밀도
    'c_star': 895.0,        # [m/s] 특성배기속도
    'a': 8.26e-3,           # [m/s per MPa^n] 연소속도 계수
    'n': 0.319              # [] 연소속도 지수
}

# [수정됨] grain_type="BATES" 인자 추가 (에러 해결 핵심)
def calculate_grain_geometry(D_chamber_mm, t_liner_mm, m_prop, At, tb, P_avg_pa, grain_type="BATES"):
    """
    그레인 형상을 설계하고 계산 결과를 반환하는 함수
    """
    D_chamber = D_chamber_mm / 1000.0
    t_liner = t_liner_mm / 1000.0
    
    mdot = m_prop / tb
    
    a = KNSB_PROPS['a']
    n = KNSB_PROPS['n']
    P_mpa = P_avg_pa / 1e6
    r = a * (P_mpa ** n) # [m/s]
    
    rho = KNSB_PROPS['density']
    Ab_req = mdot / (rho * r)
    
    # --- 형상 치수 결정 ---
    D_grain = D_chamber - (2 * t_liner)
    if D_grain <= 0:
        return {"error": "지관 두께가 챔버 내경보다 큽니다. 설정을 확인해주세요."}

    # Port Ratio >= 2.0 조건 적용
    min_port_ratio = 2.0
    d_core_min = np.sqrt((min_port_ratio * At * 4) / np.pi)
    d_core = d_core_min
    
    # 길이 계산
    A_cross = (np.pi / 4) * (D_grain**2 - d_core**2)
    L_grain = m_prop / (rho * A_cross)
    
    L_over_D = L_grain / D_grain
    
    # 침식 연소 리스크 고려
    is_erosive_risk = False
    if L_over_D > 6.0:
        is_erosive_risk = True
        target_port_ratio = 3.0 # 리스크가 있을 경우 포트 비율 상향
        d_core_erosive = np.sqrt((target_port_ratio * At * 4) / np.pi)
        
        d_core = d_core_erosive
        A_cross = (np.pi / 4) * (D_grain**2 - d_core**2)
        L_grain = m_prop / (rho * A_cross)
        L_over_D = L_grain / D_grain

    A_port = (np.pi / 4) * (d_core**2)
    final_port_ratio = A_port / At

    return {
        "Grain_Type": grain_type,
        "grain_type": grain_type,
        "D_grain_mm": D_grain * 1000,
        "d_core_mm": d_core * 1000,
        "L_grain_mm": L_grain * 1000,
        "L_over_D": L_over_D,
        "Port_Ratio": final_port_ratio,
        "Ab_req_m2": Ab_req,
        "r_mm_s": r * 1000,
        "is_erosive_risk": is_erosive_risk,
    }

# ==============================================================================
# 시각화 관련 함수 (이전과 동일하지만 그대로 유지해야 함)
# ==============================================================================

def _draw_dim_line(ax, p1, p2, text, offset_vec=(0,0), text_offset_vec=(0,0)):
    p1_off = (p1[0] + offset_vec[0], p1[1] + offset_vec[1])
    p2_off = (p2[0] + offset_vec[0], p2[1] + offset_vec[1])
    ax.annotate("", xy=p1_off, xytext=p2_off,
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
    mid_point = ((p1_off[0] + p2_off[0])/2, (p1_off[1] + p2_off[1])/2)
    text_pos = (mid_point[0] + text_offset_vec[0], mid_point[1] + text_offset_vec[1])
    ax.text(text_pos[0], text_pos[1], text, ha='center', va='center', 
            fontsize=9, fontweight='bold', 
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))

def plot_grain_geometry(grain_res):
    D = grain_res['D_grain_mm']
    d = grain_res['d_core_mm']
    L = grain_res['L_grain_mm']
    
    fig, (ax_top, ax_side) = plt.subplots(1, 2, figsize=(7, 4))
    fig.suptitle('Grain Geometry', fontsize=12)

    propellant_color = "#BDBDBD"

    # Cross Section View
    outer_circle = patches.Circle((0, 0), D/2, facecolor=propellant_color, edgecolor='black', lw=1)
    ax_top.add_patch(outer_circle)
    inner_circle = patches.Circle((0, 0), d/2, facecolor='white', edgecolor='black', lw=1)
    ax_top.add_patch(inner_circle)
    
    offset = D * 0.1
    _draw_dim_line(ax_top, (-D/2, 0), (D/2, 0), f"OD: {D:.1f} mm", 
                   offset_vec=(0, -D/2 - offset), text_offset_vec=(0, -offset*0.5))
    _draw_dim_line(ax_top, (-d/2, 0), (d/2, 0), f"Core: {d:.1f} mm", 
                   offset_vec=(0, 0), text_offset_vec=(0, d*0.35))

    ax_top.set_aspect('equal', adjustable='box')
    margin = D * 0.3
    ax_top.set_xlim(-D/2 - margin, D/2 + margin)
    ax_top.set_ylim(-D/2 - margin, D/2 + margin)
    ax_top.axis('off')

    # Longitudinal View
    wall_thickness = (D - d) / 2
    left_wall = patches.Rectangle((-D/2, 0), wall_thickness, L, facecolor=propellant_color, edgecolor='black', lw=1)
    ax_side.add_patch(left_wall)
    right_wall = patches.Rectangle((d/2, 0), wall_thickness, L, facecolor=propellant_color, edgecolor='black', lw=1)
    ax_side.add_patch(right_wall)
    ax_side.axvline(0, color='black', linestyle='-.', lw=1, alpha=0.5)

    offset_x = D * 0.2
    _draw_dim_line(ax_side, (D/2, 0), (D/2, L), f"Length: {L:.1f} mm", 
                   offset_vec=(offset_x, 0), text_offset_vec=(offset_x*0.3, 0))
    offset_y = L * 0.05
    if L < D: offset_y = D * 0.1
    _draw_dim_line(ax_side, (-D/2, L), (D/2, L), f"OD: {D:.1f} mm",
                   offset_vec=(0, offset_y), text_offset_vec=(0, offset_y*1.0))
                   
    ax_side.set_aspect('equal', adjustable='box')
    margin_x = D * 0.5
    margin_y = L * 0.2
    ax_side.set_xlim(-D/2 - margin_x, D/2 + margin_x)
    bottom_margin = margin_y if L < 3*D else margin_y*0.2
    ax_side.set_ylim(-bottom_margin, L + margin_y)
    ax_side.axis('off')

    plt.tight_layout()
    return fig
