@echo off
echo Setting up Compass AI project directories
mkdir engine
mkdir navigator_ui
mkdir bob_core
echo # Compass AI > README.md
echo # Future Plans > futureplans.md
echo Initializing git repository
git init
git remote add origin https://github.com/AT512-dev/Team-AVON-Project-for-IBM-BOB-DEV-DAY
git add .
git commit -m "Initial project structure for Compass AI"
git branch -M main
echo Project setup successful
pause