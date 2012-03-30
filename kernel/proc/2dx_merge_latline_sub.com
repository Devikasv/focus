#
#############################################################################
#                                                                           #
# This is not an executable script.                                         #
#                                                                           #
# This should be sourced from the calling script.                           #
#                                                                           #
# (C) 2dx.org, GNU Plublic License.                                         #
#                                                                           #
# Created..........: 01/03/2007                                             #
# Last Modification: 01/03/2007                                             #
# Author...........: 2dx.org                                                #
#                                                                           #
#############################################################################
#
echo bin_2dx = ${bin_2dx}
echo proc_2dx = ${proc_2dx}
echo ccp4 = ${ccp4}
echo bin_ccp4 = ${bin_ccp4}
#
# this is for a later option:
set mode = 0
#
if ( ${mode} == 0 ) then
  #
  #############################################################################
  #                                                                           #
  ${proc_2dx}/linblock "LATLINPRESCAL - to apply CTF correction and weight calculation"
  #                                                                           #
  #                                          merge_3ds.aph  =>  latlines.dat  #
  #                                                                           #
  #############################################################################
  #
  \rm -f fort.1
  \rm -f fort.3
  #
  \ln -s APH/merge.aph fort.1
  #
  echo "Calling: " > LOGS/latlinprescal.log
  echo "======== " >> LOGS/latlinprescal.log
  echo " " >> LOGS/latlinprescal.log
  #
  echo "  ${bin_2dx}/2dx_latlinprescal.exe << eot >> LOGS/latlinprescal.log " >> LOGS/latlinprescal.log
  echo "1001,${zminmax} ! NSER,ZMIN,ZMAX " >> LOGS/latlinprescal.log
  echo "${MergeIQMAX}               ! IQMAX " >> LOGS/latlinprescal.log
  echo "${max_amp_correction}       ! Max_Amp_Correction" >> LOGS/latlinprescal.log
  echo "eot " >> LOGS/latlinprescal.log
  echo " " >> LOGS/latlinprescal.log
  echo "Running: " >> LOGS/latlinprescal.log
  echo "======== " >> LOGS/latlinprescal.log
  #
  #
  ${bin_2dx}/2dx_latlinprescal.exe << eot >> LOGS/latlinprescal.log
1001,${zminmax} ! NSER,ZMIN,ZMAX
${MergeIQMAX}               ! IQMAX
${max_amp_correction}       ! Max_Amp_Correction
eot
  #
  \rm -f fort.1
  echo "################################################"
  echo "################################################"
  echo "output in file LOGS/latlinprescal.log"
  echo "################################################"
  echo "################################################"
  #
  if ( -e fort.3 ) then
    \mv -f fort.3 SCRATCH/latlines.dat
    echo "# IMAGE: LOGS/latlinprescal.log <LOG: latlinprescal output>" >> LOGS/${scriptname}.results
    echo "# IMAGE: SCRATCH/latlines.dat <Latline after prescal [H,K,Z,A,P,FOM,SAMP,SANG,IQ]>" >> LOGS/${scriptname}.results
  else
    ${proc_2dx}/protest "ERROR: latlines.dat does not exist."
  endif
  #
  echo " "
  ${proc_2dx}/lin "-"
  echo " "
  #
endif
#
#############################################################################
#                                                                           #
${proc_2dx}/linblock "LATLINEK - to fit lattice lines to merged data (D.Agard's program)"
#                                                                           #
#                latlines.dat  =>  latfitteds.dat + LATLINE.PLT + guess.dat #
#                                                                           #
#############################################################################
#
echo "<<@progress: +5>>"
#
\rm -f PLOT.PS
\rm -f PS/latline.ps
\rm -f SCRATCH/latfitteds.dat
\rm -f SCRATCH/guess.dat
\rm -f latline.statistics
#
set iplterr = 0
set idoh = 0
set idok = 0
set IAQP2 = 0
set iplterr = 1         
set imaxIQplot = 4
set MergeIGUESS = 1
#
if ( ${tempkeep} == 'y' ) then
  set iverbose = 1
