from flask import jsonify, request
from flask_cors import cross_origin
from app import app, db
from app.models import Task, Urgency, task_schema, tasks_schema


@app.route('/', methods=['GET'])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result) 
    

    
@app.route('/newtask', methods=['POST'])
@cross_origin()
def create_task():
    
    title = request.json['title']
    description = request.json['description']
    urgency = request.json['urgency']
    date = request.json['date']

    if date == 'Not set':
        date = None

    ur_query = Urgency.query.filter_by(name=urgency).first()
    if ur_query is None:
        ur_query = Urgency(urgency)
        db.session.add(ur_query)
        db.session.commit()
    else:
        ur_query.number += 1
        db.session.commit()

    new_task = Task(title, description, ur_query.id, date)
    db.session.add(new_task)
    db.session.commit()
    
    print(task_schema.jsonify(new_task))

    return task_schema.jsonify(new_task), 201


@app.route('/edit/<id>', methods=['PUT'])
def update_task(id):
    task_for = Task.query.get(id)
    title = request.json['title']
    description = request.json['description']
    urgency = request.json['urgency']
    date = request.json['date']

    ur_query  = Urgency.query.filter_by(name= urgency).first()
    task_ur_query = Urgency.query.filter_by(id= task_for.urgency_id).first()
    if ur_query is None:
        ur_query = Urgency(urgency)
        db.session.add(ur_query)
        db.session.commit()
    elif task_for.urgency_id is not ur_query.id:
        ur_query.number += 1
        task_ur_query.number -= 1
    elif task_for.urgency_id == ur_query.id:
        ur_query.number += 1

    task_for.title = title 
    task_for.description = description
    task_for.date = date
    task_for.urgency_id = ur_query.id

    db.session.commit()
    return task_schema.jsonify(task_for)


@app.route('/delete/<id>', methods=['DELETE'])
def delete_task(id):
    task_del = Task.query.get(id)
    ur_query = Urgency.query.filter_by(id=task_del.urgency_id).first()
    ur_query.number -= 1
    db.session.delete(task_del)
    db.session.commit()

    return task_schema.jsonify(task_del), 202

if __name__ == "__main__":
    app.run(debug=True)