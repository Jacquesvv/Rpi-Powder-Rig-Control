#Jacques Janse Van Vuuren



from skimage import data
from skimage.morphology import disk


from skimage.filters.rank import minimum    #Filters
from skimage.filters.rank import mean
from skimage.filters.rank import maximum
from skimage.filters import threshold_otsu
from skimage import io

import numpy as np  #Array tools
import scipy
import math

from skimage.viewer import ImageViewer  
from skimage.transform import rescale
from skimage.measure import regionprops
from skimage.measure import label

import matplotlib.pyplot as plt

from Tkinter import *   #GUI tools
import Tkinter as tk
from PIL import Image, ImageTk  #Image handler

import picamera             #Camera module
import time
import RPi.GPIO as GPIO     #GPIO



global currentPhoto         #Global variable definition
global camera
camera = picamera.PiCamera()

GPIO.setmode (GPIO.BCM)     #Setup GPIO
GPIO.setwarnings(False)

relay = 19                  #Set pin 19 as relay pin
GPIO.setup (relay, GPIO.OUT)    #Define as output



class Window(tk.Frame):             #Setup for GUI definition
    def __init__(self,master=None):     
        tk.Frame.__init__(self,master)
        self.master=master
        self.init_window()

    def init_window(self):          #GUI layout
        self.master.title("HWControl v5")
        self.pack(fill=BOTH, expand=1)

        menu = Menu(self.master)
        self.master.config(menu=menu)

        file = Menu(menu)
        file.add_command(label='Exit',command=self.client_exit)
        menu.add_cascade(label='File',menu=file)

        edit = Menu(menu)
        edit.add_command(label='Show Image 1',command=self.showImg1)
        edit.add_command(label='Show Image 2',command=self.showImg2)
        edit.add_command(label='Show Image 3',command=self.showImg3)
        edit.add_command(label='         -')
        edit.add_command(label='Show Binary 1',command=self.showBinary1)
        edit.add_command(label='Show Binary 2',command=self.showBinary2)
        edit.add_command(label='Show Binary 3',command=self.showBinary3)
        menu.add_cascade(label='Show Previous Images', menu=edit)

        cam = Menu(menu)
        cam.add_command(label='Show Feed', command=self.showCam)
        cam.add_command(label='Hide Feed', command=self.hideCam)
        menu.add_cascade(label='Camera', menu=cam) 
        
        menu.add_command(label='Help', command=self.helpPopup)
        
        self.labelInput = Label(self, text="SDP Analysis Hardware Control")
        self.labelInput.grid(row=0,column=0,columnspan =5)

        self.labelSpace = Label(self, text=" ")
        self.labelSpace.grid(row=1,column=0, sticky = W)
        
        self.labelThmin = Label(self, text="Thresh-min")
        self.labelThmin.grid(row=2,column=0, sticky = W) 
        self.entryTmin = Entry(self)
        self.entryTmin.grid(row=2,column=1,columnspan=1, sticky = W+E)
        self.entryTmin.insert(0, "40")
        
        self.labelThmax = Label(self, text="Thresh-max")
        self.labelThmax.grid(row=3,column=0, sticky = W)
        self.entryTmax = Entry(self)
        self.entryTmax.grid(row=3,column=1,columnspan=1, sticky = W+E)
        self.entryTmax.insert(0, "3000")

        self.labelThmax = Label(self, text="Thresh-intensity")
        self.labelThmax.grid(row=4,column=0, sticky = W)
        self.entryIntensity = Entry(self)
        self.entryIntensity.grid(row=4,column=1,columnspan=1, sticky = W+E)
        self.entryIntensity.insert(0, "0.075")

        

        self.Test=Button(self, text= "Test Sample", command=self.TestSample)
        self.Test.grid(row=3,column=2,columnspan =1, rowspan =3, sticky=W)
        
        self.labelSpace = Label(self, text=" ")
        self.labelSpace.grid(row=5,column=0, sticky = W)
        
        self.labelResults = Label(self, text="Results:")
        self.labelResults.grid(row=6,column=0, sticky = W)

        self.labelim1 = Label(self, text="Image1")
        self.labelim1.grid(row=8,column=0, sticky = W)

        self.labelim1 = Label(self, text="Image2")
        self.labelim1.grid(row=9,column=0, sticky = W)

        self.labelim1 = Label(self, text="Image3")
        self.labelim1.grid(row=10,column=0, sticky = W)
        
        self.labelim1 = Label(self, text="Count:")
        self.labelim1.grid(row=7,column=1, sticky = W)

        self.labelim1 = Label(self, text="Average Size(pixels):")
        self.labelim1.grid(row=7,column=2, sticky = W)

        self.labelSpace = Label(self, text=" ")
        self.labelSpace.grid(row=11,column=0, sticky = W)

        self.labelim1 = Label(self, text="Final")
        self.labelim1.grid(row=12,column=0, sticky = W)

        self.labelSpace = Label(self, text=" ")
        self.labelSpace.grid(row=13,column=0, sticky = W)

        self.labelim1 = Label(self, text="Current Action-")
        self.labelim1.grid(row=16,column=0, sticky = W)

        self.labelCurrentAction = Label(self, text="idle")
        self.labelCurrentAction.grid(row=16,column=1,columnspan =3, sticky = W) 


        self.im1Count = Label(self, text="-")
        self.im1Count.grid(row=8,column=1, sticky = W)
        self.im2Count = Label(self, text="-")
        self.im2Count.grid(row=9,column=1, sticky = W)
        self.im3Count = Label(self, text="-")
        self.im3Count.grid(row=10,column=1, sticky = W)

        self.im1Average = Label(self, text="-")
        self.im1Average.grid(row=8,column=2, sticky = W)
        self.im2Average = Label(self, text="-")
        self.im2Average.grid(row=9,column=2, sticky = W)
        self.im3Average = Label(self, text="-")
        self.im3Average.grid(row=10,column=2, sticky = W)

        self.imFinalCount = Label(self, text="-")
        self.imFinalCount.grid(row=12,column=1, sticky = W)
        self.imFinalAverage = Label(self, text="-")
        self.imFinalAverage.grid(row=12,column=2, sticky = W)

        self.sizeAct = Label(self, text="-")
        self.sizeAct.grid(row=13,column=2, sticky = W) 

        self.labelSpace = Label(self, text=" ")
        self.labelSpace.grid(row=15,column=0, sticky = W)

        self.sizeConf = Label(self, text="Confidence:")
        self.sizeConf.grid(row=14,column=0, sticky = W)
        self.ConfDisp = Label(self, text="   ", bg="grey")
        self.ConfDisp.grid(row=14,column=2, sticky = W)
        self.Confidence = Label(self, text="-")
        self.Confidence.grid(row=14,column=1, sticky = W)
        

        self.labelSpace = Label(self, text=" ")
        self.labelSpace.grid(row=17,column=0, sticky = W)
        

        self.pumpon=Button(self, text= "Pump On", command=self.pump_On)
        self.pumpon.grid(row=18,column=0, sticky=W)

        self.pumpoff=Button(self, text= "Pump Off", fg="red", command=self.pump_Off)
        self.pumpoff.grid(row=18,column=1, sticky=W)

    def showCam(self): 
        global camera
        camera.preview_fullscreen = False
        camera.preview_window=(0, 0, 1280, 960)
        camera.start_preview()

    def hideCam(self):  
        global camera
        camera.stop_preview()

    def showImg1(self):
        self.labelCurrentAction["text"] = "Resizing"
        self.update_idletasks()
        t = tk.Toplevel(self)
        t.title("Image 1")
        load = Image.open("/home/pi/PythonTempFolder/OrigPic1.jpg")
        load = load.resize((1248,702),Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        t.geometry("1248x702+0+0")
        img = Label(t, image=render)
        img.image = render
        img.place(x=0,y=0)
        self.labelCurrentAction["text"] = "idle"
        self.update_idletasks()

    def showImg2(self):
        self.labelCurrentAction["text"] = "Resizing"
        self.update_idletasks()
        t = tk.Toplevel(self)
        t.title("Image 2")
        load = Image.open("/home/pi/PythonTempFolder/OrigPic2.jpg")
        load = load.resize((1248,702),Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        t.geometry("1248x702+0+0")
        img = Label(t, image=render)
        img.image = render
        img.place(x=0,y=0)
        self.labelCurrentAction["text"] = "idle"
        self.update_idletasks()

    def showImg3(self):
        self.labelCurrentAction["text"] = "Resizing"
        self.update_idletasks()
        t = tk.Toplevel(self)
        t.title("Image 3")
        load = Image.open("/home/pi/PythonTempFolder/OrigPic3.jpg")
        load = load.resize((1248,702),Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        t.geometry("1248x702+0+0")
        img = Label(t, image=render)
        img.image = render
        img.place(x=0,y=0)
        self.labelCurrentAction["text"] = "idle"
        self.update_idletasks()

    def showBinary1(self):
        self.labelCurrentAction["text"] = "Loading"
        self.update_idletasks()
        t = tk.Toplevel(self)
        t.title("Binary 1")
        load = Image.open("/home/pi/PythonTempFolder/binary1.jpg")
        render = ImageTk.PhotoImage(load)
        t.geometry("1080x1080+0+0")
        img = Label(t, image=render)
        img.image = render
        img.place(x=0,y=0)
        self.labelCurrentAction["text"] = "idle"
        self.update_idletasks()

    def showBinary2(self):
        self.labelCurrentAction["text"] = "Loading"
        self.update_idletasks()
        t = tk.Toplevel(self)
        t.title("Binary 2")
        load = Image.open("/home/pi/PythonTempFolder/binary2.jpg")
        render = ImageTk.PhotoImage(load)
        t.geometry("1080x1080+0+0")
        
        img = Label(t, image=render)
        img.image = render
        img.place(x=0,y=0)
        self.labelCurrentAction["text"] = "idle"
        self.update_idletasks()

    def showBinary3(self):
        self.labelCurrentAction["text"] = "Loading"
        self.update_idletasks()
        t = tk.Toplevel(self)
        t.title("Binary 3")
        load = Image.open("/home/pi/PythonTempFolder/binary3.jpg")
        render = ImageTk.PhotoImage(load)
        t.geometry("1080x1080+0+0")
        img = Label(t, image=render)
        img.image = render
        img.place(x=0,y=0)
        self.labelCurrentAction["text"] = "idle"
        self.update_idletasks()

    def helpPopup(self):
        t = tk.Toplevel(self)
        t.title("Helpful Information")
        t.geometry("545x315+700+200")
        t.text1 = Label(t, text="1 Pixel ~ 113.0989 microns^2")
        t.text1.grid(row=0,column=0, sticky=W)
        t.text1 = Label(t, text="Default Threshold -   40 : 3000   -    0.075")
        t.text1.grid(row=1,column=0, sticky=W)
        t.text1 = Label(t, text=" ")
        t.text1.grid(row=2,column=0, sticky=W)
        t.text1 = Label(t, text="Processing Steps:")
        t.text1.grid(row=3,column=0, sticky=W)
        t.text1 = Label(t, text="Greyscale>Crop>minimumFilter>meanFilter>maximumFilter>Subtract from original>")
        t.text1.grid(row=4,column=0, sticky=W)
        t.text1 = Label(t, text=">Threshold(Otsu)>Binary>Analyse(Count number particles within threshold specified)")
        t.text1.grid(row=5,column=0, sticky=W)

        
        t.text1 = Label(t, text=" ")
        t.text1.grid(row=6,column=0, sticky=W)
        t.text1 = Label(t, text="Use circle approximation to calculate approximate size of particle")
        t.text1.grid(row=7,column=0, sticky=W)
        t.text1 = Label(t, text="Diameter Particle = (sqrt((no.Pixels*113.1)/3.141592))*2")
        t.text1.grid(row=8,column=0, sticky=W)
        t.text1 = Label(t, text=" ")
        t.text1.grid(row=9,column=0, sticky=W)
        t.text1 = Label(t, text="Reduce bubbles by running pump dry and dipping input for 3 second intervals")
        t.text1.grid(row=10,column=0, sticky=W)
        t.text1 = Label(t, text="If bubbles persist briefly pinch outlet tube at top of flow cell")
        t.text1.grid(row=11,column=0, sticky=W)
        t.text1 = Label(t, text=" ")
        t.text1.grid(row=12,column=0, sticky=W)
        t.text1 = Label(t, text=" ")
        t.text1.grid(row=13,column=0, sticky=W)
        t.text1 = Label(t, text=" ")
        t.text1.grid(row=14,column=0, sticky=W)
        t.text1 = Label(t, text="Programmed by Jacques Janse van Vuuren")
        t.text1.grid(row=15,column=0, sticky=W)
        t.text1 = Label(t, text="Contact: 022 6330 139")
        t.text1.grid(row=16,column=0, sticky=W)

    def showCurrent(self):
        global currentPhoto
        t = self.t = tk.Toplevel(self)
        load = scipy.misc.toimage(currentPhoto)
        render = ImageTk.PhotoImage(load)
        t.geometry("1080x1080+0+0")
        img = Label(t, image=render)
        img.image = render
        img.place(x=0,y=0)

    def pump_On(self):  
        self.labelCurrentAction["text"] = "Pumping Liquid"
        self.pumpon["fg"]="red"
        self.pumpoff["fg"]="black"
        GPIO.output(relay,1)    #Turn on pump

    def pump_Off(self):
        self.labelCurrentAction["text"] = "idle"
        self.pumpon["fg"]="black"
        self.pumpoff["fg"]="red"
        GPIO.output(relay,0)    #Turn off pump


    def TestSample(self):       #Run pump, take samples and analyse
        global currentPhoto
        self.im1Count["text"]="-"   #Reset text fields
        self.im2Count["text"]="-"
        self.im3Count["text"]="-"

        self.im1Average["text"]="-"
        self.im2Average["text"]="-"
        self.im3Average["text"]="-"

        self.imFinalCount["text"] = "-"
        self.imFinalAverage["text"] = "-"
        self.sizeAct["text"] = "-"
        self.Confidence["text"] = "-"
        self.ConfDisp["bg"] = "grey"
        
        ##'''       
        global camera
        camera.stop_preview()   #Quit preview if open



        ###########################     Run pump and take Pictures       ###############################
        
        self.pump_On()  #Turn on pump
        self.update_idletasks() #Refresh Gui

        for x in range(0,25):      #Wait 25 seconds
            self.labelCurrentAction["text"] = "Pumping Liquid - %d" %(25-x)
            self.update_idletasks()
            time.sleep(1)
        self.pump_Off() #Turn off pump


        
        for x in range(1,4):        #Take 3 images
            self.pump_Off()
            self.labelCurrentAction["text"] = "Powder Settle Time"
            self.update_idletasks()
            time.sleep(2)
            self.labelCurrentAction["text"] = "Capturing Image %d" %x
            camera.hflip = True     #Flip camera orientation appropriately
            camera.vflip = True
            camera.capture('/home/pi/PythonTempFolder/OrigPic' + str(x) + '.jpg')   #Save image to default directory

            self.update_idletasks()
            time.sleep(2)

            if (x<3):
                self.pump_On()  #Turn on pump
                for y in range(0,6):      #Wait 6 seconds
                    self.labelCurrentAction["text"] = "Pumping Liquid - %d" %(6-y)
                    self.update_idletasks()
                    time.sleep(1)
                    
                self.pump_Off() #Turn off pump
        ##'''
        ################################################################################################


        ###########################              Analyse Pictures        ###############################
        for x in range(1,4):        
            self.labelCurrentAction["text"] = "Loading image as greyscale - im %d" %x
            self.update_idletasks()
            
            image1 = io.imread('/home/pi/PythonTempFolder/OrigPic' + str(x) + '.jpg', as_grey=True) #Load image as greyscale
            
            ##
            ##image1 = io.imread('/home/pi/SDP Project/PowderTests/PPIM169041/169041Pic' + str(x) + '.jpg', as_grey=True)   ##Comment Out
            ##
            
            self.labelCurrentAction["text"] = "Cropping"    #Crop image
            self.update_idletasks()
            fromFile = np.asarray(image1, dtype=np.float32)
            orig = fromFile[0:1080,420:1500]
            currentPhoto = orig
            self.showCurrent()
            self.update_idletasks()
            time.sleep(2)

            self.labelCurrentAction["text"] = "Applying minimum filter"     #Apply minimum filter
            self.update_idletasks()
            image2 = minimum(orig, disk(6))
            currentPhoto = image2
            self.t.destroy()
            self.update_idletasks()
            self.showCurrent()
            self.update_idletasks()
            
            
            self.labelCurrentAction["text"] = "Applying mean filter"        #Apply mean filter
            self.update_idletasks()
            image3 = mean(image2,disk(22))
            currentPhoto = image3
            self.t.destroy()
            self.update_idletasks()
            self.showCurrent()
            self.update_idletasks()
            
            
            self.labelCurrentAction["text"] = "Applying maximum filter"     #Apply maximum filter
            self.update_idletasks()
            image4 = maximum(image3,disk(6))
            currentPhoto = image4
            self.t.destroy()
            self.update_idletasks()
            self.showCurrent()
            self.update_idletasks()
            time.sleep(2)

            
            self.labelCurrentAction["text"] = "Normalising"         #Subtract filtered image from original
            self.update_idletasks()
            new = np.asarray(image4, dtype=np.float32)
            new[0:,0:] = new[0:,0:]/255
            
            sub = np.subtract(orig,new)
            sub[0:,0:] += (128/255) #Scale appropriately

            imFinal= sub
            currentPhoto = sub
            self.t.destroy()
            self.update_idletasks()
            self.showCurrent()
            self.update_idletasks()
            time.sleep(1)
            
            self.labelCurrentAction["text"] = "Thresholding (Otsu)"     #Get Otsu threshold value from image
            self.update_idletasks()
            thresh = threshold_otsu(imFinal)        ##Threshold
            print("T - " + str(thresh))
                       
            intensity =float(self.entryIntensity.get()) #Get manual threshold value from text field
            
            self.labelCurrentAction["text"] = "Creating Binary Image"   #Create binary image from threshold value (changed to manual - ignore otsu)
            self.update_idletasks()
            binary = sub <= intensity #0.095 #(thresh+0.2)
            scipy.misc.imsave('/home/pi/PythonTempFolder/binary' + str(x) + '.jpg', binary) #Save binary image to default directory
            currentPhoto = binary
            self.t.destroy()
            self.update_idletasks()
            self.showCurrent()
            self.update_idletasks()

            
            labels = label(binary)
            self.labelCurrentAction["text"] = "Analysing Particles"
            self.update_idletasks()

            counter =0
            areaCount =0
            Tmin =int(self.entryTmin.get())     #Get size thresholds from text input
            Tmax =int(self.entryTmax.get())
            ################################################################################################


            

            #Tmin = 10
            #Tmax = 300
            
            for region in regionprops(labels):                      #Iterate through particles in the binary image
                if (region.area <= Tmax and region.area >= Tmin):
                    counter = counter +1                    #Count number of particles found
                    areaCount = areaCount + region.area     #Sum area of all particles

            average = areaCount/counter     #Calculate average area
            if (x == 1):
                self.im1Count["text"] = counter
                self.im1Average["text"] = round(average,5)  #Display average image 1
                counter1 = counter
                average1 = average

            if (x == 2):
                self.im2Count["text"] = counter
                self.im2Average["text"] = round(average,5) #Display average image 2
                counter2 = counter
                average2 = average

            if (x == 3):
                self.im3Count["text"] = counter
                self.im3Average["text"] = round(average,5) #Display average image 3
                counter3 = counter
                average3 = average
        
            print(counter)
            average = areaCount/counter
            #print(average)

            self.t.destroy()
            self.update_idletasks()

        
        finalCount = (counter1 + counter2 + counter3)/3     #Calculate final count all images
        finalAverage = (average1 + average2 + average3)/3   #Calculate final average all images

        self.imFinalCount["text"] = finalCount
        self.imFinalAverage["text"] = round(finalAverage,3)
        microns = (math.sqrt((finalAverage*113.0989232)/3.14159265359))*2   #Size approximation
        
        self.sizeAct["text"] = "~ " +str(round(microns,3)) + " microns"

        maxCount = max(counter1, counter2, counter3)
        Conf = float(finalCount)/float(maxCount)
        self.Confidence["text"] =str(round(Conf,3)) + " %"
        print(finalCount)
        #print(maxCount)
        print(Conf)

       
        self.ConfDisp["bg"] = "red"     #Change confidence colours
        if (Conf >= 0.84):
            self.ConfDisp["bg"] = "yellow"
        if (Conf >= 0.93):
            self.ConfDisp["bg"] = "green"
        
            
        self.labelCurrentAction["text"] = "Complete!"
        self.update_idletasks()
        time.sleep(2)
        self.labelCurrentAction["text"] = "idle"
        self.update_idletasks()

    def client_exit(self):
        exit()

def quitCamPrev(event):     #Exit camera preview on escape button press
    global camera
    #camera.stop_preview()
    #print("Button Press")
    if(event.char == ''):
        camera.stop_preview()
        print("Escape Pressed")
        

root = Tk()
root.geometry("405x365+1250+50")
app = Window(root)
root.bind('<KeyPress>', quitCamPrev)
root.mainloop()
