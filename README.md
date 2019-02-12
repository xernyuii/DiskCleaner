disk-clean-tool
=======

A tool to safely clean hard drive files according to custom rules.

## Document

Get help from bash
```bash
$ python3 CleanToolAdmin.py --help
```

Use CleanToolAdmin.py to control the action, option "--mode" and "--config" are required.
+ conf.json is for setting options and configuration.
+ record.json is a staging area to record the files scanned.

```bash
Usage: 
    $ python3 CleanToolAdmin.py --mode=normal/record/clean/clear_all/clear_all_unmark --config=conf.json --debug --help
or :
    $ python3 CleanToolAdmin.py -m normal/record/clean/clear_all/clear_all_unmark -c conf.json -d -h
```
### Config file setting
conf.json
```json
{
    "check_num" : 0,
    "OS_type" : "win",
    "set_direction" : "/Users/xern/project/DiskCleaner/test",
    "search_type" : "create_time",
    "set_time" : 0,
    "record_file" : "record.json",
    "log_file" : "recent.log",
}
```
+ "set_direction"   # Direction to start action
    + "set_direction" : "/Users/public" # Do actions in "/Users/public"
    + "set_direction" : "C:\\Users\\public" # Do actions in "C:\Users\public"
+ "search_type" # Searching type, choose one of "create time", "last modified time", "last accessed time"
    + "search_type" : "create_time" # create time
    + "search_type" : "modify_time" # last modified time
    + "search_type" : "access_time" # last accessed time
+ "set_time"    #  Set time
    + "set_time" : 86400 # 1 day
    + "set_time" : 604800 # 7 days
    + "set_time" : 2592000 # 30 days
    + "set_time" : 5184000 # 60 days
    + "set_time" : 31556926 # 1 year
+ "record_file" # File to write record
    + "record_file" : "record.json"
+  "log_file" # File to write logs
    + "log_file" : "recent.log"
    
### Mode Setting

+ normal : search the file and delete all
+ record : just record the file to the record.json
+ clean : just clean file in record.json
+ clear_all : remove all records in record.json
+ clear_all_unmark : remove records except marked

### Quick Start
```bash
$ cp conf.example.json conf.json
$ # Config conf.json
$ python3 CleanToolAdmin.py --mode=record --config=conf.json --debug # record
$ # check record.json
$ python3 CleanToolAdmin.py --mode=clean --config=conf.json --debug
```
