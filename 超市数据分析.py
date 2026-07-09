import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ========== 第1块：导入库 + 读取数据 ==========
# 设置中文显示（Windows系统，优先用微软雅黑）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据（路径改成你自己的）
df = pd.read_csv(r"C:\python123\SampleSuperstore.csv", encoding='latin-1')

# 查看数据基本情况
print("数据形状：", df.shape)
print("\n字段名：", df.columns.tolist())
print("\n前5行：")
print(df.head())
print("\n数据类型：")
print(df.dtypes)

# ========== 第2块：数据清洗 ==========
# 1. 缺失值统计
print("\n===== 缺失值统计 =====")
print(df.isnull().sum())

# 2. 新增衍生字段：利润率
df['Profit Rate'] = df['Profit'] / df['Sales']

# 3. 重复值检查
dup_count = df.duplicated().sum()
print(f"\n重复行数：{dup_count}")
if dup_count > 0:
    df = df.drop_duplicates()
    print(f"已删除重复值，剩余 {len(df)} 行")

# 4. 数值字段统计
print("\n===== 数值字段统计 =====")
print(df[['Sales', 'Quantity', 'Discount', 'Profit']].describe())

# 保存清洗后的数据
df.to_csv('superstore_cleaned.csv', index=False, encoding='utf-8-sig')
print("\n数据清洗完成，已保存 superstore_cleaned.csv")

# ========== 第3块：品类分析（大类 + 子品类） ==========
# ===== 大类分析 =====
category_stats = df.groupby('Category').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum'
}).reset_index()
category_stats['利润率'] = category_stats['Profit'] / category_stats['Sales']

print("\n===== 各大类销售情况 =====")
print(category_stats.sort_values('Sales', ascending=False))

# 画柱状图：销售额 vs 利润
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(category_stats))
width = 0.35
ax.bar(x - width/2, category_stats['Sales'], width, label='销售额', color='#4C72B0')
ax.bar(x + width/2, category_stats['Profit'], width, label='利润', color='#55A868')
ax.set_xticks(x)
ax.set_xticklabels(category_stats['Category'])
ax.set_ylabel('金额')
ax.set_title('各品类销售额与利润对比')
ax.legend()
plt.savefig('01_品类销售对比.png', dpi=150, bbox_inches='tight')
plt.show()

# ===== 子品类利润排行 =====
sub_cat = df.groupby('Sub-Category').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).sort_values('Profit', ascending=True)

plt.figure(figsize=(12, 8))
colors = ['#C44E52' if x < 0 else '#55A868' for x in sub_cat['Profit']]
sub_cat['Profit'].plot(kind='barh', color=colors)
plt.title('各子品类利润排行（红色为亏损）')
plt.xlabel('利润')
plt.tight_layout()
plt.savefig('02_子品类利润排行.png', dpi=150)
plt.show()

# ========== 第4块：地区分析 ==========
region_stats = df.groupby('Region').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index()
region_stats['利润率'] = region_stats['Profit'] / region_stats['Sales']

print("\n===== 各地区销售情况 =====")
print(region_stats.sort_values('Sales', ascending=False))

# 饼图：地区销售额占比
plt.figure(figsize=(8, 8))
plt.pie(region_stats['Sales'], labels=region_stats['Region'], 
        autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set2'))
plt.title('各地区销售额占比')
plt.savefig('03_地区销售占比.png', dpi=150)
plt.show()

# ========== 第5块：折扣与利润关系 ==========
# 按折扣率分组统计平均利润率
discount_profit = df.groupby('Discount')['Profit Rate'].mean().reset_index()

plt.figure(figsize=(10, 6))
sns.lineplot(data=discount_profit, x='Discount', y='Profit Rate', marker='o')
plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)
plt.title('折扣率与利润率的关系')
plt.xlabel('折扣率')
plt.ylabel('平均利润率')
plt.grid(alpha=0.3)
plt.savefig('04_折扣与利润率关系.png', dpi=150)
plt.show()

# 找出亏损临界点
loss_discount = discount_profit[discount_profit['Profit Rate'] < 0]['Discount'].min()
print(f"\n当折扣率 >= {loss_discount} 时，平均利润率转为亏损")

# ========== 第6块：输出分析结论 ==========
worst_subcat = sub_cat['Profit'].idxmin()
best_cat = category_stats.loc[category_stats['Sales'].idxmax(), 'Category']
best_region = region_stats.loc[region_stats['Sales'].idxmax(), 'Region']

print("\n" + "=" * 50)
print("【核心分析结论】")
print("=" * 50)

print(f"\n1. 品类表现：")
print(f"   - 销售额最高的大类：{best_cat}")
print(f"   - 亏损最严重的子品类：{worst_subcat}")
print(f"   - 建议：排查亏损子品类的成本与折扣策略")

print(f"\n2. 地区表现：")
print(f"   - 销售额最高的地区：{best_region}")
print(f"   - 建议：资源向高产出地区倾斜，薄弱地区调研原因")

print(f"\n3. 折扣策略：")
print(f"   - 折扣率超过 {loss_discount} 后单品转为亏损")
print(f"   - 建议：控制折扣力度上限，评估高折扣活动的整体ROI")

print("\n" + "=" * 50)
print("\n全部分析完成！生成了 4 张图片和 1 个清洗后的数据文件。")
