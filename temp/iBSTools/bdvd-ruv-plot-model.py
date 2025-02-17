#!/dcs01/gcode/fdu1/BDT/python/bin/python3.3

"""
bdvd-bam2mat.py

Created by Fang Du on 2014-07-24.
Copyright (c) 2014 Fang Du. All rights reserved.
"""

import sys, traceback,array
import getopt
import subprocess
import os
import shutil
import time
from datetime import datetime, date
import logging
from copy import deepcopy
import pickle

import iBSConfig
import iBSUtil
import iBSDefines
import iBSFCDClient as fcdc
import iBS
import Ice

use_message = '''
BDVD plot model

Usage:
    bdvd-ruv-plot-model.py [options] <--ruv-dir ruv-dir>

Options:
    -v/--version
    -o/--output-dir                <string>    [ default: ./ruvs_out       ]
    -p/--num-threads               <int>       [ default: 4                ]
    -m/--max-mem                   <int>       [ default: 20000            ]
    --tmp-dir                      <dirname>   [ default: <output_dir>/tmp ]

Advanced Options:
    --place-holder

'''

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

output_dir = "./plotModel_out/"
logging_dir = output_dir + "logs/"
fcdcentral_dir = output_dir + "fcdcentral/"
script_dir = output_dir + "script/"
tmp_dir = output_dir + "tmp/"
bdvd_log_handle = None #main log file handle
bdvd_logger = None # main logging object

fcdc_popen = None
fcdc_log_file=None
gParams=None

def init_logger(log_fname):
    global bdvd_logger
    bdvd_logger = logging.getLogger('project')
    formatter = logging.Formatter('%(asctime)s %(message)s', '[%Y-%m-%d %H:%M:%S]')
    bdvd_logger.setLevel(logging.DEBUG)

    # output logging information to stderr
    hstream = logging.StreamHandler(sys.stderr)
    hstream.setFormatter(formatter)
    bdvd_logger.addHandler(hstream)
    
    #
    # Output logging information to file
    if os.path.isfile(log_fname):
        os.remove(log_fname)
    global bdvd_log_handle
    logfh = logging.FileHandler(log_fname)
    logfh.setFormatter(formatter)
    bdvd_logger.addHandler(logfh)
    bdvd_log_handle=logfh.stream

class BDVDParams:

    def __init__(self):

        #max mem allowed in Mb
        self.max_mem = 2000
        self.num_threads = 4
        self.fcdc_fvworker_size=2
        self.fcdc_tcp_port=16000
        self.fcdc_threadpool_size=4
        self.workflow_node = "ruv-plotmodel"
        self.result_dumpfile = None
        self.ruv_dir = None
        self.design_file = None
        self.bdt_home = None
        self.R_bin = iBSConfig.R_BinDir
        self.k = 10
        self.extW = 0 
        
    def parse_options(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], "hvp:m:o:k:n:",
                                        ["version",
                                         "help",
                                         "output-dir=",
                                         "num-threads=",
                                         "max-mem=",
                                         "node=",
                                         "ruv-dir=",
                                         "tmp-dir=",
                                         "bdt-home"])
        except getopt.error as msg:
            raise Usage(msg)

        global output_dir
        global logging_dir
        global tmp_dir
        global fcdcentral_dir
        global script_dir

        custom_tmp_dir = None
        custom_out_dir = None

        # option processing
        for option, value in opts:
            if option in ("-v", "--version"):
                print("BDVD v",iBSUtil.get_version())
                sys.exit(0)
            if option in ("-h", "--help"):
                raise Usage(use_message)
            if option in ("-p", "--num-threads"):
                self.num_threads = int(value)
                self.fcdc_fvworker_size = 2
            if option in ("-m", "--max-mem"):
                self.max_mem = int(value)
            if option in ("-o", "--output-dir"):
                custom_out_dir = value + "/"
            if option == "--tmp-dir":
                custom_tmp_dir = value + "/"
            if option == "--node":
                self.workflow_node = value
            if option =="--ruv-dir":
                self.ruv_dir = value
            if option =="--bdt-home":
                self.bdt_home = value
 
        self.result_dumpfile = "{0}.pickle".format(self.workflow_node)
        if custom_out_dir:
            output_dir = custom_out_dir
            logging_dir = output_dir + "logs/"
            tmp_dir = output_dir + "tmp/"
            fcdcentral_dir = output_dir + "fcdcentral/"
            script_dir = output_dir + "script/"
        if custom_tmp_dir:
            tmp_dir = custom_tmp_dir

        if self.ruv_dir is not None:
            fcdcentral_dir = self.ruv_dir+"/fcdcentral/"
        
        if len(args) < 1:
            raise Usage(use_message)
        self.design_file = args[0]
        return args

# The BDVD logging formatter
def bdvd_log(out_str):
  if bdvd_logger:
       bdvd_logger.info(out_str)

