#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 12:12:43 2019

@author: polina
"""

######################################################################################
#
# The directory containing all subjects to be preprocessed is to be passed as
# a command line argument, e.g. run_fslfeat '/media/sf_Z_DRIVE/DRYRep' and has 
# to contain the template.fsf FEAT setup file template
#
# Each subjects' directory is expected to contain the following structure:
#       /02REST/ dir containing the NIFTI image
#       /01Struct/ dir containing the structural data NIFTI
#       /02REST/Sess1/ subdir holding .txt with movement parameters used in ICA-AROMA
#
######################################################################################

import os
import sys
import glob
import pexpect as p
import argparse
import sys
import time
import threading

parser = argparse.ArgumentParser()
parser.add_argument('text', nargs='*')
parser.add_argument("input_dir", help="the directory containing all subjects to be preprocessed")
args = parser.parse_args()

inputDir=args.input_dir
outputDir=inputDir + "/output/"
fourDdir ="/02REST/"
structDir="/01Struct/"
mvmntParamDir ="/02REST/Sess1/"
aromaOutputFolder='ICA_AROMA_output'
FSL_template_file='template.fsf'



class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False




if not os.path.exists(outputDir): os.makedirs(outputDir)

# Check FSL, .fsf setup and ICA_AROMA paths
(command_output, exitstatus) = p.run('whereis feat', withexitstatus=1)
if exitstatus: sys.exit("please install FSL before proceeding!") 
fsl_dir=str.split(command_output)[-1]

(ICA_AROMA, exitstatus) = p.run('locate ICA_AROMA.py', withexitstatus=1)
if exitstatus: sys.exit("please make ICA AROMA available before proceeding!") 

if not os.path.exists("%s/template.fsf"%(inputDir)): sys.exit("No FEAT setup template file found in %s, exiting script"%(inputDir)) 


# Iterate subjects
subdirs=glob.glob("%s/hum_*"%(inputDir))
with Spinner():
    for dir in list(subdirs):
      splitdir = dir.split('/')
      subj_id = splitdir[-1:]
     
      image=glob.glob("%s%s*.nii"%(dir,fourDdir))[0]
      struct_image=glob.glob("%s%s*.nii"%(dir,structDir))[0]
      
      # create an .fsf input for FSL 
      replacements = {'4D_DATA':image, 'STRUCT_IMAGE':struct_image, 'OUTPUT_DIR':outputDir}
      design_file="%sdesign_%s.fsf"%(outputDir, subj_id[0])
      with open("%s/%s"%(inputDir, FSL_template_file)) as infile: 
        with open(design_file, 'w') as outfile:
            for line in infile: 
              for src, target in replacements.items():
                line = line.replace(src, str(target))
              outfile.write(line)
       
        # run FSL
        cmd = '%s %s' % (fsl_dir, design_file)
        print('*********************** processing subject %s'%subj_id[0])
        print('running FSL')
        child = p.spawn(cmd)
        child.logfile = sys.stdout
        child.wait()
         
        mvntFile=glob.glob("%s/%s%s*.txt"%(inputDir,subj_id[0], mvmntParamDir))
        aromaInputDir=glob.glob("%s/%s%s*_output*.feat"%(inputDir, subj_id[0], fourDdir))[0]
        aromaOutputFileName='%s/%s'%(aromaInputDir,aromaOutputFolder)
      
        # run ICA-AROMA
        cmd = 'python %s -feat %s -out %s -mc %s -tr 2.0 -overwrite' % (ICA_AROMA, aromaInputDir, aromaOutputFileName,mvntFile[0])
        print('running ICA-AROMA ')
        child = p.spawn(cmd)
        child.logfile = sys.stdout
        child.wait()
        print('*********************** done with subject %s'%subj_id[0])
print('FINISHED JOB!')


