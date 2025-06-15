import json
import os
from openai import OpenAI
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_results():
    # Load sampled questions
    with open("results/sampled_questions.json", "r") as f:
        sampled_questions = json.load(f)
    
    # Load results for each model
    results = {}
    for model in ['gpt-4o', 'gpt-4o-mini']:
        filename = f"results/benchmark_results_{model.replace('-', '_')}.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                results[model] = json.load(f)
    
    return sampled_questions, results

def load_existing_evaluations():
    eval_path = "results/evaluation_results.json"
    if os.path.exists(eval_path):
        with open(eval_path, "r") as f:
            evals = json.load(f)
        # {(id, model): is_correct}
        return {(e['id'], e['model']): e['is_correct'] for e in evals}
    return {}

def save_evaluations(evaluations):
    # 直接写入 evaluations（已是列表）
    with open("results/evaluation_results.json", "w") as f:
        json.dump(evaluations, f, indent=2)

def evaluate_answer(question, ground_truth, model_answer):
    client = OpenAI()
    
    prompt = f"""You are an expert evaluator for chart-based question answering tasks.
Please evaluate if the model's answer is correct compared to the ground truth answer.

Question: {question}
Ground Truth: {ground_truth}
Model Answer: {model_answer}

Please respond with ONLY "correct" or "incorrect"."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert evaluator for chart-based question answering tasks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        evaluation = response.choices[0].message.content.strip().lower()
        return evaluation == "correct"
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return False

def main():
    print("Loading results...")
    sampled_questions, model_results = load_results()
    existing_evals = load_existing_evaluations()
    all_eval_tasks = []

    # Prepare all (model, question) pairs to evaluate
    for model in model_results:
        for question in sampled_questions:
            key = (question['id'], model)
            if key in existing_evals:
                continue  # already evaluated
            result = next((r for r in model_results[model] if r['id'] == question['id']), None)
            if result:
                all_eval_tasks.append({
                    'id': question['id'],
                    'model': model,
                    'question': question['question'],
                    'ground_truth': question['ground_truth'],
                    'model_answer': result['gpt_answer']
                })

    print(f"Need to evaluate {len(all_eval_tasks)} items (skipping already done).")

    new_evals = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_task = {
            executor.submit(
                evaluate_answer, task['question'], task['ground_truth'], task['model_answer']
            ): task for task in all_eval_tasks
        }
        for future in tqdm(as_completed(future_to_task), total=len(future_to_task), desc="Evaluating"):
            task = future_to_task[future]
            try:
                is_correct = future.result()
                new_evals.append({
                    'id': task['id'],
                    'model': task['model'],
                    'is_correct': is_correct
                })
                # 合并已存在和新评估
                all_evals = [
                    {'id': k[0], 'model': k[1], 'is_correct': v}
                    for k, v in existing_evals.items()
                ] + new_evals
                save_evaluations(all_evals)
            except Exception as e:
                print(f"Error evaluating {task['id']} ({task['model']}): {e}")

    print("Done!")

if __name__ == "__main__":
    main() 