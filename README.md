# Purpose
These are some scripts to make pcb in a convinient situation 

# full_CNC_approach
In this folder there are few scripts for making 2 layer boards. Once finished designing the PCB in KiCad 9.0, you can export them in .gbr file, then use the full_CNC_approach/generate_g_code.sh to make the GCode, this scirpt used "pcb2gcode" to make the program. if "pcb2gcode" not available, there must be other alternative for example "flatCAM" that can run under windows to make the GCode. 

# Matching patterns after flip
For CNC machines, to make 2 layer board, it is very important that the CNC's X and Y axis are orthogonal. If it is not orthogonal with each other, when flipped, the hole and the pattern will not match well with each other,however some times the CNC just built and impossible to make it full 90 degree. So there is a way to first measure how much angle is there and then use script to fix it. so the code in full_CNC_approach/fix_orthogonality.py is used for, it will parse the gcode and map the X,Y axes according to flip axis, so that the orthogonality can be fixed one way or the other so that there are holes matching.

Of course if you are only making one side board, orthogonality is not a concern at all.

# CNC supports
Some CNC that uses old GBRL may not suppot G04 commands or accept them in a wierd way. so it is important to remove them with full_CNC_approach/fix_G04.py

# Automatic Tool Changing (ACT)
Hopefully ACT on ER11 heads can be invented, so there is less human time spent on making the CNC :) 
