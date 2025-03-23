@echo off
echo ===== TurtleSim =====
echo By Psykodolph

echo Simulating...

:: Loop through all .inp files in the current directory
for %%I in (*.inp) do (
    echo Working on %%I
    python ./sim.py %%I
)

echo Done simulating!
echo Output files are:

:: Print corresponding .out filenames
for %%I in (*.inp) do echo %%~nI.out

:: Wait for user input before exiting
pause
