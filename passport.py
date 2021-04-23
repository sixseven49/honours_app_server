from passporteye import read_mrz
import datetime 
class Passport_Validator():
  def __init__(self, image_path):
    self.image_path = image_path
  def is_Passport(self): 
    mrz = read_mrz(self.image_path)
    if mrz == None or mrz.mrz_type != 'TD3':
      print("unable to do shit cause not a passport")
      return False
    else:
      return True