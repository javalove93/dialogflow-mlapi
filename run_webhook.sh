source ~/python/google/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=jerryjg-kr-ce-api-89f4c052ec8e.json

ps -ef | grep python | grep mlapi | awk '{print "kill " $2}' | sh -x
nohup python mlapi-webhook.py 2>&1 > webhook.log &
sleep 1
tail -f webhook.log

