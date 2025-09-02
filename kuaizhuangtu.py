import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
from matplotlib.colors import hsv_to_rgb
import math


def draw_rectangles_by_ratio(ratios, labels=None, image_size=6, dpi=100):
    """
    根据给定比例绘制一个正方形，并将其分割为多个小矩形

    参数:
    ratios: 列表，包含各个小矩形的面积比例
    labels: 列表，包含各个小矩形的标识文本（可选，默认为比例值）
    image_size: 正方形图片的大小（英寸）
    dpi: 图片的分辨率
    """
    # 验证比例之和是否为1 (使用 math.isclose 处理浮点数精度问题)
    total_ratio = sum(ratios)
    if not math.isclose(total_ratio, 1.0, rel_tol=1e-9):
        raise ValueError(f"Ratios must sum to 1, but got {total_ratio}")

    # 如果没有提供标签，则使用比例值作为标签
    if labels is None:
        labels = [f'{ratio:.2f}' for ratio in ratios]

    # 验证标签数量是否与比例数量一致
    if len(labels) != len(ratios):
        raise ValueError(f"Number of labels ({len(labels)}) must match number of ratios ({len(ratios)})")

    # 创建图形和坐标轴
    fig, ax = plt.subplots(1, 1, figsize=(image_size, image_size))

    # 绘制正方形边界
    square = patches.Rectangle((0, 0), 1, 1, linewidth=2, edgecolor='black', facecolor='none')
    ax.add_patch(square)

    # 使用精确的布局算法分割矩形
    rectangles = layout_rectangles_exact(ratios)

    # 为每个比例生成颜色
    colors = generate_colors(len(ratios))

    # 绘制矩形
    for i, (rect, color, label) in enumerate(zip(rectangles, colors, labels)):
        ratio = ratios[i]
        if ratio <= 0:
            continue

        x, y, width, height = rect

        # 绘制矩形
        rectangle = patches.Rectangle((x, y), width, height,
                                      linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(rectangle)

        # 在矩形中心添加标识文本
        ax.text(x + width / 2, y + height / 2,
                label, ha='center', va='center', fontsize=8,
                color='white' if is_dark_color(color) else 'black',
                weight='bold')

    # 设置坐标轴属性
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')  # 隐藏坐标轴

    # 设置标题
    plt.title('', fontsize=14, pad=20)

    # 调整布局
    plt.tight_layout()

    # 显示图形
    plt.show()

    return fig, ax


def layout_rectangles_exact(ratios):
    """
    根据比例精确计算矩形的位置和大小，确保完全填满正方形
    优化版本：使大比例矩形尽可能靠左排列

    使用改进的二叉树分割方法:
    1. 按比例大小排序索引
    2. 构建一个二叉树，每个节点代表一个矩形区域
    3. 优先将大比例矩形放在左侧
    """
    rectangles = [None] * len(ratios)

    def split_area(x, y, width, height, indices):
        """
        递归分割区域

        参数:
        x, y: 当前区域的左下角坐标
        width, height: 当前区域的宽度和高度
        indices: 需要分配到这个区域的矩形索引列表（已按比例排序）
        """
        if len(indices) == 1:
            # 只剩一个矩形，直接分配整个区域
            rectangles[indices[0]] = (x, y, width, height)
            return

        # 将索引列表分为两部分
        # 为了保持大矩形在左侧，我们按累积比例分割
        total = sum(ratios[i] for i in indices)
        target = total / 2
        cumulative = 0
        split_point = 1  # 至少左边要有1个元素

        # 寻找最佳分割点，使左侧比例尽可能接近总比例的一半
        for i in range(len(indices) - 1):  # 不包括最后一个，确保右边至少有1个元素
            cumulative += ratios[indices[i]]
            if cumulative >= target:
                # 检查当前分割点和下一个分割点哪个更接近目标
                if i + 1 < len(indices) - 1:
                    next_cumulative = cumulative + ratios[indices[i + 1]]
                    if abs(cumulative - target) <= abs(next_cumulative - target):
                        split_point = i + 1
                        break
                split_point = i + 1
                break
        else:
            # 如果循环完成仍未break，则取最后一个可能的分割点
            split_point = len(indices) - 1

        left_indices = indices[:split_point]
        right_indices = indices[split_point:]

        left_ratio = sum(ratios[i] for i in left_indices)
        right_ratio = sum(ratios[i] for i in right_indices)

        # 优先垂直分割（左右分割）以保持大矩形在左侧
        # 只有当高度远大于宽度时才考虑水平分割
        if width >= height * 0.7:  # 调整阈值以优先垂直分割
            # 垂直分割
            left_width = width * left_ratio / (left_ratio + right_ratio)
            split_area(x, y, left_width, height, left_indices)
            split_area(x + left_width, y, width - left_width, height, right_indices)
        else:
            # 水平分割
            bottom_height = height * left_ratio / (left_ratio + right_ratio)
            split_area(x, y, width, bottom_height, left_indices)
            split_area(x, y + bottom_height, width, height - bottom_height, right_indices)

    # 按比例从大到小排序索引
    indices = list(range(len(ratios)))
    indices.sort(key=lambda i: ratios[i], reverse=True)

    # 初始调用
    split_area(0, 0, 1, 1, indices)

    return rectangles


def generate_colors(n):
    """
    生成n个不同的颜色

    参数:
    n: 需要生成的颜色数量

    返回:
    包含n个颜色的列表
    """
    colors = []
    for i in range(n):
        # 使用HSV色彩空间生成均匀分布的颜色
        hue = i / n
        saturation = 0.3 + random.random() * 0.2  # 0.7-1.0的饱和度
        value = 0.6 + random.random() * 0.4  # 0.6-1.0的明度
        rgb = hsv_to_rgb([hue, saturation, value])
        colors.append(rgb)

    # 随机打乱颜色顺序，使颜色分布更自然
    random.shuffle(colors)
    return colors


def is_dark_color(color):
    """
    判断颜色是否为深色

    参数:
    color: RGB颜色值

    返回:
    如果是深色返回True，否则返回False
    """
    # 计算颜色的亮度
    brightness = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    return brightness < 0.5


def example_usage():
    """
    示例用法
    """
    # 示例比例
    ratios = [
        0.011, 0.130, 0.011, 0.011, 0.022, 0.022, 0.011, 0.033, 0.022, 0.011,
        0.022, 0.011, 0.152, 0.011, 0.022, 0.022, 0.065, 0.011, 0.011, 0.054,
        0.011, 0.033, 0.011, 0.022, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
        0.011, 0.011, 0.022, 0.011, 0.022, 0.011, 0.011, 0.011, 0.011, 0.011,
        0.011, 0.011, 0.011, 0.011, 0.011, 0.011
    ]

    # 示例标签 (修复了缺失的'95'标签)
    labels = [
        '58', '60', '62', '64', '67', '68', '69', '70', '72', '74',
        '76', '78', '80', '82', '86', '88', '90', '92', '95', '96',
        '98', '100', '105', '106', '107', '109', '110', '116', '118', '122',
        '123', '126', '128', '129', '131', '138', '150', '156', '160', '165',
        '186', '240', '252', '254', '270', '388'
    ]

    # 检查并修正数组长度不匹配问题
    if len(ratios) != len(labels):
        print(f"Warning: Array length mismatch - ratios: {len(ratios)}, labels: {len(labels)}")
        min_length = min(len(ratios), len(labels))
        ratios = ratios[:min_length]
        labels = labels[:min_length]
        print(f"Adjusted to common length: {min_length}")

    # 检查并修正比例总和问题 (使用 math.isclose 处理浮点数精度)
    total_ratio = sum(ratios)
    if not math.isclose(total_ratio, 1.0, rel_tol=1e-9):
        print(f"Warning: Ratios sum to {total_ratio}, adjusting to make sum equal 1.0")
        # 通过缩放所有比例来使其总和为1
        ratios = [r / total_ratio for r in ratios]
        print(f"Adjusted sum: {sum(ratios)}")

    # 绘制矩形
    print("Drawing rectangles with ratios:", ratios)
    print("And labels:", labels)
    draw_rectangles_by_ratio(ratios, labels)

    # 验证矩形是否完全填满正方形
    rectangles = layout_rectangles_exact(ratios)
    total_area = sum(rect[2] * rect[3] for rect in rectangles)
    print(f"Total area of all rectangles: {total_area:.6f} (should be 1.000000)")

    # 检查是否有重叠或间隙
    print("Verifying rectangle layout...")
    for i, rect1 in enumerate(rectangles):
        x1, y1, w1, h1 = rect1
        for j, rect2 in enumerate(rectangles):
            if i >= j:
                continue
            x2, y2, w2, h2 = rect2
            # 检查是否重叠
            if (x1 < x2 + w2 and x1 + w1 > x2 and
                    y1 < y2 + h2 and y1 + h1 > y2):
                print(f"Warning: Rectangles {i} and {j} overlap!")

    print("Verification complete.")


if __name__ == "__main__":
    example_usage()
