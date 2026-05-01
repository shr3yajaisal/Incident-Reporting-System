@echo off
REM Build script for Windows deployment
REM This script builds the frontend and copies it to the backend static folder

echo Building frontend...
cd frontend
call npm install
call npm run build

echo Copying frontend build to backend static folder...
cd ..
if exist backend\static rmdir /s /q backend\static
mkdir backend\static
xcopy /E /I /Y frontend\dist\* backend\static\

echo Build complete! Frontend files are in backend\static\

