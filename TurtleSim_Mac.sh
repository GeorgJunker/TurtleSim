#!/bin/bash
echo "===== TurtleSim ====="
echo "By Psykodolph"

echo "Simulating..."
for I in *.inp; do
  echo "Working on" $I
  python ./sim.py $I
done
echo "Done simulating!"
echo "Outputs files are:"
for I in *.inp; do echo ${I%inp}out;done
read -p "Press Enter to exit..."
