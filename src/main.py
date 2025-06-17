from gwt import *
from ai_analyse import *
from dotenv import load_dotenv
import os

CONFIG_FILE_NAME = 'config.env'

def get_config_path():
    return os.path.join(os.path.dirname(__file__), f'../{CONFIG_FILE_NAME}')

# Load initial environment variables from the config file.
load_dotenv(dotenv_path=get_config_path())

# Define all expected/required configuration items
EXPECTED_CONFIG = {
    'GEMINI_API_KEY': {
        'prompt_message': '请输入 GEMINI_API_KEY: ',
        'validation': lambda x: bool(x.strip()) # Must not be empty after stripping whitespace
    },
    'USER_TYPE': {
        'prompt_message': '请选择用户类型:\n1. 本科生\n2. 研究生\n3. 留学生\n4. 教师\n请输入用户类型编号（1/2/3/4）: ',
        'validation': lambda x: x.strip() in ['1', '2', '3', '4']
    },
    'DAYS_TO_ANALYZE':{
        'prompt_message': '请输入希望分析的公文通信息天数：',
        'validation': lambda x: x.isdigit(),
    }
    
    # Add more configuration items here in the future
}

def manage_configuration():
    config_path = get_config_path()
    current_file_config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    current_file_config[key.strip()] = value.strip()

    needs_file_update = False

    for key, spec in EXPECTED_CONFIG.items():
        current_value_from_file = current_file_config.get(key)
        is_valid_in_file = current_value_from_file and spec['validation'](current_value_from_file)
        
        if not is_valid_in_file:
            new_value = ""
            while True: # Loop until valid input is provided
                new_value_input = input(spec['prompt_message']).strip()
                if spec['validation'](new_value_input):
                    new_value = new_value_input
                    break
                else:
                    print(f"输入无效，请为 '{key}' 提供有效值。")
            
            current_file_config[key] = new_value # Update our representation of the file's content
            os.environ[key] = new_value         # Update os.environ for the current session
            needs_file_update = True
        else:
            # Value is valid in file. Ensure os.environ matches for this session.
            if os.getenv(key) != current_value_from_file:
                 os.environ[key] = current_value_from_file

    if needs_file_update:
        with open(config_path, 'w', encoding='utf-8') as f:
            for key_to_write, value_to_write in current_file_config.items():
                f.write(f"{key_to_write}={value_to_write}\n")
        print(f"配置已更新并保存到 {config_path}")

    all_configs_ok = True
    for key, spec in EXPECTED_CONFIG.items():
        env_val = os.getenv(key)
        if not env_val or not spec['validation'](env_val):
            print(f"警告: 配置项 '{key}' 未能正确加载或无效。请检查 {config_path}。")
            all_configs_ok = False
    return all_configs_ok

def main():
    if not manage_configuration():
        print("由于配置问题，程序无法继续。")
        return

    # Example usage of loaded configurations:
    api_key = os.getenv('GEMINI_API_KEY')
    user_type_code = os.getenv('USER_TYPE')
    days_to_analyse = int(os.getenv('DAYS_TO_ANALYZE'))
    USER_TYPE_MAP = {
    '1': '本科生',
    '2': '研究生',
    '3': '留学生',
    '4': '教师'
    }
    user_type = USER_TYPE_MAP.get(user_type_code)
    print(f"配置加载成功: API Key (验证通过), User Type: {user_type}")

    get_data_from_gwt()
    gwt_data_raw = get_data_stored(days_to_analyse)
    gwt_classify = ai_classify(user_type, gwt_data_raw)
    output(gwt_classify)

if __name__ == '__main__':
    main()


