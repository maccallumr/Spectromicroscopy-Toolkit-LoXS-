##Authors: MacCallum Robertson, Christopher Agostino##
##Contact information: maccallumr@berkeley.edu, mjrobertson@lbl.gov

#This code is used for X-ray spectro-microscopy. You will need two image sets of 
#opposite polarization with the same number of images in folders labeled "left" and "right". 
#These images should all be labeled with their respective energy values, using underscores instead of periods. 
#Note that it is set up for energies of the form XXX_XX, any alterations may need revisions. May update in later versions.


import sys
import numpy as np
import os
import scipy
import gdal
import matplotlib.pyplot as plt

from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import QTimer, SIGNAL, SLOT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mpl_toolkits.mplot3d.axes3d as p3
from mpl_toolkits.mplot3d import Axes3D
from lmfit.models import LorentzianModel
from lmfit.models import GaussianModel
from lmfit.models import VoigtModel

import gc
from numpy import trapz
from scipy.integrate import simps
plt.rc('text',usetex=True)


plt.rc('font',family='serif')
l=[]
r=[]
s=[]
l = os.listdir("left/")
r =os.listdir("right/")

l.sort()
r.sort()

#############################
####Systematic Subtraction###
#############################  
      
f=open("systematic.txt",'r')
data=f.readlines()[0:]
sy=[]
col=[]
for line in data:
    line=line.strip()
    columns=line.split()
    col.append(columns)
for i in range (0,len(col)):
    sy.append(float(col[i][0]))
    
#############################    
#############################
#############################

image_array_r =[]
image_file_r =[]
image_array_l =[]
image_file_l =[]

if 'left_png_im' not in os.listdir("."):
    os.mkdir('left_png_im')
if 'right_png_im' not in os.listdir("."):
    os.mkdir('right_png_im')

app =QApplication.instance()

if not app:
    app = QApplication(sys.argv)

   
#################################################      
#################First Window####################
#################################################
   
w = QWidget()

#Window#
w.resize(650,625)
w.setWindowTitle('XMCDpy')

def show1(w,energy):
    
    #Image#
    imagelabel=QLabel(w)
    image=QImage(energy)
    pixmap=QPixmap.fromImage(image)
    pixmap=pixmap.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel.setPixmap(pixmap)
    imagelabel.resize(10,10)
    imagelabel.setAlignment(QtCore.Qt.AlignHCenter)
    imagelabel.setScaledContents(True)
    scrollArea=QScrollArea(w)
    scrollArea.setBackgroundRole(QPalette.Dark)
    scrollArea.setWidget(imagelabel)
    scrollArea.setAlignment(QtCore.Qt.AlignHCenter)
    scrollArea.setWidgetResizable(True)
    scrollArea.move(350,10)
    scrollArea.resize(280,230)
    scrollArea.setVisible(False)
    scrollArea.setVisible(True)
    print imagelabel.alignment()
    
def show2(w,energy):    
    #Image#
    imagelabel2=QLabel(w)
    image2=QImage(energy)
    pixmap2=QPixmap.fromImage(image2)
    pixmap2=pixmap2.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel2.setPixmap(pixmap2)
    imagelabel2.setScaledContents(True)
    scrollArea2=QScrollArea(w)
    scrollArea2.setBackgroundRole(QPalette.Dark)
    scrollArea2.setWidget(imagelabel2)
    scrollArea2.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea2.setWidgetResizable(True)
    scrollArea2.move(350,270)
    scrollArea2.resize(280,230)
    scrollArea2.setVisible(False)
    scrollArea2.setVisible(True)
    


def show3(w,energy):
    
    #Image#
    imagelabel3=QLabel(w)
    image3=QImage(energy)
    pixmap3=QPixmap.fromImage(image3)
    pixmap3=pixmap3.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel3.setPixmap(pixmap3)
    imagelabel3.setScaledContents(True)
 

    scrollArea3=QScrollArea(w)
    scrollArea3.setBackgroundRole(QPalette.Dark)
    scrollArea3.setWidget(imagelabel3)
    scrollArea3.move(350,10)
    scrollArea3.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea3.setWidgetResizable(True)
    scrollArea3.resize(280,230)
    scrollArea3.setVisible(False)
    scrollArea3.setVisible(True)
 
def show4(w,energy):       
    #Image#
    imagelabel4=QLabel(w)
    image4=QImage(energy)
    pixmap4=QPixmap.fromImage(image4)
    pixmap4=pixmap4.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel4.setPixmap(pixmap4)
    imagelabel4.setScaledContents(True)
    
    scrollArea4=QScrollArea(w)
    scrollArea4.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea4.setWidgetResizable(True)
    scrollArea4.setBackgroundRole(QPalette.Dark)
    scrollArea4.setWidget(imagelabel4)
    scrollArea4.move(350,270)
    
    scrollArea4.resize(280,230)
    scrollArea4.setVisible(False)

    
    scrollArea4.setVisible(True)

#########################    
#Drop Down Material Menu#
#########################

material=QComboBox(w)
material.resize(150,20)

material.addItem('Metal')
material.addItem('Cobalt')
material.addItem('Nickel')
material.addItem('Iron')
material.move(30,30)


##########
#Buttons#
#########

button2= QPushButton('Display Images',w)
button2.setToolTip('Show Images')
button2.resize(220,30)
button2.move(375,530)
 
button4= QPushButton('Run',w)
button4.setToolTip('Run the data collection script')
button4.resize(button4.sizeHint())
button4.move(500,575)

button5= QPushButton('Skip',w)
button5.setToolTip('Skip to data analysis section ')
button5.resize(button5.sizeHint())
button5.move(375,575)

button6= QPushButton('Load Polarization 1',w)
button6.setToolTip('Loads first polarization .tiff files as .png files')
button6.resize(button6.sizeHint())
button6.move(30,55)

button7= QPushButton('Load Polarization 2',w)
button7.setToolTip('Loads second polarization .tiff files as .png files')
button7.resize(button7.sizeHint())
button7.move(30,85)

button8= QPushButton('Next',w)
button8.resize(button8.sizeHint())
button8.move(645,10)
button8.hide()

