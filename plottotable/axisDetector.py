import cv2
import numpy as np
import Image
import subprocess
import lxml.html as lh

def getPointsOnAxis(shape, size_flag=True):  #Function to decide the minimum length of axis line, depending on the size of the image
	rows=shape[0];
	cols=shape[1];


	if rows<cols:
		if size_flag:
			detPoints=int((rows-300)*(400.0/500))
		else:
			detPoints=int(rows*(400.0/500))
		# detPoints=int(rows*(330.0/500))
	else:
		if size_flag:
			detPoints=int((cols-300)*(400.0/500))
		else:
			detPoints=int(cols*(400.0/500))
		# detPoints=int(cols*(330.0/500))

	if detPoints>350:
		detPoints=350

	if detPoints<230 and detPoints>200:
		detPoints=200
	
	if detPoints<200:
		detPoints=150

	return detPoints

def getPlotLines(imgAxes, size_flag=True): #Function to implement Hough Line Transform and get the lines on the image
	shape=imgAxes.shape;

	detPoints=getPointsOnAxis(shape, size_flag)

	gray = cv2.cvtColor(imgAxes,cv2.COLOR_BGR2GRAY)
	kernel = np.ones((5,5),np.uint8)
	gray = cv2.erode(gray,kernel,iterations = 2)
	gray = cv2.dilate(gray,kernel,iterations = 2)
	edges = cv2.Canny(gray,50,200,apertureSize = 3)  #Functions to grayscale, binarize and canny edge detect image before applying Hough Line Transform

	lines = cv2.HoughLines(edges,1,np.pi/180,detPoints) #Hough line transform

	return lines

def AxesDetection(img, size_flag=True): #Fucntion to detect whether the image contains axis lines and return the axis equations
	# print "Detecting axes... ",
	imgAxes=img.copy()
	height = imgAxes.shape[0]
	width = imgAxes.shape[1]
	lines=getPlotLines(imgAxes, size_flag)
	yh=[]
	xv=[]
	for rho,theta in lines[0]:
		a = np.cos(theta)
		b = np.sin(theta)
		x0 = a*rho
		y0 = b*rho
		x1 = int(x0 + 1000*(-b))
		y1 = int(y0 + 1000*(a))
		x2 = int(x0 - 1000*(-b))
		y2 = int(y0 - 1000*(a))
		thetad= theta*(180/np.pi)
		if (x1 >= 15 and x1 <= width - 15) or (y1<=height-15 and y1>=15):
			# cv2.line(imgAxes,(x1,y1),(x2,y2),(0,0,255),2)
			thetad= theta*(180/np.pi)
			if thetad <=2 or thetad >=358 or (thetad>=178 and thetad<=182):
				xv.append(int(x0 + 1000*(-b)))
			if (thetad <=92 and thetad >=88) or (thetad>=178 and thetad<=182):
				yh.append((y0 - 1000*(a)))
	# cv2.namedWindow("ifashf", cv2.WINDOW_NORMAL)
	# cv2.imshow("ifashf",imgAxes)
	# cv2.waitKey(0)
	if len(xv) >= 2 and len(yh) >= 1:
		y=max(yh) # y coordinate of x axis
		x1=min(xv) # x coordinate of y axis
		x2=max(xv) # other end of the x axis
		y2=min(yh) # y coordinate of top boundary

		image= {
			"vaxisX":x1,
			"vaxisX2":x2,
			"haxisY":y,
			"haxisY2":y2
		}
		# print "Done!"
		return image

	# print "Not Found!"
	return None