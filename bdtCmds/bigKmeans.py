#!__PYTHON_BIN_PATH__

"""
command line tools for big k-means 
"""

import os
import sys, traceback
import getopt
import subprocess
import shutil
import time
from datetime import datetime, date
import random

import iBSConfig
BDT_HomeDir = iBSConfig.BDT_HomeDir
if os.getcwd()!=BDT_HomeDir:
    os.chdir(BDT_HomeDir)

import bdtUtil
import iBSDefines
import iBSFCDClient as fcdc
import iBS
import Ice

use_message = '''
KMeans++ (multihreads, local node)

Usage:
    pipeline-kmeans++.py [options] <--data data_file> <--nrow row_cnt> <--ncol col_cnt> <--k cluster_num> <--out out_dir>

Options:
    -v/--version
    -p/--thread-num                <int>       [ default: 4             ]
    --dist-type                    <string>    [ Euclidean, Correlation ]

Advanced Options:

'''

gParams=None
gRunner=None
gSteps = ['1-input-mat', '2-run-kmeans']

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class BDVDParams:
    def __init__(self):
        self.output_dir = None
        self.logging_dir = None
        self.start_from = '1-input-mat'
        self.dry_run = True
        self.remove_before_run = True
        self.pipeline_rundir = None
        self.data_file = None
        self.kmeansc_workercnt = 4
        self.dist_type = "Euclidean"
        self.kmeans_ks = None
        self.row_cnt = None
        self.col_cnt = None
        self.kmeans_maxiter = 100
        self.kmeans_minexplainedchange = 0.0001

    def parse_options(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], "hvp:m:o:",
                ["version",
                "help",
                "start-from=",
                "data=",
                "out=",
                "thread-num=",
                "dist-type=",
                "ncol=",
                "nrow=",
                "k=",
                "max-iter=",
                "min-expchg="])

        except getopt.error as msg:
            raise Usage(msg)

        custom_out_dir = None

        # option processing
        for option, value in opts:
            if option in ("-v", "--version"):
                print("bigKmeans v",iBSUtil.get_version())
                sys.exit(0)
            if option in ("-h", "--help"):
                raise Usage(use_message)
            if option in ("-p", "--thread-num"):
                self.kmeansc_workercnt = int(value)
            if option in ("-o", "--out"):
                custom_out_dir = value + "/"
            if option =="--start-from":
                allowedValues = gSteps;
                if value not in allowedValues:
                    raise Usage('--start-from should be one of the {0}'.format(allowedValues))
                self.start_from = value
            if option == "--data":
                self.data_file = value
            if option in ("--ncol"):
                self.col_cnt = int(value)
            if option in ("--nrow"):
                self.row_cnt = int(value)
            if option in ("--max-iter"):
                self.kmeans_maxiter = int(value)
            if option in ("--min-expchg"):
                self.kmeans_minexplainedchange = float(value)
            if option =="--dist_type":
                allowedValues = ('Euclidean', 'Correlation');
                if value not in allowedValues:
                    raise Usage('--dist_type should be one of the {0}'.format(allowedValues))
                self.dist_type = value
            if option =="--k":
                self.kmeans_ks = iBSUtil.parseIntSeq(value)
                if len(self.kmeans_ks)<1:
                    raise Usage('invalid --k')

        requiredNames = ['--data', '--k', '--out', '--ncol', '--nrow']
        providedValues = [self.data_file, self.kmeans_ks, custom_out_dir, self.col_cnt, self.row_cnt]
        noneIdx = bdtUtil.getFirstNone(providedValues)
        if noneIdx != -1:
            raise Usage("{0} is required".format(requiredNames[noneIdx]))

        self.output_dir = custom_out_dir
        self.logging_dir = output_dir + "logs/"
        self.pipeline_rundir=output_dir+"run"

        return args

# -----------------------------------------------------------
# Input Data to BigMat
# -----------------------------------------------------------
def s01_ext2mat():
    nodeName = "s01_ext2mat"
    nodeDir = gParams.pipeline_rundir + "/" + nodeName
    nodeScriptDir = nodeDir + "-script"

    subnode_picke_file = "{0}/{1}.pickle".format(nodeDir,nodeName)
    if gParams.dry_run:
        return subnode_picke_file

    if gParams.remove_before_run and os.path.exists(nodeDir):
        bdvd_logp("remove existing dir: {0}".format(nodeDir))   
        shutil.rmtree(nodeDir)

    if not os.path.exists(nodeScriptDir):
        os.mkdir(nodeScriptDir)

    #
    # prepare design file
    #
    ColCnt = gParams.col_cnt
    RowCnt = gParams.row_cnt
    DataFile = gParams.data_file
    FieldSep = " "
    SampleNames=["V{0}".format(v) for v in range(1,ColCnt+1)]
    CalcStatistics = False
    design_params=(SampleNames,ColCnt,RowCnt,DataFile,FieldSep,CalcStatistics)
    params_pickle_fn="{0}/design_params.pickle".format(nodeScriptDir)
    iBSDefines.dumpPickle(design_params, params_pickle_fn)

    design_file=BDT_HomeDir+"/iBS/iBSPy/PipelineDesigns/bdvdTxt2MatDesign.py"
    shutil.copy(design_file,nodeScriptDir)

    #
    # Run node
    #
    design_fn=os.path.abspath(nodeScriptDir)+"/bdvdTxt2MatDesign.py"
    subnode=nodeName
    cmdpath="{0}/bdvd-txt2mat.py".format(BDT_HomeDir)
    node_cmd = [cmdpath,
                "--node",nodeName,
                "--num-threads", "4",
                "--output-dir",nodeDir,
                design_fn]
      
    shell_cmd=""
    for strCmd in node_cmd:
        shell_cmd=shell_cmd+strCmd+" "
    #print(shell_cmd)

    bdvd_logp("run subtask at: {0}".format(nodeDir))
    proc = subprocess.call(node_cmd)
    bdvd_logp("end subtask \n")
    return subnode_picke_file

