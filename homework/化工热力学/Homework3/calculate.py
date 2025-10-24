import numpy as np
import pandas as pd

# 假设chemetk包在Python路径中
# 在VS Code中，如果根目录是ChemicalEngineeringToolkits，通常会自动识别
from chemetk.io.nist_webbook import fetch_isotherm_data
from chemetk.thermo.fugacity import calculate_fugacity_from_pv_data
from chemetk.visualization.plotting import plot_fugacity_results

def main():
    # --- 1. 获取数据 ---
    T = 300.0  # K
    fluid_name = 'CO₂'
    fluid_id = 'C124389' # CO₂的NIST ID
    
    print(f"正在从NIST获取 {fluid_name} 在 {T}K 的数据...")
    df = fetch_isotherm_data(fluid_id=fluid_id, temp=T, p_low=0, p_high=5, p_inc=0.01)
    
    if df is None:
        print("获取数据失败，程序终止。")
        return

    # --- 2. 数据预处理 ---
    # 将体积从 m³/mol 转换为需要的值，并处理 'infinite'
    df['Volume (m3/mol)'] = pd.to_numeric(df['Volume (m3/mol)'], errors='coerce')
    df = df.dropna(subset=['Volume (m3/mol)']) # 移除无法转换的行

    pressures_mpa = df['Pressure (MPa)'].values.astype(np.float64)
    volumes_m3_mol = df['Volume (m3/mol)'].values.astype(np.float64)
    
    # 转换为计算函数所需的单位 (Pa)
    pressures_pa = pressures_mpa * 1e6

    # --- 3. 执行计算 ---
    print("正在计算逸度和化学势...")
    fugacities_pa, phi, chemical_potentials_j_mol = calculate_fugacity_from_pv_data(
        pressures_pa, volumes_m3_mol, T, p_ref=1e5, mu_ref=0.0
    )

    # 将结果转换回常用单位用于绘图和报告
    fugacities_mpa = fugacities_pa / 1e6
    chemical_potentials_kj_mol = chemical_potentials_j_mol / 1000

    # --- 4. 绘制图表 ---
    print("正在生成图表...")
    fig, _ = plot_fugacity_results(
        pressures_mpa, 
        fugacities_mpa, 
        chemical_potentials_kj_mol,
        fluid_name=fluid_name,
        temp_k=T
    )
    fig.savefig('/home/Grtresy/VSCodeRepository/ChemicalEngineeringToolkits/examples/化工热力学/Homework3/fugacity_chemical_potential_from_chemetk.png', dpi=300)
    print("图表已保存为 'fugacity_chemical_potential_from_chemetk.png'")
    # plt.show() # 如果需要，可以取消注释以显示图表

    # --- 5. 报告结果 ---
    print("\nCO₂在300K时的逸度和化学势计算结果:")
    print("参考态: 理想气体在1bar, 参考化学势设为0")
    print("-" * 60)
    
    target_pressures = [2.0, 5.0]
    for target_p in target_pressures:
        idx = np.argmin(np.abs(pressures_mpa - target_p))
        
        print(f"目标压力: {target_p} MPa (实际数据点: {pressures_mpa[idx]:.3f} MPa)")
        print(f"  逸度 f: {fugacities_mpa[idx]:.4f} MPa")
        print(f"  逸度系数 φ: {phi[idx]:.4f}")
        print(f"  化学势 μ: {chemical_potentials_kj_mol[idx]:.4f} kJ/mol")
        print()

if __name__ == "__main__":
    main()