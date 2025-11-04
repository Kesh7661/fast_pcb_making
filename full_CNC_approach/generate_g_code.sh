#!/bin/bash
# the pcb dimention is 117x178mm
prjnm="xxxx"
align_pos="-60";
pcb2gcode \
  --metric --metricoutput \
  --front ../${prjnm}-F_Cu.gbr \
  --back ../${prjnm}-B_Cu.gbr \
  --mirror-axis 91 \
  --zwork -2.0 \
  --zsafe 1 \
  --zchange 24.0 \
  --mill-feed 500 \
  --mill-speed 400 \
	--zdrill -2.5 \
	--drill ../${prjnm}-PTH.drl \
	--drill-feed 50 \
  --drill-speed 400 \
  --offset 0 \
	--nog81 true \
	--nog64 true \
  --extra-passes 0 \
  --mill-diameters 0.8 \
  --output-dir out 


	#--spinup-time 0 \
	#--spindown-time 0 \
	#--nog64 true \
	#--nog04 true \

python fix_g04.py ./out/front.ngc ./out/front_fixed.ngc
python fix_g04.py ./out/back.ngc ./out/back_fixed.ngc
python fix_orthogonality.py ${align_pos} ./out/back_fixed.ngc ./out/back_orthogonal_fixed.ngc
python fix_g04.py ./out/drill.ngc ./out/drill_fixed.ngc

rm ./out/front.ngc
rm ./out/back.ngc
rm ./out/drill.ngc
rm ./out/back_fixed.ngc