# error msg
def bdvd_logp(out_str=""):
    print(out_str,file=sys.stderr)
    if bdvd_log_handle:
        print(out_str, file=bdvd_log_handle)

def die(msg=None):
    global fcdc_popen
    if msg is not None:
        bdvd_logp(msg)
    shutdownFCDCentral()
    sys.exit(1)

def shutdownFCDCentral():
    global fcdc_popen
    if fcdc_popen is not None:
        fcdc_popen.terminate()
        fcdc_popen.wait()
        fcdc_popen = None
        bdvd_log("FCDCentral shutdown")
    if fcdc_log_file is not None:
        fcdc_log_file.close()

# Ensures that the output, logging, and temp directories are present. If not,
# they are created
def prepare_output_dir():
    bdvd_log("Preparing output location "+output_dir)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)       

    if not os.path.exists(logging_dir):
        os.mkdir(logging_dir)
         
    if not os.path.exists(script_dir):
        os.mkdir(script_dir)
    
    shutil.copy(gParams.design_file,"{0}/bdvdRuvPlotModelDesign.py".format(script_dir))

    if not os.path.exists(tmp_dir):
        try:
          os.makedirs(tmp_dir)
        except OSError as o:
          die("\nError creating directory %s (%s)" % (tmp_dir, o))

def prepare_fcdcentral_config(tcpPort,fvWorkerSize, iceThreadPoolSize ):
    infile = open("./iBS/config/FCDCentralServer.config")
    outfile = open(fcdcentral_dir+"FCDCentralServer.config", "w")
    replacements = {"__FCDCentral_TCP_PORT__":str(tcpPort), 
                    "__FeatureValueWorker.Size__":str(fvWorkerSize), 
                    "__Ice.ThreadPool.Server.Size__":str(iceThreadPoolSize)}

    for line in infile:
        for src, target in replacements.items():
            line = line.replace(src, target)
        outfile.write(line)
    infile.close()
    outfile.close()

def launchFCDCentral():
    global fcdc_popen
    global fcdc_log_fhandle
    fcdcentral_path=os.getcwd()+"/iBS/bin/FCDCentral"
    fcdc_cmd = [fcdcentral_path]
    bdvd_log("Launching FCDCentral ...")
    fcdc_log_file = open(logging_dir + "fcdc.log","w")
    fcdc_popen = subprocess.Popen(fcdc_cmd, cwd=fcdcentral_dir, stdout=fcdc_log_file)

def exportModel(facetAdminPrx):
    global gParams
    # configuration by user
    designPath=os.path.abspath(script_dir)
    if designPath not in sys.path:
         sys.path.append(designPath)
    import bdvdRuvPlotModelDesign as design
    gParams.ColIDs =design.ColIDs
    matrix_info_fn="{0}matrix_info.txt".format(output_dir)
    facetID =1
    ruvPrx=facetAdminPrx.GetRUVFacet(facetID)
    (rt, fois) =ruvPrx.GetFeatureObservers([])
    if gParams.ColIDs is None:
        gParams.ColIDs =[v+1 for v in range(len(fois))]
    ruvPrx.SetOutputWorkerNum(gParams.num_threads)
    colCnt=len(fois)
    rowCnt=design.FeatureIdxTo - design.FeatureIdxFrom
    for cp in design.Components:
        (cpName,k,n,RUVOutputMode,RowAdjust)=cp
        ruvPrx.SetActiveK(k,n)
        ruvPrx.SetOutputMode(RUVOutputMode)
        featureIdxFrom = design.FeatureIdxFrom
        featureIdxTo = design.FeatureIdxTo
        bdvd_log("Output {0} ...".format(cpName))
        (rt,values)=ruvPrx.GetRowMatrix([],featureIdxFrom,featureIdxTo,RowAdjust)
        mat = array.array('d') # double
        mat.fromlist(values)
        mat_fn="{0}{1}.bfv".format(output_dir,cpName)
        outf = open(mat_fn, "wb")
        mat.tofile(outf)
        outf.close()


    # output matrix
    matrix_info_fn="{0}model_mats.txt".format(output_dir);
    outf = open(matrix_info_fn, "w")
    outf.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n".format("MatrixID","DataFile","k","extW","RowCnt","ColCnt","RUVOutMode","MatName"))
    i=0
    for cp in design.Components:
        (cpName,k,n,RUVOutputMode,RowAdjust)=cp
        mat_fn="{0}{1}.bfv".format(output_dir,cpName)
        outf.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n".format(
            i+1,mat_fn,k,n,rowCnt,colCnt,RUVOutputMode,cpName))
        i=i+1
    outf.close()

