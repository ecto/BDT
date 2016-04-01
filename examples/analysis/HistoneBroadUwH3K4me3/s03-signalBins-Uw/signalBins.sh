thisScriptPath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. ${thisScriptPath}/../../../config/bdt_path_linux.sh

${bdtHome}/bdvdRowSelection \
    --thread-num 4 \
    --memory-size 8000 \
    --row-selector  with-signal \
    --bdvd-dir ${thisScriptPath}/../s02-bdvd/out \
    --column-ids 40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160 \
    --with-signal-threshold 1.4 \
    --with-signal-col-cnt 3 \
    --component signal+random \
    --scale mlog \
    --artifact-detection conservative \
    --unwanted-factors 0 \
    --known-factors 0 \
    --out ${thisScriptPath}/out

