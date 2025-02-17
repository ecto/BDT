#!__PYTHON_BIN_PATH__

"""
command line tools to generate a matrix
"""

import os
import sys, traceback
import getopt
import subprocess
import shutil
import time
import re
from datetime import datetime, date
import random

BDT_HomeDir=os.path.dirname(os.path.abspath(__file__))

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
import iBSDefines
import bdtUtil
import iBSFCDClient as fcdc
import bigMatUtil
import iBS
import Ice

gParams=None
gRunner=None
gSteps = bigMatUtil.bigmat_steps
gInputHandlers = None

# -----------------------------------------------------------
# import data matrix from txt format
# -----------------------------------------------------------
def s01_txt2mat():
    nodeName = gSteps[0]
    return bigMatUtil.run_txt2Mat(
        gRunner,
        Platform,
        BDT_HomeDir,
        nodeName,
        gParams.pipeline_rundir,
        gParams.dry_run,
        gParams.remove_before_run,
        gParams.calc_statistics,
        gParams.col_cnt,
        gParams.row_cnt,
        gParams.input_location,
        gParams.col_names,
        gParams.column_sep,
        gParams.skip_cols,
        gParams.skip_rows)

# -----------------------------------------------------------
# impor rowids from txt format
# -----------------------------------------------------------
def s01_txtRowIds2mat():
    nodeName = gSteps[0]
    return bigMatUtil.run_txtRowIds2Mat(
        gRunner,
        Platform,
        BDT_HomeDir,
        nodeName,
        gParams.pipeline_rundir,
        gParams.dry_run,
        gParams.remove_before_run,
        gParams.calc_statistics,
        gParams.input_location,
        gParams.row_index_base,
        gParams.col_names,
        gParams.column_sep,
        gParams.skip_cols,
        gParams.skip_rows)


# -----------------------------------------------------------
# import data matrix from binary format (*.bfv)
# -----------------------------------------------------------
def s01_bfv2mat():
    nodeName = gSteps[0]
    return bigMatUtil.run_bfv2Mat(
        gRunner,
        Platform,
        BDT_HomeDir,
        nodeName,
        gParams.pipeline_rundir,
        gParams.dry_run,
        gParams.remove_before_run,
        gParams.calc_statistics,
        gParams.col_cnt,
        gParams.row_cnt,
        gParams.input_location,
        gParams.col_names)

# -----------------------------------------------------------
# import data matrix from bam files (*.bam)
# -----------------------------------------------------------
def s01_bam2mat():
    nodeName = gSteps[0]
    return bigMatUtil.run_bam2Mat(
        gRunner,
        Platform,
        BDT_HomeDir,
        nodeName,
        gParams.pipeline_rundir,
        gParams.dry_run,
        gParams.remove_before_run,
        gParams.calc_statistics,
        gParams.col_names,
        gParams.thread_cnt,
        gParams.chromosomes,
        gParams.bin_width,
        gParams.input_location)

# -----------------------------------------------------------
# import data matrix from bigKmeans output
# -----------------------------------------------------------
def s01_fromKmeansResult():
    nodeName = gSteps[0]
    inputPickle = iBSDefines.derivePickleFile(gParams.input_location)
    kmeansOutObj = iBSDefines.loadPickle(inputPickle)
    nodeDir = os.path.abspath("{0}/{1}".format(gParams.pipeline_rundir, nodeName))
    out_picke_file = os.path.abspath("{0}/{1}.pickle".format(nodeDir,nodeName))
    if gParams.dry_run:
        return out_picke_file
    if gParams.remove_before_run and os.path.exists(nodeDir):
        shutil.rmtree(nodeDir)
    if not os.path.exists(nodeDir):
        os.mkdir(nodeDir)

    if gParams.input_type == 'kmeans-seeds-mat':
        iBSDefines.dumpPickle(kmeansOutObj.SeedsMat, out_picke_file)
    elif gParams.input_type == 'kmeans-centroids-mat':
        iBSDefines.dumpPickle(kmeansOutObj.CentroidsMat, out_picke_file)
    elif gParams.input_type == 'kmeans-data-mat':
        iBSDefines.dumpPickle(kmeansOutObj.DataMat, out_picke_file)

    return out_picke_file

# -----------------------------------------------------------
# import data matrix from bigmat output
# -----------------------------------------------------------
def  s01_bigmat2mat():
    nodeName = gSteps[0]
    inputPickle = iBSDefines.derivePickleFile(gParams.input_location)
    nodeDir = os.path.abspath("{0}/{1}".format(gParams.pipeline_rundir, nodeName))
    out_picke_file = os.path.abspath("{0}/{1}.pickle".format(nodeDir,nodeName))
    if gParams.dry_run:
        return out_picke_file
    if gParams.remove_before_run and os.path.exists(nodeDir):
        shutil.rmtree(nodeDir)
    if not os.path.exists(nodeDir):
        os.mkdir(nodeDir)

    shutil.copy(inputPickle, out_picke_file)
    return out_picke_file

# -----------------------------------------------------------
# import data matrix from bdvd-export output
# -----------------------------------------------------------
def s01_fromBdvdExport():
    nodeName = gSteps[0]
    inputPickle = iBSDefines.derivePickleFile(gParams.input_location)
    ruvOut = iBSDefines.loadPickle(inputPickle).Export
    nodeDir = os.path.abspath("{0}/{1}".format(gParams.pipeline_rundir, nodeName))
    out_picke_file = os.path.abspath("{0}/{1}.pickle".format(nodeDir,nodeName))
    if gParams.dry_run:
        return out_picke_file
    if gParams.remove_before_run and os.path.exists(nodeDir):
        shutil.rmtree(nodeDir)
    if not os.path.exists(nodeDir):
        os.mkdir(nodeDir)

    iBSDefines.dumpPickle(ruvOut.get_default_mat(), out_picke_file)
    return out_picke_file

