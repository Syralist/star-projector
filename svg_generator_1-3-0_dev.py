# -*- coding: utf-8 -*-
from tkinter import *
from math import sin,cos,tan,pi,ceil,sqrt,acos
from copy import deepcopy
import time

# global value
phi = (1+sqrt(5))/2

def interPoints(a,b,n):
    dx = (b[0]-a[0])/n
    dy = (b[1]-a[1])/n
    coords = []

    for i in range(0,n):
        coords.append([a[0]+i*dx,a[1]+i*dy])
    return coords

def toothOverlap(length):
    #computes overlap of teeth
    return length

class ValidatingEntry(Entry):
    # base class for validating entry widgets

    def __init__(self, master, value="", **kw):
        Entry.__init__(self,master,kw)
        self.__value = value
        self.__variable = StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def extracode(self):
        pass
    
    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(newvalue)
        else:
            self.__value = value

        self.extracode()

    def validate(self, value):
        # override: return value, new value, or None if invalid
        return value


class FloatEntry(ValidatingEntry):

    def validate(self, value):
        try:
            if value:
                v = float(value)
            
            return value
        except ValueError:
            return None

class MarginEntry(FloatEntry):

    def extracode(self):
        d = diameterForm.get()
        if d == "":
            d = "0"
        m = marginForm.get()
        if m == "":
            m = "0"
        D = depthForm.get()
        if D == "":
            D = "0"
        
        # find apothem
        a = float(d)/2 + float(m) + float(D)*phi/sin(pi-acos(-1/sqrt(5)))
        # convert apothem to side length
        l = a*2*tan(pi/5)
        
        # conversion factor for dodecahedron radius
        r = l * sqrt(3)/(sqrt(5)-1)
        
        # conversion factor for dodecahedron volume
        v = l**3 * (15+7*sqrt(5))/4

        eDodeca.set(round(l,5))
        rDodeca.set(round(r,5))
        vDodeca.set(round(v,5))

def makeEdge(start,end,toothCount,toothLength,hand):
    interior = []
    exterior = []
    
    edge = interPoints(start,end,2*toothCount)
    for point in edge:
        interior.append(point)

    dx = edge[1][0]+edge[0][0]*(-1+2*hand)
    dy = edge[1][1]+edge[0][1]*(-1+2*hand)
    print(dx,dy)
    try:
        scaleFactor = toothLength/(dx**2+dy**2)**(1/2)
    except ZeroDivisionError:
        scaleFactor = 0

    toothStartX = edge[0][0]+(dy*scaleFactor)
    toothStartY = edge[0][1]-(dx*scaleFactor)

    for i in range(0,2*toothCount):
        exterior.append([toothStartX+i*dx,toothStartY+i*dy])

    weave = []
    
    for n in range(0,toothCount):
        n *= 2
        weave.append(interior[n])
        weave.append(exterior[n])
        weave.append(exterior[n+1])
        weave.append(interior[n+1])
    #weave.append([weave[-1][0]+dx,weave[-1][1]+dy])

    return weave


