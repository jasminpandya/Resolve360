cd ./agent

sh deploy_prereqs.sh

# start the backend background and copy the logs to a file and also redirect them to console and log the process id in a file
echo "Starting backend..."
nohup python end_user_api_flask.py > end_user_api_flask.log 2>&1 &
echo $! > end_user_api_flask.pid

# start the application in background and copy the logs to a file and also redirect them to console and log the process id in a file
echo "Starting application..."
nohup python app.py > app.log 2>&1 &
echo $! > app.pid

# sleep for 30 seconds and check if processes are running
sleep 30
if ps -p $(cat end_user_api_flask.pid) > /dev/null && ps -p $(cat app.pid) > /dev/null; then
    echo "Backend and application started successfully."
else
    echo "Failed to start backend or application. Check logs for details."
    #print the logs
    echo "Backend logs:"
    cat end_user_api_flask.log
    echo "Application logs:"
    cat app.log
    # clean up the processes
    rm end_user_api_flask.pid app.pid
    rm end_user_api_flask.log app.log
    exit 1
fi