else
  set iverbose = 1
endif
#
setenv  OBS   SCRATCH/latlines.dat
setenv  OUT   SCRATCH/latfitteds.dat
setenv  GUESS SCRATCH/guess.dat
#
echo " "
echo " Parameters for latline are:"
echo " "
echo "2dx_merge_latline_sub.com, ${date}"
echo "${spcgrp}                            # IPG (Plane group number 1-17)"
echo "0                             # IPAT, 0=F & Phase, 1=Intensity data"
echo "${MergeAK},${MergeIWF_VAL},${MergeIWP_VAL}                      # AK,IWF,IWP - relative weights, + individual sigmas"
echo "${ALAT},${zminmax},${MergeDELPLT}        # ALAT,ZMIN,ZMAX,DELPLT "
echo "${MergeDELPRO},${MergeRminRmax},${MergeRCUT},${MergePFACT}        # DELPRO,RMIN,RMAX,RCUT,PFACT"
echo "${MergeIGUESS},${MergeBINSIZ}                       # IGUESS,BINSIZ"
echo "${MergeNCYCLS},${MergeMPRINT}                          # NCYCLS,MPRINT"
echo "${idoh},${idok}		                          # H,K indices to plot. 0 0 = all."
echo "${IAQP2},${iplterr},${imaxIQplot}                         # IAQP2: 1=y,0=n, iplterr=1:errbar in PHS, maxIQ for PSplot"
echo " "
#
${bin_2dx}/2dx_latlinek.exe << eot > LOGS/2dx_latlinek.log
2dx_merge_latline_sub.com, ${date}
${spcgrp}                                                    ! IPG (Plane group number 1-17)
0                                                            ! IPAT, 0=F & Phase, 1=Intensity data
${MergeAK},${MergeIWF_VAL},${MergeIWP_VAL}                   ! AK,IWF,IWP - relative weights, + individual sigmas
${ALAT},${zminmax},${MergeDELPLT}                            ! ALAT,ZMIN,ZMAX,DELPLT
${MergeDELPRO},${MergeRminRmax},${MergeRCUT},${MergePFACT}   ! DELPRO,RMIN,RMAX,RCUT,PFACT
${MergeIGUESS},${MergeBINSIZ}                                ! IGUESS,BINSIZ
${MergeNCYCLS},${MergeMPRINT}                                ! NCYCLS,MPRINT
${idoh},${idok}                                              ! H,K indices to plot. 0 0 = all.
${IAQP2},${iplterr},${imaxIQplot}                            ! IAQP2: 1=y,0=n, iplterr=1:errbar in PHS, maxIQ for PSplot
eot
#
echo "################################################"
echo "################################################"
echo "output in file LOGS/2dx_latlinek.log"
echo "################################################"
echo "################################################"
#
echo "# IMAGE: LOGS/2dx_latlinek.log <LOG: 2dx_latlinek output>" >> LOGS/${scriptname}.results
echo "# IMAGE: SCRATCH/latline_stat.dat <Lattice line statistics>" >> LOGS/${scriptname}.results
echo "# IMAGE: SCRATCH/latfitteds.dat <Lattice line fit data [H,K,Z,A,PHI,SIGF,SIGP,FOM]>" >> LOGS/${scriptname}.results
if ( -e SCRATCH/guess.dat ) then
  echo "# IMAGE: SCRATCH/guess.dat <Lattice line guess data>" >> LOGS/${scriptname}.results
endif
if ( ! -e latline.statistics ) then
  ${proc_2dx}/linblock "#"
  ${proc_2dx}/linhash "3D modus, but do you have 3D (i.e. tilted) data?"
  ${proc_2dx}/protest "ERROR in latlinek. Check logfile."
endif
\mv -f latline.statistics SCRATCH/latline_stat.dat
#
if ( ! -e PLOT.PS ) then
  ${proc_2dx}/protest "2dx_latlinek: ERROR occured."
