import pandas as pd


file_path = "学生问卷172份.xlsx"
sheet_name = "Sheet1"

df = pd.read_excel(file_path, sheet_name=sheet_name)

print("1) 数据行列数")
print(df.shape)
print()

print("2) 列名清单")
print(df.columns.tolist())
print()

print("3) 前5行预览")
print(df.head())
print()

print("4) 每列的数据类型")
print(df.dtypes)