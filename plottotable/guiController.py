from __future__ import division
from functools import partial
from PyQt4 import QtGui,QtCore # Import the PyQt4 module we'll need
from subprocess import call
import os  # For listing directory methods
import sys  # We need sys so that we can pass argv to QApplication
import time
import gui  # This file holds our MainWindow and all design related things
import plottotable
from generateTables import getTables, printTables
from utils import mergeOutput, clean, plotCSV

multicrop_images_dir = "multicrop-output/"
multicrop_ext_images_dir = "multicrop-ext-output/"
csv_output_dir = "csv-output/"
pdf_output_dir = "pdf-output/"

fold_path = pdf_output_dir

# it also keeps events etc that we defined in Qt Designer
index =0
list_path = []
layout_pic_area = QtGui.QVBoxLayout()
layout_pic_hold = QtGui.QVBoxLayout()
is_default_pic_displayed = 0 


class MyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__()

        self.setWindowTitle('Processing files...')
        self.resize(300, 70)
        self.openButton = QtGui.QPushButton('Start')

        self.textBrowser = QtGui.QLabel(self)
        self.textBrowser.setText("Click start to start processing")

        self.verticalLayout = QtGui.QHBoxLayout(self)
        self.verticalLayout.addWidget(self.openButton)
        self.verticalLayout.addWidget(self.textBrowser)
    
    def iteratorthis(self,fileName, form):
        self.openButton.setEnabled(False)

        empty_layouts(form)
        QtGui.qApp.processEvents()

        self.textBrowser.setText("Extracting Plot images from input PDF...")
        QtGui.qApp.processEvents()

        plottotable.process_pdf(fileName)
        
        number_of_plots = 0
        for ff in sorted(os.listdir(multicrop_images_dir)):
            if  ff.endswith('.ppm'):
                number_of_plots += 1 

        if number_of_plots == 0:
            self.close()
            showdialog("No plots found in Input PDF")
        else:
            self.textBrowser.setText(str(number_of_plots) + " Plots extracted")
            QtGui.qApp.processEvents()

            file_number = 1

            error = 0
            for f in sorted(os.listdir(multicrop_images_dir)):
                error = 0
                # Processing image
                error = getTables(f)

                if not error == -1:
                    # converting all PDF outputs to PNG
                    convert_pdfs_to_png(f)

                    # Showing all image thumbnails in left pane
                    showimage_thumbnails(form,layout_pic_area, f)
                
                self.textBrowser.setText("Processed " + str(file_number) + " of " + str(number_of_plots))
                QtGui.qApp.processEvents()

            if error == -1:
                showdialog("Could not generate data for some of the extracted plots")
                QtGui.qApp.processEvents()

            self.close()


class QLabel_new(QtGui.QLabel):
    def __init__(self, parent = None):
        QtGui.QLabel.__init__(self, parent)
    def mousePressEvent(self, ev):
        highlight_handler()
        self.setFrameStyle(QtGui.QFrame.Panel)
        self.setLineWidth(5)
        self.emit(QtCore.SIGNAL('clicked()'))


class ClickHandler():
    def __init__(self, time):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(time)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)
        self.click_count = 0

    def timeout(self):
        if self.click_count == 1:
            # print('Single click')
            self.emit(QtCore.SIGNAL('clicked()'))
        elif self.click_count > 1:
            print('Double click')    
        self.click_count = 0

    def __call__(self):
        self.click_count += 1
        if not self.timer.isActive():
            self.timer.start()