button9= QPushButton('Prev',w)
button9.resize(button9.sizeHint())
button9.move(645,60)
button9.hide()

button10= QPushButton('Next',w)
button10.resize(button10.sizeHint())
button10.move(645,270)
button10.hide()

button11= QPushButton('Prev',w)
button11.resize(button11.sizeHint())
button11.move(645,320)
button11.hide()

button12= QPushButton('Go to L3',w)
button12.resize(button11.sizeHint())
button12.move(645,110)
button12.hide()

button13= QPushButton('Go to L2',w)
button13.resize(button11.sizeHint())
button13.move(645,160)
button13.hide()

button14= QPushButton('Go to L3',w)
button14.resize(button11.sizeHint())
button14.move(645,370)
button14.hide()

button15= QPushButton('Go to L2',w)
button15.resize(button11.sizeHint())
button15.move(645,420)
button15.hide()

########
#Labels#
########

label1 = QLabel(w)
label1.setText('XMCDpy ')
label1.move(30, 10)


label2 = QLabel(w)
label2.setText('Select Coordinates (Center of DW)')
label2.move(30, 115)

label3 = QLabel(w)
label3.setText('Select Area Size (Pixels)')
label3.move(30, 185)

label4 = QLabel(w)
label4.setText('                                                                                                        ')
label4.move(350, 245)

label5 = QLabel(w)
label5.setText('                                                                                                      ')
label5.move(350,505)

label3 = QLabel(w)
label3.setText('Select Number of Areas')
label3.move(30, 245)

###########
#Textboxes#
###########

textbox1 = QLineEdit(w)
textbox1.move(30, 135)
textbox1.resize(200, 20)
textbox1.setText('Enter X')

textbox2 = QLineEdit(w)
textbox2.move(30, 160)
textbox2.resize(200, 20)
textbox2.setText('Enter Y')

textbox3 = QLineEdit(w)
textbox3.move(185, 30)
textbox3.resize(50, 20)
textbox3.setText('L3 (eV)')

textbox4 = QLineEdit(w)
textbox4.move(240, 30)
textbox4.resize(50, 20)
textbox4.setText('L2 (eV)')

textbox7= QLineEdit(w)
textbox7.setText('')
textbox7.resize(30,20)
textbox7.move(30,265)

pol1_index= QLineEdit(w)
pol1_index.setText('                                 ')
pol1_index.resize(30,20)
pol1_index.move(30,265)
pol1_index.hide()


pol2_index= QLineEdit(w)
pol2_index.setText('                               ')
pol2_index.resize(30,20)
pol2_index.move(30,265)
pol2_index.hide()

pol= QLineEdit(w)
pol.setText('                               ')
pol.resize(30,20)
pol.move(30,265)
pol.hide()

store_count= QLineEdit(w)
store_count.setText('')
store_count.resize(30,20)
store_count.move(30,265)
store_count.hide()

#############
#Check Boxes#
#############

Check1=QCheckBox("Transmission intensity",w)
Check1.move(30,290)
Check1.setChecked(False)

Check2=QCheckBox("Absorption intensity",w)
Check2.move(30,320)
Check2.setChecked(False)

Check3=QCheckBox("Local Background",w)
Check3.move(30,350)
Check3.setChecked(False)

Check4=QCheckBox("Background Subtracted",w)
Check4.move(30,380)
Check4.setChecked(False)

Check5=QCheckBox("XMCD",w)
Check5.move(30,410)
Check5.setChecked(False)

Check6=QCheckBox("XMCD2",w)
Check6.move(30,440)
Check6.setChecked(False)

Check7=QCheckBox("Lorentzian Fit",w)
Check7.move(30,470)
Check7.setChecked(False)

Check8=QCheckBox("Gaussian Fit",w)
Check8.move(30,500)
Check8.setChecked(False)

Check9=QCheckBox("Voigt Fit",w)
Check9.move(30,530)
Check9.setChecked(False)


Check11=QCheckBox("5 x 5 ",w)
Check11.move(30,200)
Check11.setChecked(False)

Check12=QCheckBox("8 x 8",w)
Check12.move(100,200)
Check12.setChecked(False)

Check13=QCheckBox("10 x 10",w)
Check13.move(30,220)
Check13.setChecked(False)

Check14=QCheckBox("15 x 15",w)
Check14.move(100,220)
Check14.setChecked(False)

image=QImage()
image.isNull()

#########
#Actions#
#########

def on_click_button2():
    c1=closest(float(textbox3.text()),photon_energies)
    c2=closest2(float(textbox3.text()),photon_energies2)
    l3_in=float(c1)
    l3_in2=float(c2)
    
    c1_name=str(c1)
    c2_name=str(c2)
    if '.' in c1_name:
        c1_name = c1_name.replace(".","_")
    if '.' in c2_name:
        c2_name = c2_name.replace(".","_")
    pol1="left_png_im"+"/"+c1_name+'.PNG' 
    pol2="right_png_im"+"/"+c2_name+'.PNG'   

    pol1_index.setText(str(photon_energies.index(l3_in)))
    pol2_index.setText(str(photon_energies2.index(l3_in2)))
    print pol1,pol2
    label4.setText('Energy Level(eV):'+ str(l3_in)+ "@ Polarization 1")
    label5.setText('Energy Level(eV):'+ str(l3_in2)+"@ Poalrization 2")
    w.resize(750,625)
    button8.show()
    button9.show()
    button10.show()
    button11.show()
    button12.show()
    button13.show()
    button14.show()
    button15.show()
    print pol1,pol2
    
    imagelabel_new=QLabel(w)
    image_new=QImage(pol1)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,10)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
    
    imagelabel_new2=QLabel(w)
    image_new2=QImage(pol2)
    pixmap_new2=QPixmap.fromImage(image_new2)
    pixmap_new2=pixmap_new2.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new2.setPixmap(pixmap_new2)
    imagelabel_new2.setScaledContents(True)
 

    scrollArea_new2=QScrollArea(w)
    scrollArea_new2.setBackgroundRole(QPalette.Dark)
    scrollArea_new2.setWidget(imagelabel_new2)
    scrollArea_new2.move(350,270)
    scrollArea_new2.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new2.resize(280,230)
    scrollArea_new2.setVisible(False)
    scrollArea_new2.setVisible(True)
        