endif
#
\mv -f PLOT.PS PS/latline.ps 
echo "# IMAGE-IMPORTANT: PS/latline.ps <PS: Lattice lines>" >> LOGS/${scriptname}.results
#
echo " "
${proc_2dx}/lin "-"
echo " "
#
echo "<<@progress: +5>>"
#
# if ( ${mode} != 0 ) then
#   exit
# endif
#
#############################################################################
#                                                                           #
${proc_2dx}/linblock "PREPMKMTZ - Program to convert fitted data to CCP4 format"
#                                                                           #
#############################################################################
#
\rm -f APH/latfitted_nosym.hkl
#
setenv IN SCRATCH/latfitteds.dat
setenv OUT APH/latfitted_nosym.hkl
setenv REFHKL APH/latfittedref_nosym.hkl
#
${bin_2dx}/prepmklcf.exe << eot > LOGS/prepmklcf.log
${RESMAX},1.5                          ! RESOLUTION,REDUCAC (1.5 = 60deg phase error)
${realcell},${realang},${ALAT}         ! a,b,gamma,c
1.0                                    ! SCALE
eot
#
echo "################################################"
echo "################################################"
echo "output in file LOGS/prepmklcf.log"
echo "################################################"
echo "################################################"
#
echo "# IMAGE: LOGS/prepmklcf.log <LOG: prepmklcf output>" >> LOGS/${scriptname}.results
echo "# IMAGE: APH/latfitted_nosym.hkl <APH: Latline for vol after prepmklcf [H,K,L,A,P,FOM]>" >> LOGS/${scriptname}.results
echo "# IMAGE: APH/latfittedref_nosym.hkl <APH: Latline for ref after prepmklcf [H,K,L,A,P,FOM,SIGA]>" >> LOGS/${scriptname}.results
#
echo "<<@progress: +5>>"
#
#############################################################################
${proc_2dx}/linblock "2dx_hklsym2 - to apply symmetry to latfitted APH file, for volume"
#############################################################################  
#
${bin_2dx}/2dx_hklsym2.exe << eot
APH/latfitted_nosym.hkl
APH/latfitted.hkl
${spcgrp}
0     ! no header line
0     ! no sigma column
eot
#
echo "<<@progress: +5>>"
#
if ( ! -e APH/latfitted.hkl ) then
  ${proc_2dx}/protest "ERROR: APH/latfitted.hkl not produced."
endif
#
echo "# IMAGE: APH/latfitted.hkl <APH: Latline for vol after sym [H,K,L,A,P,FOM]>" >> LOGS/${scriptname}.results
#
#############################################################################
${proc_2dx}/linblock "2dx_hklsym2 - to apply symmetry to latfitted APH file, for reference"
#############################################################################  
#
${bin_2dx}/2dx_hklsym2.exe << eot
APH/latfittedref_nosym.hkl
APH/latfittedref.hkl
${spcgrp}
0     ! no header line
1     ! with sigma column
eot
#
echo "<<@progress: +5>>"
#
if ( ! -e APH/latfittedref.hkl ) then
  ${proc_2dx}/protest "ERROR: APH/latfittedref.hkl not produced."
