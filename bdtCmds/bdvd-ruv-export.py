#!__PYTHON_BIN_PATH__

"""
bdvd-ruv export data
"""
import sys, traceback
import getopt
import subprocess
import os
import shutil
import time
from datetime import datetime, date
import logging
from copy import deepcopy

BDT_HomeDir=os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"../../..")

Platform = None
if Platform == "Windows":
    # this file will be at install\
    bdtInstallDir = BDT_HomeDir
    icePyDir = os.path.abspath(bdtInstallDir+"/dependency/IcePy")
    bdtPyDir = os.path.abspath(bdtInstallDir+"/bdt/bdtPy")
    for dir in [icePyDir, bdtPyDir]:
        if dir not in sys.path:
            sys.path.append(dir)

import iBSConfig
iBSConfig.BDT_HomeDir = BDT_HomeDir

import bdtUtil
import iBSDefines
import iBSFCDClient as fcdc
import bigMatUtil
import iBS
import Ice

use_message = '''
bdvd-export
'''

gParams=None
gRunner=None

class BdvdExportParams:
    def __init__(self):
        self.output_dir = None
        self.bigmat_dir = None
        self.max_mem = 2000
        self.num_threads = 4
        self.fcdc_fvworker_size=2
        self.fcdc_tcp_port=16000
        self.fcdc_threadpool_size=2
        self.workflow_node = "export"
        self.result_dumpfile = None
        self.design_file = None
        self.export_rows_pickle = None

    def parse_options(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], "",
                ["out=",
                    "num-threads=",
                    "max-mem=",
                    "node=",
                    "bigmat-dir=",
                    "export-rows="])
        except getopt.error as msg:
            raise iBSDefines.BdtUsage(msg)

        for option, value in opts:
            if option in ("-p", "--num-threads"):
                self.num_threads = int(value)
                self.fcdc_fvworker_size = 2
            if option in ("-m", "--max-mem"):
                self.max_mem = int(value)
            if option in ("-o", "--out"):
                self.output_dir = value
            if option == "--node":
                self.workflow_node = value
            if option =="--bigmat-dir":
                self.bigmat_dir = value
            if option == "--export-rows":
                self.export_rows_pickle = value
        
        self.result_dumpfile = "{0}.pickle".format(self.workflow_node)
        self.output_dir = os.path.abspath(self.output_dir)

        if self.bigmat_dir is None:
            raise iBSDefines.BdtUsage("--bigmat-dir is required")
        self.bigmat_dir = os.path.abspath(self.bigmat_dir)

        if len(args) < 1:
            raise iBSDefines.BdtUsage("design file is required")
        self.design_file = args[0]
        return args

def prepare_output_dir():
    shutil.copy(gParams.design_file,
            os.path.abspath("{0}/bdvdRuvExportDesign.py".format(gRunner.script_dir)))

def dumpOutput(obj):
    fn = "{0}/{1}".format(gParams.output_dir,gParams.result_dumpfile)
    iBSDefines.dumpPickle(obj,fn)

def attachInputBigMatrix(bigmat,fcdcPrx, requireStats):
    gRunner.log("attach mat: {0} x {1} from {2}".format(bigmat.RowCnt,bigmat.ColCnt,bigmat.StorePathPrefix))
    (rt, outOIDs)=fcdcPrx.AttachBigMatrix(bigmat.ColCnt,bigmat.RowCnt,bigmat.ColNames,bigmat.StorePathPrefix)
    #bdvd_log("assigned colIDs: {0}".format(str(outOIDs)))
    if requireStats:
        minSampleID = min(outOIDs)
        if bigmat.ColStats is None:
            raise iBSDefines.BdtUsage("calc-statistics required")
        osis=bigmat.ColStats
        for i in range(len(osis)):
            osi=osis[i]
            osis[i].ObserverID=outOIDs[i]
            gRunner.logp("Sample {0}: Max = {1}, Min = {2}, Sum = {3}".format(osi.ObserverID - minSampleID +1, int(osi.Max), int(osi.Min), int(osi.Sum)))
        rt=fcdcPrx.SetObserverStats(osis)
    return outOIDs

