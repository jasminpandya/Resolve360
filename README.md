# Resolve360
Resolve360 - Hackathon repository

## Run below commands in git bash for one time set up
```
cd ./agent
pip install --upgrade --force-reinstall -r requirements.txt
aws config
export AWS_ACCESS_KEY_ID="<AWS_ACCESS_KEY_ID>"
export AWS_SECRET_ACCESS_KEY="<AWS_SECRET_ACCESS_KEY>"
export AWS_SESSION_TOKEN="<AWS_SESSION_TOKEN>"
sh deploy_prereqs.sh
```

## Run to start the backend in separate git bash
```
cd ./agent
python end_user_api_flask.py
```

## Run to start the UI in separate git bash
```
cd ./agent
python app.py
```

## Do clean up once program is executed
```
cd ./agent
sh cleanup.sh
```
