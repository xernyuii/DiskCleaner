import sys
import getopt
import os
import json
import time
import logging
import logging.config

# Usage: CleanToolAdmin.py --mode=normal/record/clean/clear_all/clear_all_unmark --config=conf.json --debug --help

def help():
    print("Usage: CleanToolAdmin.py --mode=normal/record/clean/clear_all/clear_all_unmark --config=conf.json --debug --help")

def args_check(config_file, mode, parsed_config):
    #print(parsed_config)
    if config_file == "":
        print("ERROR: No config file.")
        sys.exit(2)
    elif isinstance(parsed_config["check_num"], int) == False:
        print("ERROR: Config file not correct! (parsed)")
        sys.exit(2)
    elif mode not in {"normal", "protect", "force", "record", "clean", "clear_all", "clear_all_unmark"}:
        print("Warning: Mode not set by arg.")

def args_parse():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:c:dh",["mode=", "config=", "debug", "help"])
    except getopt.GetoptError:
        print("ERROR: Usage error")
        help()
        sys.exit(2)
    mode = ""
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("#help")
            help()
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
            print("#mode", mode)
        elif opt in ("-c", "--config"):
            config_file = arg
            with open(config_file, 'r') as jsonfile:
                parsed_config = json.load(jsonfile)
                #print(parsed_config)
        elif opt in ("-d", "--debug"):
            debug = True
            print("#debug", debug)
    return debug, config_file, mode, parsed_config

def set_unit(fsize):
    if fsize < 1024:
        fsize = fsize
        unit = "B"
    elif fsize < (1024 * 1024):
        fsize = fsize / (1024)
        unit = "KB"
    elif fsize < (1024 * 1024 * 1024):
        fsize = fsize / (1024 * 1024)
        unit = "MB"
    else:
        fsize = fsize / (1024 * 1024 * 1024)
        unit = "GB"

    return unit

def dfs(target_direction, search_type, set_time, now, local_time, only, parsed_record_file, parsed_config):
    for path, dirs, files in os.walk(target_direction):
        #print(dirs)
        for name in files:
            if parsed_config["custom_rules"]["is_enable"] != []:
                if os.path.splitext(name)[-1][1:] not in only:
                    continue
            fullpath = os.path.join(path, name)
            logging.info("%r scan %r",local_time, fullpath)
            if os.path.exists(fullpath):

                if search_type == "create_time":
                    ftime = os.path.getctime(fullpath)
                elif search_type == "modify_time":
                    ftime = os.path.getmtime(fullpath)
                elif search_type == "access_time":
                    ftime = os.path.getmtime(fullpath)
                
                if (now - ftime) >= set_time:
                    fsize = os.path.getsize(fullpath)
                    
                    unit = set_unit(fsize)

                    ftime_local = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ftime))
                    if fullpath in parsed_record_file["files_on_mark"].keys():
                        flag = "mark again"
                    else:
                        flag = "mark"
                    parsed_record_file["files_on_mark"][fullpath] = {"state" : flag, "search_type" : search_type, "ftime" : ftime, "ftime_local" : ftime_local, "time_set" : set_time, "size" : str(fsize) + " " + unit, "search_date" : local_time}
        
    # for root, dirs, files in os.walk(target_direction, topdown=False):
    #     if not files and not dirs:
    #         print("!"+root)

def rcs_search(parsed_config, parsed_record_file):
    search_type = parsed_config["search_type"]
    set_time = parsed_config["set_time"]
    set_direction = parsed_config["set_direction"]
    #parsed_record_file = {}
    now = time.time()
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logging.info("\n### Start %r search_type:%r set_time:%r set_direction%r", local_time, search_type, set_time, set_direction)
    only = set()
    for rule_name in parsed_config["custom_rules"]["is_enable"]:
        for rule in parsed_config["custom_rules"][rule_name]["rules"]:
            only.add(rule)
    #print(only)
    for target_direction in set_direction:
        dfs(target_direction, search_type, set_time, now, local_time, only, parsed_record_file, parsed_config)

def do_record(record_file, parsed_record_file):
    with open(record_file,"w") as dump_f:
        json.dump(parsed_record_file, dump_f, indent=4, separators=(',', ':'))

def do_delete_from_parsed_record_file(parsed_record_file):
    for fullpath in parsed_record_file["files_on_mark"]:
        if os.path.isfile(fullpath) == True :
            try:
                os.remove(fullpath)
                logging.info("delete %r", fullpath)
            except OSError as err:
                logging.error("OSError: {0}".format(err))
                parsed_record_file["files_on_mark"][fullpath]["state"] = "error during delete"
            else:
                parsed_record_file["files_on_mark"][fullpath]["state"] = "cleaned"
        elif os.path.isdir(fullpath) == True :
            try:
                os.remove(fullpath)
                logging.info("delete %r", fullpath)
            except OSError as err:
                logging.error("OSError: {0}".format(err))
                parsed_record_file["files_on_mark"][fullpath]["state"] = "error during delete"
            else:
                parsed_record_file["files_on_mark"][fullpath]["state"] = "cleaned"
        else:
            parsed_record_file["files_on_mark"][fullpath]["state"] = "not exist"

def do_delete_empty_dir(parsed_config):
    set_direction = parsed_config["set_direction"]
    for target_direction in set_direction:
        for root, dirs, files in os.walk(target_direction, topdown=False):
            # print("#", root)
            # print(os.listdir(root))
            if not os.listdir(root):
                os.rmdir(root)
                logging.info("delete dir %r", root)

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

def clear_all_record_unmark(parsed_record_file):
    ready_clear_record = []
    for fullpath in parsed_record_file["files_on_mark"]:
        if parsed_record_file["files_on_mark"][fullpath]["state"] in {"not exist", "cleaned"}:
            ready_clear_record.append(fullpath)
    
    for fullpath in ready_clear_record:
        parsed_record_file["files_on_mark"].pop(fullpath)

def mode_action(mode, parsed_config):

    record_file = parsed_config["record_file"]
    if mode == "":
        mode = parsed_config["default_mode"]
        logging.warning("Mode set by config %r", mode)

    if mode == "normal":
        parsed_record_file = load_parsed_record_file_from_record_file(record_file)
        rcs_search(parsed_config, parsed_record_file)
        do_delete_from_parsed_record_file(parsed_record_file)
        do_delete_empty_dir(parsed_config)
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
    elif mode == "clear_all_unmark":
        parsed_record_file = load_parsed_record_file_from_record_file(record_file)
        clear_all_record_unmark(parsed_record_file)
        do_record(record_file, parsed_record_file)   

def main():

    # Parse args and check
    debug, config_file, mode ,parsed_config = args_parse()
    args_check(config_file, mode, parsed_config)
    if debug == True:
        logging.basicConfig(filename = parsed_config["log_file"],level = logging.DEBUG)
    else:
        logging.basicConfig(filename = parsed_config["log_file"],level = logging.INFO)
    # Do actions
    mode_action(mode, parsed_config)
    logging.info("\n### End")

if __name__ == "__main__":
    main()

# normal : load(from record) & search & delete & record
# record : load(from record) & search & record(mark)
# clean : delete (in record) & record
# check : update (in record) & record
# clear_all : clear record
# clear_all_unmark : clear record cleaned & not exist