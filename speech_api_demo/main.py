#
#   Test: gs://jerry-sample-data/speech/temp/_tmp_tmpie8R3Y
#

# [START app]
import os
import logging
import requests
from functools import wraps
import tempfile
from speech import transcribe_gcs, transcribe_gcs_async
from gcs import download_gcs, upload_gcs, delete_gcs

from flask import Flask
from flask import request, Response

from pydub import AudioSegment
from pydub.utils import mediainfo
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/opt/download/'

def requires_auth(f):
     @wraps(f)
     def decorated(*args, **kwargs):
          auth = request.authorization
          if not auth or not check_auth(auth.username, auth.password):
               return authenticate()
          return f(*args, **kwargs)
     return decorated

def check_auth(username, password):
    return username == 'google' and password == 'gcct-kr'

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials\n', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/')
def hello():
    msg = """
        <h1>Welcome to Jerry's Google Cloud Demo</h1>
    """
    return Response(
        msg, 200
    )

@app.route('/speech')
@requires_auth
def speech():
    file=open('speech_request.html')
    msg = file.read()
    msg = msg.replace('___RUN_SPEECH_API___', '/speech_api')
    return Response(
        msg, 200
    )

@app.route('/speech_api', methods=['POST'])
@requires_auth
def speech_api():
    recognize = request.form.get('recognize')
    audioInfo = request.form.get('audioInfo')
    url = request.form.get('url')
    file = None
    if 'file' in request.files:
        file = request.files['file']
    language = request.form.get('language')
    sync = request.form.get('sync')
    model = request.form.get('model')
    rate = int(request.form.get('rate'))
    start_time = int(request.form.get('start_time'))
    end_time = int(request.form.get('end_time'))
    # print file
    print recognize
    print audioInfo

    gcs_url = None
    if file != None:
        # print file.filename
        fileName = tempfile.mktemp(dir='/opt/download/')
        file.save(fileName)
        # print fileName
        info = mediainfo(fileName)
        # print info
        codec_name = info['codec_name']
        channel = info['channels']
        sample_rate = info['sample_rate']
        print "Codec: " + codec_name
        print "Sample Rate: " + sample_rate
        print "Channels: " + channel

        if codec_name not in ('flac'):
            fileName_flac = tempfile.mktemp(dir='/opt/download/', suffix='.flac')
            audio = AudioSegment.from_file(fileName)
            # audio = audio - 5
            one_min = 60 * 1000
            if end_time == -1:
                audio_export = audio[one_min * start_time:]
            else:
                audio_export = audio[one_min * start_time:one_min * end_time]
            # -q:a 0 the best quality
            audio_export.export(fileName_flac, format='flac', parameters=["-q:a", "0", "-ac", "1"])
            os.remove(fileName)
            fileName = fileName_flac

        gcs_temp_name = tempfile.mktemp().replace('/', '_').replace('\\', '_')
        url = 'gs://jerry-sample-data/speech/temp/' + gcs_temp_name
        gcs_url = url
        upload_gcs(url, fileName)

        rate = int(sample_rate)

        os.remove(fileName)

    if recognize != None and len(recognize) > 0:
        if sync == 'Yes':
            msg = transcribe_gcs(url, language, rate, model)
        else:
            transcribe_gcs_async(url, language, rate, model)
            msg = "OK"

        if gcs_url != None:
            delete_gcs(gcs_url)

        return Response(
            msg, 200
        )
    elif audioInfo != None:
        f = tempfile.NamedTemporaryFile()
        if url.startswith('gs://'):
            download_gcs(url, f)
        else:
            r = requests.get(url)
            f.write(r.content)

        f.flush()
        info = mediainfo(f.name)
        msg = "<p>URL: " + url + "</p>"
        msg = msg + "<p>Sample Rate: " + info['sample_rate'] + "</p>" + "<p>Channels: " + info['channels'] + "</p>"
        msg = msg + "<input type='button' value='  Back  ' onClick='history.go(-1)'>"
        f.close()
        return Response(
            msg, 200
        )

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=False)
# [END app]
