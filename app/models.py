from app import db
from app import ma
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

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
