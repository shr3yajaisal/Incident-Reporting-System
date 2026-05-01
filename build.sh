#!/bin/bash

# Build script for deployment
# This script builds the frontend and copies it to the backend static folder

echo "Building frontend..."
cd frontend
npm install
npm run build

echo "Copying frontend build to backend static folder..."
cd ..
rm -rf backend/static/*
cp -r frontend/dist/* backend/static/

echo "Build complete! Frontend files are in backend/static/"

