import os
import json
import base64
from tqdm import tqdm
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_gpt4v_response(question, chart_paths, model="gpt-4-vision-preview"):
    # Encode all images
    encoded_images = [encode_image(path) for path in chart_paths]
    
    # Prepare messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": question
                }
            ]
        }
    ]
    
    # Add each image to the message
    for encoded_image in encoded_images:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{encoded_image}"
            }
        })
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting response: {e}")
        return None

def collect_questions(data_dir="data"):
    """Collect all questions from the data directory"""
    questions = []
    for subdir in os.listdir(data_dir):
        subdir_path = os.path.join(data_dir, subdir)
        if os.path.isdir(subdir_path):
            json_path = os.path.join(subdir_path, f"{subdir}.json")
            if not os.path.exists(json_path):
                json_path = os.path.join(subdir_path, "chart-path_and_question-answer_pair.json")
            
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    for qa in data:
                        # Ensure charts is a list
                        charts = qa.get('image', [])
                        if not isinstance(charts, list):
                            charts = [charts]
                            
                        # Create full paths for each chart
                        chart_paths = []
                        for chart in charts:
                            # Handle both relative and absolute paths
                            if chart.startswith('data'):
                                # Convert Windows path to Unix path and get the filename
                                chart = os.path.basename(chart.replace('\\', '/'))
                            chart_path = os.path.join(subdir_path, chart)
                            chart_paths.append(chart_path)
                        
                        # Verify all chart files exist
                        if all(os.path.exists(path) for path in chart_paths):
                            questions.append({
                                'id': f"{subdir}_{qa['id']}",
                                'question': qa['question'],
                                'ground_truth': qa['answer'],
                                'charts': chart_paths
                            })
                        else:
                            print(f"Warning: Some chart files missing for question {qa['id']} in {subdir}")
                            print(f"Expected paths: {chart_paths}")
    return questions

def load_results(file_path):
    """Load results from a JSON file"""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        return json.load(f)

def save_results(results, file_path):
    """Save results to a JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(results, f, indent=2)

def get_results_file_path(model, results_dir="results"):
    """Get the results file path for a given model"""
    return os.path.join(results_dir, f"benchmark_results_{model.replace('-', '_')}.json")

def process_question(question, model):
    """Process a single question with the given model"""
    try:
        gpt_answer = get_gpt4v_response(question['question'], question['charts'], model)
        if gpt_answer:
            return {
                'id': question['id'],
                'question': question['question'],
                'ground_truth': question['ground_truth'],
                'gpt_answer': gpt_answer,
                'charts': question['charts'],
                'model': model
            }
    except Exception as e:
        print(f"Error processing question {question['id']}: {e}")
    return None 