def launchExportTask(fcdcPrx, bdvdFacetAdminPrx, computePrx, exportRowsOid, rowCnt):
    # configuration by user
    designPath=os.path.abspath(gRunner.script_dir)
    if designPath not in sys.path:
         sys.path.append(designPath)
    import bdvdRuvExportDesign as design

    facetID=1
    ruvPrx=bdvdFacetAdminPrx.GetRUVFacet(facetID)
    (rt, rfi)=bdvdFacetAdminPrx.GetRUVFacetInfo(facetID)
    ruvPrx.SetOutputWorkerNum(design.OutputWorkerNum)
    ruvPrx.SetOutputMode(design.RUVOutputMode)
    ruvPrx.SetOutputScale(design.RUVOutputScale)
    ks=   design.Ks
    extWs=design.Ns
    sampleIDs = rfi.SampleIDs
    if design.ColIds is not None:
        sampleIDs = []
        # sampleIDs in design start from 1
        for si in design.ColIds:
            sampleIDs.append(rfi.SampleIDs[si-1])

    (rt,ofis)=fcdcPrx.GetFeatureObservers(sampleIDs)
    outpath=os.path.abspath(gParams.output_dir)
    tasks=[]
    bfvFiles=[]
    for i in range(len(ks)):
        if exportRowsOid is not None:
            task=computePrx.GetBlankExportByRowIdxsTask()
            task.FeatureIdxsOid=exportRowsOid
        else:
            task=computePrx.GetBlankExportRowMatrixTask()
            task.FeatureIdxFrom = design.FeatureIdxFrom
            task.FeatureIdxTo = design.FeatureIdxTo
            rowCnt = task.FeatureIdxTo - task.FeatureIdxFrom

        task.TaskName=design.OutMatNames[i]
        task.reader=ruvPrx
        task.SampleIDs= sampleIDs
        task.OutID=10001+i
        task.OutPath=outpath
        bfvFile = os.path.abspath("{0}/{1}".format(gParams.output_dir, design.OutMatNames[i]))
        task.OutFile = os.path.abspath("{0}/{1}".format(gParams.output_dir, design.OutMatNames[i]))
        bfvFiles.append(task.OutFile)
        tasks.append(task)

    nd_outobj = iBSDefines.RUVMatrixExportOutputDefine()
    nd_outobj.OutMatNames = design.OutMatNames
    nd_outobj.BfvFiles = bfvFiles
    nd_outobj.ColCnt = len(sampleIDs)
    nd_outobj.ColIDs = sampleIDs
    nd_outobj.ColNames = [si.ObserverName for si in ofis]
    nd_outobj.Ks = ks
    nd_outobj.Ns = extWs
    nd_outobj.RowCnt = rowCnt
    nd_outobj.RUVOutputMode = design.RUVOutputMode
    nd_outobj.RUVOutputScale = design.RUVOutputScale

    if exportRowsOid is not None:
        batchTask=computePrx.GetBlankRUVExportByRowIdxsBatchTask()
    else:
        batchTask=computePrx.GetBlankRUVExportRowMatrixBatchTask()
    batchTask.ruv=ruvPrx
    batchTask.ks=ks
    batchTask.extWs=extWs
    batchTask.Tasks=tasks

    if exportRowsOid is not None:
        (rt,amdTaskID)=computePrx.RUVExportByRowIdxsBatch(batchTask)
    else:
        (rt,amdTaskID)=computePrx.RUVExportRowMatrixBatch(batchTask)
    

    preMsg=""
    amdTaskFinished=False
    gRunner.log("Export with {0} threads ...".format(gParams.num_threads ))
    while (not amdTaskFinished):
        (rt,amdTaskInfo)=fcdcPrx.GetAMDTaskInfo(amdTaskID)
        thisMsg="task: {0}, batch processed: {1}/{2}".format(amdTaskInfo.TaskName, amdTaskInfo.FinishedCnt, amdTaskInfo.TotalCnt)
        if preMsg!=thisMsg:
            preMsg = thisMsg
            gRunner.log(thisMsg)
        if amdTaskInfo.Status!=iBS.AMDTaskStatusEnum.AMDTaskStatusNormal:
            amdTaskFinished = True;
        else:
            time.sleep(4)
    
    return (rt,amdTaskID,nd_outobj)

def saveResults(outObj):
    fn = os.path.abspath("{0}/{1}".format(gParams.output_dir,gParams.result_dumpfile))
    iBSDefines.dumpPickle(outObj,fn)

def main(argv=None):
    global gParams
    global gRunner
    gParams = BdvdExportParams()
    gRunner = bigMatUtil.bigMatRunner(iBSConfig.BDT_HomeDir, 'bdvd')

    run_argv = sys.argv[:]

    try:
        if argv is None:
            argv = sys.argv
        args = gParams.parse_options(argv)

        start_time = datetime.now()

        gRunner.prepare_dirs(gParams.output_dir, gParams.bigmat_dir)
        prepare_output_dir()
        gRunner.init_logger("bdvd-export.log")

        gRunner.logp()
        gRunner.log("Beginning bdvd-export run (v"+bdtUtil.get_version()+")")
        gRunner.logp("-----------------------------------------------")

        gParams.fcdc_tcp_port = bdtUtil.getUsableTcpPort()
        gRunner.prepare_bigmat_config(gParams.fcdc_tcp_port, 
                                  gParams.fcdc_fvworker_size, 
                                  gParams.fcdc_threadpool_size)

        gRunner.launch_bigMat()
        fcdc.Init()

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
            raise iBSDefines.BdtUsage("connection timeout")

        bdvdFacetAdminPrx = fcdc.GetBdvdFacetAdminProxy(fcdcHost)
        computePrx=fcdc.GetComputeProxy(fcdcHost)
  
        gRunner.log("bdtCore activated")
        
        exportRowsOid = None
        rowCnt = None
        if gParams.export_rows_pickle is not None:
            ctrObj = iBSDefines.loadPickle(gParams.export_rows_pickle)
            ctrlMat = ctrObj.BigMat
            gRunner.log("export row cnt = {0}".format(ctrlMat.RowCnt))
            exportRowsOid = attachInputBigMatrix(ctrlMat, fcdcPrx, False)[0]
            rowCnt = ctrlMat.RowCnt

        (rt, amdTaskID, outObj) = launchExportTask(fcdcPrx, bdvdFacetAdminPrx, computePrx, exportRowsOid, rowCnt)
        
        # -----------------------------------------------------------
        # Output Results
        # -----------------------------------------------------------
        saveResults(outObj)

        gRunner.shutdown_bigMat()

        finish_time = datetime.now()
        duration = finish_time - start_time
        gRunner.logp("-----------------------------------------------")
        gRunner.log("Run complete: %s elapsed" %  bdtUtil.formatTD(duration))

    except iBSDefines.BdtUsage as err:
        gRunner.shutdown_bigMat()
        gRunner.logp(sys.argv[0].split("/")[-1] + ": " + str(err.msg))
        return 2
    
    except:
        gRunner.logp(traceback.format_exc())
        gRunner.die()


if __name__ == "__main__":
    sys.exit(main())