# -----------------------------------------------------------
# KMeans ++
# -----------------------------------------------------------
def s02_kmeansPP(datamatPickle):
    nodeName = "s02_kmeansPP"
    nodeDir=gParams.pipeline_rundir+"/"+nodeName
    nodeScriptDir=nodeDir+"-script"

    if not os.path.exists(nodeScriptDir):
        os.mkdir(nodeScriptDir)

    #
    # prepare design file
    #
    Ks = gParams.kmeans_ks
    Distance = iBS.KMeansDistEnum.KMeansDistEuclidean
    if gParams.dist_type=="Correlation":
        Distance = iBS.KMeansDistEnum.KMeansDistCorrelation
    MaxIteration = gParams.kmeans_maxiter
    MinExplainedChanged = gParams.kmeans_minexplainedchange
    FeatureIdxFrom = None
    FeatureIdxTo = None
    KMeansContractorWorkerCnt = gParams.kmeansc_workercnt

    design_params=(Ks,Distance,MaxIteration,MinExplainedChanged,FeatureIdxFrom,FeatureIdxTo,KMeansContractorWorkerCnt)
    params_pickle_fn="{0}/design_params.pickle".format(nodeScriptDir)
    iBSDefines.dumpPickle(design_params, params_pickle_fn)

    design_file=BDT_HomeDir+"/iBS/iBSPy/PipelineDesigns/bigclustKMeansPPDesign.py"
    shutil.copy(design_file,nodeScriptDir)

    #
    # Run node
    #
    design_fn=os.path.abspath(nodeScriptDir)+"/bigclustKMeansPPDesign.py"
    subnode=nodeName
    cmdpath="{0}/bigclust-kmeans++.py".format(BDT_HomeDir)
    node_cmd = [cmdpath,
                "--node",nodeName,
                "--datamat", datamatPickle,
                "--output-dir",nodeDir,
                design_fn]
      
    shell_cmd=""
    for str in node_cmd:
        shell_cmd=shell_cmd+str+" "
    #print(shell_cmd)

    bdvd_logp("run subtask at: {0}".format(nodeDir))
    proc = subprocess.call(node_cmd)
    subnode_picke_file="{0}/{1}.pickle".format(nodeDir,nodeName)
    bdvd_logp("end subtask \n")
    return (nodeDir,subnode_picke_file)

def preparePipelineResult(kmeansPPNodeDir):
    outfile="{0}cluster_assignments.bfv".format(output_dir)
    shutil.copy("{0}/gid_10001.bfv".format(kmeansPPNodeDir),
                "{0}cluster_assignments.bfv".format(output_dir))

    bdvd_logp("cluster_assignments: {0}\n".format(outfile))

def main(argv=None):
    global gParams
    global gRunner
    gParams = BDVDParams()
    gRunner = bdtUtil.bdtRunner()
    run_argv = sys.argv[:]

    try:
        if argv is None:
            argv = sys.argv
        args = gParams.parse_options(argv)
       
        start_time = datetime.now()

        gRunner.prepare_dirs(gParams.output_dir, gParams.logging_dir, gParams.pipeline_rundir)
        gRunner.init_logger(gParams.logging_dir + "bigKmeans.log")

        gRunner.logp()
        gRunner.log("Beginning bigKmeans run v({0})".format(bdtUtil.get_version()))
        gRunner.logp("-----------------------------------------------")

        # -----------------------------------------------------------
        # launch bigMat
        # -----------------------------------------------------------
       
        if gParams.dry_run and gParams.start_from == gSteps[0]:
            gParams.dry_run = False

        datamatPickle = s01_ext2mat()

        if gParams.dry_run:
            gRunner.log("retrieve existing result for: {0}".format(gSteps[0]))
            gRunner.log("from: {0}".format(datamatPickle))
            if not os.path.exists(datamatPickle):
                gRunner.die('file not exist')
            gRunner.log("")
        
        if gParams.dry_run and gParams.start_from == gSteps[1]:
            gParams.dry_run = False

        (nodeDir,subnode_picke)=s02_kmeansPP(datamatPickle)
        preparePipelineResult(nodeDir)

        finish_time = datetime.now()
        duration = finish_time - start_time
        gRunner.logp("-----------------------------------------------")
        gRunner.log("Run complete: %s elapsed" %  iBSUtil.formatTD(duration))

    except Usage as err:
        gRunner.logp(sys.argv[0].split("/")[-1] + ": " + str(err.msg))
        gRunner.logp("    for detailed help see url ...")
        return 2
    
    except:
        gRunner.logp(traceback.format_exc())
        die()

if __name__ == "__main__":
    sys.exit(main())
