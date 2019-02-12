import sys
import getopt
import os
import json
import time

# Usage: CleanToolAdmin.py --mode=protect/force/record/clean --config=conf.json --debug --help

def help():
    print("Usage: CleanToolAdmin.py --mode=protect/force/record/clean --config=conf.json --debug --help")

def args_check(config_file, mode, parsed_config):
    #print(parsed_config)
    if config_file == "":
        print("ERROR: No config file.")
        sys.exit(2)
    elif isinstance(parsed_config["check_num"], int) == False:
        print("ERROR: Config file not correct! (parsed)")
        sys.exit(2)
    elif mode not in {"normal", "protect", "force", "record", "clean", "clear_all"}:
        print("ERROR: Mode not correct.")
        sys.exit(2)

def args_parse():
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
                #print(parsed_config)
        elif opt in ("-d", "--debug"):
            debug = True
            print("#debug", debug)
    return debug, config_file, mode, parsed_config

def rcs_search(parsed_config, parsed_record_file):
    search_type = parsed_config["search_type"]
    set_time = parsed_config["set_time"]
    set_direction = parsed_config["set_direction"]
    #parsed_record_file = {}
    now = time.time()
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    for path, dirs, files in os.walk(set_direction):
        for name in files:
            fullpath = os.path.join(path, name)
            if os.path.exists(fullpath):
                mtime = os.path.getmtime(fullpath)
                fsize = os.path.getsize(fullpath) / (1024)
                # if (now - mtime) > set_time:
                #     print(fullpath)
                # print(fullpath)
                if fullpath in parsed_record_file["files_on_mark"].keys():
                    flag = "mark again"
                else:
                    flag = "mark"
                parsed_record_file["files_on_mark"][fullpath] = {"state" : flag, "search_type" : search_type, "time_res" : set_time, "size" : str(fsize) + " KB", "search_date" : local_time}
    

def do_record(record_file, parsed_record_file):
    with open(record_file,"w") as dump_f:
        json.dump(parsed_record_file, dump_f, indent=4, separators=(',', ':'))

def do_delete_from_parsed_record_file(parsed_record_file):
    for fullpath in parsed_record_file["files_on_mark"]:
        if os.path.exists(fullpath) == True :
            try:
                print("delete", fullpath)
            except OSError as err:
                print("OSError: {0}".format(err))
                parsed_record_file["files_on_mark"][fullpath]["state"] = "error during delete"
            else:
                parsed_record_file["files_on_mark"][fullpath]["state"] = "cleaned"
        else:
            parsed_record_file["files_on_mark"][fullpath]["state"] = "not exist"

def load_parsed_record_file_from_record_file(record_file):
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if os.path.exists(record_file):
        with open(record_file, 'r') as recordfile:
            parsed_record_file = json.load(recordfile)
        parsed_record_file["last_modified_date"] = local_time
    else:
        parsed_record_file = {"last_modified_date" : local_time, "files_on_mark" : {}}

    return parsed_record_file

def update_state_from_parsed_record_file(parsed_record_file):
    for fullpath in parsed_record_file["files_on_mark"]:
        if os.path.exists(fullpath) == True :
            parsed_record_file["files_on_mark"][fullpath]["state"] = "mark again"
        else:
            parsed_record_file["files_on_mark"][fullpath]["state"] = "not exist"

def clear_all_record(parsed_record_file):
    parsed_record_file["files_on_mark"].clear()

def mode_action(mode, parsed_config):

    record_file = parsed_config["record_file"]

    if mode == "normal":
        parsed_record_file = load_parsed_record_file_from_record_file(record_file)
        rcs_search(parsed_config, parsed_record_file)
        do_delete_from_parsed_record_file(parsed_record_file)
        do_record(record_file, parsed_record_file)
    elif mode == "record":
        parsed_record_file = load_parsed_record_file_from_record_file(record_file)
        rcs_search(parsed_config, parsed_record_file)
        do_record(record_file, parsed_record_file)
    elif mode == "clean":
        parsed_record_file = load_parsed_record_file_from_record_file(record_file)
        do_delete_from_parsed_record_file(parsed_record_file)
        do_record(record_file, parsed_record_file)
    elif mode == "check":
        parsed_record_file = load_parsed_record_file_from_record_file(record_file)
        update_state_from_parsed_record_file(parsed_record_file)
        do_record(record_file, parsed_record_file)
    elif mode == "clear_all":
        parsed_record_file = load_parsed_record_file_from_record_file(record_file)
        clear_all_record(parsed_record_file)
        do_record(record_file, parsed_record_file)

def main():

    # Parse args and check
    debug, config_file, mode ,parsed_config = args_parse()
    args_check(config_file, mode, parsed_config)

    # Serach the direction recursively
    
    # Do actions
    mode_action(mode, parsed_config)

if __name__ == "__main__":
    main()


# normal : load(from record) & search & delete & record 
# record : load(from record) & search & record(mark)
# clean : delete (in record) & record
# check : update (in record) & record
# clear_all : clear record