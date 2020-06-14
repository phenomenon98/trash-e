from firebase import firebase
import base64
from datetime import datetime
from google.cloud import storage
import os

class Database:

	def __init__(self):
		self.firebase = firebase.FirebaseApplication("https://smartbin-47f77.firebaseio.com/", None)
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/mainproject/smartbin-47f77-48fbd74c644e.json"
		self.client = storage.Client()
		self.bucket = self.client.get_bucket('smartbin-47f77.appspot.com')
		self.imageBlob = self.bucket.blob("/")
		
	def write_result(self, imageFilePath, pickedRecyclingLabel):
		# imagePath = [os.path.join(self.path,f) for f in os.listdir(self.path)]
		now = datetime.now()
		dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
		imagePath = imageFilePath
		bucketpath = "classificationImage"+dt_string
		self.imageBlob = self.bucket.blob(bucketpath)
		self.imageBlob.upload_from_filename(imagePath)
		
		image = open(imageFilePath, "rb")
		imagebase64 = base64.b64encode(image.read())
		data = {'image':bucketpath, 'timestamp': dt_string, 'recyclingLabel': pickedRecyclingLabel}
		#self.firebase.child("smartbin").push(data)
		self.firebase.post("smartbin", data)

