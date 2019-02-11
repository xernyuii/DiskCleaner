import sys, getopt
import os
import json

# Usage: CleanToolAdmin.py --mode=protect/force/record/clean --config=conf.json --debug --help

def help():
    print("Usage: CleanToolAdmin.py --mode=protect/force/record/clean --config=conf.json --debug --help")

def main():
    debug = False
    config_file = ""
    parsed_config = ""
    mode = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:c:dh",["mode=", "config=", "debug", "help"])
        print("~",opts)
        print("~",args)
    except getopt.GetoptError:
        print("ERROR: Usage: CleanToolAdmin.py --mode=protect/force/record/clean --config=conf.json --debug --help")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("#help")
            sys.exit()
        elif opt in ("-m", "--mode"):
            inputfile = arg
            print("#mode")
        elif opt in ("-c", "--config"):
            config_file = arg
            with open(config_file, 'r') as jsonfile:
                parsed_config = json.load(jsonfile)
            print(parsed_config)
        elif opt in ("-d", "--debug"):
            debug = True
            print("#debug")
    
    if config_file == "":
        print("ERROR: No config file")
        sys.exit(2)
    elif isinstance(parsed_config["check_num"], int) == False:
        print("ERROR: Config file not correct! (parsed)")
        sys.exit(2)
    elif mode == "":
        print("ERROR: Mode not selected")
        sys.exit(2)

if __name__ == "__main__":
    main()
