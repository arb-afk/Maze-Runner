#!/bin/bash
# Build script for Vercel deployment
# This script builds the game and prepares it for deployment

echo "Installing pygbag..."
pip install pygbag --user --upgrade

echo "Building game for web..."
pygbag --build main.py

echo "Build complete! Files are in build/web/"
echo "You can now deploy to Vercel with: vercel --prod"





