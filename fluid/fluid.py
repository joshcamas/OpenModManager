"""
    Fluid (Fluid and Lush User Interface Deity) is a small helper module to aid in prototyping
    and general user interface structure and design. It includes a powerful graphing and plotting system, built
    atop the wonderful matplotlib.

"""

"""
    TODO:

        -use matplotlib as a generator of labels, so we can have latex interpreted labels
        
        -instead of hardcoding plot options (color, marker) automate this by simply referencing 
        matplotlib's Line2D

"""

import sys
import math
import csv 

#TODO: Get rid of this import mess
import matplotlib as mpl
mpl.use('TkAgg')
from matplotlib import rc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib import pyplot as plt
from PIL import ImageGrab


import tkinter as tk
from tkinter import ttk as ttk

from scipy.interpolate import spline

def quicksetupapp(app,windowtitle=None):
    root = tk.Tk()

    app = app(root)
    app.frame.pack(side="top", fill="both", expand=True)
    app.build()
    app.root = root
    if(windowtitle != None):
        root.title(windowtitle)
    root.mainloop()
    

class Frame():
    """
    An small container that holds a frame. Can attach to a widget, a Frame, or nothing
    """
    
    def __init__(self, parent, *args, **kwargs):
        #Attach to Frame
        if(isinstance(parent,Frame)):
            self.frame = tk.Frame(parent.frame,*args, **kwargs)
        else:
            self.frame = tk.Frame(parent, *args, **kwargs)

        self.parent = parent

    def grid(self,**kwargs):
        self.frame.grid(kwargs)
    
    def setoutline(self,color,thickness=1):
        self.frame.config(highlightbackground=color,highlightcolor=color, highlightthickness=thickness)
    
    def setpadding(self,x,y):
        self.grid(padx=x,pady=y)
    
    def setinternalpadding(self,x,y):
        self.grid(ipadx=x,ipady=y)
        
        
class App(Frame):
    """
    Contains all content of an application window
    
    The master frame that contains all widgets and subframes in
    an application.
    """

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.signals = []
        plt.rcParams.update({'font.size': 9})
        
    def build():
        pass
    
    def screenshot(self,widget,path):
        x=self.parent.winfo_rootx()+widget.winfo_x()
        y=self.parent.winfo_rooty()+widget.winfo_y()
        x1=x+widget.winfo_width()
        y1=y+widget.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save(path)
        
        
    #Signals are a simple way to allow communication between applications
    def addsignal(id,function):
        signal = Signal(id,function)
        self.signals.append(signal)

    def sendsignal(id,*args, **kwargs):
        for i in range(len(self.signals)):
            if(id == self.signals[i].id):
                self.signals[i].function(*args, **kwargs)
                return True
        print("Could not send signal " + id)
        return False
		 
	

class Signal():
    def __init__(self,id,function):
        self.id = id
        self.function = function
		
class Widget(Frame):
    """
    A single component of the interface
    
    A singular component that can be attached to a `Frame`
    """
    def __init__(self,parent=None):
        Frame.__init__(self,parent)

    def grid(self,**kwargs):
        self.frame.grid(**kwargs)
    
    def hide(self):
        self.frame.grid_remove()
    
    def show(self):
        self.frame.grid()
        
class LatexLabel(Widget):
    def __init__(self,master,size):
        
        Widget.__init__(self,master)
        self.figure = Figure(figsize=size)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nw")
        self.canvas.show()
        
        rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
        rc('text', usetex=True)
        
        
        plt.title(r"\TeX\ is Number "
          r"$\displaystyle\sum_{n=1}^\infty\frac{-e^{i\pi}}{2^n}$!",
          fontsize=16, color='gray')
          
      #  rc('text', usetex=False)
        
        plt.draw()
        self.canvas.draw()
    def update():
        plt.draw()
        self.canvas.draw()
        
        