def on_click_button4():
    xcoord=float(textbox1.text())
    ycoord=float(textbox2.text())
    area_num=int(textbox7.text())
  
    
    producedata(list_images_l,list_images_r,area_num,[xcoord,ycoord],direct=1,det=0)
    
 
    w.hide()
    w2.show()
    
def on_click_button5():
    w.hide()
    w2.show()

def on_click_button6():
    l_count=0
    for fil in l:
	if fil.endswith(".tif"):
		image =gdal.Open('left/'+fil)
		image_array_l.append(scipy.array(image.GetRasterBand(1).ReadAsArray()))
		image_file_l.append(fil)
		filename="left_png_im"+"/"+fil[:-3]+"PNG"
		implot=plt.imshow(image_array_l[l_count],cmap='gray')
		plt.savefig(filename)
		l_count+=1
		
def on_click_button7():
    r_count=0
    for fil in r:
	if fil.endswith(".tif"):
		image =gdal.Open('right/'+fil)
		image_array_r.append(scipy.array(image.GetRasterBand(1).ReadAsArray()))
		image_file_r.append(fil)
		filename="right_png_im"+"/"+fil[:-3]+"PNG"
		implot=plt.imshow(image_array_r[r_count],cmap='gray')
		plt.savefig(filename)
		r_count+=1
 
def on_click_button8():
    
    count=int(pol1_index.text())
    new_index=count+1
    val=str(photon_energies[new_index])
    if "." in val:
        val=val.replace(".",'_')
    if len(val)==5:
        val=val+"0"
    filename="left_png_im"+"/"+val+".PNG"
    pol1_index.setText(str(new_index))
    label4.setText('Energy (eV):'+ val + "@ Polarization 1")
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,10)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
    
   
def on_click_button9(): 
    
    count=int(pol1_index.text())
    new_index=count-1
    val=str(photon_energies[new_index])
    if "." in val:
        val=val.replace(".",'_')
    if len(val)==5:
        val=val+"0"
    filename="left_png_im"+"/"+val+".PNG"
    pol1_index.setText(str(new_index))
    label4.setText('Energy (eV):'+ val+ "@ Polarization 1")
    
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
  

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,10)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
  
def on_click_button10():
    count=int(pol2_index.text())
    new_index=count+1
    val=str(photon_energies2[new_index])
    if "." in val:
        val=val.replace(".",'_')
    if len(val)==5:
        val=val+"0"
    filename="right_png_im"+"/"+val+".PNG"
    pol2_index.setText(str(new_index))
    label5.setText('Energy (eV):'+ val+ "@ Polarization 2")
    
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,270)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
   
def on_click_button11():
  
    count=int(pol2_index.text())
    new_index=count-1
    val=str(photon_energies2[new_index])
    if "." in val:
        val=val.replace(".",'_')
    if len(val)==5:
        val=val+"0"
    filename="right_png_im"+"/"+val+".PNG"
    pol2_index.setText(str(new_index))
    label5.setText('Energy (eV):'+ val+ "@ Polarization 2")
    
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,270)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
    
    
def on_click_button12():

    l3=closest(float(textbox3.text()),photon_energies)
    l3_in=float(l3)
    l3_name=str(l3)
    if '.' in l3_name:
        l3_name = l3_name.replace(".","_")
    pol1_index.setText(str(photon_energies.index(l3_in)))
    filename="left_png_im"+"/"+l3_name+'.PNG' 
    label4.setText('Energy Level(eV):'+ str(l3_in)+ "@ Polarization 1")
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,10)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)

def on_click_button13():
    
    l2=closest(float(textbox4.text()),photon_energies)
    l2_name=str(l2)
    l2_in=float(l2)
    if '.' in l2_name:
        l2_name = l2_name.replace(".","_")
    pol1_index.setText(str(photon_energies.index(l2_in)))
    filename="left_png_im"+"/"+l2_name+'.PNG'  
    label4.setText('Energy Level(eV):'+ str(l2_in)+ "@ Polarization 1")
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,10)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
    
def on_click_button14():
    
    l3=closest2(float(textbox3.text()),photon_energies2)
    l3_in=float(l3)
    l3_name=str(l3)  
    if '.' in l3_name:
        l3_name = l3_name.replace(".","_")
    pol2_index.setText(str(photon_energies2.index(l3_in)))
    filename="right_png_im"+"/"+l3_name+'.PNG' 
    label5.setText('Energy Level(eV):'+ str(l3_in)+"@ Poalrization 2")
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,270)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
    
def on_click_button15():
    
    l2=closest2(float(textbox4.text()),photon_energies2)
    l2_name=str(l2)
    l2_in=float(l2)
    if '.' in l2_name:
        l2_name = l2_name.replace(".","_")
    pol2_index.setText(str(photon_energies2.index(l2_in)))
    filename="right_png_im"+"/"+l2_name+'.PNG' 
    label5.setText('Energy Level(eV):'+ str(l2_in)+"@ Poalrization 2")
    
    imagelabel_new=QLabel(w)
    image_new=QImage(filename)
    pixmap_new=QPixmap.fromImage(image_new)
    pixmap_new=pixmap_new.scaled(900,900,QtCore.Qt.KeepAspectRatio)
    imagelabel_new.setPixmap(pixmap_new)
    imagelabel_new.setScaledContents(True)
 

    scrollArea_new=QScrollArea(w)
    scrollArea_new.setBackgroundRole(QPalette.Dark)
    scrollArea_new.setWidget(imagelabel_new)
    scrollArea_new.move(350,270)
    scrollArea_new.setAlignment(QtCore.Qt.AlignCenter)
    scrollArea_new.resize(280,230)
    scrollArea_new.setVisible(False)
    scrollArea_new.setVisible(True)
   
#####################   
#ComboBox activation#
#####################

def on_activated2(text):
    
	text_str = str(text)
	textbox3.setText(str(Metals[text_str][0]))
	textbox4.setText(str(Metals[text_str][1]))
	

###############
#Metal L edges#
###############