class SpeakerFace:
    def __init__(self,holeDiameter,circleCount,margin,faceDepth,toothCount,includeLastCircle,faceCount=5,overhang=False):
        iR = holeDiameter/2+margin
        toothLength = faceDepth*phi
        r = iR/cos(pi/5)        #Circumradius (for plotting corners)
        
        corners = []
        for i in range(0,5):
            n = ((5-i)*2*pi/5)+pi
            corners.append((r*cos(n),r*sin(n)))

        weave = []
        for i in range(0,faceCount):
            edge = makeEdge(corners[-i],corners[-i-1],toothCount,toothLength,0)
            for point in edge:
                weave.append(point)

        for p in makeEdge(corners[-i-1],corners[-i+3],toothCount,toothLength,0)[0:2]:
            weave.append(p)
        #weave.append(corners[-(i+1)])

        

        #####

        self.toothLength=toothLength
        self.vertices=weave
        self.includeLastCircle = includeLastCircle
        self.circleCount = circleCount
        includeLastCircle = rbBorderCircle.get()
        self.holeDiameter = holeDiameter
        self.margin = margin
        self.strokeWidth = strokeWidth
        self.offset = [0,0]
        self.angle = 0
        self.apothem = holeDiameter/2 + margin + toothLength
        self.side = self.apothem*2*tan(pi/5)

    def translate(self,dx,dy):
        self.offset[0] += dx
        self.offset[1] += dy

    def rotate(self,theta):
        self.angle += theta
    
    def getPathString(self):
        Xa = cos(self.angle)
        Xb = sin(self.angle)
        Ya = cos(self.angle+pi/2)
        Yb = sin(self.angle+pi/2)
        pathString = ""
        for point in self.vertices:
            #point[0]*(xa,xb) + point[1]*(ya,yb)
            #point[0]*xa + point[1] * ya, point[0]*xb+point[1]*yb
            pathString += str(point[0]*Xa+point[1]*Ya+self.offset[0])+","+str(point[0]*Xb+point[1]*Yb+self.offset[1])+" "

        return "M " + pathString

    def getCircleMarkup(self):
        string = """<circle
       cx="%s"
       cy="%s"
       r="%s"
       stroke-width="%s"
       id="circle1"
       style="fill:none;stroke:#000000;stroke-opacity:1;stroke-width:%s" />
"""%(self.offset[0],self.offset[1],self.holeDiameter/2,strokeWidth,strokeWidth)
        
        for i in range(1,self.circleCount+self.includeLastCircle):
            string += """
        <circle
           cx="%s"
           cy="%s"
           r="%s"
           stroke-width="0.1"
           id="circle%s"
           style="fill:none;stroke:#FF0000;stroke-opacity:1;stroke-width:%s" />\n\n"""%(self.offset[0],self.offset[1],self.holeDiameter/2+self.margin*(i/(self.circleCount)),i,self.strokeWidth)

        return string
    
    def getFullString(self):
        string = self.getCircleMarkup()
        
        string += """
        <path
           style="fill:none;stroke:#000000;stroke-width:0.36000000999999998;stroke-linejoin:miter;stroke-miterlimit:4;stroke-width:%s;stroke-opacity:1;stroke-dasharray:none"
           d="%s"
           id="path2993"
           connector-curvature="0"
           nodetypes="ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc" />
"""%(self.strokeWidth,self.getPathString())

        return string
        

