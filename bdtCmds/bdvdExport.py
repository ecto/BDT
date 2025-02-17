#!__PYTHON_BIN_PATH__

"""
command line tool for bdvd export
"""
import os
import sys, traceback
import getopt
import subprocess
import shutil
import time
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
import bigKmeansUtil
import iBSFCDClient as fcdc
import bigMatUtil
import bdvdUtil
import iBS
import Ice

gParams=None
gRunner=None
gSteps = ['1-row-idxs','2-run-export']
gRowSelectors = ['all', 'range', 'specified-rows']
gComponents = ['signal', 'artifact', 'random', 'signal+random']
gScales = ['mlog', 'original']
gArtifactDetections = ['aggressive', 'conservative']

class BDVDParams:
    def __init__(self):
        self.output_dir = None
        self.logging_dir = None
        self.start_from = gSteps[0]
        self.dry_run = True
        self.remove_before_run = True
        self.pipeline_rundir = None
        self.workercnt = 4
        self.memory_size = 2000
        self.row_selector = gRowSelectors[0]
        self.rowidx_from = None
        self.rowidx_to = None
        self.rowidxs_params = None
        self.rowidxs_indir = None
        self.column_ids = None
        self.bdvd_dir = None
        self.export_component = None
        self.export_scale =gScales[0]
        self.artifact_detection =gArtifactDetections[1]
        self.unwanted_factors = None
        self.known_factors = None
        self.export_names = None

    def parse_options(self, argv):
        rowIdxsParams = bigMatUtil.BigMatParams()
        args = argv[1:]
        args = rowIdxsParams.strip_argv('rowidxs-', args)
        rowIdxsArgv = rowIdxsParams.argv
        bdvdArgv = args
        try:
            opts, args = getopt.getopt(bdvdArgv, "",
                ["version",
                "help",
                "thread-num=",
                "memory-size=",
                "out=",
                "column-ids=",
                "row-selector=",
                "rowidx-from=",
                "rowidx-to=",
                "bdvd-dir=",
                "component=",
                "scale=",
                "artifact-detection=",
                "unwanted-factors=",
                "known-factors=",
                "export-names="])

        except getopt.error as msg:
            raise iBSDefines.BdtUsage(msg)

        for option, value in opts:
            if option == "--version":
                print("bdvd v",bdtUtil.get_version())
                sys.exit(0)
            if option == "--help":
                raise iBSDefines.BdtUsage(use_message)
            if option == "--thread-num":
                self.workercnt = int(value)
            if option == "--memory-size":
                self.memory_size = int(value)
            if option in ("-o", "--out"):
                self.output_dir = value
            if option == "--row-selector":
                allowedValues = gRowSelectors;
                if value not in allowedValues:
                    raise iBSDefines.BdtUsage('--row-selector should be one of the {0}'.format(allowedValues))
                self.row_selector = value
            if option == "--rowidx-from":
                self.rowidx_from = int(value)
            if option == "--rowidx-to":
                self.rowidx_to = int(value)
            if option =="--column-ids":
                self.column_ids = bdtUtil.parseIntSeq(value)
                if len(self.column_ids)<1:
                    raise iBSDefines.BdtUsage('invalid column-ids: {0}'.format(value))
            if option =="--start-from":
                allowedValues = gSteps;
                if value not in allowedValues:
                    raise iBSDefines.BdtUsage('--start-from should be one of the {0}'.format(allowedValues))
                self.start_from = value
            if option =="--bdvd-dir":
                self.bdvd_dir = value
            if option == "--component":
                allowedValues = gComponents;
                if value not in allowedValues:
                    raise iBSDefines.BdtUsage('--component should be one of the {0}'.format(allowedValues))
                self.export_component = value
            if option == "--scale":
                allowedValues = gScales;
                if value not in allowedValues:
                    raise iBSDefines.BdtUsage('--scale should be one of the {0}'.format(allowedValues))
                self.export_scale = value
            if option == "--artifact-detection":
                allowedValues = gArtifactDetections;
                if value not in allowedValues:
                    raise iBSDefines.BdtUsage('--artifact-detection should be one of the {0}'.format(allowedValues))
                self.artifact_detection = value
            if option =="--unwanted-factors":
                self.unwanted_factors = bdtUtil.parseIntSeq(value)
                if len(self.unwanted_factors)<1:
                    raise iBSDefines.BdtUsage('invalid unwanted_factors: {0}'.format(value))
            if option =="--known-factors":
                self.known_factors = bdtUtil.parseIntSeq(value)
                if len(self.known_factors)<1:
                    raise iBSDefines.BdtUsage('invalid known-factors: {0}'.format(value))
            if option =="--export-names":
                self.export_names=value.split(',')
                if len(self.export_names)<1:
                    raise iBSDefines.BdtUsage('invalid export-names: {0}'.format(value))

        requiredNames = ['--out', '--bdvd-dir', '--column-ids', '--component', '--unwanted-factors']
        providedValues = [self.output_dir, self.bdvd_dir, self.column_ids, self.export_component, self.unwanted_factors]
        noneIdx = bdtUtil.getFirstNone(providedValues)
        if noneIdx != -1:
            raise iBSDefines.BdtUsage("{0} is required".format(requiredNames[noneIdx]))

        self.bdvd_dir = os.path.abspath(self.bdvd_dir)
        self.output_dir = os.path.abspath(self.output_dir)
        self.logging_dir = os.path.abspath(self.output_dir + "/logs")
        self.pipeline_rundir=os.path.abspath(self.output_dir + "/run")

        if self.row_selector == "specified-rows" or len(rowIdxsArgv) > 0:
            self.rowidxs_indir=os.path.abspath("{0}/{1}".format(self.pipeline_rundir, gSteps[0]))
            rowIdxsArgv.extend(['--rowidxs-out',self.rowidxs_indir])
            self.rowidxs_params = bigMatUtil.BigMatParams()
            self.rowidxs_params.parse_options("rowidxs-", rowIdxsArgv)
        if self.known_factors is None:
            self.known_factors =[0]*len(self.unwanted_factors)
        if len(self.known_factors) != len(self.unwanted_factors):
            raise iBSDefines.BdtUsage("unwanted-factors and known-factors must have equal lenght")
        if self.export_names is None:
            self.export_names = ['export_{0}'.format(v+1) for v in range(len(self.unwanted_factors))]
        return args

