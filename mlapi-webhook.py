# -*- coding:utf8 -*-

import json
import csv
import random

from flask import Flask, request, make_response, jsonify

from apiclient import discovery
from oauth2client import client
from google.cloud import translate


APP = Flask(__name__)
LOG = APP.logger

quiz = []
currentQuestion = []

@APP.route('/health')
def health():
    msg = {'msg': 'OK'}
    return make_response(jsonify(msg))

@APP.route('/', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print 'Dialogflow Request:'
    print json.dumps(req, indent=4)
    try:
        action = req.get('queryResult').get('action')
        print "Aciont: " + action
    except AttributeError:
        return 'json error'

    parameters = req['queryResult']['parameters']
    contexts = {}
    if 'outputContexts' in req['queryResult']:
        contexts = req['queryResult']['outputContexts']

    if action == 'start-english':
        res = startEnglish(parameters, contexts)
    elif action == 'question':
        res = question(parameters, contexts)
    elif action == 'question-again':
        res = question(parameters, contexts)
    elif action == 'answer':
        res = answer(parameters, contexts)
    elif action == 'answer.answer-next':
        res = nextQuestion(parameters, contexts)
    elif action == 'translation.translation-custom':
        res = translatePhrase(parameters, contexts)
    elif action == 'google-photo':
        res = googlePhoto(parameters, contexts)
    else:
        LOG.error('Unexpected action.')

    print 'Response: ' + json.dumps(res)

    # return make_response(jsonify(res))
    return json.dumps(res)

def startEnglish(parameters, contexts):
    # question Intent로 이동
    res = {
		'followupEventInput': {
            'name': 'QUESTION'
        }
	}
    return res

def nextQuestion(parameters, contexts):
    # english-test 컨텍스트 제거 후
    # question Intent로 이동
    res = {
		'followupEventInput': {
            'name': 'QUESTION'
        },
        'outputContexts': [
            {
                'name': "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/english-test",
                'lifespanCount': 0
            }
        ]
	}
    return res

def translatePhrase(parameters, contexts):
    phrase = parameters['phrase']
    contextParams = None
    for context in contexts:
        if context['name'].endswith('/translation-followup'):
            if 'parameters' in context:
                contextParams = context['parameters']
    if contextParams['language'] == u'영어':
        target = 'en'
    elif contextParams['language'] == u'일본어':
        target = 'ja'
    elif contextParams['language'] == u'중국어':
        target = 'zh-CN'
    else:
        res = {
            'fulfillmentText': u'지원하지 않는 언어: ' + contextParams['language']
        }
        return res

    translate_client = translate.Client()
    translation = translate_client.translate(
        phrase,
        source_language='ko',
        target_language=target)

    print(u'Translation: {}'.format(translation['translatedText']))

    res = {
		'fulfillmentText': translation['translatedText']
    }

    return res

def googlePhoto(parameters, contexts):
    # question Intent로 이동
    res = {
        "fulfillmentMessages": [
            {
                "platform": "TELEGRAM",
                "image": {
                    "imageUri": "https://lh4.googleusercontent.com/proxy/HnNSQi9CR-N2ezU28NX38XylJYK0sFywUnU3RZtorXIpMwIJQAIBN4A7XmpE63DZN0dOTF1MJF7wcA304yRVp66M5hSvdAx_ypBgXZK94avk8YmsL2RWFnbK3tzzBEeofXatSrfqbK6PtVnpP8fGTq6VyoN-25OEHLuk335boNLhIF1dqHA9weCXsilA6HrYDDzNTc47Qii2XfCWAafMe1yoqoeS_Gw3ymMPWZ1N06lTdVfW5n-s4VxmK5dspShYBfM=w5000-h5000"
                }
            }
        ]
    }
    return res


def question(parameters, contexts):
    global currentQuestion
    global quiz

    contextParams = None
    for context in contexts:
        if context['name'].endswith('/english-test'):
            if 'parameters' in context:
                contextParams = context['parameters']

    if contextParams == None or 'question' not in contextParams:
        size = len(quiz)
        num = random.randint(0, size - 1)
        print 'Question No: ' + str(num)
        currentQuestion = quiz[num]
        question = currentQuestion[0]
        answers = currentQuestion[1]
    else:
        question = contextParams['question']
        answers = contextParams['answers']

    res = {
		'fulfillmentText': u'문제: ' + question,
        'outputContexts': [
            {
                'name': "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/english-test",
                'lifespanCount': 10,
                'parameters': {
                    'question': question,
                    'answers': answers
                }
            }
        ]
	}

    return res

def answer(parameters, contexts):
    global currentQuestion
    global quiz

    answer = parameters['answer']
    answers = []
    contextAnswers = None
    for context in contexts:
        if context['name'].endswith('/english-test'):
            contextAnswers = context['parameters']['answers']
    if contextAnswers == None:
        res = {
            'fulfillmentText': '문제가 주어지지 않았습니다'
        }
    else:
        # print "dlkfadsjlkfdsj"
        # print contextAnswers
        for a in contextAnswers.split(','):
            answers.append(a.strip())
        print answers
        if answer in answers:
            res = {
                'fulfillmentText': '맞았습니다'
            }
        else:
            res = {
                'fulfillmentText': '틀렸습니다'
            }

    return res

def loadSheet():
    global quiz
    credentials = client.GoogleCredentials.get_application_default()
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', credentials=credentials,
                            discoveryServiceUrl=discoveryUrl)

    # Change id to your Google Sheets
    spreadsheetId = '1gg8KK6nJewBV46u1EZ5rIabs8SVJqW4cRJuIFsgmjIE'
    rangeName = 'Sheet1!A:C'
    majorDimension = 'ROWS'

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName, majorDimension=majorDimension).execute()
    quiz = result.get('values', [])[1:]
    print quiz

if __name__ == '__main__':
    random.seed()
    loadSheet()
    APP.run(debug=True, host='0.0.0.0', port=6000)
