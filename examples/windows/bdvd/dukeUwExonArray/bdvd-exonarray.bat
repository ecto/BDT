@ECHO OFF
SET thisScriptPath=%~dp0
SET pathConfigBat=%~dp0..\..\..\config\bdt_path_win.bat
call %pathConfigBat%

py %bdtInstallDir%\bdvd ^
	--data-input text-mat@%bdtDatasetsDir%\DukeUWExon\GeneBASE_DukeUWExon_qn.csv ^
	--data-nrow 18524 ^
	--data-ncol 334 ^
	--data-col-names K562_wg530_s1,K562_wg530_s2,K562_wg530_s3,K562_wg530_s4,GM12878_wg534_s5,GM12878_wg534_s6,GM12878_wg534_s7,HepG2_wg537_s8,HepG2_wg537_s9,HepG2_wg537_s10,HeLa-S3_wg540_s11,HeLa-S3_wg540_s12,HeLa-S3_wg540_s13,HUVEC_wg548_s14,HUVEC_wg548_s15,NHEK_wg553_s16,NHEK_wg553_s17,H1-hESC_wg556_s18,H1-hESC_wg556_s19,H1-hESC_wg556_s20,H1-hESC_wg556_s21,GM12891_wg564_s22,GM12891_wg564_s23,GM12892_wg565_s24,GM12892_wg565_s25,GM19238_wg566_s26,GM19238_wg566_s27,GM19239_wg567_s28,GM19239_wg567_s29,GM19240_wg568_s30,GM19240_wg568_s31,Medullo_wg574_s32,Medullo_wg574_s33,Medullo_wg574_s34,ProgFib_wg576_s35,ProgFib_wg576_s36,HeLa-S3_wg577_s37,HeLa-S3_wg577_s38,MCF-7_wg579_s39,GM18507_wg581_s40,GM18507_wg581_s41,GM18507_wg581_s42,Fibrobl_wg583_s43,Fibrobl_wg583_s44,HSMM_wg584_s45,HSMM_wg584_s46,HSMM_wg584_s47,HSMMtube_wg585_s48,HSMMtube_wg585_s49,HSMMtube_wg585_s50,H9ES_wg594_s51,H9ES_wg594_s52,H9ES_wg594_s53,Chorion_wg595_s54,AoSMC_wg601_s55,AoSMC_wg601_s56,Melano_wg602_s57,Melano_wg602_s58,Melano_wg602_s59,Melano_wg602_s60,Myometr_wg603_s61,Myometr_wg603_s62,A549_wg095_s63,A549_wg095_s64,LNCaP_wg096_s65,LNCaP_wg096_s66,LNCaP_wg097_s67,LNCaP_wg097_s68,Osteobl_wg098_s69,Osteobl_wg098_s70,Osteobl_wg098_s71,Gliobla_wg100_s72,Gliobla_wg100_s73,Gliobla_wg100_s74,Gliobla_wg100_s75,HMEC_wg101_s76,HMEC_wg101_s77,8988T_wg103_s78,8988T_wg103_s79,CLL_wg104_s80,CLL_wg104_s81,HTR8svn_wg105_s82,HTR8svn_wg105_s83,HPDE6-E6E7_wg106_s84,HPDE6-E6E7_wg106_s85,Hepatocytes_wg107_s86,Hepatocytes_wg107_s87,Stellate_wg108_s88,Stellate_wg108_s89,Huh-7_wg111_s90,Huh-7_wg111_s91,Huh-7.5_wg112_s92,Huh-7.5_wg112_s93,Urothelia_wg113_s94,Urothelia_wg113_s95,Urothelia_wg114_s96,Urothelia_wg114_s97,MCF-7_wg745_s98,Colo829_wg549_s99,Colo829_wg549_s100,H7-hESC_wg554_s101,H7-hESC_wg554_s102,H7-hESC_wg554_s103,HSMM_FSHD_wg556_s104,HSMM_FSHD_wg556_s105,HSMM_FSHD_wg556_s106,Mel_2183_wg557_s107,Mel_2183_wg557_s108,iPS_NIHi7_wg558_s109,iPS_NIHi7_wg558_s110,K562_wg559_s111,K562_wg559_s112,K562_wg559_s113,K562_wg559_s114,iPS_CWRU1_wg560_s115,iPS_CWRU1_wg560_s116,iPS_NIHi11_wg561_s117,iPS_NIHi11_wg561_s118,HEK293T_wg565_s119,HEK293T_wg565_s120,FibroP_AG08395_wg567_s121,FibroP_AG08395_wg567_s122,FibroP_AG08395_wg567_s123,FibroP_AG08396_wg568_s124,FibroP_AG08396_wg568_s125,FibroP_AG08396_wg568_s126,FibroP_AG20443_wg569_s127,FibroP_AG20443_wg569_s128,FibroP_AG20443_wg569_s129,MCF-7_wg467_s130,MCF-7_wg467_s131,MCF-7_wg467_s132,MCF-7_wg468_s133,MCF-7_wg468_s134,MCF-7_wg468_s135,AoSMC_wgSMC_s136,AoSMC_wgSMC_s137,AoSMC_wgGFb_s138,AoSMC_wgGFb_s139,NH-A_wgocy_s140,NH-A_wgocy_s141,HeLa-S3_wgFNg_s142,HeLa-S3_wgg4h_s143,HSMMtube_FSHD_wgSHD_s144,HSMMtube_FSHD_wgSHD_s145,HSMMtube_FSHD_wgSHD_s146,MCF-7_wggen_s147,MCF-7_wggen_s148,MCF-7_wgcle_s149,MCF-7_wgcle_s150,UCH-1_wgH-1_s151,UCH-1_wgH-1_s152,GM06990_wg481_s1,GM06990_wg481_s2,HepG2_wg537_s3,HepG2_wg537_s4,Th1_wg483_s5,K562_wg530_s6,K562_wg530_s7,K562_wg530_s8,SK-N-SH_RA_wg485_s9,SK-N-SH_RA_wg485_s10,SK-N-SH_RA_wg485_s11,Caco-2_wg486_s12,CACO2_wg486_s13,BJ_wg487_s14,BJ_wg487_s15,BJ_wg487_s16,HUVEC_wg548_s17,HUVEC_wg548_s18,HL-60_wg489_s19,HL-60_wg489_s20,SKMC_wg490_s21,SKMC_wg490_s22,SKMC_wg490_s23,Th2_wg491_s24,GM12878_wg534_s25,GM12878_wg534_s26,GM12878_wg534_s27,HRCEpiC_wg493_s28,HRCEpiC_wg493_s29,HRE_wg494_s30,HRE_wg494_s31,HeLa-S3_wg540_s32,HeLa-S3_wg540_s33,HeLa-S3_wg540_s34,JURKAT_wg497_s35,JURKAT_wg497_s36,NB4_wg498_s37,NB4_wg498_s38,NB4_wg498_s39,NHEK_wg553_s40,PANC-1_wg500_s41,PANC-1_wg500_s42,SAEC_wg501_s43,SAEC_wg501_s44,MCF-7_wg579_s45,MCF-7_wg579_s46,HMEC_wg101_s47,HMEC_wg101_s48,HMEC_wg101_s49,HGF_wg504_s50,HGF_wg504_s51,AG04449_wg505_s52,AG04449_wg505_s53,AG04450_wg506_s54,AG04450_wg506_s55,AG09309_wg507_s56,AG09309_wg507_s57,AG09319_wg508_s58,AG09319_wg508_s59,AG10803_wg509_s60,AG10803_wg509_s61,CMK_wg510_s62,H7-hESC_wg554_s63,H7-hESC_wg554_s64,HAEpiC_wg512_s65,HAEpiC_wg512_s66,HCF_wg513_s67,HCF_wg513_s68,HCPEpiC_wg514_s69,HCPEpiC_wg514_s70,HEEpiC_wg515_s71,HEEpiC_wg515_s72,HNPCEpiC_wg516_s73,HNPCEpiC_wg516_s74,HRPEpiC_wg517_s75,HRPEpiC_wg517_s76,NHDF-neo_wg518_s77,NHDF-neo_wg518_s78,HCM_wg519_s79,HCM_wg519_s80,GM12865_wg520_s81,GM12865_wg520_s82,NHLF_wg521_s83,NHLF_wg521_s84,AoAF_wg161_s85,AoAF_wg161_s86,HCT-116_wg162_s87,HCT-116_wg162_s88,HMVEC-LBl_wg163_s89,HMVEC-LBl_wg163_s90,HCFaa_wg164_s91,HCFaa_wg164_s92,HConF_wg165_s93,HConF_wg165_s94,HMF_wg166_s95,HMF_wg166_s96,HMVEC-LLy_wg167_s97,HMVEC-LLy_wg167_s98,HMVEC-dBl-Ad_wg168_s99,HMVEC-dBl-Ad_wg168_s100,HMVEC-dBl-Neo_wg169_s101,HMVEC-dBl-Neo_wg169_s102,HMVEC-dLy-Ad_wg170_s103,HMVEC-dLy-Ad_wg170_s104,HMVEC-dLy-Neo_wg171_s105,HMVEC-dLy-Neo_wg171_s106,HMVEC-dNeo_wg172_s107,HMVEC-dNeo_wg172_s108,HPAF_wg173_s109,HPAF_wg173_s110,HPF_wg174_s111,HPF_wg174_s112,HPdLF_wg175_s113,HPdLF_wg175_s114,HVMF_wg176_s115,HVMF_wg176_s116,NHDF-Ad_wg177_s117,NHDF-Ad_wg177_s118,HBMEC_wg178_s119,HBMEC_wg178_s120,NH-A_wg179_s121,NH-A_wg179_s122,A549_wg095_s123,A549_wg095_s124,BE2_C_wg181_s125,BE2_C_wg181_s126,GM12864_wg182_s127,HA-sp_wg183_s128,HA-sp_wg183_s129,HIPEpiC_wg184_s130,HIPEpiC_wg184_s131,HSMM_wg584_s132,HSMM_wg584_s133,HSMM_wg584_s134,HSMM_wg584_s135,LNCaP_wg097_s136,LNCaP_wg097_s137,RPTEC_wg188_s138,RPTEC_wg188_s139,SK-N-MC_wg189_s140,SK-N-MC_wg189_s141,WERI-Rb-1_wg190_s142,HA-h_wg191_s143,HA-h_wg191_s144,HAc_wg192_s145,HAc_wg192_s146,HFF_wg193_s147,HFF_wg193_s148,HFF_Myc_wg194_s149,HFF_Myc_wg194_s150,HRGEC_wg195_s151,HRGEC_wg195_s152,Monocytes-CD14+_RO01746_wg196_s153,WI-38_wg197_s154,WI-38_wg197_s155,WI-38_wg198_s156,WI-38_wg198_s157,HPAEC_wg886_s158,NT2-D1_wg887_s159,NT2-D1_wg887_s160,PrEC_wg888_s161,PrEC_wg888_s162,HMVEC-dAd_wg889_s163,HMVEC-dAd_wg889_s164,H7-hESC_wg576_s165,H7-hESC_wg576_s166,H7-hESC_wg577_s167,H7-hESC_wg577_s168,H7-hESC_wg578_s169,H7-hESC_wg578_s170,HBVP_wg579_s171,HBVSMC_wg580_s172,HBVSMC_wg580_s173,NHBE_RA_wg582_s174,NHBE_RA_wg582_s175,H7-hESC_wg019_s176,H7-hESC_wg019_s177,AH3_wgAH3_s178,AH3_wgAH3_s179,HEK293_wg293_s180,HEK293_wg293_s181,HEK293_wg293_s182 ^
	--data-skip-cols 1 ^
	--data-skip-rows 1 ^
	--data-col-sep "," ^
	--data-calc-statistics ^
	--out %thisScriptPath%01-out ^
	--thread-num 4 ^
	--memory-size 1000 ^
	--sample-groups [1,2,3,4,158,159,160],[5,6,7,177,178,179],[8,9,10,155,156],[11,12,13,184,185,186],[14,15,169,170],[16,17,192],[18,19,20,21],[22,23],[24,25],[26,27],[28,29],[30,31],[32,33,34],[35,36],[37,38],[39,197,198],[40,41,42],[43,44],[45,46,47,284,285,286,287],[48,49,50],[51,52,53],[54],[55,56],[57,58,59,60],[61,62],[63,64,275,276],[65,66],[67,68,288,289],[69,70,71],[72,73,74,75],[76,77,199,200,201],[78,79],[80,81],[82,83],[84,85],[86,87],[88,89],[90,91],[92,93],[94,95],[96,97],[98],[99,100],[101,102,103,215,216],[104,105,106],[107,108],[109,110],[111,112,113,114],[115,116],[117,118],[119,120],[121,122,123],[124,125,126],[127,128,129],[130,131,132],[133,134,135],[136,137],[138,139],[140,141],[142],[143],[144,145,146],[147,148],[149,150],[151,152],[153,154],[157],[161,162,163],[164,165],[166,167,168],[171,172],[173,174,175],[176],[180,181],[182,183],[187,188],[189,190,191],[193,194],[195,196],[202,203],[204,205],[206,207],[208,209],[210,211],[212,213],[214],[217,218],[219,220],[221,222],[223,224],[225,226],[227,228],[229,230],[231,232],[233,234],[235,236],[237,238],[239,240],[241,242],[243,244],[245,246],[247,248],[249,250],[251,252],[253,254],[255,256],[257,258],[259,260],[261,262],[263,264],[265,266],[267,268],[269,270],[271,272],[273,274],[277,278],[279],[280,281],[282,283],[290,291],[292,293],[294],[295,296],[297,298],[299,300],[301,302],[303,304],[305],[306,307],[308,309],[310],[311,312],[313,314],[315,316],[317,318],[319,320],[321,322],[323],[324,325],[326,327],[328,329],[330,331],[332,333,334] ^
	--ruv-scale mlog ^
	--ruv-mlog-c 1 ^
	--ruv-type ruvs ^
	--control-rows-method all ^
	--permutation-num 10