Metals = {
                  'Cobalt':[778, 792],	
                  'Iron':[708, 720],
                  'Nickel':[820, 853]	
                 
}

material.activated[str].connect(on_activated2)

button2.clicked.connect(on_click_button2)

button4.clicked.connect(on_click_button4)
button5.clicked.connect(on_click_button5)
button6.clicked.connect(on_click_button6)
button7.clicked.connect(on_click_button7)
button8.clicked.connect(on_click_button8)
button9.clicked.connect(on_click_button9)
button10.clicked.connect(on_click_button10)
button11.clicked.connect(on_click_button11)
button12.clicked.connect(on_click_button12)
button13.clicked.connect(on_click_button13)
button14.clicked.connect(on_click_button14)
button15.clicked.connect(on_click_button15)

##############################################################
##########################Second Window#######################
##############################################################

w2 = QWidget()

w2.resize(300,500)
w2.setWindowTitle('XMCDpy')

new='on'


textboxS = QLineEdit(w2)
textboxS.move(30, 185)
textboxS.resize(100, 20)
textboxS.setText(new)
textboxS.hide()

def showB():
    labelB.show()
    labelB1.show()
    labelB2.show()
    labelB3.show()
    textboxB1.show()
    textboxB2.show()
    
def hideB():
    labelB.hide()
    labelB1.hide()
    labelB2.hide()
    labelB3.hide()
    textboxB1.hide()
    textboxB2.hide()

labelB = QLabel(w2)
labelB.setText('Recent File Parameters')
labelB.move(30, 135)
labelB.show() 
       
labelB1 = QLabel(w2)
labelB1.setText('Input Area Number')
labelB1.move(30, 160)
labelB1.show()
    
labelB2 = QLabel(w2)
labelB2.setText('Input Pixel Value')
labelB2.move(30, 220)
labelB2.show()

labelB3 = QLabel(w2)
labelB3.setText('Selected File:')
labelB3.move(30, 385)
labelB3.show()

    
textboxB1= QLineEdit(w2)
textboxB1.setText('')
textboxB1.resize(80,20)
textboxB1.move(30,190)
textboxB1.show()
    
textboxB2= QLineEdit(w2)
textboxB2.setText('')
textboxB2.resize(80,20)
textboxB2.move(30,250)
textboxB2.show()
           
def showC():
    labelC.show()
    labelC1.show()
    labelC2.show()
    labelC3.show()
    labelC4.show()
    textboxC1.show()
    textboxC2.show()
    textboxC3.show()
    textboxC4.show()
    
def hideC():
    labelC.hide()
    labelC1.hide()
    labelC2.hide()
    labelC3.hide()
    labelC4.hide()
    textboxC1.hide()
    textboxC2.hide()
    textboxC3.hide()
    textboxC4.hide()
    
labelC = QLabel(w2)
labelC.setText('New File Parameters')
labelC.move(30, 135)
labelC.hide()

labelC1 = QLabel(w2)
labelC1.setText('Input Area Number')
labelC1.move(30, 240)
labelC1.hide()
    
labelC2 = QLabel(w2)
labelC2.setText('Input Pixel Value')
labelC2.move(30, 290)
labelC2.hide()
    
labelC3 = QLabel(w2)
labelC3.setText('Input (X,Y) Coordinates')
labelC3.move(30, 165)
labelC3.hide()
    
labelC4 = QLabel(w2)
labelC4.setText('Selected File:')
labelC4.move(30, 385)
labelC4.hide()
    
    
textboxC1= QLineEdit(w2)
textboxC1.setText('')
textboxC1.resize(80,20)
textboxC1.move(30,260)
textboxC1.hide()
    
textboxC2= QLineEdit(w2)
textboxC2.setText('')
textboxC2.resize(80,20)
textboxC2.move(30,310)
textboxC2.hide()

textboxC3 = QLineEdit(w2)
textboxC3.move(30, 185)
textboxC3.resize(100, 20)
textboxC3.setText('Enter X')
textboxC3.hide()   
    
textboxC4 = QLineEdit(w2)
textboxC4.move(30, 215)
textboxC4.resize(100, 20)
textboxC4.setText('Enter Y')
textboxC4.hide()
  
labelD = QLabel(w2)
labelD.setText('                                                                                            ')
labelD.move(30, 400)  

#######
#Plots#
#######

def plots(x,y,x_axis,y_axis,title,name):
    plt.plot(x, y)
    plt.xlabel(x_axis,fontsize=20)
    plt.ylabel(y_axis,fontsize=20)
    plt.title(title,fontsize=22)
    plt.grid(True)
    plt.savefig(name+".png")
    plt.close()
    
def plots2(x,y,y2,x_axis,y_axis,info1,info2,title,name):
    left=plt.plot(x, y)
    right=plt.plot(x,y2)
    plt.xlabel(x_axis,fontsize=20)
    plt.ylabel(y_axis,fontsize=20)
    plt.title(title,fontsize=22)
    plt.grid(True)
    plt.savefig(name+".png")
    plt.close()

store_value=QLineEdit(w2)
store_value.setText('')
store_value.hide()

store_value2=QLineEdit(w2)
store_value2.setText('')
store_value2.hide()

#################
#Make Data Files#
#################

def makefile():
    
    if textboxS.text()=='on':
        xcoord=textbox1.text()
        ycoord=textbox2.text()
        xcoord=float(xcoord)
        ycoord=float(ycoord)
        fold=str(xcoord)+"_"+str(ycoord)
        filename=2
        dirstr=1
        pixel=textboxB2.text()
        num=textboxB1.text()
        print num,pixel
        filename=fold+"/"+str(xcoord)+"_"+str(ycoord)+"_" + str(num) +"_area_"+str(pixel) +'dir_'+"r"+".csv"
        
    else:
        xcoord=textboxC3.text()
        ycoord=textboxC4.text()
        xcoord=float(xcoord)
        ycoord=float(ycoord)
        fold=str(xcoord)+"_"+str(ycoord)
        dirstr='r'
        pixel=textboxC2.text()
        num=textboxC1.text()
        filename=fold+"/"+str(xcoord)+"_"+str(ycoord)+"_" + str(num) +"_area_"+str(pixel) +'dir_'+dirstr+".csv"    
    
    
    labelD.setText(filename)
    labelD.show()
    
    store_value.setText(filename)