def s01_rowidxs():
    nodeName = gSteps[0]
    return bigMatUtil.run_bigMat(
        gRunner,
        Platform,
        BDT_HomeDir,
        nodeName,
        gParams.pipeline_rundir,
        gParams.dry_run,
        gParams.remove_before_run,
        gParams.rowidxs_params)

def s02_run_export(rowIdxsPickle):
    nodeName = gSteps[1]
    return bdvdUtil.run_bdvd_ruv_export(
        gRunner,
        Platform,
        BDT_HomeDir,
        nodeName,
        gParams.pipeline_rundir,
        gParams.dry_run,
        gParams.remove_before_run,
        rowIdxsPickle,
        gParams.row_selector,
        gParams.rowidx_from,
        gParams.rowidx_to,
        gParams.column_ids,
        gParams.workercnt,
        gParams.memory_size,
        gParams.bdvd_dir,
        gParams.export_component,
        gParams.export_scale,
        gParams.artifact_detection,
        gParams.unwanted_factors,
        gParams.known_factors,
        gParams.export_names);

def outputR():
    obj = iBSDefines.loadPickle(
        iBSDefines.derivePickleFile(gParams.output_dir))

    infile = open("{0}/bdt/bdtR/outputTemplates/bdvdExportOutputTemplate.R".format(BDT_HomeDir))
    outfile = open("{0}/logs/output.R".format(gParams.output_dir), "w")

    ruvOut = obj.Export
    replacements = {
                    "__BFV_FILES__": str(ruvOut.BfvFiles).replace('[','').replace(']',''),
                    "__OUT_MAT_NAMES__": str(ruvOut.OutMatNames).replace('[','').replace(']',''),
                    "__MAT_ROW_CNT__":str(ruvOut.RowCnt),
                    "__MAT_COL_CNT__":str(ruvOut.ColCnt),
                    "__MAT_COL_NAMES__":str(ruvOut.ColNames).replace('[','').replace(']',''),
                    "__MAT_COL_IDS__":str(ruvOut.ColIDs).replace('[','').replace(']','')
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
    gParams = BDVDParams()
    gRunner = bdtUtil.bdtRunner()
    run_argv = sys.argv[:]

    try:
        if argv is None:
            argv = sys.argv
        args = gParams.parse_options(argv)
       
        start_time = datetime.now()

        gRunner.prepare_dirs(gParams.output_dir, gParams.logging_dir, gParams.pipeline_rundir)
        gRunner.init_logger(os.path.abspath(gParams.logging_dir + "/bdvd-export.log"))

        gRunner.logp()
        gRunner.log("Beginning bdvd export run v({0})".format(bdtUtil.get_version()))
        gRunner.logp("-----------------------------------------------")

        if gParams.dry_run and gParams.start_from == gSteps[0]:
            gParams.dry_run = False

        rowIdxsPickle = None
        if gParams.rowidxs_params is not None:
            if gParams.dry_run and gParams.start_from == gSteps[0]:
                gParams.dry_run = False
            rowIdxsPickle = s01_rowidxs()
            if gParams.dry_run and not os.path.exists(rowIdxsPickle):
                gRunner.log("retrieve existing result for: {0}".format(gSteps[0]))
                gRunner.log("from: {0}".format(rowIdxsPickle))
                gRunner.die('file not exist')
                gRunner.log("")

        if gParams.dry_run and gParams.start_from == gSteps[1]:
            gParams.dry_run = False

        s02_run_export(rowIdxsPickle)

        runSummary = iBSDefines.NodeRunSummaryDefine()
        runSummary.NodeDir = gParams.output_dir
        runSummary.NodeType = "bdvd-export"
        runSummaryPicke = "{0}/logs/runSummary.pickle".format(gParams.output_dir)
        iBSDefines.dumpPickle(runSummary, runSummaryPicke)

        # dump pickles generated from each step into one pickle
        allResults = iBSDefines.BdvdExportResultsDefine()
        bdvdExportPickle = os.path.abspath("{0}/run/{1}/{1}.pickle".format(gParams.output_dir, gSteps[1]))
        allResultsPicke = os.path.abspath("{0}/logs/results.pickle".format(gParams.output_dir))
        allResults.Export = iBSDefines.loadPickle(bdvdExportPickle)
        iBSDefines.dumpPickle(allResults, allResultsPicke)

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
