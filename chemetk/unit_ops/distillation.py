# chemetk/unit_ops/distillation.py
import pandas as pd

class McCabeThiele:
    """
    使用McCabe-Thiele法进行二元精馏塔的理论塔板计算。
    支持常规操作和全回流操作。
    """
    def __init__(self, vle, x_D: float, x_W: float, x_F: float, q: float, 
                 R: float, D: float = 0., F: float = 0., W: float = 0.):
        """
        初始化精馏塔参数。
        
        :param vle: VLE实例
        :param x_D: 馏出液组成
        :param x_W: 釜液组成
        :param x_F: 进料组成（全回流时可省略）
        :param q: 进料热状态参数（全回流时可省略）
        :param R: 回流比（全回流时为无穷大，用None表示）
        :param D: 馏出液流量（全回流时为0）
        :param F: 进料流量（全回流时为0）
        :param W: 釜液流量（全回流时为0）
        """
        self.vle = vle
        self.x_D = x_D
        self.x_W = x_W
        self.x_F = x_F
        self.q = q
        self.R = R
        self.D = D
        self.F = F
        self.W = W
        
        # 判断是否为全回流操作
        self.total_reflux = (float(F) == 0. and float(D) == 0. and float(W) == 0.)
        
        if self.total_reflux:
            print("检测到全回流操作模式")
            # 全回流时操作线为对角线 y = x
            self.L_over_V = 1.0
            self.D_xD_over_V = 0.0
            self.L_prime_over_V_prime = 1.0
            self.W_xW_over_V_prime = 0.0
            # 全回流时，切换点无意义，可以设为 x_F
            self.x_intersect = x_F
            self.y_intersect = x_F
        else:
            # 计算操作线参数
            self.L = R * D  # 精馏段液相流量
            self.V = (R + 1) * D  # 精馏段气相流量
            
            # 提馏段流量计算
            self.L_prime = self.L + q * F
            self.V_prime = self.V - (1 - q) * F
            
            # 预计算一些常用的操作线参数
            self.L_over_V = R / (R + 1)
            self.D_xD_over_V = D * x_D / self.V
            self.L_prime_over_V_prime = self.L_prime / self.V_prime
            self.W_xW_over_V_prime = W * x_W / self.V_prime
            
            # ---------- <<< 修改开始 >>> ----------
            # 计算操作线的交点，作为正确的切换点
            if q == 1:
                self.x_intersect = x_F
            elif q == 0:
                y_int_temp = x_F
                # 从 y = (L/V)x + D*xD/V 反解 x
                self.x_intersect = (y_int_temp - self.D_xD_over_V) / self.L_over_V
            else:
                m_q = q / (q-1) # q线的斜率
                b_q = x_F - m_q * x_F # q线的截距 y = m_q*x + b_q
                # 联立精馏段操作线 y = (L/V)x + D*xD/V
                # m_q*x + b_q = (L/V)x + D*xD/V
                # (m_q - L/V)x = D*xD/V - b_q
                self.x_intersect = (self.D_xD_over_V - b_q) / (m_q - self.L_over_V)
            
            # 计算交点的 y 坐标
            self.y_intersect = self.L_over_V * self.x_intersect + self.D_xD_over_V
            print(f"操作线交点计算: x_intersect = {self.x_intersect:.4f}, y_intersect = {self.y_intersect:.4f}")
            # ---------- <<< 修改结束 >>> ----------

    def calculate_stages(self, start_from: str = 'top', murphree_efficiency: float = 1.0,
                        return_decimal_stages: bool = False):
        """
        计算理论塔板数。
        
        :param start_from: 'top' 或 'bottom'，决定从塔顶还是塔釜开始计算。
        :param murphree_efficiency: 默弗里塔板效率 (0 to 1.0)，从塔顶计算使用液相Murphree效率，从塔釜计算使用气相Murphree效率。
        :param return_decimal_stages: 是否返回小数形式的理论级数（用于全塔板效率计算）
        :return: 如果return_decimal_stages为True，返回(塔板DataFrame, 小数理论级数)；否则返回塔板DataFrame
        """
        if start_from == 'top':
            result = self._calculate_from_top(murphree_efficiency)
        elif start_from == 'bottom':
            result = self._calculate_from_bottom(murphree_efficiency)
        else:
            raise ValueError("start_from must be 'top' or 'bottom'")
        
        if return_decimal_stages:
            decimal_stages = self._calculate_decimal_stages(result, start_from)
            return result, decimal_stages
        else:
            return result

    def _calculate_from_top(self, E_ml: float = 1.0):
        """
        从塔顶开始迭代计算精馏塔的理论塔板数，考虑液相Murphree效率。
        
        :param E_ml: 液相Murphree效率
        :return: 每级塔板的信息DataFrame
        """
        stages = []
        stage_number = 1
        
        # 从塔顶开始计算 (x = x_D)
        current_x = self.x_D
        current_y = self.x_D  # 塔顶气相组成等于馏出液组成
        
        print("从塔顶开始塔板迭代计算 (考虑液相Murphree效率)...")
        print(f"目标釜液组成 x_W = {self.x_W}")
        print(f"液相Murphree效率 E_ml = {E_ml}")
        if self.total_reflux:
            print("操作模式: 全回流")
        print("-" * 80)
        
        while current_x > self.x_W:
            # 记录当前级信息
            stage_info = {
                'stage': stage_number,
                'x_liquid': current_x,
                'y_vapor': current_y,
                'temperature': float(self.vle.get_temperature_by_x(current_x)),
                'relative_volatility': float(self.vle.get_alpha_by_x(current_x)),
                'efficiency': E_ml if stage_number > 1 else 1.0,  # 塔顶效率为1
                'section': self._get_section(current_x)
            }
            stages.append(stage_info)
            
            # 打印当前级信息
            print(f"第{stage_number:2d}级: x = {current_x:.4f}, y = {current_y:.4f}, "
                  f"温度 = {stage_info['temperature']:.1f}°C, 段别 = {stage_info['section']}")
            
            # 计算下一级的气相组成
            if self.total_reflux:
                # 全回流操作线: y = x
                next_y = current_x
            else:
                # ---------- <<< 修改开始 >>> ----------
                # 使用正确的切换点 x_intersect
                if current_x > self.x_intersect:
                # ---------- <<< 修改结束 >>> ----------
                    # 精馏段操作线
                    next_y = self.L_over_V * current_x + self.D_xD_over_V
                else:
                    # 提馏段操作线
                    next_y = self.L_prime_over_V_prime * current_x - self.W_xW_over_V_prime
            
            # 通过平衡关系由y求平衡液相组成 x*
            x_equilibrium_next = float(self.vle.get_x_by_y(next_y))
            
            # 使用液相Murphree效率计算实际液相组成
            # 对于从上往下的计算: x_n = x_{n-1} - E_ml * (x_{n-1} - x*_n)
            # 其中 x_{n-1} 是上一级的液相组成 (当前级的 current_x)
            x_actual_next = current_x - E_ml * (current_x - x_equilibrium_next)
            
            # 更新为下一级的值
            current_x = x_actual_next
            current_y = next_y
            stage_number += 1
            
            # 安全保护，避免无限循环
            if stage_number > 150:  # 增加安全保护次数
                print("警告: 迭代次数超过150次，强制停止")
                break
        
        # 记录最后一级
        if stages and current_x <= self.x_W:
            final_stage = {
                'stage': stage_number,
                'x_liquid': current_x,
                'y_vapor': current_y,
                'temperature': float(self.vle.get_temperature_by_x(current_x)),
                'relative_volatility': float(self.vle.get_alpha_by_x(current_x)),
                'efficiency': E_ml,
                'section': self._get_section(current_x)
            }
            stages.append(final_stage)
            print(f"第{stage_number:2d}级: x = {current_x:.4f}, y = {current_y:.4f}, "
                  f"温度 = {final_stage['temperature']:.1f}°C, 段别 = {final_stage['section']}")
            print(f"达到目标釜液组成 x_W = {self.x_W}")
        
        return pd.DataFrame(stages)

    def _calculate_from_bottom(self, E_mv: float = 1.0):
        """
        从塔釜开始迭代计算精馏塔的理论塔板数，考虑气相Murphree效率。
        
        :param E_mv: 气相Murphree效率
        :return: 每级塔板的信息DataFrame
        """
        stages = []
        stage_number = 1
        
        # 从塔釜开始计算 (x = x_W)
        current_x = self.x_W
        current_y_equilibrium = float(self.vle.get_y_by_x(self.x_W))  # 平衡气相组成
        current_y_actual = current_y_equilibrium  # 塔釜通常视为平衡状态
        
        print("从塔釜开始塔板迭代计算 (考虑气相Murphree效率)...")
        print(f"目标馏出液组成 x_D = {self.x_D}")
        print(f"气相Murphree效率 E_mv = {E_mv}")
        if self.total_reflux:
            print("操作模式: 全回流")
        print("-" * 80)
        
        while current_y_actual < self.x_D:
            # 记录当前级信息
            stage_info = {
                'stage': stage_number,
                'x_liquid': current_x,
                'y_vapor_actual': current_y_actual,
                'y_vapor_equilibrium': current_y_equilibrium,
                'temperature': float(self.vle.get_temperature_by_x(current_x)),
                'relative_volatility': float(self.vle.get_alpha_by_x(current_x)),
                'efficiency': E_mv if stage_number > 1 else 1.0,  # 塔釜效率为1
                'section': self._get_section(current_x)
            }
            stages.append(stage_info)
            
            # 打印当前级信息
            print(f"第{stage_number:2d}级: x = {current_x:.4f}, y_实际 = {current_y_actual:.4f}, "
                  f"y_平衡 = {current_y_equilibrium:.4f}, 段别 = {stage_info['section']}")
            
            # 计算下一级的液相组成
            if self.total_reflux:
                # 全回流操作线: x = y
                next_x = current_y_actual
            else:
                # ---------- <<< 修改开始 >>> ----------
                # 使用正确的切换点 x_intersect
                if current_x <= self.x_intersect:
                # ---------- <<< 修改结束 >>> ----------
                    # 提馏段操作线
                    next_x = (self.V_prime * current_y_actual + self.W * self.x_W) / self.L_prime
                else:
                    # 精馏段操作线
                    next_x = (self.V * current_y_actual - self.D * self.x_D) / self.L
            
            # 通过平衡关系由x求平衡气相组成 y*
            y_equilibrium_next = float(self.vle.get_y_by_x(next_x))
            
            # 使用气相Murphree效率计算实际气相组成
            # 对于从下往上的计算: y_n = y_{n-1} + E_mv * (y*_n - y_{n-1})
            y_actual_next = current_y_actual + E_mv * (y_equilibrium_next - current_y_actual)
            
            # 更新为上一级的值
            current_x = next_x
            current_y_actual = y_actual_next
            current_y_equilibrium = y_equilibrium_next
            stage_number += 1
            
            # 安全保护，避免无限循环
            if stage_number > 150:  # 增加安全保护次数
                print("警告: 迭代次数超过150次，强制停止")
                break
        
        # 记录最后一级
        if stages and current_y_actual >= self.x_D:
            final_stage = {
                'stage': stage_number,
                'x_liquid': current_x,
                'y_vapor_actual': current_y_actual,
                'y_vapor_equilibrium': current_y_equilibrium,
                'temperature': float(self.vle.get_temperature_by_x(current_x)),
                'relative_volatility': float(self.vle.get_alpha_by_x(current_x)),
                'efficiency': E_mv,
                'section': self._get_section(current_x)
            }
            stages.append(final_stage)
            print(f"第{stage_number:2d}级: x = {current_x:.4f}, y_实际 = {current_y_actual:.4f}, "
                  f"y_平衡 = {current_y_equilibrium:.4f}, 段别 = {final_stage['section']}")
            print(f"达到目标馏出液组成 x_D = {self.x_D}")
        
        return pd.DataFrame(stages)

    def _get_section(self, x: float) -> str:
        """根据液相组成判断塔段"""
        if self.total_reflux:
            return "全回流段"
        # ---------- <<< 修改开始 >>> ----------
        elif x > self.x_intersect:
            return "精馏段"
        else:
            return "提馏段"
        # ---------- <<< 修改结束 >>> ----------

    def _calculate_decimal_stages(self, stages_df, calculation_direction: str) -> float:
        """
        计算小数形式的理论级数，用于全塔板效率计算。
        
        :param stages_df: 塔板数据DataFrame
        :param calculation_direction: 计算方向 'top' 或 'bottom'
        :return: 小数形式的理论级数
        """
        if len(stages_df) < 2:
            return len(stages_df)
        
        if calculation_direction == 'top':
            # 从塔顶计算：寻找跨越目标组成x_W的两个塔板
            for i in range(len(stages_df) - 1):
                x_current = stages_df.iloc[i]['x_liquid']
                x_next = stages_df.iloc[i + 1]['x_liquid']
                
                if x_current >= self.x_W >= x_next:
                    # 线性插值计算小数部分
                    fraction = (x_current - self.x_W) / (x_current - x_next)
                    decimal_stages = i + fraction
                    print(f"小数理论级数计算: 第{i}级x={x_current:.4f}, 第{i+1}级x={x_next:.4f}")
                    print(f"在x_W={self.x_W}处插值, 小数部分 = {fraction:.3f}")
                    print(f"总小数理论级数 = {decimal_stages:.3f}")
                    return decimal_stages
        
        else:  # bottom
            # 从塔釜计算：寻找跨越目标组成x_D的两个塔板
            for i in range(len(stages_df) - 1):
                y_current = stages_df.iloc[i]['y_vapor_actual']
                y_next = stages_df.iloc[i + 1]['y_vapor_actual']
                
                if y_current <= self.x_D <= y_next:
                    # 线性插值计算小数部分
                    fraction = (self.x_D - y_current) / (y_next - y_current)
                    decimal_stages = i + fraction
                    print(f"小数理论级数计算: 第{i}级y={y_current:.4f}, 第{i+1}级y={y_next:.4f}")
                    print(f"在x_D={self.x_D}处插值, 小数部分 = {fraction:.3f}")
                    print(f"总小数理论级数 = {decimal_stages:.3f}")
                    return decimal_stages
        
        # 如果没有找到跨越点，返回整数级数
        print("警告: 无法计算小数理论级数，返回整数级数")
        return len(stages_df)

    def print_summary(self, stages_df, calculation_direction: str = 'top', decimal_stages: float | None = None):
        """
        以表格形式打印塔板计算结果。
        
        :param stages_df: 塔板数据DataFrame
        :param calculation_direction: 计算方向 'top' 或 'bottom'
        :param decimal_stages: 小数形式的理论级数（可选）
        """
        if calculation_direction == 'top':
            print("\n" + "="*90)
            if self.total_reflux:
                print("全回流精馏塔理论塔板计算汇总 (从塔顶开始)")
            else:
                print("精馏塔理论塔板计算汇总 (从塔顶开始，考虑液相Murphree效率)")
            print("="*90)
            print(f"{'塔板级数':<10} {'液相组成(x)':<12} {'气相组成(y)':<12} {'温度(℃)':<10} {'效率':<8} {'段别':<10}")
            print("-"*90)
            
            for _, stage in stages_df.iterrows():
                print(f"{stage['stage']:<10} {stage['x_liquid']:<12.4f} {stage['y_vapor']:<12.4f} "
                      f"{stage['temperature']:<10.1f} {stage['efficiency']:<8.2f} {stage['section']:<10}")
        
        else:  # bottom
            print("\n" + "="*100)
            if self.total_reflux:
                print("全回流精馏塔理论塔板计算汇总 (从塔釜开始)")
            else:
                print("精馏塔理论塔板计算汇总 (从塔釜开始，考虑气相Murphree效率)")
            print("="*100)
            print(f"{'塔板级数':<10} {'液相组成(x)':<12} {'实际气相(y)':<12} {'平衡气相(y*)':<12} {'温度(℃)':<10} {'效率':<8} {'段别':<10}")
            print("-"*100)
            
            for _, stage in stages_df.iterrows():
                print(f"{stage['stage']:<10} {stage['x_liquid']:<12.4f} {stage['y_vapor_actual']:<12.4f} "
                      f"{stage['y_vapor_equilibrium']:<12.4f} {stage['temperature']:<10.1f} {stage['efficiency']:<8.2f} {stage['section']:<10}")
        
        print("-" * (100 if calculation_direction == 'bottom' else 90))
        
        # 输出理论级数信息
        integer_stages = len(stages_df)
        print(f"整数理论塔板数: {integer_stages} 级")
        
        if decimal_stages is not None:
            print(f"小数理论塔板数: {decimal_stages:.3f} 级")
            print(f"全塔板效率计算用理论级数: {decimal_stages:.3f}")
        
        if not self.total_reflux:
            # 常规操作时显示段别分布
            if calculation_direction == 'top':
                rectifying_stages = len(stages_df[stages_df['section'] == '精馏段'])
                stripping_stages = len(stages_df[stages_df['section'] == '提馏段'])
                print(f"其中精馏段: {rectifying_stages} 级")
                print(f"其中提馏段: {stripping_stages} 级")
                print(f"进料板位置: 第{rectifying_stages + 1}级")
            else:
                stripping_stages = len(stages_df[stages_df['section'] == '提馏段'])
                rectifying_stages = len(stages_df[stages_df['section'] == '精馏段'])
                print(f"其中提馏段: {stripping_stages} 级")
                print(f"其中精馏段: {rectifying_stages} 级")
                print(f"进料板位置: 第{stripping_stages}级")