def show_im_A():
    w2.resize(1100,600)
    imageA=QImage('transmission.PNG')
    pixmapA=QPixmap.fromImage(imageA)
    pixmapA=pixmapA.scaled(700,700,QtCore.Qt.KeepAspectRatio)
    imagelabelA=QLabel(w2)
    imagelabelA.setPixmap(pixmapA)
    imagelabelA.move(300,30)
    imagelabelA.setScaledContents(True)
    imagelabelA.show()
def show_im_B():
    w2.resize(1100,600)
    imageB=QImage('abs.PNG')
    pixmapB=QPixmap.fromImage(imageB)
    pixmapB=pixmapB.scaled(700,700,QtCore.Qt.KeepAspectRatio)
    imagelabelB=QLabel(w2)
    imagelabelB.setPixmap(pixmapB)
    imagelabelB.move(300,30)
    imagelabelB.setScaledContents(True)
    imagelabelB.show()
def show_im_C():
    w2.resize(1100,600)
    imageC=QImage('background.PNG')
    pixmapC=QPixmap.fromImage(imageC)
    pixmapC=pixmapC.scaled(700,700,QtCore.Qt.KeepAspectRatio)
    imagelabelC=QLabel(w2)
    imagelabelC.setPixmap(pixmapC)
    imagelabelC.move(300,30)
    imagelabelC.setScaledContents(True)
    imagelabelC.show()
def show_im_D():
    w2.resize(1100,600)
    imageD=QImage('bs.PNG')
    pixmapD=QPixmap.fromImage(imageD)
    pixmapD=pixmapD.scaled(700,700,QtCore.Qt.KeepAspectRatio)
    imagelabelD=QLabel(w2)
    imagelabelD.setPixmap(pixmapD)
    imagelabelD.move(300,30)
    imagelabelD.setScaledContents(True)
    imagelabelD.show()
def show_im_E():
    w2.resize(1100,600)
    imageE=QImage('xmcd.PNG')
    pixmapE=QPixmap.fromImage(imageE)
    pixmapE=pixmapE.scaled(700,700, QtCore.Qt.KeepAspectRatio)
    imagelabelE=QLabel(w2)
    imagelabelE.setPixmap(pixmapE)
    imagelabelE.move(300,30)
    imagelabelE.setScaledContents(True)
    imagelabelE.show()
def show_im_F():
    w2.resize(1100,600)
    imageF=QImage('xmcd2.PNG')
    pixmapF=QPixmap.fromImage(imageF)
    pixmapF=pixmapF.scaled(700,700,QtCore.Qt.KeepAspectRatio)
    imagelabelF=QLabel(w2)
    imagelabelF.setPixmap(pixmapF)
    imagelabelF.move(300,30)
    imagelabelF.setScaledContents(True)
    imagelabelF.show()
def show_im_G():
    w2.resize(1100,600)
    imageG=QImage('lorentzian.PNG')
    pixmapG=QPixmap.fromImage(imageG)
    pixmapG=pixmapG.scaled(700,700,QtCore.Qt.KeepAspectRatio)
    imagelabelG=QLabel(w2)
    imagelabelG.setPixmap(pixmapG)
    imagelabelG.move(300,30)
    imagelabelG.setScaledContents(True)
    imagelabelG.show()
def show_im_H():
    w2.resize(1100,600)
    imageH=QImage('gaussian.PNG')
    pixmapH=QPixmap.fromImage(imageH)
    pixmapH=pixmapH.scaled(700,700,QtCore.Qt.KeepAspectRatio)
    imagelabelH=QLabel(w2)
    imagelabelH.setPixmap(pixmapH)
    imagelabelH.move(300,30)
    imagelabelH.setScaledContents(True)
    imagelabelH.show()

def on_click_buttonB():
    
    hideC()
    showB()
    textboxS.setText('on')
    
def on_click_buttonC():
    hideB()
    showC()
    textboxS.setText('off')
 
def on_click_buttonD():
    makefile()
    filename=store_value.text()
    read_dat(filename)
    
buttonB= QPushButton('Use Recent Files',w2)
buttonB.setToolTip('Select files just generated by XMCDpy')
buttonB.resize(buttonB.sizeHint())
buttonB.move(30,50)

buttonC= QPushButton('Use New Files',w2)
buttonC.setToolTip('Select already existing files ')
buttonC.resize(buttonC.sizeHint())
buttonC.move(30,90)

buttonD= QPushButton('Retrieve File',w2)
buttonD.setToolTip('Retrieve file corresponding to the parameters above')
buttonD.resize(buttonD.sizeHint())
buttonD.move(30,340)

options=QComboBox(w2)
options.resize(150,20)
options.move(30,430)
options.hide()

def on_activated3(text):
	text_str = str(text)
	if text_str=='Transmission':
	    show_im_A()
	if text_str=='Absorption':
	    show_im_B()
	if text_str=='Background':
	    show_im_C() 
	if text_str=='Background Subtraction':
	    show_im_D()
	if text_str=='XMCD':
	    show_im_E()   
	if text_str=='XMCD2':
	    show_im_F()    
	if text_str=='Lorentzian':
	    show_im_G()    
	if text_str=='Gaussian':
	    show_im_H()   
	     


options.activated[str].connect(on_activated3)
buttonB.clicked.connect(on_click_buttonB)
buttonC.clicked.connect(on_click_buttonC)
buttonD.clicked.connect(on_click_buttonD)

############
#Functions#
###########

def closest(num,lst):
    closest_num=min(photon_energies, key=lambda x:abs(x-num))
    return closest_num
def closest2(num,lst):
    closest_num=min(photon_energies2, key=lambda x:abs(x-num))
    return closest_num
    