class Graph(Widget):
    """
    A widget with graphing and plotting capabilities
    
    A widget that interfaces with MatPlotLib to generate graphs, 
    and in turn, plots
    
    Parameters
    ----------
    """
    
    def __init__(self,master,size):    
        """
        Set up basic widget, and initialize graph system
        
        Parameters
        ----------
        parent : Frame
            Parent frame to attach to. Default is the application's
            frame.
        size : Data2D
            The scaling of the graph.
            
        Returns
        -------
        Frame
            Created frame.
        
        """
        Widget.__init__(self,master)
        
        self.figure = Figure(figsize=size)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.canvas.show()

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None

        self.patches = []
        self.plots = []
        self.title = None
        self.xaxis = None;
        self.yaxis = None;
        self.hlines = []
        self.vlines = []

    def buildplot(self,getdata=None):
        """
        Generates new plot with a function that grabs data
        .. note:: Deprecated in Fluid 0.8.0 
            `buildPlot` is no longer necessary, and will be 
            replaced with something new in a coming update. 
            The getData feature is not only confusing, but also
            simply bad design
        
        Parameters
        ----------
        getData : function
            function plot will run to get data
        """
        plot = Plot(self)
        #plot.init()
        if(getdata != None):
            plot.getdata = getdata
        self.addplot(plot)
        return(plot)
    
    
    def buildcontourplot(self,getdata=None):
        """
        Generates new contour plot with a function that grabs data
        .. note:: Deprecated in Fluid 0.8.0 
            `buildPlot` is no longer necessary, and will be 
            replaced with something new in a coming update. 
            The getData feature is not only confusing, but also
            simply bad design
        
        Parameters
        ----------
        getData : function
            function plot will run to get data
        """
        plot = ContourPlot(self)
        #plot.init()
        if(getdata != None):
            plot.getdata = getdata
        self.addplot(plot)
        return(plot)
        
        
    def addplot(self,plot):
        """
        Adds a `Plot` to the `Graph`
        
        Parameters
        ----------
        plot : Plot
            The plot to add
        """
        self.plots.append(plot)
        return(plot)

    def enablegrid(self):
        """
        Adds a simple `Grid` to the `Graph`
        """
        
        self.grid = Grid(self)
        #self.grid.init()
        self.plots.insert(0,self.grid)

    def vline(self,x,color="black",linewidth=1):
        """
        Add a vertical line to the `Graph`
        
        Parameters
        ----------
        x : float
            X-position of the line
        color : color, optional
            Color of line (default is 'black')
        linewidth : float, optional
            Width of line (default is 1)
            
        """
        
        line = AxisLine(x,color,linewidth)
        self.vlines.append(line)

    def hline(self,y,color="black",linewidth=1):
        """
        Add a horizontal line to the `Graph`
        
        Parameters
        ----------
        y : float
            Y-position of the line
        color : color, optional
            Color of line (default is 'black')
        linewidth : float, optional
            Width of line (default is 1)
            
        """
        
        line = AxisLine(y,color,linewidth)
        self.hlines.append(line)
        
    def setlimits(self,xmin=None,xmax=None,ymin=None,ymax=None):
        """
        Sets the vertical and horizontal limits of the graph.
        
        Parameters
        ----------
        xMin : float, optional
            minimum x value in limit. Default is None, which means no limit
        xMax : float, optional
            maximum x value in limit. Default is None, which means no limit
        yMin : float, optional
            minimum y value in limit. Default is None, which means no limit
        yMax : float, optional
            maximum y value in limit. Default is None, which means no limit
            
        """
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def updategraph(self):
        """
        Clears and renders `Graph`, and all `Plot`s within
        """
        if(len(self.plots) == 0):
            return

        self.plots[0].plot.clear()
        
        for i in range(0,len(self.plots)):
            self.plots[i]._updateplot()

        if(self.title != 0):
            self.plots[0].plot.set_title(self.title)
            
        #set limits
        if(self.xmin != None):
            self.plots[0].plot.set_xlim(xmin=self.xmin) 

        if(self.xmax != None):
            self.plots[0].plot.set_xlim(xmax=self.xmax) 

        if(self.ymin != None):
            self.plots[0].plot.set_ylim(ymin=self.ymin) 

        if(self.ymax != None):
            self.plots[0].plot.set_ylim(ymax=self.ymax) 
        
        #draw vertical lines
        for i in range(len(self.vlines)):
            
            x = self.vlines[i].point
            color = self.vlines[i].color
            linewidth = self.vlines[i].linewidth
            
            self.plots[0].plot.axvline(x=x, color=color, linewidth=linewidth)
        
        #draw horizontal lines
        for i in range(len(self.hlines)):
            
            y = self.hlines[i].point
            color = self.hlines[i].color
            linewidth = self.hlines[i].linewidth
            
            self.plots[0].plot.axhline(y=y, color=color, linewidth=linewidth)
        
        #draw x label
        if(self.xaxis != None):
            self.plots[0].plot.set_xlabel(self.xaxis)
        
        #draw y label
        if(self.yaxis != None):
            self.plots[0].plot.set_ylabel(self.yaxis)
        
        #draw legend
        self.drawlegend()
        
        plt.draw()

        self.canvas.draw()

    def addlegend(self,label,plot):
        """
        Adds a colored label to the legend, based on the plot
        
        Parameters
        ----------
        label: string
            name of label
        plot: Plot
            plot you want to reference
        
        """

        patch = {"plot":plot,"label":label}
        self.patches.append(patch)
    
    def drawlegend(self):
        """
        Renders a legend (Internal)
        """
        if(len(self.patches) > 0):
            labels = [0 for x in range(len(self.patches))]
            patches = [0 for x in range(len(self.patches))]
            for i in range(0,len(self.patches)):
                labels[i] = self.patches[i]["label"]
                patches[i] = self.patch = mpatches.Patch(color=self.patches[i]["plot"].color)

            self.figure.legend(handles=patches,labels=labels)
            
