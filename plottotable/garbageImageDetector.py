from __future__ import division
from axisDetector import getPointsOnAxis
import cv2
import numpy as np

#Returns True if x and y axises are present 
def isAxisPresent(img):

	imgAxes=img.copy();

	shape=imgAxes.shape;

	detPoints=getPointsOnAxis(shape)

	gray = cv2.cvtColor(imgAxes,cv2.COLOR_BGR2GRAY)
	edges = cv2.Canny(gray,50,200,apertureSize = 3)

	lines = cv2.HoughLines(edges,1,np.pi/180,detPoints)

	vflag=hflag=0

	if lines is not None:

		for rho,theta in lines[0]:
			thetad= theta*(180/np.pi)

			if thetad <= 2 or (thetad >= 88 and thetad <=92):
				a = np.cos(theta)
		    	b = np.sin(theta)
		    	x0 = a*rho
		    	y0 = b*rho
		        if thetad<=2 and vflag==0:
		        	vflag=1
		        	xv1 = int(x0 + 1000*(-b))
		        	yv1 = int(y0 + 1000*(a))
		        	xv2 = int(x0 - 1000*(-b))
		        	yv2 = int(y0 - 1000*(a))
		        elif (thetad >= 88 and thetad <=92) and hflag==0:
		        	hflag=1
		        	xh1 = int(x0 + 1000*(-b))
		        	yh1 = int(y0 + 1000*(a))
		        	xh2 = int(x0 - 1000*(-b))
		        	yh2 = int(y0 - 1000*(a))
		        else:
		        	x1 = int(x0 + 1000*(-b))
		        	y1 = int(y0 + 1000*(a))
		        	x2 = int(x0 - 1000*(-b))
		        	y2 = int(y0 - 1000*(a))
		        	if thetad <= 2 and x1 < xv1:
		        		xv1=x1
		        		yv1=y1
		        		xv2=x2
		        		yv2=y2
		        	elif(thetad >= 88 and thetad <=92) and y1 > yh1:
		        		xh1=x1
		        		yh1=y1
		        		xh2=x2
		        		yh2=y2
		
		if vflag==1 and hflag==1:
			return True

		return False

	return False


#Returns true if image is a table
def isTable(img):
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	edges = cv2.Canny(gray,50,200,apertureSize = 3)
	height,width = img.shape[0:2]
	thresh = (height-300)*(3/5)	

	print "height ", height
	print thresh
	lines = cv2.HoughLines(edges,1,np.pi/180,int(thresh))

	ver_lines = 0
	if lines is not None:
		for rho,theta in lines[0]:
			thetad= theta*(180/np.pi)
			if (thetad <= 2):
				ver_lines = ver_lines + 1

	print "vl ", ver_lines
	if(int(ver_lines/2) > 2):
		return True
	return False

#Returns true if image is a garbage image
def isGarbageImage(img):
	
	if not isAxisPresent(img):
		return True

	return False

# img=cv2.imread("multicrop-ext-output/raw_mc_04-006.ppm")
# isAxisPresent(img)