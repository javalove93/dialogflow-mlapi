
def transcribe_gcs(gcs_uri, lang, rate, model):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    # from google.cloud import speech as speech
    from google.cloud import speech_v1p1beta1 as speech

    client = speech.SpeechClient()

    print "model: %s" % (model)
    print "language: %s" % (lang)

    audio = speech.types.RecognitionAudio(uri=gcs_uri)
    # metadata = speech.types.RecognitionMetadata()
    # metadata.interactionType = (speech.enums.RecognitionMetadata.InteractionType.DISCUSSION)
    # metadata.industryNaicsCodeOfAudio = '541411'
    # metadata.recordingDeviceType = (speech.enums.RecognitionMetadata.RecordingDeviceType.OTHER_INDOOR_DEVICE)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=rate,
        use_enhanced=True,
        # metadata=metadata,
        model=model,
        enable_word_time_offsets=True,
        language_code=lang)

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = operation.result(timeout=1800)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    msg = "<p>Sample Rate: " + str(rate) + "</p>"
    for result in response.results:
        msg = msg + u'Transcript: {}'.format(result.alternatives[0].transcript) + u'<br>'
        msg = msg + u'Confidence: {}'.format(result.alternatives[0].confidence) + u'<br>'

    return msg

# Should process asynchronous request
def transcribe_gcs_async(gcs_uri, lang, rate, model):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    # from google.cloud import speech as speech
    from google.cloud import speech_v1p1beta1 as speech

    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=gcs_uri)
    # metadata = speech.types.RecognitionMetadata()
    # metadata.interactionType = (speech.enums.RecognitionMetadata.InteractionType.DISCUSSION)
    # metadata.industryNaicsCodeOfAudio = '541411'
    # metadata.recordingDeviceType = (speech.enums.RecognitionMetadata.RecordingDeviceType.OTHER_INDOOR_DEVICE)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=rate,
        use_enhanced=True,
        # metadata=metadata,
        model=model,
        enable_word_time_offsets=True,
        language_code=lang)

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = operation.result(timeout=600)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))
        print('Confidence: {}'.format(result.alternatives[0].confidence))
