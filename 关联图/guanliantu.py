import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import os
import matplotlib.font_manager as fm
import random


def read_excel_data(file_path):
    """
    读取Excel文件中的数据
    
    参数:
    file_path: Excel文件路径
    
    返回:
    DataFrame: 包含Excel数据的DataFrame
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    
    # 读取Excel文件
    df = pd.read_excel(file_path, header=None)
    
    # 设置列名
    df.columns = ['干预措施', '具体名称（中医药)', '中医证型']
    
    # 删除第一行（原来的列名）
    df = df.drop(0).reset_index(drop=True)
    
    return df


def filter_data_by_treatment(df, treatment_type):
    """
    根据干预措施类型筛选数据
    
    参数:
    df: 包含所有数据的DataFrame
    treatment_type: 干预措施类型 ('中成药' 或 '中药汤剂')
    
    返回:
    DataFrame: 筛选后的数据
    """
    filtered_df = df[df['干预措施'] == treatment_type]
    return filtered_df.reset_index(drop=True)


def count_combinations(df):
    """
    统计中医证型和具体名称的组合数量
    
    参数:
    df: 筛选后的DataFrame
    
    返回:
    dict: {(证型, 药品名称): 数量} 的字典
    """
    combinations = {}
    
    for _, row in df.iterrows():
        pattern_drug = (row['中医证型'], row['具体名称（中医药)'])
        combinations[pattern_drug] = combinations.get(pattern_drug, 0) + 1
    
    return combinations


def generate_random_colors(n):
    """
    生成n个随机颜色
    
    参数:
    n: 需要生成的颜色数量
    
    返回:
    list: 包含n个颜色的列表
    """
    colors = []
    for _ in range(n):
        # 生成随机RGB颜色
        color = (random.random(), random.random(), random.random())
        colors.append(color)
    return colors


def draw_association_chart(combinations, treatment_type):
    """
    绘制关联图
    
    参数:
    combinations: {(证型, 药品名称): 数量} 的字典
    treatment_type: 干预措施类型
    """
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
    
    # 获取所有唯一的证型和药品名称
    patterns = sorted(list(set([item[0] for item in combinations.keys()])))
    drugs = sorted(list(set([item[1] for item in combinations.keys()])))
    
    # 根据数据量动态调整图形大小，确保所有内容都能完整显示
    # 纵轴项越多，图形高度越高；横轴项越多，图形宽度越宽
    fig_width = max(15, len(drugs) * 0.6)  # 宽度根据药品数量调整，最小15
    fig_height = max(12, len(patterns) * 0.35)  # 高度根据证型数量调整，减小系数以减小间距，最小12
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # 调整坐标轴间隔，优化纵轴上下边界的空白
    x_margin = 0.3  # 横轴间隔
    y_margin = 1.5  # 进一步减小纵轴间隔，从0.7减小到0.5以减小上下边界空白
    ax.set_xlim(-x_margin, len(drugs) - 1 + x_margin)
    ax.set_ylim(-y_margin, len(patterns) - 1 + y_margin)
    
    # 设置等比例坐标轴，确保圆是标准圆形而不是椭圆
    ax.set_aspect('equal', adjustable='box')
    
    # 绘制网格线
    ax.set_xticks(range(len(drugs)))
    ax.set_yticks(range(len(patterns)))
    ax.grid(True, linestyle='-', alpha=0.3)
    
    # 设置刻度和标签，调整标签间距
    ax.set_xticklabels(drugs, rotation=45, ha='right', fontsize=9)  # 横轴显示药品名称
    ax.set_yticklabels(patterns, fontsize=10)  # 纵轴显示证型
    
    # 为每个组合生成随机颜色
    unique_combinations = list(combinations.keys())
    colors = generate_random_colors(len(unique_combinations))
    color_map = dict(zip(unique_combinations, colors))
    
    # 绘制空心圆，增加半径范围，使圆可以跨越网格线
    max_count = max(combinations.values()) if combinations else 1
    min_count = min(combinations.values()) if combinations else 1
    
    # 如果最大值和最小值相同，则所有圆使用相同大小
    if max_count == min_count:
        radius_factor = 0.4  # 增大固定半径
    else:
        # 计算半径缩放因子，使差异更明显
        radius_factor = 0.7 / (max_count - min_count)
    
    for (pattern, drug), count in combinations.items():
        x = drugs.index(drug)  # x轴为药品名称
        y = patterns.index(pattern)  # y轴为证型
        
        # 根据数量确定圆的大小，使用更大幅度的半径变化
        if max_count == min_count:
            radius = radius_factor
        else:
            # 使用平方函数来放大差异，使大数量的圆更大
            normalized_count = (count - min_count) / (max_count - min_count)
            radius = 0.15 + 0.6 * (normalized_count ** 1.5)
        
        # 获取颜色
        color = color_map[(pattern, drug)]
        
        # 绘制空心圆
        circle = Circle((x, y), radius, fill=False, edgecolor=color, linewidth=2)
        ax.add_patch(circle)
        
        # 在圆心添加数量标签
        ax.text(x, y, str(count), ha='center', va='center', fontsize=9, color='black')
    
    # # 设置标题
    # plt.title(f'{treatment_type}关联图', fontsize=16, pad=20)
    
    # 调整布局，进一步优化显示效果
    plt.tight_layout(pad=4.5)  # 减小pad值以减少边缘空间
    
    # 显示图形
    plt.show()
    
    return fig, ax


def main(treatment_type='中成药'):
    """
    主函数
    
    参数:
    treatment_type: 干预措施类型 ('中成药' 或 '中药汤剂')
    """
    # 读取Excel文件
    file_path = '方药-证型.xlsx'
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    
    try:
        df = read_excel_data(full_path)
        print(f"成功读取数据，共 {len(df)} 行")
        
        # 筛选数据
        filtered_df = filter_data_by_treatment(df, treatment_type)
        print(f"筛选出 {treatment_type} 数据 {len(filtered_df)} 行")
        
        # 统计组合
        combinations = count_combinations(filtered_df)
        print(f"共有 {len(combinations)} 种组合")
        
        # 绘制关联图
        if combinations:
            draw_association_chart(combinations, treatment_type)
        else:
            print(f"没有找到 {treatment_type} 的数据")
            
    except Exception as e:
        print(f"处理过程中出现错误: {e}")


if __name__ == "__main__":
    # 可以通过修改参数来选择不同的干预措施类型
    main('中药汤剂')  # 或者 '中药汤剂'