endif
#
echo "# IMAGE: APH/latfittedref.hkl <APH: Latline for ref after sym [H,K,L,A,P,FOM,SIGA]>" >> LOGS/${scriptname}.results
#
#############################################################################
${proc_2dx}/linblock "2dx_phasezero - to zero phases for PSF calculation"
#############################################################################
#
\rm -f APH/latfitted_phase_zero.hkl
#
${bin_2dx}/2dx_phasezero.exe << eot
APH/latfitted.hkl
APH/latfitted_phase_zero.hkl
0
eot
#
#############################################################################
${proc_2dx}/linblock "f2mtz - Program to convert hkl data into MTZ format, for PSF"
#############################################################################
#
set infile = APH/latfitted_phase_zero.hkl
\rm -f merge3D_phase_zero.mtz
#
${bin_ccp4}/f2mtz hklin ${infile} hklout merge3D_phase_zero.mtz << eof
TITLE  P1 map, ${date}
CELL ${realcell} ${ALAT} 90.0 90.0 ${realang}
SYMMETRY ${CCP4_SYM}
LABOUT H K L F PHI FOM
CTYPOUT H H H F P W
FILE ${infile}
SKIP 0
END
eof
#
echo "# IMAGE: merge3D_phase_zero.mtz <MTZ: Full latline for PSF>" >> LOGS/${scriptname}.results
echo "<<@progress: +5>>"
#
#############################################################################
${proc_2dx}/linblock "f2mtz - Program to convert hkl data into MTZ format, for volume"
#############################################################################
#
set infile = APH/latfitted.hkl
\rm -f merge3D.mtz
#
${bin_ccp4}/f2mtz hklin ${infile} hklout merge3D.mtz << eof
TITLE  P1 map, ${date}
CELL ${realcell} ${ALAT} 90.0 90.0 ${realang}
SYMMETRY ${CCP4_SYM}
LABOUT H K L F PHI FOM
CTYPOUT H H H F P W
FILE ${infile}
SKIP 0
END
eof
#
echo "# IMAGE-IMPORTANT: merge3D.mtz <MTZ: Full latline for volume>" >> LOGS/${scriptname}.results
echo "<<@progress: +5>>"
#
#
#############################################################################
${proc_2dx}/linblock "f2mtz - Program to convert hkl data into MTZ format, for reference"
#############################################################################
#
set infile = APH/latfittedref.hkl
\rm -f merge3Dref.mtz
#
${bin_ccp4}/f2mtz hklin ${infile} hklout merge3Dref.mtz << eof
TITLE  P1 map, ${date}
CELL ${realcell} ${ALAT} 90.0 90.0 ${realang}
SYMMETRY ${CCP4_SYM}
LABOUT H K L F PHI FOM SIGA
CTYPOUT H H H F P W W
FILE ${infile}
SKIP 0
END
eof
#
echo "# IMAGE-IMPORTANT: merge3Dref.mtz <MTZ: Full latline for reference>" >> LOGS/${scriptname}.results
#
####################################################################################
#                                                                                  #
${proc_2dx}/linblock "sftools to expand mtz and to eliminate lattice lines with illegal phases"
#                                                                                  #
####################################################################################
#
\rm -f merge3D_phase_zero_nophaerr.mtz
#
${bin_ccp4}/sftools << eof
read merge3D_phase_zero.mtz
sort h k l 
set spacegroup
${CCP4_SYM}
select phaerr
select invert
purge
y
set spacegroup
1
expand
reindex matrix 1 0 0  0 0 1  0 1 0  
y
sort h k l 
write merge3D_phase_zero_nophaerr.mtz
quit
eof
#
echo "# IMAGE: merge3D_phase_zero_nophaerr.mtz <MTZ: Full latline for PSF, nophaerr>" >> LOGS/${scriptname}.results
echo "<<@progress: +5>>"
#
####################################################################################
#                                                                                  #
${proc_2dx}/linblock "sftools to expand mtz and to eliminate lattice lines with illegal phases"
#                                                                                  #
####################################################################################
#
\rm -f SCRATCH/merge3Dref_nophaerr_tmp.mtz
#
${bin_ccp4}/sftools << eof
read merge3Dref.mtz
sort h k l 
set spacegroup
${CCP4_SYM}
select phaerr
select invert
purge
y
set spacegroup
1
expand
write SCRATCH/merge3Dref_nophaerr_tmp.mtz
quit
eof
#
if ( ! -e SCRATCH/merge3Dref_nophaerr_tmp.mtz ) then
  ${proc_2dx}/protest "ERROR: SCRATCH/merge3Dref_nophaerr_tmp.mtz was not created."
endif
#
# this should guarantee that the file is never missing:
\mv -f SCRATCH/merge3Dref_nophaerr_tmp.mtz merge3Dref_nophaerr.mtz
# \cp -f merge3Dref_nophaerr.mtz merge3Dref.mtz
#
echo "# IMAGE-IMPORTANT: merge3Dref_nophaerr.mtz <MTZ: Latlines without phase-error for synref>" >> LOGS/${scriptname}.results
echo "<<@progress: +5>>"
#
#

