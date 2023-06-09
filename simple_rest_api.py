import json
import pickle
from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# Load projects from JSON file
with open('projects.json', 'r') as file:
    projects_data = json.load(file)
    projects = projects_data['projects']

# Read projects from pickle file on startup
try:
    with open('projects.pickle', 'rb') as file:
        projects = pickle.load(file)
except FileNotFoundError:
    pass

# Get project by ID
@app.route('/project/<project_id>')
def get_project(project_id):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project:
        return jsonify(project)
    else:
        return jsonify({'message': 'Project not found'}), 404

# Create a new project
@app.route('/project', methods=['POST'])
def create_project():
    try:
        request_data = request.get_json()
        name = request_data['name']
        creation_date = request_data['creation_date']
        completed = request_data['completed']
        tasks = request_data['tasks']

        new_project_id = uuid.uuid4().hex[:24]
        new_project = {
            'id': new_project_id,
            'name': name,
            'creation_date': creation_date,
            'completed': completed,
            'tasks': tasks
        }

        projects.append(new_project)
        save_data(projects)

        return jsonify({'message': f'Project created with id: {new_project_id}'}), 200
    except:
        return jsonify({'message': 'Invalid request'}), 400

# Mark a project as completed
@app.route('/project/<project_id>/complete', methods=['POST'])
def complete_project(project_id):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project:
        if not project['completed']:
            project['completed'] = True
            save_data(projects)
        return jsonify(project)
    else:
        return jsonify({'message': 'Project not found'}), 404

# Add a task to a project
@app.route('/project/<project_id>/task', methods=['POST'])
def add_task_to_project(project_id):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project:
        try:
            request_data = request.get_json()
            task_name = request_data['name']
            task_completed = request_data['completed']
            checklist = request_data['checklist']

            task_id = uuid.uuid4().hex[:24]
            task = {
                'id': task_id,
                'name': task_name,
                'completed': task_completed,
                'checklist': checklist
            }

            project['tasks'].append(task)
            save_data(projects)

            return jsonify({'message': f'Task created with id: {task_id}'}), 200
        except:
            return jsonify({'message': 'Invalid request'}), 400
    else:
        return jsonify({'message': 'Project not found'}), 404

# Save projects to pickle file
def save_data(data):
    with open('projects.pickle', 'wb') as file:
        pickle.dump(data, file)

# Filter the list of dictionaries based on specified fields
def filter_list_of_dicts(list_of_dicts, fields):
    filtered_dicts = []
    for item in list_of_dicts:
        filtered_item = item.copy()
        for key in item.keys():
            if key not in fields:
                del filtered_item[key]
        filtered_dicts.append(filtered_item)
    return filtered_dicts

# Get all projects
@app.route('/projects')
def get_projects():
    try:
        request_data = request.get_json()
        if 'fields' in request_data:
            fields = request_data['fields']
            filtered_projects = filter_list_of_dicts(projects, fields)
            return jsonify(filtered_projects)
    except:
        pass
    return jsonify(projects)

# Get all tasks in a project
@app.route('/project/<project_id>/tasks')
def get_all_tasks_in_project(project_id):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project:
        try:
            request_data = request.get_json()
            if 'fields' in request_data:
                fields = request_data['fields']
                filtered_tasks = filter_list_of_dicts(project['tasks'], fields)
                return jsonify(filtered_tasks)
        except:
            pass
        return jsonify(project['tasks'])
    else:
        return jsonify({'message': 'Project not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
