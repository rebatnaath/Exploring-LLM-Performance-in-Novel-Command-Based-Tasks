# LLM Command Task Evaluation

> Evaluating Large Language Models on novel command-based tasks requiring both structured syntax and spatial reasoning.

## Project Structure
.
├── ai-paint/ # Pixel-based drawing task application
│ ├── main.py # Main interface for pixel art generation
│ ├── efficiency.py # Efficiency analysis tools
│ ├── rate-flags.py # Flag evaluation interface
│ └── actual-flags/ # Reference images of original flags
│
├── maze/ # Maze navigation task application
│ ├── maze-main.py # Maze generation and navigation interface
│ ├── mazes/ # Maze configurations used in experiments
│ └── solutions/ # LLM-generated maze solutions
│
└── datas/ # Analysis data for model performance
├── flag_efficiency_detailed.json # Detailed efficiency metrics
└── flag_ratings.json # Human evaluation results


## Overview

This repository contains the code and data used in our research paper "Exploring LLM Performance in Novel Command-Based Tasks". We developed two custom applications to evaluate how seven leading Large Language Models perform on tasks requiring precise command syntax and spatial reasoning:

1. **Pixel Painting Task**: LLMs generate commands to recreate national flags using algebraic notation
2. **Maze Navigation Task**: LLMs produce movement sequences to navigate from start to goal in randomized mazes

Our evaluation found significant differences in model performance, with only one model successfully completing all maze navigation tasks.

## Key Findings

| LLM | Pixel Painting Score | Maze Success Rate |
|-----|----------------------|-------------------|
| GPT-o1 | 54.19 | 100% |
| Deepseek-r1 | 53.47 | 0% |
| Claude 3.5 | 48.80 | 0% |
| GPT-4o mini | 46.92 | 0% |
| Gemini 2.0 | 41.40 | 0% |
| Deepseek-V3 | 30.41 | 0% |
| Llama 3 | 28.69 | 0% |


