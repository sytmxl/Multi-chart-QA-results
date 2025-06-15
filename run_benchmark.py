import os
import json
import random
from tqdm import tqdm
from benchmark_utils import (
    load_results, save_results, get_results_file_path,
    process_question, collect_questions
)
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

batch_size = 2

def load_sampled_questions(sample_file):
    """Load previously sampled questions"""
    if os.path.exists(sample_file):
        with open(sample_file, 'r') as f:
            return json.load(f)
    return None

def save_sampled_questions(questions, sample_file):
    """Save sampled questions"""
    os.makedirs(os.path.dirname(sample_file), exist_ok=True)
    with open(sample_file, 'w') as f:
        json.dump(questions, f, indent=2)

def process_questions(questions, results, results_file, model, batch_size=2):
    """Process a list of questions and save results (with concurrency)"""
    processed_ids = {r['id'] for r in results}
    questions_to_process = [q for q in questions if q['id'] not in processed_ids]
    if not questions_to_process:
        print("All questions have been processed.")
        return

    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        future_to_q = {
            executor.submit(process_question, q, model): q for q in questions_to_process
        }
        for future in tqdm(as_completed(future_to_q), total=len(future_to_q), desc=f"Processing questions with {model}"):
            q = future_to_q[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    save_results(results, results_file)
            except Exception as e:
                print(f"Error processing question {q['id']}: {e}")

def run_benchmark(model_name, num_questions=150, batch_size=3):
    """
    Run the benchmark for a specific model.
    
    Args:
        model_name (str): Name of the model to benchmark
        num_questions (int): Total number of questions to have (including existing ones)
        batch_size (int): Number of questions to process in each batch
    """
    # Get results file path
    results_file = get_results_file_path(model_name)
    # Use a shared sample file for all models
    sample_file = os.path.join(os.path.dirname(results_file), "sampled_questions.json")
    
    # Load existing results if any
    results = load_results(results_file)
    processed_ids = {r['id'] for r in results}
    
    # Try to load previously sampled questions
    sampled_questions = load_sampled_questions(sample_file)
    
    if sampled_questions is None:
        # Get all questions
        all_questions = collect_questions()
        
        # Filter out already processed questions
        remaining_questions = [q for q in all_questions if q['id'] not in processed_ids]
        
        # Randomly sample questions if needed
        if num_questions and len(remaining_questions) > num_questions:
            remaining_questions = random.sample(remaining_questions, num_questions)
        
        # Save sampled questions
        save_sampled_questions(remaining_questions, sample_file)
        print(f"Sampled {len(remaining_questions)} questions and saved to {sample_file}")
    else:
        # If we already have sampled questions, check if we need to add more
        current_count = len(sampled_questions)
        if current_count < num_questions:
            print(f"Current sample has {current_count} questions, adding {num_questions - current_count} more...")
            
            # Get all questions
            all_questions = collect_questions()
            
            # Filter out already processed and sampled questions
            sampled_ids = {q['id'] for q in sampled_questions}
            remaining_questions = [q for q in all_questions 
                                if q['id'] not in processed_ids and q['id'] not in sampled_ids]
            
            # Calculate how many more questions we need
            additional_needed = num_questions - current_count
            if len(remaining_questions) > additional_needed:
                additional_questions = random.sample(remaining_questions, additional_needed)
                sampled_questions.extend(additional_questions)
                save_sampled_questions(sampled_questions, sample_file)
                print(f"Added {len(additional_questions)} more questions to the sample")
            else:
                print(f"Warning: Only {len(remaining_questions)} additional questions available")
                sampled_questions.extend(remaining_questions)
                save_sampled_questions(sampled_questions, sample_file)
                print(f"Added all remaining {len(remaining_questions)} questions to the sample")
        
        remaining_questions = sampled_questions
        print(f"Using {len(remaining_questions)} total sampled questions from {sample_file}")
    
    # 只处理未完成的题目
    remaining_questions = [q for q in sampled_questions if q['id'] not in processed_ids]
    if not remaining_questions:
        print("All questions have been processed.")
        return
    process_questions(remaining_questions, results, results_file, model_name, batch_size)

def main():
    parser = argparse.ArgumentParser(description='Run benchmark for multiple models')
    parser.add_argument('--models', nargs='+', default=['gpt-4o', 'gpt-4o-mini'],
                        help='List of models to benchmark')
    parser.add_argument('--num-questions', type=int, default=2000,
                        help='Number of questions to sample')
    parser.add_argument('--batch-size', type=int, default=batch_size,
                        help='Number of questions to process in each batch')
    args = parser.parse_args()
    
    for model in args.models:
        print(f"\nRunning benchmark for model: {model}")
        run_benchmark(model, args.num_questions, args.batch_size)

if __name__ == "__main__":
    main() 