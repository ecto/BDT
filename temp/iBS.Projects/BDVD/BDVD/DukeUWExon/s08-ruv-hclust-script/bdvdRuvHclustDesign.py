import math
import iBS

# ----------------------------------------------------------------------
# RUV
# ----------------------------------------------------------------------

# specify number of unwanted factors to use
Ks=   [0,0,1,2,3,4,5,6,7,8,9,10,20,30,40,50]

# specify number of known factors to use
Ns=   [1,0,0,0,0,0,0,0,0,0,0,0, 0, 0, 0, 0 ]

RUVOutputMode = iBS.RUVOutputModeEnum.RUVOutputModeYminusZY

# specify expected groups, e.g., biological group
ExpectedGroups=[
    [1, 2, 3, 4, 158, 159, 160],
	[5, 6, 7, 177, 178, 179],
	[8, 9, 10, 155, 156],
	[11, 12, 13, 184, 185, 186],
	[14, 15, 169, 170],
	[16, 17, 192],
	[39, 197, 198],
	[45, 46, 47, 284, 285, 286, 287],
	[63, 64, 275, 276],
	[67, 68, 288, 289],
	[76, 77, 199, 200, 201],
	[101, 102, 103, 215, 216]]

labNames=["Duke","UW"]
dukeSamples=list(range(1,152+1))
uwSamples=list(range(153,334+1))

# specify unwanted group, e.g., labs
UnwantedGroups=[
    ("Duke", dukeSamples),
    ("UW", uwSamples)]

pdf_width=18
pdf_height=16