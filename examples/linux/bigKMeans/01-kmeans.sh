thisScriptPath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. ${thisScriptPath}/../../config/bdt_path_linux.sh
${bdtHome}/bigKmeans \
	--data-input text-mat@${bdtDatasetsDir}/txtMat/dnase_test.txt \
	--data-nrow 92554 \
	--data-ncol 45 \
	--k 100 \
	--out ${thisScriptPath}/01-out \
	--thread-num 4 \
	--dist-type Euclidean \
	--max-iter 100 \
	--min-expchg 0.0001
