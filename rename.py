import os

def rename_files(old_names_file, new_names_file):
    try:
        with open(old_names_file, 'r', encoding='utf-8') as old_file, \
             open(new_names_file, 'r', encoding='utf-8') as new_file:
            
            old_names = old_file.readlines()
            new_names = new_file.readlines()
            
            if len(old_names) != len(new_names):
                print("Error: The number of old names and new names do not match.")
                return
            
            for old_name, new_name in zip(old_names, new_names):
                old_name = old_name.strip()
                new_name = new_name.strip()
                
                if not os.path.isfile(old_name):
                    print(f"File not found: {old_name}")
                    continue
                
                # 处理新文件名中的目录结构
                new_dir = os.path.dirname(new_name)
                if new_dir and not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                
                try:
                    os.rename(old_name, new_name)
                    print(f"Renamed: {old_name} -> {new_name}")
                except Exception as e:
                    print(f"Failed to rename {old_name} to {new_name}: {e}")
                    
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    old_names_file = 'old_name.txt'
    new_names_file = 'new_name.txt'
    rename_files(old_names_file, new_names_file)