class ExampleApp(QtGui.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        self.showMaximized()
        self.setWindowTitle('plot2table')

    


    def browse_folder(self):
        self.listWidget.clear() # In case there are any existing elements in the list
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Pick a folder")
        # execute getExistingDirectory dialog and set the directory variable to be equal
        # to the user selected directory

        if directory: # if user didn't pick a directory don't continue
            for file_name in os.listdir(directory): # for all files, if any, in the directory
                self.listWidget.addItem(file_name)  # add file to the listWidget

    def add_pic_to_display(self,event,name,checked = False):
        global layout_pic_hold
        disp_contents = QtGui.QWidget(self.pic_hold)
        layout = QtGui.QVBoxLayout(disp_contents)
        layout_pic_hold = layout
        self.pic_hold.setWidget(disp_contents)

        name = (name.split('.'))[0]
        path = fold_path + name
        print "reached "+path
        for ff in sorted(os.listdir(path)):
            if  ff.endswith('.jpeg') or ff.endswith('.png'): 
                label = QtGui.QLabel()
                pixmap = QtGui.QPixmap(path+'/'+ff)
                # pixmap = pixmap.scaledToWidth(self.pic_hold.frameGeometry().width(),self.pic_hold.frameGeometry().height(),QtCore.Qt.KeepAspectRatio, transformMode = QtCore.Qt.SmoothTransformation)
                pixmap = pixmap.scaledToWidth(self.pic_hold.frameGeometry().width()-150,  QtCore.Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                label.setAlignment(QtCore.Qt.AlignCenter)
                layout.addWidget(label)

    def actOpen(self,form,layout):
        # opening file chooser
        try:
            path = plottotable.__file__[:-12]
            path += "test-inputs/"

            fileName = QtGui.QFileDialog.getOpenFileName(self,
                    "Choose Input File", path,
                    "All Files (*.pdf)")
        except Exception,e:
            print str(e)

            fileName = QtGui.QFileDialog.getOpenFileName(self,
                    "Choose Input File", '',
                    "All Files (*.pdf)")

        if not len(fileName) == 0:
            global index
            index= 0
            global list_path
            list_path = []
            global is_default_pic_displayed
            is_default_pic_displayed = 0

            dialogTextBrowser = MyDialog(self)

            # Creating dialog for image processing
            dialogTextBrowser.connect(dialogTextBrowser.openButton, QtCore.SIGNAL('clicked()'), partial(dialogTextBrowser.iteratorthis,fileName, form))  
            dialogTextBrowser.exec_()
            

    def actPrint(self,form,layout):

        selected_images = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if type(widget) is QtGui.QCheckBox:
                    if widget.isChecked():
                        print "--"+str(int(i/2)+1)+" checked --\n"
                        print list_path[(int(i/2))]+"\n"
                        selected_images.append(list_path[int(i/2)])

        if len(list_path) == 0:
            showdialog("Please upload Input PDF first")
        else:
            if len(selected_images) == 0:
                showdialog("Please select at least one image")
            else:
                mergeOutput(selected_images, "./print.pdf")

                dialog = QtGui.QPrintDialog()
                if dialog.exec_() == QtGui.QDialog.Accepted:
                    self.editor.document().print_(dialog.printer())

def empty_layouts(form):
    global layout_pic_hold
    global layout_pic_area

    layout = layout_pic_area
    clearLayout(layout)   
    layout = layout_pic_hold
    clearLayout(layout)

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())            

def convert_pdfs_to_png(_file):
    # for subdir, dirs, files in os.walk(fold_path):
    #     for _file in files:
    #         if _file.endswith('.pdf'):
    name = _file.split('.')[0]
    pdf_file = name + ".pdf"
    os.mkdir(fold_path + name)
    call(["pdftoppm","-png","-r","300",fold_path+pdf_file, fold_path+name+'/new'])

def showimage_thumbnails(form,layout, _file):

    jpeg_file = _file.split('.')[0] + ".jpeg"
    print fold_path + jpeg_file

    add_pic_to_thumbnails(form, jpeg_file, layout) 

def add_pic_to_thumbnails(form, name, layout):
    global index
    global list_path
    global is_default_pic_displayed
    index = index +1
    label = QLabel_new()
    path = fold_path + name
    pixmap = QtGui.QPixmap(path)
    list_path.append(name)
    form.connect(label, QtCore.SIGNAL('clicked()'), partial(form.add_pic_to_display,form,name))  
    pixmap = pixmap.scaledToWidth(form.pic_area.frameGeometry().width()-40,  QtCore.Qt.SmoothTransformation)
    label.setPixmap(pixmap)
    layout.addWidget(label)

    box = QtGui.QCheckBox()
    box.setText('                        '+str(index))
    layout.addWidget(box)
    if(is_default_pic_displayed==0) :
        label.emit(QtCore.SIGNAL('clicked()'))
        label.setFrameStyle(QtGui.QFrame.Panel)
        label.setLineWidth(5)
        is_default_pic_displayed = 1

def selected_pdfs(form,layout):
    global index

    selected_images = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is not None:
            widget = item.widget()
            if type(widget) is QtGui.QCheckBox:
                if widget.isChecked():
                    print "--"+str(int(i/2)+1)+" checked --\n"
                    print list_path[(int(i/2))]+"\n"
                    selected_images.append(list_path[int(i/2)])

    if len(list_path) == 0:
        showdialog("Please upload Input PDF first")
    else:
        if len(selected_images) == 0:
            showdialog("Please select at least one image.")
        else:
            fileName = QtGui.QFileDialog.getSaveFileName(form,
                "Choose Path and File name", '',
                "All Files (*.pdf)")

            mergeOutput(selected_images, fileName)

def plot_data(form,layout):
    global index

    selected_images = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is not None:
            widget = item.widget()
            if type(widget) is QtGui.QCheckBox:
                if widget.isChecked():
                    print "--"+str(int(i/2)+1)+" checked --\n"
                    print list_path[(int(i/2))]+"\n"
                    selected_images.append(list_path[int(i/2)])

    if len(list_path) == 0:
        showdialog("Please upload Input PDF first")
    else:
        if len(selected_images) == 0:
            showdialog("Please select at least one image.")
        else:
            for img in selected_images:
                plotCSV(img)

def pdf_help(form):
    disp_contents = QtGui.QWidget(form.pic_hold)
    layout = QtGui.QVBoxLayout(disp_contents)
    layout_pic_hold = layout
    form.pic_hold.setWidget(disp_contents)
    path = plottotable.__file__[:-12]
    path += "user-manual/"
    for ff in sorted(os.listdir(path)):
        if  ff.endswith('.jpeg') or ff.endswith('.png'): 
            label = QtGui.QLabel()
            pixmap = QtGui.QPixmap(path+'/'+ff)
            # pixmap = pixmap.scaledToWidth(form.pic_hold.frameGeometry().width(),form.pic_hold.frameGeometry().height(),QtCore.Qt.KeepAspectRatio, transformMode = QtCore.Qt.SmoothTransformation)
            pixmap = pixmap.scaledToWidth(form.pic_hold.frameGeometry().width()-150,  QtCore.Qt.SmoothTransformation)
            label.setPixmap(pixmap)
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)