def read_dat(filename):
    fil = np.loadtxt(filename, skiprows=1)
    fil_t=fil.transpose()
    
    ###############
    #Transmission#
    ##############
    
    if Check1.isChecked() == True:
        plots2(fil_t[0],fil_t[2],fil_t[3],"Photon Energy", "Intensity","Polarization 1","Polarization 2", "Transmitted Intensity", "transmission")
        options.removeItem(0)
        options.addItem('Transmission')
        
    ############   
    #Absorption#
    ############
    
    if Check2.isChecked() == True:
        plots2(fil_t[0],fil_t[7],fil_t[8],"Photon Energy", "Intensity","Polarization 1","Polarization 2", "Absorption Intensity", "abs")
        options.removeItem(1)
        options.addItem('Absorption')
        
    ############    
    #background#
    ############
    
    if Check3.isChecked() == True:
        plots2(fil_t[0],fil_t[9],fil_t[10],"Photon Energy", "Intensity","Polarization 1","Polarization 2", "Background Intensity", "background")
        options.removeItem(2)
        options.addItem('Background')
        
    ########    
    #combo#
    #######
    
    if Check4.isChecked() == True:
        plots2(fil_t[0],fil_t[5],fil_t[6],"Photon Energy", "Intensity","Polarization 1","Polarization 2","Background Subtracted", "bs")
        options.removeItem(3)
        options.addItem('Background Subtraction')
        
    #######    
    #XMCD#
    ######
    
    if Check5.isChecked() == True:
        plots(fil_t[0],fil_t[4],"Photon Energy", "Intensity", "XMCD", "xmcd")
        options.removeItem(4)
        options.addItem('XMCD')
        
    ########    
    #XMCD2#
    #######
    
    if Check6.isChecked() == True:
        plots(fil_t[0],fil_t[1],"Photon Energy", "Intensity", "XMCD2", "xmcd2")
        options.removeItem(5)
        options.addItem('XMCD2')
        
    ############
    #Lorenztian#
    ############
    
    if Check7.isChecked()==True:
        plots2(fil_t[0],fil_t[1],fil_t[11],"Photon Energy", "Intensity","XMCD","Lorentzian", "Lorentzian Fit", "lorentzian")
        options.addItem('Lorentzian')   
        
    ###########    
    #Gaussian#
    ##########
    
    if Check8.isChecked()==True:
        plots2(fil_t[0],fil_t[1],fil_t[12],"Photon Energy", "Intensity", "XMCD","Gaussian","Gaussian Fit", "gaussian")
        options.removeItem(6)
        options.addItem('Gaussian')
    options.show()
    
   ####### 
   #Voigt#
   #######
   
    if Check9.isChecked()==True:
        plots2(fil_t[0],fil_t[1],fil_t[13],"Photon Energy", "Intensity","XMCD","Voigt", "Voigt Fit", "voigt")
        options.removeItem(0)
        options.addItem('Voigt')

def assign_images(lst = None):
	new_array_r =[]
	file_list_r =[]
	new_array_l =[]
	file_list_l =[]
	for fil in l:
		if fil.endswith(".tif"):
			new =gdal.Open('left/'+fil)
			new_array_l.append(scipy.array(new.GetRasterBand(1).ReadAsArray()))
			file_list_l.append(fil)
	for fil in r:
		if fil.endswith(".tif"):
			new =gdal.Open('right/'+fil)
			new_array_r.append(scipy.array(new.GetRasterBand(1).ReadAsArray()))
			file_list_r.append(fil)	
	return [file_list_l,file_list_r, new_array_l,new_array_r]
list_files_l,list_files_r , list_images_l, list_images_r = assign_images()
photon_energies = []
for i in list_files_l:
	if 'tif' in i:
		if '_R' in i:
			i = i.replace("_R.tif","")
		if "_L" in i:
			i=i.replace("_L.tif",'')
                if "_" in i:
			i=i.replace("_",'.')
			i=i.replace(".tif",'')
			
		else:
			i=i.replace(".tif",'')
		
	photon_energies.append(float(i))
	
photon_energies2 = []
for i in list_files_r:
	if 'tif' in i:
		if '_R' in i:
			i = i.replace("_R.tif","")
		if "_L" in i:
			i=i.replace("_L.tif",'')
                if "_" in i:
			i=i.replace("_",'.')
			i=i.replace(".tif",'')
			
		else:
			i=i.replace(".tif",'')
		

	photon_energies2.append(float(i))
gc.collect()

def pick_domain_wall_point(image):
	plt.imshow(image,cmap='Greys_r')
	coords = plt.ginput(1)
	coords = coords[0]
	return np.array(coords) 
	
def calculate_nth_average_intensity(image_left,image_right,coordinate, size,size2, number,direct=1,det=0,phot_e=0):
	intensities_right = []
	intensities_left = []
	output_array = []
	count_x = 0
	norm_l =[]
	x, y = coordinate
	norm_r =[]
	diff_1 = np.array([])
	diff_2 = np.array([])
	if det:	
		for a in range(coordinate[0]-5,coordinate[0]+5):
			left_1 =[]
			right_1 =[]
			left_2 =[]
			right_2 =[]
			for j in range(size+1):
				for i in range(size):
					left_1.append(image_left[y+i][a-j])
					right_1.append(image_left[y+i][a+j])
					
					left_2.append(image_right[y+i][a-j])
					right_2.append(image_right[y+i][a+j])

			left_1, right_1 = np.array(left_1), np.array(right_1)
			left_1, right_1 = np.mean(left_1), np.mean(right_1)
			m0_1 = (left_1+right_1)/2
			left_2, right_2 = np.array(left_2), np.array(right_2)
			left_2, right_2 = np.mean(left_2), np.mean(right_2)
			m0_2 = (left_2+right_2)/2
			diff1 = m0_1-image_left[y][a]
			diff_1 = np.append(diff_1,diff1)
			diff2 = m0_2-image_right[y][a]
			diff_2 = np.append(diff_2, diff2)
		choice = np.where( abs(diff_1) + abs(diff_2) == min( abs(diff_1)+abs(diff_2)) )[0][0]
		choice -=5
		
		x+=choice
		if phot_e == 778.0:
			print choice,x
	norm_l =[]
	norm_r =[]
	#gets the left and right normalizations
	for j in range(-size,size+1): 
		for i in range(size):
			norm_l.append(image_left[y+i][x+j])
			norm_r.append(image_right[y+i][x+j])
	#turn them into numpy arrays idk why
	norm_l, norm_r = np.array(norm_l),np.array(norm_r) 
	#set them equal to their mean to subtract from the XMCD later on
	norm_l =np.mean(norm_l)
	norm_r = np.mean(norm_r)
	
	back = (norm_l+norm_r)
	#overall background
	#now get the actual xray absorption curves for each
	# does the right polarized images
	while count_x < size:
		intensities_right.append(image_right[y][x+direct*count_x+size2*(number-1)])
		intensities_left.append(image_left[y][x+direct*count_x+direct*size2*(number-1)])
		count_y = 1
		while count_y < size:
			intensities_right.append(image_right[y+count_y][x+direct*count_x+direct*size2*(number-1)])
		        intensities_left.append(image_left[y+count_y][x+direct*count_x+direct*size2*(number-1)])
			count_y+=1
		count_x +=1 	
	intens_left=np.sum(intensities_left)/abs(count_x*count_y)#-norm_l
	intens_right = np.sum(intensities_right)/(abs(count_x)*count_y)#-norm_r
	xmcd= intens_left-intens_right
	intens=(intens_left-norm_l) -(intens_right-norm_r)
	sum_l_r= intens_right+intens_left
	I_plus = sum_l_r/2. + intens/2.
	I_minus = sum_l_r/2. -intens/2.
	return [intens,I_plus, I_minus,intens_left, intens_right,norm_l, norm_r,intens_left-norm_l, intens_right-norm_r] 

