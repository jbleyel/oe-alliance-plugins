#!/bin/sh

echo ""
echo "PEP8 double aggressive safe cleanup by Persian Prince"
# Script by Persian Prince for https://github.com/OpenVisionE2
# You're not allowed to remove my copyright or reuse this script without putting this header.
echo ""
echo "Changing py files, please wait ..." 
begin=$(date +"%s")

echo ""
echo "Fuff"
ruff check $(find . -type f -name "*.py" -printf "%h\n" | sort -u)
#git add -u
#git add *
#git commit -m "PEP8 double aggressive E401"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Change time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast changing would be less than 1 minute."
echo ""
echo "PEP8 Done!"
echo ""