def showdialog(text):
   msg = QtGui.QMessageBox()
   msg.setIcon(QtGui.QMessageBox.Warning)
   msg.setText(text)
   msg.setWindowTitle("Note")
   msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
   msg.exec_()

def highlight_handler():
    layout  = layout_pic_area
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is not None:
            widget = item.widget()
            if type(widget) is QLabel_new:
                widget.setFrameStyle(QtGui.QFrame.NoFrame)

def main():
    global layout_pic_area
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)

    form.pic_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    scrollContents = QtGui.QWidget()
    layout = QtGui.QVBoxLayout(scrollContents)
    layout_pic_area = layout
    form.pic_area.setWidget(scrollContents)
    layout.setAlignment(QtCore.Qt.AlignTop)

    p = scrollContents.palette()
    p.setColor(scrollContents.backgroundRole(), QtCore.Qt.white)
    scrollContents.setPalette(p)

    q = form.widget_4.palette()
    q.setColor(form.widget_4.backgroundRole(), QtCore.Qt.red)
    form.widget_4.setPalette(q)
    
    # Utility panel and File buttons
    try:
        form.open_btn.clicked.connect(partial(form.actOpen,form,layout))
        form.connect(form.actionOpen, QtCore.SIGNAL('triggered()'), partial(form.actOpen,form,layout)) 
    except Exception,e:
        print str(e)
        showdialog("Could not Open Input PDF")
        
    try:
        form.save_btn.clicked.connect(partial(selected_pdfs,form,layout))
        form.connect(form.actionPlot, QtCore.SIGNAL('triggered()'), partial(plot_data,form,layout)) 
    except Exception,e:
        print str(e)
        showdialog("Could not Save selected files")

    try:
        form.plot_btn.clicked.connect(partial(plot_data,form,layout))
        form.connect(form.actionSave, QtCore.SIGNAL('triggered()'), partial(selected_pdfs,form,layout))  
    except Exception,e:
        print str(e)
        showdialog("Could not Plot selected files")

    try:
        form.print_btn.clicked.connect(partial(form.actPrint,form,layout))
        form.connect(form.actionPrint, QtCore.SIGNAL('triggered()'), partial(form.actPrint,form,layout))
    except Exception,e:
        print str(e)
        showdialog("Could not Print selected files")

    # Help buttons
    try:
        form.connect(form.actionusermanual, QtCore.SIGNAL('triggered()'), partial(pdf_help,form))
    except Exception,e:
        print str(e)
        showdialog("Could not load User Manual")

    form.show()  # Show the form

    _exit = app.exec_()  # and execute the app

    # Exit code
    clean()

    sys.exit(_exit)