def doTheWork():
    
    ##### Set up conversion factors
    
    mm = 3.543307   # px/mm
    inch = 90       # px/in
    cm = mm*10
    m = cm*100
    ft = inch*12

    ##### Get the parameters all right
    
    unit = iUnits.get()
    if len(unit) == 0:
        messagebox.showinfo("Error","Please select a unit from the listbox. If working with raw coordinates, select 'pixels.'")
        return 0
    
    
    if unit == 'm':
        factor = m
    elif unit == 'ft':
        factor = ft
    elif unit == 'in':
        factor = inch
    elif unit == 'cm':
        factor = cm
    elif unit == 'mm':
        factor = mm
    elif unit == 'px':
        factor = 1
    else:
        print("Something has gone terribly, terribly wrong.")
        print(unit,type(unit))
        return 0
    
    d = diameterForm.get()
    if d == "":
        d = "0"
    m = marginForm.get()
    if m == "":
        m = "0"
    D = depthForm.get()
    if D == "":
        D = "0"
    
    holeDiameter = float(d) * factor
    circleCount = int(circlesForm.get())
    margin = float(m) * factor
    faceDepth = float(D) * factor
    toothCount = int(teethForm.get())
    
    ##### Create & place faces

    pageScaleFactor = 1.0   # because margins look good

    faceString = ""

    layout = vLayout.get()
    
    if layout == "Snowflake":
        baseFace = SpeakerFace(holeDiameter,circleCount,margin,faceDepth,toothCount,rbBorderCircle.get())
        pageWidth = (2*phi+1)*baseFace.side * pageScaleFactor
        pageHeight = baseFace.apothem*(5/2+3*sqrt(5)/2) * pageScaleFactor   #(2/cos(pi/5)+3+cos(2*pi/5)/cos(pi/5))
        faces = []
        distance = baseFace.apothem*2-baseFace.toothLength
        
        for i in range(0,5):
            t = pi+2*pi*i/5
            dx = cos(t)*distance
            dy = sin(t)*distance
            f = deepcopy(baseFace)
            f.translate(dx+pageWidth/2,dy+pageHeight/2)
            f.rotate(2*pi/5*(3+i))
            x = f.vertices[0][0] - (f.vertices[-1][0]-f.vertices[-2][0])
            y = f.vertices[0][1] - (f.vertices[-1][1]-f.vertices[-2][1])
            f.vertices.append(f.vertices[0])
            f.vertices.append([x,y])
            faceString += f.getFullString()

        f = deepcopy(baseFace)
        f.translate(pageWidth/2,pageHeight/2)
        f.rotate(pi)
        faceString += f.getCircleMarkup()
        
    if layout == "Single":
        baseFace = SpeakerFace(holeDiameter,circleCount,margin,faceDepth,toothCount,rbBorderCircle.get())
        baseFace.rotate(pi)
        pageWidth = pageScaleFactor * baseFace.apothem * (1+1/cos(pi/5))
        pageHeight = 2*baseFace.apothem * (sin(2*pi/5)/cos(pi/5)) * pageScaleFactor
        baseFace.translate(baseFace.apothem*pageScaleFactor,pageHeight/2)
        baseFace.translate(5,3)
        pageWidth+=10
        pageHeight+=6
        faceString += baseFace.getFullString()

    if layout == "Double":
        left = SpeakerFace(holeDiameter,circleCount,margin,faceDepth,toothCount,rbBorderCircle.get())
        right = SpeakerFace(holeDiameter,circleCount,margin,faceDepth,toothCount,rbBorderCircle.get(),faceCount=4)

        apothem = left.toothLength/2+left.holeDiameter/2+left.margin
        altitude = apothem+(left.holeDiameter/2+left.margin)/cos(pi/5)+cos(pi/5)*left.toothLength
        
        pageWidth= pageScaleFactor * 2 * altitude
        pageHeight = 2*left.apothem * (sin(2*pi/5)/cos(pi/5)) * pageScaleFactor
        
        left.translate(pageScaleFactor*(altitude-apothem),pageHeight/2)
        right.translate(pageScaleFactor*(altitude-apothem),pageHeight/2)
        
        right.rotate(pi+3*2*pi/5)
        right.translate(pageScaleFactor*apothem*2,0)
        
        left.translate(5,3)
        right.translate(5,3)
        pageWidth+=10
        pageHeight+=6
        faceString += left.getFullString()+right.getFullString()
        

