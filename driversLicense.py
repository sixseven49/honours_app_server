import pytesseract
import cv2
import os
import re
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascPath)

class Text_Extractor():
  def __init__(self, image_path): #Constructor
      self.image_path= image_path
      if self is None:
        return 0

  def extract_text(self): #Function to extract the text from image as string 
    try:
      image = cv2.imread(self.image_path) # read image
      image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # set image to colour
      text_res = pytesseract.image_to_string(image) # extract text with Tesseract
      return text_res
    except Exception as e:
      print(f'error: {str(e)}')

#class to validate if an image is a drivers licence 
class Drivers_Licence_Validator:
    #Constructor
    def __init__(self, text, image_path):
        self.text = text
        self.image_path = image_path
        self.dl_number = ''
#Function to validate  a driving licence
    def isThereAFace(self): # Detect faces in the image
        image=cv2.imread(self.image_path)

        faces = faceCascade.detectMultiScale(image,
                                             scaleFactor=1.1,
                                             minNeighbors=5,
                                             minSize=(30, 30))
        print("Found {0} faces!".format(len(faces)))
        return len(faces) > 0
    def license_number_valid(self):
        res = self.text.split()
        license_number_regex= "^^[A-Z9]{5}\d{6}[A-Z9]{2}\d[A-Z]{2}$$"
        dl_nums = []
        for element in res:
            if re.match(license_number_regex, element):
              dl_nums.append(element)
        if len(dl_nums) == 1: #should be one as there is only 1 dl number
          self.dl_number = dl_nums[0]
          return True
        else: 
          print("couldn't detect driver license number")
          return False
    def is_licence(self):
        res = self.text.split('/n')
        for word in res:
          if word.find("Driving") != -1 or word.find("DRIVING") != -1:
              print("Document is a Drivers licence")
              return True
          else:
              print("Document is not a Drivers licence")
              print("Can't find words DRIVERS LICENCE")
              return False
    #Function to find the age of the licence holder
    def age(self,y,m,d):
        dob = datetime.date(y,m,d)
        today = datetime.date.today()
        years = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            years -= 1
        return years

    #Function to validate if driving licence is expired or not
    def is_valid(self):
      if not self.text == None:
        if (self.is_licence() and self.isThereAFace()):
            if (self.license_number_valid()):
                res=self.text.split()   
                match=None
                day=None
                month=None
                year=None
                date_of_expiry=None
                dob=None
                issueDate=None
                count=0
                s=None
                strings_with_states=[]
         #get all the dates in a list
                regex = "[0-9][0-9][.][0-9][0-9][.][0-9][0-9][0-9][0-9]"
                p = re.compile(regex)
                dates = p.findall(self.text)
                if (len(dates) >= 1):
                  now = datetime.datetime.now()
                  for date in dates:
                    if '.' in date:
                        day,month,year=date.split(".")
                    else:
                        break
                    age=self.age(int(year),int(month),int(day)) # calcualtes the number of years from today
                    temp_date = datetime.datetime(int(year), int(month),int(day))

                    if temp_date>=now: #formatted date is greaster or equal to now... its the expiry date
                      date_of_expiry=temp_date
                    if age>=17: # checks if the 'age' calculated is greater than or equal to 17 making it the age
                      dob=temp_date
                    if age>=0:
                      issueDate = temp_date
                  if date_of_expiry :
                    print("Date of expiry :"+ str( date_of_expiry.strftime('%Y.%m.%d')))
                    print(f'expiration: {date_of_expiry}')
                    isItExpired = 'Valid' if date_of_expiry.date() > datetime.datetime.now().date() else 'Expired'
                    print(f'Is it still valid? {isItExpired}')
                  else:
                    print("Cannot determine the date of expiry or the licence has expired")
                  if dob:
                    print("Date of birth :"+ str(dob.strftime('%Y.%m.%d')))
                  elif 'DOB' in res:
                      index=res.index('DOB')
                      if ':' not in res[index+1]:
                        print( 'DOB is: '+ res[index+1])
                      else:
                        print( 'DOB is: '+ res[index+2])
                  else:
                    print("Cannot determine the date of birth or DOB is invlaid")
                    return False
                  if issueDate:
                    print(f'date of issue{issueDate}')
                  else :
                    print('could not determine issue date')
                  return True
                else:
                  print("Cannot find any dates with the format dd.mm.yyyy")
                  return False
            else:
              print("DL number not valid or couldn't detect; therefore can't verify to be drivers license")
              return False
        else:
            print("Is not drivers license")
      else:
        return False
    

  
