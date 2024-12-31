import os

# 初始化变量
start_num = 1    # 起始编号
end_num = 17000  # 结束编号
missing_files = []  # 存储缺失的文件编号

# 读取文件路径列表
with open('new_name.txt', 'r') as file:
    existing_file_paths = [line.strip() for line in file]

# 创建一个集合，用于快速查找现有文件名
existing_filenames = set()
for path in existing_file_paths:
    filename = os.path.basename(path)  # 提取文件名
    existing_filenames.add(filename)

# 检查每个编号的文件是否存在
for num in range(start_num, end_num + 1):
    filename = f"A{num:05d}.azw3"  # 格式化文件名，确保编号是5位数
    if filename not in existing_filenames:
        missing_files.append(filename)

# 输出缺失的文件
if missing_files:
    print("以下文件缺失：")
    for mf in missing_files:
        print(mf)
else:
    print("没有缺失的文件。")
