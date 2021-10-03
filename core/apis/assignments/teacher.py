from flask import Blueprint
from flask.json import jsonify
from flask.wrappers import Request
from marshmallow.fields import Method
from sqlalchemy.orm import session
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from flask import request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified

from .schema import AssignmentSchema, AssignmentGradedSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)

@teacher_assignments_resources.route('/assignments', methods=['GET'])
@decorators.auth_principal
def list_assignments(p):
    '''returns a list of assignments'''
    teacher_assignment_recieved = Assignment.get_assignments_to_teacher(teacher_id=p.teacher_id)
    teacher_assignment_dump = AssignmentSchema().dump(teacher_assignment_recieved, many=True)
    return APIResponse.respond(data=teacher_assignment_dump)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.auth_principal
def grade_assignments(p, incoming_payload):
    '''returns graded assignments'''
    
    assignment_recieved = AssignmentGradedSchema().load(incoming_payload)

    graded_assignment = Assignment.grading(
        _id=assignment_recieved.id,
        grade = assignment_recieved.grade, 
        principal=p
    )

    db.session.add(graded_assignment)
    db.session.commit()
    student_assignment_graded = AssignmentSchema().dump(graded_assignment)
    

    return APIResponse.respond(data=student_assignment_graded)
