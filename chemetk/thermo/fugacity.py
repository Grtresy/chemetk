import numpy as np
from scipy import integrate

# 常数
R = 8.314  # J/mol·K

def calculate_fugacity_from_pv_data(pressures_pa, volumes_m3_per_mol, temp_k,p_ref=1e5, mu_ref=0.0):
    """
    根据P-V-T数据计算逸度、逸度系数和化学势。

    Args:
        pressures_pa (np.array): 压力数组 (单位: Pa).
        volumes_m3_per_mol (np.array): 摩尔体积数组 (单位: m³/mol).
        temp_k (float): 体系温度 (单位: K).
        p_ref (float): 参考压力 (默认: 1e5 Pa).
        mu_ref (float): 参考化学势 (默认: 0.0 J/mol).

    Returns:
        tuple: 包含逸度(Pa), 逸度系数(无量纲), 化学势(J/mol)的元组。
    """
    # 确保数据点一一对应
    if len(pressures_pa) != len(volumes_m3_per_mol):
        raise ValueError("压力和体积数组的长度必须相等。")

    # 被积函数: V/RT - 1/p
    # 注意处理 p=0 的情况，此时被积函数为0
    integrand = np.zeros_like(pressures_pa, dtype=float)
    non_zero_p_mask = pressures_pa > 0
    
    p_nonzero = pressures_pa[non_zero_p_mask]
    v_nonzero = volumes_m3_per_mol[non_zero_p_mask]
    
    integrand[non_zero_p_mask] = v_nonzero / (R * temp_k) - 1.0 / p_nonzero
    
    # 梯形法数值积分计算逸度系数的对数
    # integrate.cumtrapz 返回比输入短一个元素的数组，我们在前面补0
    ln_phi_integrated = integrate.cumulative_trapezoid(integrand[non_zero_p_mask], p_nonzero, initial=0)

    ln_phi = np.zeros_like(pressures_pa, dtype=float)
    ln_phi[non_zero_p_mask] = ln_phi_integrated

    # 逸度系数和逸度
    phi = np.exp(ln_phi)
    fugacities_pa = phi * pressures_pa
    
    # 计算化学势 (参考态: 理想气体在1bar)    
    # 避免对0取对数
    chemical_potentials_j_mol = np.full_like(fugacities_pa, -np.inf)
    valid_f_mask = fugacities_pa > 0
    chemical_potentials_j_mol[valid_f_mask] = mu_ref + R * temp_k * np.log(fugacities_pa[valid_f_mask] / p_ref)
    
    return fugacities_pa, phi, chemical_potentials_j_mol