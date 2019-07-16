from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from pathlib import Path
import os
import sys
import glob


class ProgressBar(QThread):
    p_changed = pyqtSignal(int)
    p_calculate = pyqtSignal()
    finished = pyqtSignal(dict)

    
    def __init__(self, m_file_types, dir_path, file_types):
        super().__init__()
        self.m_file_types = m_file_types
        self.dir_path = dir_path
        self.file_types = file_types
        self.t_files = 0
        
    def run(self):
        print("In Thread")
        self.calculateTotal()
        self.getFileTypes()

    def categorize(self, filename):
        file = filename.split(".")
        ext = file[-1].lower()
        # self.file_types[ext] = filename 
        if self.file_types.get(ext):
            self.file_types[ext].append(filename)
        else:
            self.file_types[ext] = [filename]
        

    def calculateTotal(self):

        # self.p_calculate.emit()
        for root, dirs, files in os.walk(self.dir_path):
            self.t_files += len(files) 
            self.p_calculate.emit()

    def update(self, done):
        progress = int(round((done/float(self.t_files)) * 100))
        # print(progress)
        self.p_changed.emit(progress)


    def getFileTypes(self):
        
        self.m_file_types.clear()
        self.file_types = {}
        f_done = 0 
        for root, dirs, files in os.walk(self.dir_path):
            for f in files:
                # print(f, end=" ")
                self.categorize(f)
                f_done += 1
                self.update(f_done)
        
        self.finished.emit(self.file_types)

    


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Organizer.ui", self)
        self.setWindowTitle("My First App")
        self.appVariables()
        self.connectDropdown()
        self.goOnClick()
        self.show()
        
    def pBarInitialize(self):
        print("Progress Bar initialized")
        self.progressBar.show()
        # self.progressBar.setValue(100)
        self.progressBar.setFormat("Initializing...")

    def pBarDestroy(self, file_types):
        self.progressBar.setFormat("Done")
        self.file_types = file_types
        # print(self.file_types)
        self.addItems()

    def pBarCalculate(self):
        self.progressBar.setFormat("Calculating...")
         

    def pBarSetValue(self, value):
        # print(value)
        self.progressBar.setValue(value)
        self.progressBar.setFormat(str(value) + "%")
        
    def appVariables(self):

        self.dir_path = []
        self.file_types = {}
        self.m_file_types = QStandardItemModel()
        self.v_file_types.setModel(self.m_file_types)
        self.v_file_types.clicked.connect(self.displayTypeContents)
        self.m_contents = QStandardItemModel()
        self.v_contents.setModel(self.m_contents)
        self.progressBar.setRange(0, 100)

    def connectDropdown(self):
        if sys.platform != "linux": 
            import wmi
            c = wmi.WMI()
            for physical_disk in c.Win32_DiskDrive ():
                for partition in physical_disk.associators ("Win32_DiskDriveToDiskPartition"):
                    for logical_disk in partition.associators ("Win32_LogicalDiskToPartition"):
                        print(logical_disk.Caption)
                        self.comboBox.addItem(logical_disk.Caption)
                        self.progressBar.hide()
                        # --> It's wrong
                        # self.commandLinkButton.clicked.connect(self.goOnclick)

    def goOnClick(self):
        # self.progressBar.show()
        
        if sys.platform == "linux":
            self.base_dir = str(Path.home()) 
            for dir in os.listdir(self.base_dir):
                if not os.path.isdir(dir) and '.' not in dir:
                    self.comboBox.addItem(dir)
                    d_path = self.base_dir + "/" + dir
                    self.dir_path.append(d_path)
        
        #  print(self.dir_path)
        self.comboBox.currentIndexChanged.connect(self.display)

        # self.comboBox.activated[str].connect(self.display)
    
    def displayFileTypes(self):
        for key, val in self.file_types.items():
            print(key, val)
   

    def displayTypeContents(self, index):

        self.m_contents.clear()
        item = self.m_file_types.itemFromIndex(index)
        # print(item.text())
        key_ftype = item.text()
        # print(self.file_types.get(key_ftype))
        '''
        TODO: insert all the values of the key in the second ListView
        '''
        # self.m_contents = QStandardItemModel()
        # self.v_contents.setModel(self.m_contents)
        for value in self.file_types.get(key_ftype):
            item = QStandardItem(value)
            self.m_contents.appendRow(item)

    def addItems(self):
        for key in self.file_types.keys():
            item = QStandardItem(key)
            self.m_file_types.appendRow(item)

    def display(self, index):
        print("Selected")
        self.progress = ProgressBar(self.m_file_types,
                               self.dir_path[index],
                               self.file_types)
        self.progress.started.connect(self.pBarInitialize)
        self.progress.p_calculate.connect(self.pBarCalculate)
        self.progress.finished.connect(self.pBarDestroy)
        self.progress.p_changed.connect(self.pBarSetValue)
        self.progress.start()
        
        self.m_contents.clear()
        self.m_file_types.clear()
      



def main():
    main = QApplication(sys.argv)
    app = App()
    main.exec_()

main()