class Plot():
    """
    A single layer of a graph

    """
    def __init__(self,graph):   
        """
        Initialize plot
        
        Parameters
        ----------
        graph: Graph
            Parent graph
        
        Returns
        -------
        Frame
            Created frame.
            
        """
        self.graph = graph 
        self.plot = self.graph.figure.add_subplot(111)
        self.color = None
        self.linestyle = "-"
        self.marker = "None"
        self.markersize = 5
        self.fillStyle = "full"
        self.linewidth = 1.2
        self.inputData = Data2D()
        self.smooth_amount = 1
        
    def setinputdata(self,x,y):
        """
        Updates plot data. Note you must update the parent
        graph to actually see the changes
        
        Parameters
        ----------
        x, y: array of floats
            input data for plot
        
        """
        self.inputData.x = x
        self.inputData.y = y
        
    def getdata(self,data):
        """
        .. note:: Deprecated in Fluid 0.8.0
        """
        
        class dataClass:
            def __init__(self):
                self.xVals = data.x
                self.yVals = data.y
        return(dataClass())

    def _updateplot(self):
        """
        Renders plot (Internal)
        
        Parameters
        ----------
        case: (Deprecated)
        
        """
        data = self.getdata(self.inputData)
        
        x = data.xVals
        y = data.yVals
        
        if(self.smooth_amount != 1):
            x,y = self._smooth(x,y)
        
        if(self.color == None):
            plot = self.plot.plot(x, y, fillstyle=self.fillStyle, marker=self.marker, markersize = self.markersize, linestyle=self.linestyle, linewidth=self.linewidth)

            self.color = plot[0].get_color()
        else:
            self.plot.plot(x, y, fillstyle=self.fillStyle, marker=self.marker, markersize = self.markersize, linestyle=self.linestyle, linewidth = self.linewidth, color=self.color)
            
    def addlegend(self,label):
        self.graph.addlegend(label,self)

    #Load csv data and push this data into the plot
    #Default: column 1 = x values, column 0 = y. Rotate flips this (row 1 = x, row 2 = y)
    def load_csv_data(self,source,yColumn=0,xColumn=1,rotate=False):
        """
        Generates plot based on CSV data
        
        Parameters
        ----------
        source: string
            path where csv file is
        yColumn: int (optional)
            column where the y values are. (Default is 0)
        xColumn: init (optional)
            column where the x values are. (Default is 1)
        rotate: bool (optional)
            whether to read rows instead of columns (Default is false)
        
        """
        
        with open(source, 'r') as f:
            reader = csv.reader(f)
            raw = list(reader)
            
        for x in range(0,len(raw)):
            for y in range(0,len(raw[0])):
                if(raw[x][y] != ""):
                    raw[x][y] = float(raw[x][y])
                else:
                    raw[x][y] = None

        if(rotate == False):
            raw = list(zip(*raw))[::-1]
            raw.reverse()

        self.setinputdata(raw[xColumn],raw[yColumn])


    def write_to_csv(self,source):
        """
        Writes plot data to a csv file
        
        Parameters
        ----------
        source: string
            path to file to write to
            
        """
        newArray = [[] for x in range(2)]
        newArray[0] = self.inputData.y
        newArray[1] = self.inputData.x

        newArray = list(zip(*newArray))[::-1]
        newArray.reverse()
            
        with open(source, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(newArray)

class ContourPlot(Plot):
    """
    A plot with contour-style data
    """
    
    def setinputdata(self,x,y,z):
        """
        Updates plot data. Note you must update the parent
        graph to actually see the changes
        
        Parameters
        ----------
        x, y, z: array of floats
            input data for plot
        
        """
        self.inputData.x = x
        self.inputData.y = y
        self.inputData.z = z
        
        
    def _updateplot(self):
        #data = self.getData(case)

        self.plot.contour(self.inputData.x, self.inputData.y, self.inputData.z, self.levels, colors='k', linewidths=self.linewidth)
        self.plot.contourf(self.inputData.x, self.inputData.y, self.inputData.z, self.levels)

class BarPlot(Plot):
    """
    A plot with contour-style data
    """
    
    def __init__(self,graph):
        Plot.__init__(self,graph)
        
        self.align='center'
        self.barwidth = 0.8
        self.bottom = 0

    def _updateplot(self):
        #data = self.getData(case)
        
        #Default color
        if(self.color == None):
            self.color = "grey"
        
        self.plot.bar(self.inputData.x, self.inputData.y,self.barwidth,self.bottom, align = self.align, color = self.color, linewidth = self.linewidth)

class HistPlot(Plot):
    def __init__(self,graph):
        Plot.__init__(self,graph)
        
        self.align='center'
        self.barwidth = 0.8
        self.bottom = 0

    def _updateplot(self):
        #data = self.getData(case)

        self.plot.hist(self.inputData.y, bins=self.inputData.x)
    
    
    
class Grid(Plot):
    """
    A simple grid to add to graphs
    """
    def __init__(self,graph):   
        Plot.__init__(self,graph)

    def _updateplot(self,case):
        self.plot.grid(which='both')
        
class Button(Widget):
    """
    A button widget with text
    
    """
    def __init__(self,parent,text):
        """
        Initialize widget
        
        Parameters
        ----------
        parent: Frame
            Frame to attach to
        text: string, optional
            Text to display on button. (Default is 'Button')
        
        Returns
        -------
        Frame
            Created frame.
        
        """
        Widget.__init__(self,parent)
        self.button = tk.Button(master=self.frame, text=text)
        self.button.grid(row=0,column=0,padx=2)

    def setcommand(self,command):
        """
        Set function to run when button is pressed
        
        Parameters
        ----------
        command: function
            Function to run
        """
        self.button.configure(command=command)

class InputBox(Widget):
    """
    A widget with a label and a textbox
    """
    def __init__(self,parent,label,default="",width=10):
        """
        Initialize widget
        
        Parameters
        ----------
        parent: Frame
            Frame to attach to
        label: string
            Label of widget
        default: string, optional
            Default value of textbox. (Default is '')
        width: float, optional
            Width of textbox (Default is 10)
        Returns
        -------
        Frame
            Created frame.
        
        """
        Widget.__init__(self,parent)

        self.label = tk.Label(self.frame, text=label)
        self.entry = tk.Entry(self.frame,width=width)
        self.label.grid(row=0,column=0,padx=2)
        self.entry.grid(row=0,column=1,padx=1)

        self.entry.insert(0,default)
        
       # return(self.frame)

    def setvalue(self,value):
        """
        Set value of textbox
        
        Parameters
        ----------
        value: string
            value of textbox
        """
        self.entry.insert(0,value)

    def getvalue(self):
        """
        Get value of textbox
        
        Returns
        -------
        string
            value of textbox
        """
        return(self.entry.get())

class CheckBox(Widget):
    """
    A widget with a label and a checkbutton
    """
    def __init__(self,parent,label,default=0,width=10):
        """
        Initialize widget
        
        Parameters
        ----------
        parent: Frame
            Frame to attach to
        label: string
            Label of widget
        default: int, optional
            Default value of checkbox. (Default is 0)
        width: float, optional
            Width of checkbox (Default is 10)
        Returns
        -------
        Frame
            Created frame.
        
        """
        Widget.__init__(self,parent)

        self.value = tk.IntVar()
        self.value.set(default)
        #self.label = tk.Label(self.frame, text=label)
        self.check = tk.Checkbutton(self.frame, text=label, variable=self.value)
        
        #self.label.grid(row=0,column=0,padx=2)
        self.check.grid(row=0,column=1,padx=1)

       # return(self.frame)
    
    def setcommand(self,command):
        self.check.configure(command=command)
        
    def setvalue(self,value):
        """
        Set value of textbox
        
        Parameters
        ----------
        value: string
            value of textbox
        """
        self.check.set(value)

    def getvalue(self):
        """
        Get value of textbox
        
        Returns
        -------
        string
            value of textbox
        """
        return(self.value.get())


class Scale(Widget):
    """
    A widget with a tk Scale
    """
    def __init__(self,parent,label,start=0,end=100,default=0):
        """
        Initialize widget
        
        Parameters
        ----------
        parent: Frame
            Frame to attach to
        label: string
            Label of widget
        default: int, optional
            Default value of checkbox. (Default is 0)
        width: float, optional
            Width of checkbox (Default is 10)
        Returns
        -------
        Frame
            Created frame.
        
        """
        Widget.__init__(self,parent)

        #self.label = tk.Label(self.frame, text=label)
        self.scale = tk.Scale(self.frame, label=label,from_=start, to=end,orient=tk.HORIZONTAL)
        
        #self.label.grid(row=0,column=0,padx=2)
        self.scale.grid(row=0,column=1,padx=1)

       # return(self.frame)
    
    def setcommand(self,command):
        self.scale.configure(command=command)
        
    def setvalue(self,value):
        """
        Set value of textbox
        
        Parameters
        ----------
        value: float
            value of scale
        """
        self.scale.set(value)

    def getvalue(self):
        """
        Get value of scale
        
        Returns
        -------
        float
            value of scale
        """
        return(self.scale.get())

class Label(Widget):
    def __init__(self,parent,label,bold=False):
        Widget.__init__(self,parent)
        
        if(bold == False):
            f = "arial 9"
        else:
            f = "arial 9 bold"
            
        self.label = tk.Label(self.frame,text=label,font=f)
        self.label.grid(row=0,column=0,padx=2)
        
    def setText(self,label):
        self.label['text']=label
		
class OutputBox(Widget):
    """
    A widget with a label and another label. Used to display small bits of data
    """
    
    def __init__(self,master,label,value,vertical=False):
        """
        Initialize widget
        
        Parameters
        ----------
        parent: Frame
            Frame to attach to
        label: string
            Label of widget
        value: string
            Default value of displayed label
        vertical: bool, optional
            Whether to enable vertical mode or not (Default is false, disabled)
        Returns
        -------
        Frame
            Created frame.
        
        """
        Widget.__init__(self,master)
        
        self.label = tk.Label(self.frame, text=label,font = "arial 9 bold")
        self.value = tk.Label(self.frame, text=value)
        
        if(vertical == False):
            self.label.grid(row=0,column=0,padx=2)
            self.value.grid(row=0,column=1,padx=1)
        else:
            self.label.grid(row=0,column=0,padx=2)
            self.value.grid(row=1,column=0,padx=1)
        
    def setvalue(self,value,roundamount=None):
        """
        Sets value of display to a string
        
        Parameters
        ----------
        value: string
            value of display
        roundAmount: int, optional
            Number of digits to round to. (Default is None, will not round)
        """
        if(roundamount != None):
            value = str(round(value,roundamount))
        self.value.config(text=value)

class AxisLine:
    """
    Small helper class to hold data for axis lines in a `Graph`.
    """
    def __init__(self):
        self.point = 0
        self.color = "r"
        self.linewidth = 1
        
    def init(self,point,color,linewidth):
        self.point = point
        self.color = color
        self.linewidth = linewidth
        
class Data2D:
    """
    Small helper class to hold two dimensional points.
    (Should probably be renamed 'Vector2D' in the future)
    """
    def __init__(self):
        self.x = []
        self.y = []
    def init(x,y):
        self.x = x
        self.y = y