def exportColNames(facetAdminPrx):
    facetID =1
    #(rt,rfi)=facetAdminPrx.GetRUVFacetInfo(facetID)
    ruvPrx=facetAdminPrx.GetRUVFacet(facetID)
    (rt, fois) =ruvPrx.GetFeatureObservers([])
    sampleIDs=[v.ObserverID for v in fois]
    (rt,groupIDs)=ruvPrx.GetConditionIdxs(sampleIDs)
    colNames = [v.ObserverName for v in fois]
    
    #output colNames
    colnames_fn="{0}colnames.txt".format(output_dir);
    outf = open(colnames_fn, "w")
    for i in range(len(colNames)):
        outf.write("{0}\t{1}\n".format(colNames[i],groupIDs[i]+1))
    outf.close()

def prepareRScripts():
    RDir="{0}/R".format(output_dir)
    if not os.path.exists(RDir):
        os.mkdir(RDir)
    
    RScriptDir=os.path.abspath(RDir)

    # ==============================
    # BetaBinFit.R
    infile = open("./iBS/iBS.R/BDVD/Common.R")
    outfile = open(RScriptDir+"/Common.R", "w")

    replacements = {"__NOTHING__":"__SOMETHING__"}

    for line in infile:
        for src, target in replacements.items():
            line = line.replace(src, target)
        outfile.write(line)
    infile.close()
    outfile.close()

    # ==============================
    # RUV_Fstats.R
    infile = open("./iBS/iBS.R/BDVD/RUV_PlotModel.R")
    outfile = open(RScriptDir+"/RUV_PlotModel.R", "w")
    replacements = {"__RSCRIPT_DIR__":RScriptDir,
                    "__DATA_DIR__":output_dir[:-1],
                    "__OUT_DIR__":output_dir[:-1],
                    "__ColIDs__":str(gParams.ColIDs).replace('[','').replace(']',''),
                    }
    for line in infile:
        for src, target in replacements.items():
            line = line.replace(src, target)
        outfile.write(line)
    infile.close()
    outfile.close()

##
## run RUV-RUV_PlotModel.R
##
def runRScript():
    RDir="{0}/R".format(output_dir)
    RScriptDir=os.path.abspath(RDir)

    cmdpath="{0}/Rscript".format(gParams.R_bin)
    r_cmd = [cmdpath,
                "--no-restore",
                "--no-save",
                "{0}/{1}".format(RScriptDir,"RUV_PlotModel.R")]
      
    shell_cmd=""
    for str in r_cmd:
        shell_cmd=shell_cmd+str+" "
    print(shell_cmd)
    subnode = "R"
    bdvd_logp("run subtask at: {0}{1}".format(output_dir,subnode))
    proc = subprocess.call(r_cmd)

def main(argv=None):

    # Initialize default parameter values
    global gParams
    gParams = BDVDParams()
    run_argv = sys.argv[:]

    global fcdc_popen
    fcdc_popen = None

    try:
        if argv is None:
            argv = sys.argv
        args = gParams.parse_options(argv)
       
        start_time = datetime.now()

        prepare_output_dir()
        init_logger(logging_dir + "bdvd.log")

        bdvd_logp()
        bdvd_log("Beginning RUV plot model run (v"+iBSUtil.get_version()+")")
        bdvd_logp("-----------------------------------------------")

        gParams.fcdc_tcp_port = iBSUtil.getUsableTcpPort()
        prepare_fcdcentral_config(gParams.fcdc_tcp_port, 
                                  gParams.fcdc_fvworker_size, 
                                  gParams.fcdc_threadpool_size)
        print("fcdc_tcp_port = ",gParams.fcdc_tcp_port)

        launchFCDCentral()

        fcdc.Init();
        fcdcHost="localhost -p "+str(gParams.fcdc_tcp_port)

        fcdcPrx = None
        tryCnt=0
        while (tryCnt<20) and (fcdcPrx is None):
            try:
                fcdcPrx=fcdc.GetFCDCProxy(fcdcHost)
            except Ice.ConnectionRefusedException as ex:
                tryCnt=tryCnt+1
                time.sleep(1)

        if fcdcPrx is None:
            raise Usage("connection timeout")

        facetAdminPrx=fcdc.GetFacetAdminProxy(fcdcHost)
        computePrx=fcdc.GetComputeProxy(fcdcHost)
        samplePrx=fcdc.GetSeqSampleProxy(fcdcHost)
    
        bdvd_log("FCDCentral activated")
        
        exportModel(facetAdminPrx)
        exportColNames(facetAdminPrx)
        prepareRScripts()
        bdvd_log("Run R Script")
        runRScript()
        bdvd_log("RUV plot model [done]")

        shutdownFCDCentral()
        finish_time = datetime.now()
        duration = finish_time - start_time
        bdvd_logp("-----------------------------------------------")
        bdvd_log("Run complete: %s elapsed" %  iBSUtil.formatTD(duration))

    except Usage as err:
        shutdownFCDCentral()
        bdvd_logp(sys.argv[0].split("/")[-1] + ": " + str(err.msg))
        bdvd_logp("    for detailed help see url ...")
        return 2
    
    except:
        bdvd_logp(traceback.format_exc())
        die()


if __name__ == "__main__":
    sys.exit(main())
