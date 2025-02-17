#qsub -M fdu1@jhmi.edu -m e -cwd -pe local 30 -l mem_free=2G,h_vmem=200G correlation.sh

cd /dcs01/gcode/fdu1/BDT
node="s06-ruv-annotation"
projectDir="/dcs01/gcode/fdu1/projects/BDVD/DukeUWDNase/100bp/ruvs-var-r1"
nodeOutDir="${projectDir}/${node}"
#if [ -d "${nodeOutDir}" ]; then
	#rm ${nodeOutDir} -rf
#fi

designFile="${projectDir}/s06-ruv-annotation-script/ruvAnnotateDesign.py"

bdvd-ruv-annotation.py --node ${node} \
		--num-threads 36 \
		--max-mem 16000 \
		--output-dir ${nodeOutDir} \
		--resume \
		${designFile}

