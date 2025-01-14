import numpy as np
import cv2
import matplotlib
from matplotlib import pyplot as plt
image_path = 'test_images/sharapova1.jpg'
img = cv2.imread(image_path)
#print(img.shape)

plt.imshow(img)
#plt.show()


gray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
#print(gray.shape)
plt.imshow(gray, cmap='gray')
#plt.show()

face_cascade = cv2.CascadeClassifier('opencv/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('opencv/haarcascades/haarcascade_eye.xml')

faces = face_cascade.detectMultiScale(gray , 1.3 , 5)
#print(faces)

(x , y , w, h) = faces[0]

face_img = cv2.rectangle(img, (x,y), (x+w,y+h),(255,0,0),2)
#plt.imshow(face_img)
#plt.show()

cv2.destroyAllWindows()
for (x,y,w,h) in faces:
    face_img = cv2.rectangle(img, (x,y) , (x+w, y+h), (255,0,0),2)
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = face_img[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray)
    for (ex , ey , ew , eh) in eyes:
        cv2.rectangle(roi_color, (ex,ey), (ex+ew, ey+eh), (0,255,0),2)

#plt.figure()
#plt.imshow(face_img, cmap='gray')
#plt.show()

def get_cropped_image_if_2_eyes(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3 , 5)
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h , x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            return roi_color
        

cropped_image = get_cropped_image_if_2_eyes('test_images/sharapova1.jpg')
#plt.imshow(cropped_image) # type: ignore
#plt.show()

cropped_image_no_2_eyes = get_cropped_image_if_2_eyes('test_images/sharapova2.JPG')
#print(cropped_image_no_2_eyes)

org_image_obstructed = cv2.imread('./test_images/sharapova2.jpg')
#plt.imshow(org_image_obstructed)
#plt.show()


path_to_data = "./dataset/"
path_to_cr_data = "./dataset/cropped/"

import os
img_dirs = []
for entry in os.scandir(path_to_data):
    if entry.is_dir():
        img_dirs.append(entry.path)

#print(img_dirs)

import shutil
if os.path.exists(path_to_cr_data):
    shutil.rmtree(path_to_cr_data)
os.mkdir(path_to_cr_data)


cropped_image_dirs = []
celebrity_file_names_dict = {}
for img_dir in img_dirs:
    count = 1
    celebrity_name = img_dir.split('/')[-1]
    celebrity_file_names_dict[celebrity_name] = []
    for entry in os.scandir(img_dir):
        roi_color = get_cropped_image_if_2_eyes(entry.path)
        if roi_color is not None:
            cropped_folder = path_to_cr_data + celebrity_name
            if not os.path.exists(cropped_folder):
                os.makedirs(cropped_folder)
                cropped_image_dirs.append(cropped_folder)
                #print("Generating cropped images in folder: ",cropped_folder)
            cropped_file_name = celebrity_name + str(count) + ".png"
            cropped_file_path = cropped_folder + "/" + cropped_file_name
            cv2.imwrite(cropped_file_path, roi_color)
            celebrity_file_names_dict[celebrity_name].append(cropped_file_path)
            count += 1
#print(celebrity_file_names_dict)

import numpy as np
import pywt
import cv2

def w2d(img , mode='haar',level=1):
    imArray = img
    imArray = cv2.cvtColor(imArray, cv2.COLOR_RGB2GRAY)
    imArray = np.float32(imArray)
    imArray /= 255;
    coeffs = pywt.wavedec2(imArray, mode , level= level)

    coeffs_H = list(coeffs)

    coeffs_H[0]  *= 0;
    imArray_H = pywt.waverec2(coeffs_H, mode);
    imArray_H *= 255;
    imArray_H = np.uint8(imArray_H)

    return imArray_H

im_har = w2d(cropped_image , 'db1', 5)
plt.imshow(im_har, cmap= 'gray')
#plt.show()

celebrity_file_names_dict = {}
for img_dir in cropped_image_dirs:
    celebrity_name = img_dir.split('/')[-1]
    file_list = []
    for entry in os.scandir(img_dir):
        file_list.append(entry.path)
    celebrity_file_names_dict[celebrity_name] = file_list
class_dict = {}
count = 0
for celebrity_name in celebrity_file_names_dict.keys():
    class_dict[celebrity_name] = count
    count = count + 1

#print(class_dict)
X, y = [], []
for celebrity_name, training_files in celebrity_file_names_dict.items():
    for training_image in training_files:
        img = cv2.imread(training_image)
        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img,'db1',5)
        scalled_img_har = cv2.resize(img_har, (32, 32)) # type: ignore
        combined_img = np.vstack((scalled_raw_img.reshape(32*32*3,1),scalled_img_har.reshape(32*32,1)))
        X.append(combined_img)
        y.append(class_dict[celebrity_name]) 

#print(len(X))

X = np.array(X).reshape(len(X),4096).astype(float)


from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

pipe = Pipeline([('scalar', StandardScaler()), ('svc', SVC(kernel= 'rbf', C =10))])
pipe.fit(X_train,y_train)
#print(pipe.score(X_test, y_test))


from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV

model_params = {
    'svm' :{
        'model' : svm.SVC(gamma='auto',probability=True),
        'params' : {
            'svc__C' : [1,10, 100, 1000],
            'svc__kernel': ['rbf','linear']
        }
    },
    'random_forest' : {
        'model': RandomForestClassifier(),
        'params' : {
            'randomforestclassifier__n_estimators': [1,5,10]
        }
    },
    'logistic_regression' : {
        'model': LogisticRegression(solver='liblinear',multi_class='auto'),
        'params': {
            'logisticregression__C': [1,5,10]
        }
    }
 }

scores = []
best_estimators = {}
import pandas as pd
for algo, mp in model_params.items():
    pipe = make_pipeline(StandardScaler(), mp['model'])
    clf = GridSearchCV(pipe , mp['params'], cv = 5 , return_train_score= False)
    clf.fit(X_train, y_train)
    scores.append({
        'model' : algo,
        'best_score' : clf.best_score_,
        'best_params': clf.best_params_
    })
    best_estimators[algo] = clf.best_estimator_

df = pd.DataFrame(scores, columns= ['model', 'best_score', 'best_params'])
#print(df)

best_clf = best_estimators['svm']

import joblib 
# Save the model as a pickle in a file 
joblib.dump(best_clf, 'saved_model.pkl')


import json
with open("class_dictionary.json","w") as f:
    f.write(json.dumps(class_dict))
