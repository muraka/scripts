#!/usr/bin/python3

import sys
import os
import argparse
import subprocess
import glob


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type = str, help = "required");
    parser.add_argument("--version", type = str, help = "required");
    parser.add_argument("--src-dir", type = str, help = "required");
    parser.add_argument("--dst-dir", type = str, help = "required");
    
    args = parser.parse_args()
    return(args)
    
def runCommand(cmd, show = False):
    if show:
        print("command: " + cmd + "\n")
    
    subprocess.run([cmd], shell=True, stdout=subprocess.PIPE)
    
def runCommandAndGetResult(cmd, show=False):
    if show:
        print("command: " + cmd + "\n")
        
    return subprocess.getoutput(cmd)

def mkdirIfNotExists(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
        print(dir + " has generated")
        
def remoteFileFound(url):
    result = runCommandAndGetResult("wget -q --spider " + url + "; echo $?")
    return result == "0"

def main():
    args = getArgs()
    error = False
    package = args.package
    version = args.version
    src_dir = args.src_dir
    dst_dir = args.dst_dir
    
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
        
    print("package: " + package)
    print("version: " + version)
    print("src dir: " + src_dir)
    print("dst dir: " + dst_dir)
    
    fetchAndInstall(package, version, src_dir, dst_dir)
    

def fetchAndInstall(package, version, src_dir, dst_dir):
    first_letter    = package[0:1]
    package_version = package + "_" + version
    package_dir     = src_dir + "/" + package_version
    
    for ext in [["xz", "J"], ["bz2", "j"]]:
        package_file_tmp = package_version + ".orig.tar." + ext[0]
        url_tmp = "http://ftp.debian.org/debian/pool/main/" + first_letter + "/" + package + "/" + package_file_tmp
        
        if remoteFileFound(url_tmp):
            package_file      = package_file_tmp
            url               = url_tmp
            decompress_option = ext[1]
            break
          
    print("url: "+  url)
    mkdirIfNotExists(package_dir)
    runCommand("wget -O - '" + url + "' | tar xf" + decompress_option + " - -C " + package_dir)
    
    work_dir = glob.glob(package_dir + "/*")[0]
    os.chdir(work_dir)
    
    install_cmd  = "./configure --prefix=" + dst_dir + " && make && make install"
    runCommand(install_cmd)
    

if __name__ == '__main__':
    main()