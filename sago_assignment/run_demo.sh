#!/bin/bash

# Sago Assignment Demo Runner
# This script sets up the environment, generates a dummy PDF, and runs the agent.

echo "Setting up Sago Pitch Deck Agent..."
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "Generating dummy pitch deck..."
python scripts/generate_pdf.py

echo "Running Agentic verification..."
echo "-----------------------------------"
python src/main.py --input data/samples/pitch_deck_dummy.pdf --output output_report.md

echo "-----------------------------------"
echo "Done! Report saved to 'output_report.md'"
