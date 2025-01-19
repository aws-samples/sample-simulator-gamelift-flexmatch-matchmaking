from lambda_function import lambda_handler,read_json_file
import sys,json,os



# 检查是否有传递参数
if len(sys.argv) > 1:
    # 遍历所有参数
    for arg in sys.argv[1:]:
        # 检查参数是否以 "-" 开头,表示是一个选项
        if arg.startswith("-"):
            # 获取选项名称,去掉前缀 "-"
            option = arg[1:]
            configJson = read_json_file(f"{os.getcwd()}/Multi-pools/Configs/config.json")

            # 根据选项名称执行相应操作
            if option == "help":
                print("Usage: main.py [options] [arguments]")
                print("Options:")
                print("\t-help: Show this help message")
                print("\t-json: output json config")
                print("\t-sample: sample json of a player")
                print("\t-flexmatch: Update flexmatch sets")
                print("\t-benchmark: Start a benchmark")
            elif option == "json":
                if configJson is not None:
                    print(configJson['flexmatch'])
                    print(configJson['benchmark'])
                pass
            elif option == "flexmatch":
                if configJson is not None:
                    lambda_handler(None, configJson)
            elif option == "sample":
                lambda_handler('sample', configJson)
            elif option == "benchmark":
                lambda_handler('benchmark', configJson)
            else:
                print(f"Unknown option: {arg}")
        else:
            # 处理非选项参数
            print(f"Argument: {arg}")
else:
    print("No arguments provided.")
