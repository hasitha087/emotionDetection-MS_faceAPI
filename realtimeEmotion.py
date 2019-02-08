import cv2
import pypyodbc
import params
import requests
import time
import datetime


server = "\"Server=" + params.SQLServer + ";\""
db = "\"Database=" + params.database + ";\""
userPW = "\"uid=" + params.uid + ";pwd=" + params.pwd + "\""


## SQL Server Connection
def dbConnection():
    cnxn = pypyodbc.connect("Driver={SQL Server Native Client 11.0};"
                            + server + db + userPW)
    return cnxn



faceCascade = cv2.CascadeClassifier('haarcascade_files/haarcascade_frontalface_default.xml')


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)  # set Width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  # set Height
frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))



feelings_faces = []
for index, emotion in enumerate(params.EMOTIONS):
    feelings_faces.append(cv2.imread('./emojis/' + emotion + '.png', -1))

count = 0
framesSkip = 10


while True:
    ret, img = cap.read()

    if (count % framesSkip == 0):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        ## Draw rectangle
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

        if len(faces) > 0:
            ## Save captured image
            img_str = cv2.imencode('.jpg', img)[1].tostring()

            ## API request
            response = requests.post(params.face_api_url, params=params.params, headers=params.headers, data=img_str)
            face = response.json()
            print(face)

            ## Put text on video
            emotionArray = {}

            try:
                for index, emotion in enumerate(params.EMOTIONS):
                    cv2.putText(img, emotion, (10, index * 20 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.rectangle(img, (130, index * 20 + 10), (130 + int(face[0]['faceAttributes']['emotion'][emotion] * 100), (index + 1) * 20 + 4),(255, 0, 0), -1)
                    emotionArray.update({emotion: face[0]['faceAttributes']['emotion'][emotion]})
                print(emotionArray)
                maximum = max(emotionArray, key=emotionArray.get)
                print(maximum, emotionArray[maximum])
                print(list(emotionArray.keys()).index(maximum))

                ## Display Emoji
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img, params.EMOTIONS[list(emotionArray.keys()).index(maximum)], (10, 360), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
                face_image = feelings_faces[list(emotionArray.keys()).index(maximum)]

                for c in range(0, 3):
                    img[200:320, 10:130, c] = face_image[:, :, c] * (face_image[:, :, 3] / 255.0) + img[200:320, 10:130, c] * (1.0 - face_image[:, :, 3] / 255.0)

                ## Display Age
                cv2.putText(img, 'Age:  ' + str(face[0]['faceAttributes']['age']), (10, 175 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                try:
                    cnxn = dbConnection()
                    cursor = cnxn.cursor()
                    ###Insert into SQL Server
                    ts = time.time()
                    time_key = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    probability = str(emotionArray[maximum])
                    query = "insert into dbo.emotions values(" + "'" + time_key + "'" + "," + "'" + maximum + "'" + "," + "'" + probability + "'" + ")"
                    cursor.execute(query)
                    cnxn.commit()
                except pypyodbc.Error:
                    print("Database insertion failed")

            except IndexError:
                print("No face detected")

        cv2.imshow('Video', cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
    count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()