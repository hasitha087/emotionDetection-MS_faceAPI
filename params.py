SQLServer = "serverName"
database = "databaseName"
uid = "userID"
pwd = "password"

EMOTIONS = ['anger', 'contempt', 'disgust', 'fear', 'happiness', 'neutral', 'sadness', 'surprise']

##This can be changed according to the location you selected
face_api_url = 'https://southcentralus.api.cognitive.microsoft.com/face/v1.0/detect'

headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
         }

params = {
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,emotion'
    }