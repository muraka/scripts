#!/usr/bin/python3

import sys
import os
import argparse
import subprocess
import glob
import pathlib


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package" , type = str, help = "required");
    parser.add_argument("--version" , type = str, help = "required");
    parser.add_argument("--src-dir" , type = str, help = "required");
    parser.add_argument("--dst-dir" , type = str, help = "required");
    parser.add_argument("--log-file", type = str);
    
    args = parser.parse_args()
    return(args)
    
def runCommand(cmd, show = False):
    if show:
        print("command: " + cmd + "\n")
    
    subprocess.run([cmd], shell=True, stdout=subprocess.PIPE)
    
def runCommandAndGetResult(cmd, show = False):
    tmp = subprocess.getoutput(cmd + "; echo $?").split("\n")
    status = tmp.pop()
    output = "\n".join(tmp)
    
    if show:
        print("command: " + cmd)
        print("output : " + output)
        print("status : " + status)
        
    return {"output": output, "status": status}

def mkdirIfNotExists(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
        print(dir + " has generated")
        
def remoteFileFound(url):
    ret = runCommandAndGetResult("wget -q --spider " + url, True)
    return ret["status"] == "0"
    

def main():
    args = getArgs()
    error = False
    package  = args.package
    version  = args.version
    src_dir  = str(pathlib.Path(str(args.src_dir)).resolve())
    dst_dir  = str(pathlib.Path(str(args.dst_dir)).resolve())
    log_file = str(pathlib.Path(str(args.log_file)).resolve() or "")
    
    if not package:
        error = True
        print ("--package is required.")
        
    if not version:
        error = True
        print ("--version is required.")
        
    if not src_dir:
        error = True
        print ("--src-dir is required.")
        
    if not dst_dir:
        error = True
        print ("--dst-dir is required.")
        
    if error:
        exit()
    
    print("==== manual_install_debian_pachages.py ====")
    print("package: "  + package)
    print("version: "  + version)
    print("src dir: "  + src_dir)
    print("dst dir: "  + dst_dir)
    print("log file: " + log_file)
    print()
    
    fetchAndInstall(package, version, src_dir, dst_dir, log_file)
    

def fetchAndInstall(package, version, src_dir, dst_dir, log_file):
    first_letter    = package[0:1]
    package_version = package + "_" + version
    package_dir     = src_dir + "/" + package_version
    package_found   = False
    
    for ext in [["xz", "J"], ["bz2", "j"]]:
        package_file_tmp = package_version + ".orig.tar." + ext[0]
        url_tmp = "http://ftp.debian.org/debian/pool/main/" + first_letter + "/" + package + "/" + package_file_tmp
        
        if remoteFileFound(url_tmp):
            package_file      = package_file_tmp
            url               = url_tmp
            decompress_option = ext[1]
            package_found     = True
            break
    
    if not package_found:
        print("NO PACKAGE FOUND")
        exit()
    
    print("url: "+  url)
    mkdirIfNotExists(package_dir)
    runCommand("wget -O - '" + url + "' | tar xf" + decompress_option + " - -C " + package_dir)
    
    work_dir = glob.glob(package_dir + "/*")[0]
    os.chdir(work_dir)
    
    install_cmd = "./configure --prefix=" + dst_dir + " && make && make install"
    ret = runCommandAndGetResult(install_cmd)
    
    if log_file and ret["status"]:
        with open(log_file, "at") as f:
            f.write(runCommandAndGetResult("env LANG=C date ")["output"].strip() + ": " + package_version + "\n")
    

if __name__ == '__main__':
    main()