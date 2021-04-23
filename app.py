# import Flask class from the flask module
from flask import Flask, request, Response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from sklearn import svm
from sklearn.cluster import KMeans
import face_recognition
import numpy as np
import pickle
import cv2
import os
import driversLicense
import passport
# Create Flask object to run
app = Flask(__name__)
UPLOAD_FOLDER = './public/user/uploads'
MODELS_FOLDER = './public/models'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
  return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def blurry(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #CONVERTING IN TO LAPLACIAN IMAGE FOR EDGE DETECTION
    lap = cv2.Laplacian(gray.copy(), cv2.CV_64F)
    #CONDITION : VARIANCE OF LAPLACIAN MATRIX
    if lap.var() < 200.0 :
        return True
    else:
        return False

def classify(path):
  image= cv2.imread(path, cv2.COLOR_BGR2RGB)
  IMG_WIDTH=340
  IMG_HEIGHT=500
  image=cv2.resize(image, (IMG_HEIGHT, IMG_WIDTH),interpolation = cv2.INTER_AREA).flatten()
  image=np.array(image)
  image = image.astype('float32')
  image /= 255

  class_prediced = SVCModel.predict([image])[0]
  output = str(class_prediced) 
  return output
def validation(paths):
  selfie = face_recognition.load_image_file(paths[0])
  selfie_encoding = face_recognition.face_encodings(selfie)[0]

  document = face_recognition.load_image_file(paths[1])
  document_encoding = face_recognition.face_encodings(document)[0]
  results = face_recognition.compare_faces([selfie_encoding], document_encoding)

  if results[0] == True:
    return 'Selfie matches document image'
  else:
    return 'Not validated, selfie image does not match document profile'
def clear():
  folder = app.config['UPLOAD_FOLDER']
  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

@app.route('/docify/vv', methods = ['POST'])
def verifyValidate():
  # check if the post request has the file part
    if 'document' not in request.files and 'me' not in request.files:
      return Response("Missing required files", status=401, mimetype='application/json')
    else:
      # Get images from request
      document_file = request.files['document']
      selfie_file = request.files['me'] 

      files = [document_file, selfie_file]
      paths = []
      for file in files: #for each files
        if file.filename == '': #does the file name exist
          files= [] #reset array
          return Response("File Missing Name", status=401, mimetype='application/json')
        if file and allowed_file(file.filename): # is the file in the right file format
            filename = secure_filename(file.filename) 
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            paths.append(image_path) #add to paths array
            file.save(image_path)

            # check if the image is blurry
            isItBlurry = blurry(image_path)
            if (isItBlurry):
              return Response("Image is blurry", status=401, mimetype='application/json')
        else:
          return Response("uploaded files are not in correct format", status=401, mimetype='application/json')
      
      classification = classify(paths[0])
      print(classification)
      if classification == 'dl':
        # go to driver's licence route
        extractor = driversLicense.Text_Extractor(paths[0])
        image_text = extractor.extract_text()		#call the text extractor function 
        dlv = driversLicense.Drivers_Licence_Validator(image_text, paths[0])
        verdict = 'DL' if dlv.is_valid() else 'unknown'
        message = 'is it valid: ' + str(verdict)
      elif classification == 'passport':
        # go to passport route
        pport = passport.Passport_Validator(paths[0])
        verdict = 'Passport' if pport.is_Passport() else 'unknown'
        message = 'is it valid: ' + verdict
      else:
        clear()
        return Response(classification, status=201, mimetype='application/json')

      validate = validation(paths)
      message = message + ' '+str(validate)
      clear()
      return Response(message, status=200, mimetype='application/json')


	
	
# Load the pre-trained and persisted SVM model
# Note: The model will be loaded only once at the start of the server
def load_model():
	# global kMeansModel
	
	# kMeansFile = open('./models/kmeansCluster.pckl', 'rb')
	# kMeansModel = pickle.load(kMeansFile)
	# kMeansFile.close()
	global SVCModel
	
	SVCFile = open('./models/SVMModel.pckl', 'rb')
	SVCModel = pickle.load(SVCFile)
	SVCFile.close()
# --------------------------------------
if __name__ == "__main__":
    
	print("**Starting Server...")
	
	# Call function that loads Model
	load_model()
	
	# Run Server
	app.run(debug=True)