#    if layout == "Double":
        


    ##### Be smug
    
    print("Well, how about that.")

    ##### Write the actual SVG
    
    header = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Generated by Eli Sohl's toothed dodecahedral face template generator! -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   width="%s"
   height="%s"
   id="svg2"
   version="1.1">
  <defs
     id="defs4" />
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     id="layer1"
     style="fill:none;stroke:#000000;stroke-opacity:1;stroke-width:%s">
       """%(pageWidth,pageHeight,strokeWidth)
    
    
    #h=hole diameter; m=margin, c=circle count; d=face depth; t=tooth count; b=border circle
    targetFilename = "(%s)h=%sm=%sc=%sd=%st=%sb=%s %s.svg" % (unit,holeDiameter/factor,margin/factor,circleCount,faceDepth/factor,toothCount,rbBorderCircle.get(),vLayout.get())

    targetFilename = time.strftime("%Y-%m-%d %H;%M;%S") + targetFilename
    
    targetFile = open(targetFilename,"w")

    targetFile.truncate(0)
    targetFile.writelines(header)
    targetFile.writelines(faceString)
    targetFile.writelines("""</g>
    </svg>""")
    targetFile.close()

    ##### Show metrics

    if rbShowMetrics.get():
        metricWindow = Toplevel()
        t = Text(metricWindow)
        t.insert(END,"Edge length: %s\n"%(eDodeca.get()))
        t.insert(END,"Radius of bounding sphere: %s\n"%(rDodeca.get()))
        t.insert(END,"Volume of dodecahedron: %s\n"%(vDodeca.get()))
        t.insert(END,"Page width: %s\n"%(pageWidth))
        t.insert(END,"Page height: %s\n"%(pageHeight))
        
        t.pack()
        metricWindow.mainloop()
    

# Input panel

root = Tk()
root.title("Awesome Toothed Pentagon Generator")
root["padx"]=15
root["pady"]=5

strokeWidth = 0.07
yPad = 1
tFile = StringVar()
iUnits = StringVar()
iUnits.set("mm")
vLayout = StringVar()
vLayout.set("Single")

rDodeca = DoubleVar()
rDodeca.set(0)
vDodeca = DoubleVar()
vDodeca.set(0)
eDodeca = DoubleVar()
eDodeca.set(0)


rbBorderCircle = IntVar()
rbShowMetrics = IntVar()


Label(root,text="Values").grid(row=0,column=1,columnspan=2)
Label(root,text="Units").grid(row=0,column=3)

Label(root,text="Hole diameter:").grid(row=1,sticky=E,pady=yPad)
Label(root,text="Hole-tooth margin:").grid(row=2,sticky=E,pady=yPad)
Label(root,text="# of etched circles:").grid(row=3,sticky=E,pady=yPad)
Label(root,text="Face depth:").grid(row=4,sticky=E,pady=yPad)
Label(root,text="Number of teeth:").grid(row=5,sticky=E,pady=yPad)

for n,v in enumerate((("Face edge length",eDodeca),("Radius of bounding sphere",rDodeca),("Volume",vDodeca))):
    stat = LabelFrame(root,text=v[0])
    stat.grid(row=7,column=n)
    Label(stat,textvariable=v[1]).grid(row=0,column=0)
    Label(stat,textvariable=iUnits).grid(row=0,column=1)
    if v[0]=="Volume":
        Label(stat,text="³").grid(row=0,column=2)

diameterForm = MarginEntry(root,width=39,value=0)
marginForm = MarginEntry(root,width=39,value=0)
circlesForm = Spinbox(root,from_=0,to=5,width=37)
depthForm = MarginEntry(root,width=39,value=0)
teethForm = Spinbox(root,from_=1,to=15,width=37)
bigButton = Button(root, text="Crunch the numbers!", command=doTheWork)
borderCheck = Checkbutton(root,text="Remove inradial circle?",variable=rbBorderCircle)
timeCheck = Checkbutton(root,text="Popup statistics after?",variable=rbShowMetrics)


i = 0
for name,abbr in (("Pixels","px"),("Millimeters","mm"),("Centimeters","cm"),("Inches","in"),("Feet","ft"),("Meters","m")):
    b = Radiobutton(root,text=name,value=abbr,variable=iUnits,indicatoron=0,width=12)
    b.grid(row=1+i,column=3)
    i += 1

frame = LabelFrame(root,text="Layout")
frame.grid(row=7,column=3)
OptionMenu(frame,vLayout,"Single","Double","L","3-line","Quad","Snowflake").grid(row=0,column=0)

diameterForm.grid(row=1,column=1,columnspan=2)
marginForm.grid(row=2,column=1,columnspan=2)
circlesForm.grid(row=3,column=1,columnspan=2)
depthForm.grid(row=4,column=1,columnspan=2)
teethForm.grid(row=5,column=1,columnspan=2)

borderCheck.grid(row=6,column=0)
timeCheck.grid(row=6,column=1)

bigButton.grid(row=9,column=0,columnspan=4)

root.mainloop()
