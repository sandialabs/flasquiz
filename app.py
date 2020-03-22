#!/usr/bin/python
'''
This is a small (but elegant) quiz application written for Flask.
See README.md for details.

Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC
(NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
Government retains certain rights in this software.

This file is part of Flasquiz.

Flasquiz is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Flasquiz is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import os
import sys
from copy import deepcopy
from glob import glob
from time import time
from random import shuffle, seed

import yaml
from flask import Flask, session, render_template, url_for, redirect, request, flash
from flask_mail import Mail, Message

import config

seed()
# Create a flask app and set its secret key
app = Flask(__name__)
app.config.from_object('config')
mail = Mail(app)


quizzes = dict()

def strip_response(resp):
    return resp.strip() if isinstance(resp, str) else resp

def submission_email(submission_id, sender):
    if config.MAIL_SERVER == 'mail.example.com' or \
            not config.DEVEL_EMAILS or \
            len(config.DEVEL_EMAILS) == 1 and config.DEVEL_EMAILS[0] == 'admin@example.com':
        return
    msg = Message(
        'SFU245 Quiz Submission %d' % submission_id,
        sender=sender,
        recipients=config.DEVEL_EMAILS)
    with open('submissions/%d.yaml'%submission_id, 'r') as yml_f:
        msg.body = yml_f.read()
    mail.send(msg)

def get_answer_entered():
    return request.form.get('answer_python', '')

def load_quizzes():
    global quizzes
    quizzes = dict()
    for yml_file in glob('quizzes/*.yml'):
        with open(yml_file, 'r') as stream:
            quiz_d = yaml.load(stream, yaml.FullLoader)
            quizzes[quiz_d['title']] = quiz_d

    # Process questions and detect errors
    for quiz_name, quiz in quizzes.items():
        for i, question in enumerate(quiz['questions']):
            if isinstance(question['correct'], str):
                quizzes[quiz_name]['questions'][i]['correct'] = \
                    strip_response(question['correct'])
            options = [question['correct']]

            if isinstance(question['correct'], bool):
                options.append(str(not question['correct']))
                if 'distractors' not in question:
                    question['distractors'] = str(not question['correct'])
                question['correct'] = str(question['correct'])
                continue # no need to check for distractors

            if isinstance(question['distractors'], list):
                quizzes[quiz_name]['questions'][i]['distractors'] = [
                    strip_response(distractor) \
                    for distractor in question['distractors']]
                options.extend(question['distractors'])
            else:
                quizzes[quiz_name]['questions'][i]['distractors'] = \
                    strip_response(question['distractors'])
                options.append(question['distractors'])

            if len(set(options)) < len(options):
                print('Duplicate options detected for question "%s"!' \
                      % question['prompt'], file=sys.stderr)

load_quizzes()


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        session['user_email'] = request.form['email']
        app.logger.info('user provided email: %s', session['user_email'])

# Check if the user is already working on a quiz
    if 'quiz_name' in session:
        return redirect(url_for('answer'))

    if 'user_email' in session and session['user_email']:
        return render_template(
            'select.html',
            title=config.TITLE,
            quiz_list=sorted(quizzes.keys()),
            nquiz=len(quizzes),
            email=session['user_email'])

    return render_template('login.html', title=config.TITLE)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()

    return redirect(url_for('index'))

# Route for the URL /python accepting GET and POST methods
@app.route('/python', methods=['GET', 'POST'])
def answer():
# This app uses flask session variables to keep track of the current question
# the user is on.
    if request.method == 'POST' and 'quiz_name' not in session:
        # The user just selected a quiz
        app.logger.debug('Select quiz %s', request.form.get('sel_quiz', ''))
        session['quiz_name'] = request.form.get('sel_quiz', '')
    if 'questions' not in session:
        app.logger.debug('Copy questions into session')
        session['questions'] = deepcopy(quizzes[session['quiz_name']]['questions'])
        session['complete'] = False

    if 'user_email' not in session or 'quiz_name' not in session or \
        not session['user_email'] or not session['quiz_name']:
        return redirect(url_for('index'))

    if request.method == "POST":
        entered_answer = get_answer_entered()
        if not entered_answer:
            # Show error if no answer entered
            if 'current_question' in session:
                flash("Please choose an answer to proceed", "error")

        else:
            # The user has just answered a question

            curr_answer = request.form['answer_python']

            qstn_i = int(session['current_question'])
            app.logger.info('question: "%s"', session['questions'][qstn_i]['prompt'])
            app.logger.info('entered_answer: "%s"', entered_answer)

            session['questions'][qstn_i]['answer'] = curr_answer

            # Set the current question to the next number when checked
            session['current_question'] = str(qstn_i+1)

            if int(session["current_question"]) < len(session['questions']):
                # If the question exists in the dictionary, redirect to the question
                redirect(url_for('answer'))

            else:
                # Else, redirect to the summary template as the quiz is complete
                return redirect(url_for('end_quiz'))

    if "current_question" not in session:
        # The first time the page is loaded, the current question is not set.
        # This means that the user has not answered a question yet. So, set the
        # current question to question in the session to the first one.
        session["current_question"] = "0"

    elif int(session['current_question']) >= len(session['questions']):
        # If the current question number is not available in the questions
        # dictionary, it means that the user has completed the quiz. So show
        # the summary page.
        return redirect(url_for('end_quiz'))

    # If the request is a GET request
    qstn_i = int(session['current_question'])
    qstn_dict = session['questions'][qstn_i]
    # If the distractors key is not a list, use the single item
    opt_list = list(qstn_dict['distractors'] \
        if isinstance(qstn_dict['distractors'], list) else \
        [qstn_dict['distractors']])
    opt_list.append(qstn_dict['correct'])
    shuffle(opt_list)
    opt_list = [str(opt) for opt in opt_list]

    old_answer = session['questions'][qstn_i]['answer'] \
        if 'answer' in session['questions'][qstn_i] \
        else None
    if 'answer' in session['questions'][qstn_i]:
        app.logger.info('old answer %s type %s',
                        old_answer, type(old_answer))
    app.logger.debug('opt list: %s', opt_list)


    return render_template(
        'quiz.html',
        title=config.TITLE,
        num=qstn_i+1,
        ntot=len(session['questions']),
        complete=session['complete'],
        question=qstn_dict['prompt'],
        old_answer=old_answer,
        opt_list=opt_list,
        email=session['user_email'],
        quiz_name=session['quiz_name'])


@app.route('/end', methods=['GET', 'POST'])
def end_quiz():
    if 'current_question' not in session or \
        'questions' not in session:
        return redirect(url_for('index'))

    submission_id = int(time())
    session['complete'] = True

    for question in session['questions']:
        question['answer_correct'] = question['answer'] == question['correct']
        app.logger.debug(
            'correctness decision: %s (type %s) == %s (type %s) : %s',
            question['answer'], type(question['answer']),
            question['correct'], type(question['correct']),
            question['answer_correct'])

    answer_correct_list = [q['answer_correct'] for q in session['questions']]
    n_total = len(session['questions'])
    n_correct = sum(answer_correct_list)
    n_wrong = n_total - n_correct

    wrong_i = [
        i+1 for i, q in enumerate(session['questions']) \
        if not q['answer_correct']]
    wrong_prompts = [
        q['prompt'] for q in session['questions'] \
        if not q['answer_correct']]
    wrong_answers = [
        q['answer'] for q in session['questions'] \
        if not q['answer_correct']]
    wrong_hints = [
        q['hint'] if 'hint' in q else '' \
        for q in session['questions'] \
        if not q['answer_correct']]
    score = int(100 * float(n_correct) / n_total)
    quiz_pass = score >= config.QUIZ_PASSING_SCORE

    data = {
        'user_email': session['user_email'],
        'quiz_name': session['quiz_name'],
        'n_wrong': n_wrong,
        'n_correct': n_correct,
        'n_total': n_total,
        'questions': [q for q in session['questions'] if not q['answer_correct']],
        'pass': quiz_pass,
        'passing_score': config.QUIZ_PASSING_SCORE,
        'score': score
        }
    if not os.path.isdir('submissions'):
        os.mkdir('submissions')
    with open('submissions/%d.yaml'%submission_id, 'w') as yamlout:
        yaml.dump(data, yamlout, default_flow_style=False)
    if quiz_pass:
        submission_email(submission_id, session['user_email'])

    return render_template(
        "end.html",
        title=config.TITLE,
        submission_id=submission_id,
        wrong_i=wrong_i,
        wrong_prompts=wrong_prompts,
        wrong_answers=wrong_answers,
        wrong_hints=wrong_hints,
        submit_emails=config.DEVEL_EMAILS,
        email=session['user_email'],
        quiz_name=session['quiz_name'],
        score=score,
        passing_score=config.QUIZ_PASSING_SCORE,
        quiz_pass=quiz_pass)


@app.route('/back', methods=['GET', 'POST'])
def back():
    if request.method == "POST":
        if get_answer_entered():
            curr_answer = request.form['answer_python']
            qstn_i = int(session['current_question'])
            session['questions'][qstn_i]['answer'] = curr_answer

    prev_q = max(int(session["current_question"])-1, 0)
    session["current_question"] = str(prev_q)

    return redirect(url_for('answer'))


@app.route('/reset', methods=['GET', 'POST'])
def reset_page():
    session.pop('quiz_name', None)
    session.pop('current_question', None)
    session.pop('questions', None)
    session.pop('complete', None)
    return redirect(url_for('index'))


@app.route('/jumpto', methods=['GET', 'POST'])
def jump_to():
    if request.method == "POST":
        if get_answer_entered():
            curr_answer = request.form['answer_python']
            qstn_i = int(session['current_question'])
            session['questions'][qstn_i]['answer'] = curr_answer

    target = request.args.get('target', '')
    if target:
        session['current_question'] = str(int(target)-1)

    return redirect(url_for('answer'))


@app.route('/reload_quizzes', methods=['GET'])
def reload_quizzes():
    load_quizzes()
    return redirect(url_for('index'))


# Creates a server for the app on the specified port
if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