def lorentzfit(photon_e, xmcd):
	#performs a single peak lorentzian fit on data
	mod = LorentzianModel()
	pars = mod.guess(xmcd, x=photon_e)
	out  = mod.fit(xmcd, pars, x=photon_e)
	return out.best_fit
def gauss(photon_e, xmcd):
	#performs single peak gaussian fit on data
	mod= GaussianModel()
	pars = mod.guess(xmcd, x=photon_e)
	out=mod.fit(xmcd, pars,x=photon_e)
	return out.best_fit
def voigt(photon_e, xmcd):
	#performs single peak voigt fit on data
	mod =VoigtModel()
	pars = mod.guess(xmcd, x= photon_e)
	out=mod.fit(xmcd, pars, x=photon_e)
	return out.best_fit
def ls_ratio(a3,a2):
	#using sum rules, calculates the L/S ratio
	ls=(2*(a3+a2))/(3*(a3-2*a2))
	return ls

def producedata(image_list_l,image_list_r,number,point,direct=1,det=0):
	#produces lots of xmcd curves for a given point using different sizes for averaging and different distances 
	pixel_list=[]
        if Check11.isChecked() == True:
            pixel_list.append(5)
    
        if Check12.isChecked() == True:
            pixel_list.append(8)
    
        if Check13.isChecked() == True:
            pixel_list.append(10)
    
        if Check14.isChecked() == True: 
            pixel_list.append(15)  
	
	totxmcd=[]	
	for pixel in pixel_list:
		for num in range(1,number+1):
			intens =[]
			list_intensities= []
			intensleft = []
			print num
			intensright = []
			back_l = []
			back_r =[]
			norm_l = []
			norm_r =[]
			combo_l=[]
			combo_r=[]
			for i in range(len(image_list_r)):
				if photon_energies[i] == 778.0: print photon_energies[i]
				list_intensities.append(calculate_nth_average_intensity(image_list_l[i],image_list_r[i],point,pixel,1,num,direct=direct,det=det,phot_e = photon_energies[i]))
			#assign all useful info from calculations
			for j in range(len(list_intensities)):
				intens.append(list_intensities[j][0])
				intensleft.append(list_intensities[j][1])
				intensright.append(list_intensities[j][2])
				back_l.append(list_intensities[j][3])
				back_r.append(list_intensities[j][4])
				norm_l.append(list_intensities[j][5])
				norm_r.append(list_intensities[j][6])
				combo_l.append(list_intensities[j][7])
				combo_r.append(list_intensities[j][8])
			#turning them into absorptions
			combo_l = np.array(combo_l)
			combo_l-= np.median(combo_l[0:9])
			combo_r= np.array(combo_r)
			combo_r-= np.median(combo_r[0:9])			
			xmcd = combo_r-combo_l
			totxmcd.append(xmcd)
			
			p_abs_l = -np.log(back_l)
			p_abs_r = -np.log(back_r)
			
			avg_l=sum(p_abs_l[0:5])/5
			avg_r=sum(p_abs_r[0:5])/5
			p_abs_l2=p_abs_l+2*abs(avg_l)
			p_abs_r2=p_abs_r+2*abs(avg_r)
		        avg_l2=sum(p_abs_l2[0:5])/5
			avg_r2=sum(p_abs_r2[0:5])/5
			q_abs_l = (p_abs_l2/(avg_l2))-1
			q_abs_r = (p_abs_r2/(avg_r2))-1
			
			
			##Fitting attempt
			pre_e=photon_energies[0:7]
			post_e=photon_energies[-7:]
			fit_e=np.append(pre_e,post_e)
			pre_i_l=q_abs_l[0:7]
			post_i_l=q_abs_l[-7:]
			pre_i_r=q_abs_l[0:7]
			post_i_r=q_abs_l[-7:]
	
			#fit=np.polyfit(fitting_energies,fitting_values,3)
			fit_l=np.polyfit(pre_e,post_i_l,2)
			fit_r=np.polyfit(pre_e,post_i_r,2)
			
		
			a_l=float(fit_l[1])
			b_l=float(fit_l[0])
			c_l=float(fit_l[2])
			a_r=float(fit_r[1])
			b_r=float(fit_r[0])
			c_r=float(fit_l[2])
			x=np.array(photon_energies)
			#y=a+b*x+c*x**2+d*x**3+e*x**4+f*x**5
			y_l=c_l+a_l*x+b_l*x**2
			y_r=c_r+a_r*x+b_r*x**2
			
		        abs_l=q_abs_l-y_l
		        abs_r=q_abs_r-y_r-sy
			
			xmcd2=abs_r-abs_l
			#plt.plot(fitting_energies,fitting_values,"o")
			#plt.plot(x,y,"b")
			#plt.show
			##
			
			#writing them to filesI m
			#SUBTRACTING  A LINEAR FIT OF THE START AND END PART BECAUSE THEY ARE SUPPOSED TO BE ZERO
			tes,xtes = np.array(xmcd[0:30]), np.array(photon_energies[0:30])
			tes,xtes= np.append(tes,xmcd[-10:]), np.append(xtes, photon_energies[-10:])
			m, yint = np.polyfit(xtes, tes,1)
			#ZEROED XMCD
			xmcd = xmcd- np.array(photon_energies) *m-yint #trying to do linear fit
	
			
			#doing a lorentzian fit on them for the double peaks
			lorentzfit_top = lorentzfit(np.array(photon_energies)[-25:], xmcd2[-25:])
			lorentzfit_bot = lorentzfit(np.array(photon_energies[:-20]), xmcd2[:-20])

			# integ to l/s with trapz
			integ_lorentz_top_trapz = trapz(lorentzfit_top, x= np.array(photon_energies)[-25:])
			integ_lorentz_bot_trapz = trapz(lorentzfit_bot, x=np.array(photon_energies[:-20]) )
			# integ to l/s with simps
			integ_lorentz_top_simps = simps(lorentzfit_top, x= np.array(photon_energies)[-25:])
			integ_lorentz_bot_simps = simps(lorentzfit_bot, x=np.array(photon_energies[:-20]) )
			
			lorentzfit_bot = np.append(lorentzfit_bot, np.zeros(20))
			lorentzfit_top = np.append(np.zeros(len(photon_energies)-25),lorentzfit_top)
			lorentz_tot = lorentzfit_top + lorentzfit_bot

			ls_trapz_lor = ls_ratio(integ_lorentz_top_trapz,integ_lorentz_bot_trapz)
			ls_simps_lor = ls_ratio(integ_lorentz_top_simps, integ_lorentz_bot_simps)

			gaussfit_top = gauss(np.array(photon_energies)[-25:], xmcd2[-25:])
			gaussfit_bot = gauss(np.array(photon_energies[:-20]), xmcd2[:-20])
			# integ to l/s with trapz
			integ_gauss_top_trapz = trapz(gaussfit_top, x= np.array(photon_energies)[-25:])
			integ_gauss_bot_trapz = trapz(gaussfit_bot, x=np.array(photon_energies[:-20]) )
			# integ to l/s with simps
			integ_gauss_top_simps = simps(gaussfit_top, x= np.array(photon_energies)[-25:])
			integ_gauss_bot_simps = simps(gaussfit_bot, x=np.array(photon_energies[:-20]) )
			
			gaussfit_bot = np.append(gaussfit_bot, np.zeros(20))
			gaussfit_top = np.append(np.zeros(len(photon_energies)-25),gaussfit_top)
			gaussfit_tot = gaussfit_top + gaussfit_bot
			
			ls_trapz_gauss = ls_ratio(integ_gauss_top_trapz,integ_gauss_bot_trapz)
			ls_simps_gauss = ls_ratio(integ_gauss_top_simps, integ_gauss_bot_simps)

			
			voigtfit_top = voigt(np.array(photon_energies)[-25:], xmcd2[-25:])
			voigtfit_bot = voigt(np.array(photon_energies[:-20]), xmcd2[:-20])

			# integ to l/s with trapz
			integ_voigt_top_trapz = trapz(voigtfit_top, x= np.array(photon_energies)[-25:])
			integ_voigt_bot_trapz = trapz(voigtfit_bot, x=np.array(photon_energies[:-20]) )
			# integ to l/s with simps
			integ_voigt_top_simps = simps(voigtfit_top, x= np.array(photon_energies)[-25:])
			integ_voigt_bot_simps = simps(voigtfit_bot, x=np.array(photon_energies[:-20]))
			

			voigtfit_bot = np.append(voigtfit_bot, np.zeros(20))
			voigtfit_top = np.append(np.zeros(len(photon_energies)-25),voigtfit_top)
			voigtfit_tot = voigtfit_top + voigtfit_bot
		 	
			ls_trapz_voigt = ls_ratio(integ_voigt_top_trapz,integ_voigt_bot_trapz)
			ls_simps_voigt = ls_ratio(integ_voigt_top_simps, integ_voigt_bot_simps)
			directions = {1:'r',-1:'l'}
			dirstr = directions[direct]
			fold = str(point[0])+"_"+str(point[1]) 
			if fold not in os.listdir("."):
				os.mkdir(fold)
			fileref= open(fold+"/"+str(point[0])+"_"+str(point[1])+"_" + str(num) +"_area_"+str(pixel) +'dir_'+dirstr+".csv" ,'w')
			fileref.write('eV XMCD2 trans_l trans_r XMCD combo_l combo_r abs_l abs_r background_l background_r lorentzfit gaussfit voigtfit ls_lor_simps ls_lor_trapz ls_gauss_simps ls_gauss_trapz ls_voigt_simps ls_voigt_trapz '+'\n')
			
			for k in range(len(photon_energies)):
				fileref.write(str(photon_energies[k]) + " " + str(xmcd2[k]) + " " + str(back_l[k]) +" " +str(back_r[k])+" " 
					+str(xmcd[k]) +" "+str(combo_l[k])+" "+str(combo_r[k]) +" " +str(abs_l[k]) + " " +str(abs_r[k])+" "+str(norm_l[k]) + " " +str(norm_r[k]) +" " +str(lorentz_tot[k])+" " +str(gaussfit_tot[k])+" " +str(voigtfit_tot[k])+" " +str(ls_simps_lor)+" " +str(ls_trapz_lor)+" " +str(ls_simps_gauss)+" " +str(ls_trapz_gauss)+" " +str(ls_simps_voigt)+" " +str(ls_trapz_voigt)+ "\n")
			fileref.close()
			del back_l
			del back_r
			del combo_l
			del combo_r
			del abs_r
			del abs_l
			del norm_l
			del norm_r
	print totxmcd
	
w.show()

w2.hide()

sys.exit(app.exec_())
	
#producedata(list_images_l,list_images_r, pixel_list,5,[500,500],direct=1,det=0)