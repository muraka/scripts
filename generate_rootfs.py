#!/usr/bin/python3

import sys
import os
import argparse
import subprocess
import glob
import pathlib
import time
import json


installer = ""


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type = str, help = "required");
    parser.add_argument("--src-dir" , type = str, help = "required");
    parser.add_argument("--dst-dir" , type = str, help = "required");
    parser.add_argument("--log-file", type = str);
    parser.add_argument("--tar-src" , type = str, help = "required");
    parser.add_argument("--tar-dst" , type = str, help = "required");
    
    args = parser.parse_args()
    return(args)


def runCommand(cmd, show = False):
    tmp = subprocess.getoutput(cmd + "; echo $?").split("\n")
    status = tmp.pop()
    output = "\n".join(tmp)
    
    if show:
        print("command: " + cmd)
        print("output : " + output)
        print("status : " + status)
        
    return {"output": output, "status": status}


def loadJson(file_full_path):
    with open(file_full_path, "r") as f:
        return json.load(f)


def main():
    global installer
    args = getArgs()
    error = False
        
    if not args.settings:
        error = True
        print ("--settings is required.")
        
    if not args.src_dir:
        error = True
        print ("--src-dir is required.")
        
    if not args.dst_dir:
        error = True
        print ("--dst-dir is required.")
        
    if not args.tar_src:
        error = True
        print ("--tar-src is required.")
        
    if not args.tar_dst:
        error = True
        print ("--tar-dst is required.")
        
    if error:
        exit()
        
    settings_file = str(pathlib.Path(str(args.settings)).resolve())
    src_dir       = str(pathlib.Path(str(args.src_dir)).resolve())
    dst_dir       = str(pathlib.Path(str(args.dst_dir)).resolve())
    log_file      = str(pathlib.Path(str(args.log_file)).resolve() or "")
    tar_src       = str(pathlib.Path(str(args.tar_src)).resolve())
    tar_dst       = str(pathlib.Path(str(args.tar_dst)).resolve())
    
    settings = loadJson(settings_file)
    
    print("==== generate_rootfs.py ====")
    print("settings file: " + settings_file)
    print("src dir:       " + src_dir)
    print("dst dir:       " + dst_dir)
    print("log file:      " + log_file)
    print("tar src:       " + tar_src)
    print("tar dst:       " + tar_dst)
    print()
    
    this_file_dir = "/".join(str(pathlib.Path(str(__file__)).resolve()).split("/")[0:-1])
    installer = this_file_dir + "/manual_install_debian_pachage.py"
    
    all_completed = installAll(settings, src_dir, dst_dir, log_file, tar_src, tar_dst)
    if all_completed:
        print("===============================")
        print("======== ALL COMPLETED ========")
        print("===============================")


def installAll(settings, src_dir, dst_dir, log_file, tar_src, tar_dst):
    log_file_obj = open(log_file, "at")
    
    for version in settings:
        log_file_obj.write("======== " + version + " ========\n")
        
        log_file_obj.write("latest:\n")
        print("latest")
        for package in settings[version]["latest"]:
            completed = install(package["package"], package["version"], src_dir, dst_dir, log_file)
            if not completed:
                log_file_obj.close()
                return False
        
        log_file_obj.write("not latest:\n")
        print("not latest")
        for package in settings[version]["not latest"]:
            completed = install(package["package"], package["version"], src_dir, dst_dir, log_file)
            if not completed:
                log_file_obj.close()
                return False
    
    log_file_obj.close()
    return True
    
    
def install(package, version, src_dir, dst_dir, log_file):
    cmd  = "python3 " + installer
    cmd += " --package "  + package
    cmd += " --version "  + version
    cmd += " --src-dir "  + src_dir
    cmd += " --dst-dir "  + dst_dir
    cmd += " --log-file " + log_file
    
    ret = runCommand(cmd, True)
    
    if ret["status"] != "0":
        print("==== ERROR ====")
        print("package: " + package)
        print("version: " + version)
        return False
    
    return True
    

if __name__ == '__main__':
    main()