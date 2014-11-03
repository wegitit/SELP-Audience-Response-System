from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from main.models import Session, Current_question, Question_option, Student_response, Enrollment, Student
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

import json
import datetime
import random

def respond(request, session_code):
    # If a session exists, go to the response page, otherwise throw a 404
    try:
        s = Session.objects.get(url_code=session_code, course__enrollment__student__user=request.user, running=True)
    except ObjectDoesNotExist:
        raise Http404

    data = {}

    data['session'] = s

    return render_to_response('response.html', data, context_instance=RequestContext(request))

def check_question_availability(request):
    session_code = request.GET.get('session_code')

    # Check if the session exists and that the student is allowed to access it
    try:
        s = Session.objects.get(url_code=session_code, course__enrollment__student__user=request.user, running=True)
    except ObjectDoesNotExist:
        raise Http404

    data = {'question_available': False}
    # Now check if there is an assigned question for this session
    session_questions = Current_question.objects.filter(session=s).order_by('-start_time');
    if session_questions:
        newest_assignment = session_questions[0]
        # Check if this assignment is still valid
        if timezone.now() < newest_assignment.start_time:
            # Get a shuffled list of all question options
            question_options = []
            for option in Question_option.objects.filter(question=newest_assignment.question):
                question_options.append({'body': option.body, 'id': option.id})
            random.shuffle(question_options)

            # Calculate the number of miliseconds until the question is due to start
            time_to_start = (int) ((newest_assignment.start_time - timezone.now()).total_seconds() * 1000)
            data['question_available'] = True
            data['time_to_start'] = time_to_start
            data['question_body'] = newest_assignment.question.question_body
            data['question_options'] = question_options
            data['run_time'] = newest_assignment.run_time

    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def log_response(request):
    if request.method != 'POST':
        raise Http404

    session_code = request.POST.get('sessionCode')
    option_id = request.POST.get('optionId')

    data = {'success': True, 'message': 'Response has been collected successfully'}

    # We must now do some strict checking to ensure that the user is allowed to
    # answer this question and if all that passes, we insert the response
    try:
        pass
        # User must be allowed to access this session and session must be active
        session = Session.objects.get(url_code=session_code, running=True)
        enrollment = Enrollment.objects.get(course=session.course, student__user=request.user)
        # This option must be part of the current and the question must be active
        option = Question_option.objects.get(pk=option_id)
        current_question = Current_question.objects.filter(session=session, question=option.question).order_by('-start_time')
        if not current_question:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        data['success'] = False
        data['message'] = 'You do not have permission to respond to this session with that option'

    
    if data['success']:
        # Now check that the current question is still running
        newest_assignment = current_question[0]
        end_time = newest_assignment.start_time+datetime.timedelta(0, newest_assignment.run_time)
        if timezone.now() > end_time:
            data['success'] = False
            data['message'] = 'This question has expired'
        else:
            # Only insert an answer if this student hasn't already responded
            # This should never happen during normal operation however it will
            # protect against users deliberately trying to break the system
            option = Question_option.objects.get(pk=option_id)
            already_responded = bool(Student_response.objects.filter(student__user=request.user, option=option))
            if not already_responded:
                student = Student.objects.get(user=request.user)
                sr = Student_response()
                sr.student = student
                sr.option_id = option_id
                sr.save()

    return HttpResponse(json.dumps(data), content_type='application/json')