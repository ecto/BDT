thisScriptPath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. ${thisScriptPath}/../../../config/bdt_path_linux.sh

${bdtHome}/bdvd \
		--data-input binary-mat@${bdtDatasetsDir}/zebrafish/data.bfv \
		--data-nrow 20865 \
		--data-ncol 6 \
		--data-col-names Ctl1,Ctl3,Ctl5,Trt9,Trt11,Trt13 \
		--data-calc-statistics \
		--out ${thisScriptPath}/01-out \
		--thread-num 4 \
		--memory-size 1000 \
		--pre-normalization column-sum \
		--common-column-sum median \
		--sample-groups [1,2,3],[4,5,6] \
		--ruv-scale mlog \
		--ruv-mlog-c 1 \
		--ruv-type ruvg \
		--control-rows-method specified-rows \
		--ctrl-rows-input text-rowids@${bdtDatasetsDir}/zebrafish/control-rows.txt \
		--ctrl-rows-index-base 1
