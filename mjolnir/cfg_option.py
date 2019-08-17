import sys
from config_handler import ConfigHandler

if __name__ == '__main__':
    config_handler = ConfigHandler(sys.argv[1])
    option_dict = config_handler.get_eval_option(sys.argv[2], sys.argv[3])
    print(option_dict[sys.argv[4]])
