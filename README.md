# MultiChartQA

This repository contains the questions and answers for our Multi-chart Benchmark. At present, only the data is available, but the test code will be provided soon. We welcome everyone to use and explore our benchmark!

## Introduction

MultiChartQA is an extensive and demanding benchmark that features real-world charts. We source charts from various places to ensure both diversity and completeness. Each multi-chart group includes 2 or 3 charts, and each group is accompanied by 4 questions, typically spanning four distinct main categories. Now the expanded version of MultiChartQA contains 500 sets of multi-chart samples, 1370 charts, and 2000 questions.

## Overview

![method_00](https://github.com/user-attachments/assets/99165254-bf8c-43a0-b62e-1ae5e0b9ebdf)

## New Features()

### Benchmark Testing Tools

We have added tools to help run and evaluate the benchmark:

1. **Test Runner (`run_benchmark.py`)**
   - Runs the benchmark using GPT-4V
   - Supports random sampling of questions
   - Saves results incrementally
   - Features:
     - Random sampling of 100 questions
     - Progress tracking
     - Error handling
     - Results saving after each question

2. **Answer Evaluator (`evaluate_answers.py`)**
   - Evaluates GPT-4V answers using GPT-4
   - Provides detailed evaluation metrics
   - Features:
     - Correctness assessment
     - Confidence scoring
     - Explanation generation
     - Incremental saving

3. **Results Visualizer (`visualize_results.html`)**
   - Interactive visualization of test results
   - Features:
     - Chart display
     - Question and answer comparison
     - Correctness indicators (✅/❌)
     - Filtering and search
     - Statistics display
     - Responsive design

### Usage Instructions

1. **Running the Benchmark**
   ```bash
   pip install -r requirements.txt
   export OPENAI_API_KEY='your-api-key'
   python run_benchmark.py
   ```

2. **Evaluating Answers**
   ```bash
   python evaluate_answers.py
   ```

3. **Viewing Results**
   ```bash
   python server.py
   ```
   Then open `http://localhost:8000/visualize_results.html` in your browser

### File Structure

- `run_benchmark.py`: Main script for running the benchmark
- `evaluate_answers.py`: Script for evaluating answers
- `visualize_results.html`: Interactive visualization interface
- `server.py`: Simple HTTP server for visualization
- `requirements.txt`: Python dependencies
- `data/`: Contains all benchmark data
  - Each subdirectory contains:
    - Chart images (PNG files)
    - Question-answer pairs (JSON file)

### Dependencies

- Python 3.x
- openai>=1.0.0
- tqdm>=4.65.0

## License

[Add your license information here]

# Multi-Chart QA Results Visualization

This repository contains the visualization results for the Multi-Chart QA benchmark.

## Live Demo

Visit the live demo at: [https://sytmxl.github.io/Multi-chart-QA-results/visualize_results.html](https://sytmxl.github.io/Multi-chart-QA-results/visualize_results.html)

## Local Development

To run this visualization locally:

1. Clone this repository
2. Start a local server (e.g., using Python):
   ```bash
   python -m http.server 8000
   ```
3. Open http://localhost:8000/visualize_results.html in your browser

## Project Structure

- `visualize_results.html` - Main visualization page
- `results/` - Directory containing the benchmark results
  - `sampled_questions.json` - Sampled questions for evaluation
  - `benchmark_results_gpt_4o.json` - Results from GPT-4
  - `benchmark_results_gpt_4o_mini.json` - Results from GPT-4-mini
  - `evaluation_results.json` - Evaluation results

## Features

- Interactive visualization of QA results
- Filter questions by type and correctness
- Search functionality
- Annotation system for marking questions
- Export/Import annotations
- Statistics dashboard

## License

MIT License

