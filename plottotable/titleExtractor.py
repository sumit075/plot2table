from axisDetector import AxesDetection
import cv2
import subprocess
import os
from preprocessor import sharpenImage, cluster, resizeImage, otsusBinarization, enhance, histogram

def getTitle(inImg): #get title of image

	img= cv2.imread(inImg)

	imgAxes=AxesDetection(img)
	
	height, width = img.shape[:2]
	# print imgAxes

	if imgAxes == None:
		print "imgAxes is False"
		return None

	# padding for the title
	left = max(imgAxes['vaxisX']-50, 0)
	right = min(imgAxes['vaxisX2']+50, width)

	img = img[0:height, left:right]
	height, width = img.shape[:2]

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	rows, cols= gray.shape

	# varibales to mark gaps
	coord2=coord1=1
	flag=0

	# negate the image for countNonZero
	gray = 255-gray
	# print "nz --------- ",cv2.countNonZero(gray),cols*rows

	# percent of white pixels ie text
	globalPercent=100*float(cv2.countNonZero(gray))/(cols*rows)

	# check the top of plot for title
	print "Finding window on histogram - top ... ",
	for i in range(int(imgAxes['haxisY2']) - 50, 0, -1):
		sumr=0
		for j in range(0,cols):
			sumr+=gray[i][j]

		percent=(float(sumr)/(255*cols))*100

		if i and percent>=globalPercent and coord1==1:
			coord1=i
			# label white

		if percent<globalPercent and coord1 is not 1:
			flag=1
			# gap black

		if percent>=globalPercent and flag==1:
			coord2=i
			# stray text white

	split=int(float(coord1+coord2)/2)
	print "Done!"

	# print split
	# print int(imgAxes['haxisY2'])
	# print left
	# print right

	top_img = img[split:int(imgAxes['haxisY2']), 0:cols]
	img1 = sharpenImage(top_img)
	img2 = cluster(img1)[0]

	# cv2.imshow("fin1", img2)
	# cv2.waitKey(0)

	out = otsusBinarization(img2)
	out1 = enhance(out)
	cv2.imwrite("top.tiff", out1)

	print "Testing for text... ",
	subprocess.call("tesseract -psm 7 top.tiff out", shell=True)

	try:
		os.remove('top.tiff')
		with open('out.txt','r') as f:
			content = f.read()
			content = content.replace('\n','')
			content = content.strip()
			# print content
			if len(content) > 0:
				os.remove('out.txt')
				print "Found!"
				return content

	except Exception,e:
		print str(e)

	print "Not found at top"
	# flags 
	coord4=coord3=coord2=coord1=1
	flag=0

	# print "gp__________",globalPercent

	# check the bottom, beyond the xlabel
	
	print "Finding window on histogram - bottom ... ",
	for i in range(int(imgAxes['haxisY']) + 5, rows):
		sumr=0
		for j in range(0,cols):
			sumr+=gray[i][j]

		percent=(float(sumr)/(255*cols))*100
		# print "myp============ ", percent, i
		# black 1 gap
		# if percent<globalPercent and coord1==1:

		if percent>=globalPercent and coord1==1:
			coord1=i
			# white 2 numbers

		if percent<globalPercent and coord1!=1:
			flag=1
			# black 3 gap

		if percent>=globalPercent and flag==1:
			coord2=i
			# white 4 label

		if percent<globalPercent and coord2!=1:
			flag=2
			# black 5 gap

		if percent>=globalPercent and flag==2:
			# white 6 title possibly
			coord3=i

		if percent<globalPercent and coord3!=1:
			coord4=i
			# black 5 gap possibly

	print "Done!"
	# exit if no text is found
	if coord2 == 1 or coord3 == 1:
		return None

	split=int(float(coord2+coord3)/2)

	# print split
	# print coord1
	# print coord2
	# print coord3
	# print coord4

	# fix for end of image
	if coord4==1:
		coord4 = rows


	bot_img = img[split:coord4, 0:cols]
	
	# cv2.imshow("fin2", bot_img)
	# cv2.waitKey(0)

	img1 = sharpenImage(bot_img)
	img2 = cluster(img1)[0]
	out = otsusBinarization(img2)
	out1 = enhance(out)
	cv2.imwrite("bot.tiff", out1)
	print "Testing for OCR... ",
	subprocess.call("tesseract -psm 7 bot.tiff out", shell=True)
	try:
		os.remove('bot.tiff')
		with open('out.txt','r') as f:
			content = f.read()
			content = content.replace('\n','')
			content = content.strip()
			# print content
			if len(content) > 0:
				print "Found!"
				return content
	except Exception,e:
		print str(e)

	print "No text found!"
	return None

# print getHorizontalSplit('multicrop-ext-output/tmp_raw_mc_02-004.ppm')
