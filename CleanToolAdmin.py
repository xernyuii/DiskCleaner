import sys
import getopt
import os
import json
import time

# Usage: CleanToolAdmin.py --mode=protect/force/record/clean --config=conf.json --debug --help

def help():
    print("Usage: CleanToolAdmin.py --mode=protect/force/record/clean --config=conf.json --debug --help")

def main():
    debug = False
    config_file = ""
    parsed_config = ""
    mode = ""

    # parse arguments
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
            help()
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
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

    # config file arguments
    search_type = parsed_config["search_type"]
    set_time = parsed_config["set_time"]
    set_direction = parsed_config["set_direction"]
    record_file = parsed_config["record_file"]
    parsed_record_file = {}

    now = time.time()
    if os.path.exists(record_file):
        with open(record_file, 'r') as recordfile:
            parsed_record_file = json.load(recordfile)
        parsed_record_file["last_modified_date"]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    else:
        parsed_record_file = {"last_modified_date" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "files_on_mark" : {}}
    
    for path, dirs, files in os.walk(set_direction):
        for name in files:
            fullpath = os.path.join(path, name)
            if os.path.exists(fullpath):
                mtime = os.path.getmtime(fullpath)
                # if (now - mtime) > set_time:
                #     print(fullpath)
                print(fullpath)                
                parsed_record_file["files_on_mark"][fullpath] = {"state" : "mark", "search_type" : search_type, "time_res" : "1000", "size" : "100", "search_date" : "2019-1-1"}

    with open(record_file,"w") as dump_f:
        json.dump(parsed_record_file, dump_f, indent=4, separators=(',', ':'))

if __name__ == "__main__":
    main()
