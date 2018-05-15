source ~/python/google/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=speech-demo.json

ps -ef | grep python | grep mlapi | awk '{print "kill " $2}' | sh -x
nohup python mlapi-webhook.py 2>&1 > webhook.log &
sleep 1
tail -f webhook.log

