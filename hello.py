from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema



app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USER:PASSWORD@localhost/flasktask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Task(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(150))
    urgency_id = db.Column(db.Integer, db.ForeignKey('urgency.id'))
    date = db.Column(db.DateTime, nullable=True)


    def __init__(self, title, description, urgency_id, date):
        self.title = title
        self.description = description
        self.urgency_id = urgency_id
        self.date = date

class Urgency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    number = db.Column(db.Integer)
    tasks = db.relationship('Task', backref='urgency', lazy=True)

    def __init__(self, name):
        self.name = name
        self.number = 1

db.create_all()

class UrgencySchema(SQLAlchemyAutoSchema): 
    class Meta:
        model = Urgency

class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'date', 'urgency')

    urgency = ma.Nested(UrgencySchema)
    

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


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

    return task_schema.jsonify(new_task)


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

    return task_schema.jsonify(task_del)

if __name__ == "__main__":
    app.run(debug=True)