# 使用示例
if __name__ == "__main__":
    # 假设已有vle实例和参数
    # vle = MethanolWaterVLE()
    
    # 常规操作示例
    # x_D, x_W, x_F, q, R, D, F, W = ...  # 实际参数
    # mt = McCabeThiele(vle, x_D, x_W, x_F, q, R, D, F, W)
    
    # 全回流操作示例
    # x_D, x_W = 0.95, 0.05  # 仅需指定塔顶塔釜组成
    # mt_total_reflux = McCabeThiele(vle, x_D=x_D, x_W=x_W, F=0, D=0, W=0)
    
    # 从塔顶计算，考虑液相效率0.7，获取小数级数
    # stages_top, decimal_stages = mt.calculate_stages(start_from='top', murphree_efficiency=0.7, return_decimal_stages=True)
    # mt.print_summary(stages_top, 'top', decimal_stages)
    
    # 从塔釜计算，考虑气相效率0.7，仅获取整数级数
    # stages_bottom = mt.calculate_stages(start_from='bottom', murphree_efficiency=0.7)
    # mt.print_summary(stages_bottom, 'bottom')
    
    # 全回流计算
    # stages_total, decimal_total = mt_total_reflux.calculate_stages(start_from='top', return_decimal_stages=True)
    # mt_total_reflux.print_summary(stages_total, 'top', decimal_total)
    pass