def s01_fromBigmatExport():
    nodeName = gSteps[0]
    inputPickle = iBSDefines.derivePickleFile(gParams.input_location)
    bigmat = iBSDefines.loadPickle(inputPickle).Export
    nodeDir = os.path.abspath("{0}/{1}".format(gParams.pipeline_rundir, nodeName))
    out_picke_file = os.path.abspath("{0}/{1}.pickle".format(nodeDir,nodeName))
    if gParams.dry_run:
        return out_picke_file
    if gParams.remove_before_run and os.path.exists(nodeDir):
        shutil.rmtree(nodeDir)
    if not os.path.exists(nodeDir):
        os.mkdir(nodeDir)

    iBSDefines.dumpPickle(bigmat, out_picke_file)
    return out_picke_file

def s01_fromNodeOutput():
    defaultOutput = iBSDefines.getDefaultMatNameFromeNodeDir(gParams.input_location)
    if defaultOutput is None:
        raise iBSDefines.BdtUsage('no valid mat input found in {0}'.format(gParams.input_location))
    return gInputHandlers[defaultOutput]()

def outputR():
    obj = iBSDefines.loadPickle(
        iBSDefines.derivePickleFile(gParams.output_dir))

    infile = open("{0}/bdt/bdtR/outputTemplates/bigMatOutputTemplate.R".format(BDT_HomeDir))
    outfile = open("{0}/logs/output.R".format(gParams.output_dir), "w")

    bigMat = obj
    if (hasattr(obj, 'BigMat')):
        bigMat = obj.BigMat

    if (hasattr(obj, 'BinMap')):
        binMap = obj.BinMap

    if (not hasattr(obj, 'BinMap')):
        binMap = iBSDefines.RefNoneoverlapBinMap()
        binMap.as_emtpy()

    replacements = {"__INPUT_TYPE__": gParams.input_type,
                    "__NAME__": bigMat.Name,
                    "__STORE_PATH_PREFIX__": bigMat.StorePathPrefix.replace('\\','/'),
                    "__ROW_CNT__":str(bigMat.RowCnt),
                    "__COL_CNT__":str(bigMat.ColCnt),
                    "__COL_NAMES__":str(bigMat.ColNames).replace('[','').replace(']',''),
                    "__COL_IDS__":str(bigMat.ColIDs).replace('[','').replace(']',''),

                    "__BIN_WIDTH__":str(binMap.BinWidth),
                    "__REF_NAMES__":str(binMap.RefNames).replace('[','').replace(']',''),
                    "__BIN_FROMS__":str(binMap.RefBinFroms).replace('[','').replace(']',''),
                    "__BIN_TOS__":str(binMap.RefBinTos).replace('[','').replace(']','')
                    }

    for line in infile:
        for src, target in replacements.items():
            line = line.replace(src, target)
        outfile.write(line)
    infile.close()
    outfile.close()

def main(argv=None):
    global gParams
    global gRunner
    global gInputHandlers

    gParams = bigMatUtil.BigMatParams()
    gRunner = bdtUtil.bdtRunner()
    gInputHandlers = {
        'text-mat': s01_txt2mat,
        'binary-mat': s01_bfv2mat,
        'text-rowids': s01_txtRowIds2mat,
        'bams': s01_bam2mat,
        'bigmat': s01_bigmat2mat,
        'kmeans-seeds-mat': s01_fromKmeansResult,
        'kmeans-centroids-mat': s01_fromKmeansResult,
        'kmeans-data-mat': s01_fromKmeansResult,
        'bdvd-export-mat': s01_fromBdvdExport,
        'bigmat-export-mat': s01_fromBigmatExport,
        'output': s01_fromNodeOutput}

    run_argv = sys.argv[:]

    try:
        if argv is None:
            argv = sys.argv
        gParams.parse_options("", argv[1:])
       
        start_time = datetime.now()

        gRunner.prepare_dirs(gParams.output_dir, gParams.logging_dir, gParams.pipeline_rundir)
        gRunner.init_logger(os.path.abspath(gParams.logging_dir + "/bigMat.log"))

        gRunner.logp()
        gRunner.log("Beginning bigMat run v({0})".format(bdtUtil.get_version()))
        gRunner.logp("-----------------------------------------------")

        # -----------------------------------------------------------
        # launch bigMat
        # -----------------------------------------------------------     
        if gParams.dry_run and gParams.start_from == gSteps[0]:
            gParams.dry_run = False

        datamatPickle = None
        datamatPickle = gInputHandlers[gParams.input_type]()

        if gParams.dry_run:
            gRunner.log("retrieve existing result for: {0}".format(gSteps[0]))
            gRunner.log("from: {0}".format(datamatPickle))
            if not os.path.exists(datamatPickle):
                gRunner.die('file not exist')
            gRunner.log("")

        runSummary = iBSDefines.NodeRunSummaryDefine()
        runSummary.NodeDir = gParams.output_dir
        runSummary.NodeType = "bigMat"
        runSummaryPicke = "{0}/logs/runSummary.pickle".format(gParams.output_dir)
        iBSDefines.dumpPickle(runSummary, runSummaryPicke)

        outputR()

        finish_time = datetime.now()
        duration = finish_time - start_time
        gRunner.logp("-----------------------------------------------")
        gRunner.log("Run complete: %s elapsed" %  bdtUtil.formatTD(duration))

    except iBSDefines.BdtUsage as err:
        gRunner.logp(sys.argv[0].split("/")[-1] + ": " + str(err.msg))
        return 2
    
    except:
        gRunner.logp(traceback.format_exc())
        gRunner.die()

if __name__ == "__main__":
    sys.exit(main())
