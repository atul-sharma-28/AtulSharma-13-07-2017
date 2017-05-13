import os
import csv
import collections
import tkinter as tk
from tkinter import messagebox


scriptDir = os.path.split(os.path.abspath(__file__))[0]
datasetPath = os.path.join(scriptDir, 'students_dataset.csv')

class Cache():
    def __init__(self):
        self.listIndex = 0
        self.cacheLimit = 20
        self.cache = collections.OrderedDict()
        self.writeCache = {}
        self.datasetFilePath = datasetPath
        return

    def createCache(self):
        with open(self.datasetFilePath,'r') as csvfile:
            self.csvReader = csv.DictReader(csvfile, delimiter=',')
            self.tempList = []
            for row in self.csvReader:
                self.tempList.append({
                        'StudentID':row['StudentID'],
                        'Class1':row['Class1'],
                        'Class2':row['Class2'],
                        'Class3':row['Class3'],
                        'Marks-Class1':row['Marks-Class1'],
                        'Marks-Class2':row['Marks-Class2'],
                        'Marks-Class3':row['Marks-Class3'],
                        'Marks-Total': int(row['Marks-Class1'])+int(row['Marks-Class2'])+int(row['Marks-Class3']),
                        })
            self.tempList = sorted(self.tempList, key=lambda k: k['Marks-Total'], reverse=True)
            for studentData in self.tempList:
                if(self.listIndex<20):
                    self.setData(studentData['StudentID'],studentData)
                self.listIndex +=1
            self.tempList = None
        return
    
    def peekData(self,key):
        try:
            return self.cache.get(key)
        except KeyError:
            return -1
            
    
    def getData(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return -1

    def setData(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.cacheLimit:
                self.lastUsedItem = self.cache.popitem(last=False)
                #print(self.lastItem)
                self.addToWriteCache(self.lastUsedItem)
        self.cache[key] = value
        return

    def addToWriteCache(self, kv_tuple):
        try:
            if kv_tuple[0] in self.writeCache:
                pass
            else:
                self.writeCache[kv_tuple[0]] = kv_tuple[1]
                #print(kv_tuple[0],kv_tuple[1])
        except KeyError:
            print("Error in key")
    
    def dumpCache(self):
        for value in self.cache.items():
            #value = self.cache.popitem()
            #print(value)
            self.addToWriteCache(value)
        return
    
    def writeToFile(self):
        self.dumpCache()
        with open(self.datasetFilePath,'r') as csvfile:
            self.csvReader = csv.DictReader(csvfile, delimiter=',')
 
            self.tempList = []
            for row in self.csvReader:
                self.tempList.append({
                        'StudentID':row['StudentID'],
                        'Class1':row['Class1'],
                        'Class2':row['Class2'],
                        'Class3':row['Class3'],
                        'Marks-Class1':row['Marks-Class1'],
                        'Marks-Class2':row['Marks-Class2'],
                        'Marks-Class3':row['Marks-Class3'],
                        'Marks-Total': int(row['Marks-Class1'])+int(row['Marks-Class2'])+int(row['Marks-Class3']),
                        })
            #self.tempList = sorted(self.tempList, key=lambda k: k['Marks-Total'], reverse=True)
            for studentData in self.tempList:
                    self.addToWriteCache((studentData['StudentID'],studentData))
            self.tempList = None
            self.writeList = self.writeCache.values()
            with open(self.datasetFilePath,'w') as csvfile:
                self.fieldnames = ['StudentID', 'Class1','Class2', 'Class3','Marks-Class1', 'Marks-Class2','Marks-Class3']
                self.csvWriter = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                self.writeList = sorted(self.writeList, key=lambda k: k['StudentID'])
                self.csvWriter.writeheader()
                for row in self.writeList:
                    row = {key: value for key, value in row.items() if key != 'Marks-Total'}
                    self.csvWriter.writerow(row)
        return
    
    def deleteData(self, key):
        try:
            self.cache.pop(key)
        except KeyError:
            print("Key does not exist")
        return
    
    def keys(self):
        return self.cache.keys()

class initApp(tk.Frame):
    listIndex = 0
    cacheLimit = 20
    studentSelected = None
    studentIndex = None
    dataCache = None
    
    def __init__(self,master=None):
        super().__init__(master)
        self.pack(fill="both",expand=True)
        self.dataCache = Cache()
        self.createCache()
        self.createWidgets()
        return
    
    def createWidgets(self):
        self.listFrame = tk.Frame(self)
        self.crudFrame = tk.Frame(self)
        self.listFrame.pack(side="top", fill="y")
        self.crudFrame.pack(side="bottom", fill="y")
        self.cacheLabel = tk.Label(self.listFrame,text="Cache").pack(expand=False)
        self.lb = tk.Listbox(self.listFrame, name='lb', selectmode=tk.SINGLE)
        self.refreshList()
        self.lb.pack()
        self.lb.config(width=0,height=0)
        self.lb.bind('<<ListboxSelect>>', self.onselect)
        self.createButton = tk.Button(self.crudFrame, text="Create",
                                        command=self.createNewEntry)
        self.createButton.grid(row=0,column=0)
        self.editButton = tk.Button(self.crudFrame, text="Edit",
                                        command=self.editEntry)
        self.editButton.grid(row=0,column=2)
        self.deleteButton = tk.Button(self.crudFrame, text="Delete",
                                        command=self.deleteEntry)
        self.deleteButton.grid(row=0,column=3)
        self.readButton = tk.Button(self.crudFrame, text="Read",
                                    command=self.readEntry)
        self.readButton.grid(row=0,column=1)
        self.quit = tk.Button(self.crudFrame, text="QUIT", command=self.quitApp)
        self.quit.grid(row=1,column=1,columnspan=2)
        return
    
    def createCache(self):
        self.dataCache.createCache()
        return
    
    def refreshList(self):
        if self.lb.size() > 0:
            self.lb.delete(0,tk.END)
        for key in self.dataCache.keys():
            #print(key)
            self.lb.insert(tk.END, "%-9s\t%-9s\t%-9s\t%-9s\t%-9s\t%-9s\t%-9s"
                           %(self.dataCache.peekData(key)['StudentID'],self.dataCache.peekData(key)['Class1'],
				self.dataCache.peekData(key)['Class2'],self.dataCache.peekData(key)['Class3'],
                             	self.dataCache.peekData(key)['Marks-Class1'],self.dataCache.peekData(key)['Marks-Class2'],
				self.dataCache.peekData(key)['Marks-Class3'],))
        return
    
    def createNewEntry(self):
        self.createWindow = tk.Toplevel(self)
        self.createWindow.wm_title("Create new Entry")
        self.newStudentName = tk.Label(self.createWindow,text="Student ID:")
        self.newStudentName.grid(row=0,column=0,sticky="e")
        self.newNameEntry = tk.Entry(self.createWindow)
        self.newNameEntry.grid(row=0,column=1,columnspan=2)
        self.newClass1Name = tk.Label(self.createWindow,text="Class1:")
        self.newClass1Name.grid(row=1,column=0,sticky="e")
        self.newClass1Entry = tk.Entry(self.createWindow)
        self.newClass1Entry.grid(row=1,column=1,columnspan=2)
        self.newClass2Name = tk.Label(self.createWindow,text="Class2:")
        self.newClass2Name.grid(row=2,column=0,sticky="e")
        self.newClass2Entry = tk.Entry(self.createWindow)
        self.newClass2Entry.grid(row=2,column=1,columnspan=2)
        self.newClass3Name = tk.Label(self.createWindow,text="Class3:")
        self.newClass3Name.grid(row=3,column=0,sticky="e")
        self.newClass3Entry = tk.Entry(self.createWindow)
        self.newClass3Entry.grid(row=3,column=1,columnspan=2)
        self.newClass1MarksName = tk.Label(self.createWindow,text="Marks-Class1:")
        self.newClass1MarksName.grid(row=4,column=0,sticky="e")
        self.newClass1MarksEntry = tk.Entry(self.createWindow)
        self.newClass1MarksEntry.grid(row=4,column=1,columnspan=2)
        self.newClass2MarksName = tk.Label(self.createWindow,text="Marks-Class2:")
        self.newClass2MarksName.grid(row=5,column=0,sticky="e")
        self.newClass2MarksEntry = tk.Entry(self.createWindow)
        self.newClass2MarksEntry.grid(row=5,column=1,columnspan=2)
        self.newClass3MarksName = tk.Label(self.createWindow,text="Marks-Class3:")
        self.newClass3MarksName.grid(row=6,column=0,sticky="e")
        self.newClass3MarksEntry = tk.Entry(self.createWindow)
        self.newClass3MarksEntry.grid(row=6,column=1,columnspan=2)

        self.saveButton = tk.Button(self.createWindow,text="Save",bg="blue",
                                    command=self.saveEntry)
        self.saveButton.grid(row=7,column=1)
        self.cancelButton = tk.Button(self.createWindow,text="Cancel",
                                      command=self.createWindow.destroy)
        self.cancelButton.grid(row=7,column=2)
        return

    def readEntry(self):
        if self.studentSelected == None:
            messagebox.showwarning("Selection Warning","Please select a student from the list to read")
            return
        self.studentData = self.dataCache.getData(self.studentSelected)
        self.readWindow = tk.Toplevel(self)
        self.readWindow.wm_title("Edit Entry")
        self.studentIDLabel = tk.Label(self.readWindow,text="Student ID: %s" %self.studentData['StudentID'])
        self.studentIDLabel.grid(row=0,column=0)
        self.class1Label = tk.Label(self.readWindow,text="Class1: %s"%self.studentData['Class1'])
        self.class1Label.grid(row=1,column=0)
        self.class2Label = tk.Label(self.readWindow,text="Class2: %s"%self.studentData['Class2'])
        self.class2Label.grid(row=2,column=0)
        self.class3Label = tk.Label(self.readWindow,text="Class3: %s"%self.studentData['Class3'])
        self.class3Label.grid(row=3,column=0)
        self.class1MarksLabel = tk.Label(self.readWindow,text="Marks-Class1: %s"%self.studentData['Marks-Class1'])
        self.class1MarksLabel.grid(row=4,column=0)
        self.class2MarksLabel = tk.Label(self.readWindow,text="Marks-Class2: %s"%self.studentData['Marks-Class2'])
        self.class2MarksLabel.grid(row=5,column=0)
        self.class3MarksLabel = tk.Label(self.readWindow,text="Marks-Class3: %s"%self.studentData['Marks-Class3'])
        self.class3MarksLabel.grid(row=6,column=0)
        self.closeButton = tk.Button(self.readWindow,text="Close",
                                            command=self.closeWindow)
        self.closeButton.grid(row=7,column=2)
        return
    
    def editEntry(self):
        if self.studentSelected == None:
            messagebox.showwarning("Selection Warning","Please select a student from the list to edit")
            return
        self.studentData = self.dataCache.getData(self.studentSelected)
        self.editWindow = tk.Toplevel(self)
        self.editWindow.wm_title("Edit Entry")
        self.nameLabel = tk.Label(self.editWindow,text="Student ID:")
        self.nameLabel.grid(row=0,column=0,sticky="e")
        self.nameEdit = tk.Entry(self.editWindow)
        self.nameEdit.grid(row=0,column=1,columnspan=2)
        self.nameEdit.insert(0, self.studentData['StudentID'])
        self.class1NameLabel = tk.Label(self.editWindow,text="Class1:")
        self.class1NameLabel.grid(row=1,column=0,sticky="e")
        self.class1NameEdit = tk.Entry(self.editWindow)
        self.class1NameEdit.grid(row=1,column=1,columnspan=2)
        self.class1NameEdit.insert(0, self.studentData['Class1'])
        self.class2NameLabel = tk.Label(self.editWindow,text="Class2:")
        self.class2NameLabel.grid(row=2,column=0,sticky="e")
        self.class2NameEdit = tk.Entry(self.editWindow)
        self.class2NameEdit.grid(row=2,column=1,columnspan=2)
        self.class2NameEdit.insert(0, self.studentData['Class2'])
        self.class3NameLabel = tk.Label(self.editWindow,text="Class3:")
        self.class3NameLabel.grid(row=3,column=0,sticky="e")
        self.class3NameEdit = tk.Entry(self.editWindow)
        self.class3NameEdit.grid(row=3,column=1,columnspan=2)
        self.class3NameEdit.insert(0, self.studentData['Class3'])
        self.class1MarksLabel = tk.Label(self.editWindow,text="Marks-Class1:")
        self.class1MarksLabel.grid(row=4,column=0,sticky="e")
        self.class1MarksEdit = tk.Entry(self.editWindow)
        self.class1MarksEdit.grid(row=4,column=1,columnspan=2)
        self.class1MarksEdit.insert(0, self.studentData['Marks-Class1'])
        self.class2MarksLabel = tk.Label(self.editWindow,text="Marks-Class2:")
        self.class2MarksLabel.grid(row=5,column=0,sticky="e")
        self.class2MarksEdit = tk.Entry(self.editWindow)
        self.class2MarksEdit.grid(row=5,column=1,columnspan=2)
        self.class2MarksEdit.insert(0, self.studentData['Marks-Class2'])
        self.class3MarksLabel = tk.Label(self.editWindow,text="Marks-Class3:")
        self.class3MarksLabel.grid(row=6,column=0,sticky="e")
        self.class3MarksEdit = tk.Entry(self.editWindow)
        self.class3MarksEdit.grid(row=6,column=1,columnspan=2)
        self.class3MarksEdit.insert(0, self.studentData['Marks-Class3'])
        self.saveChangeButton = tk.Button(self.editWindow,text="Save",
                                          bg="blue", command=self.saveEdit)
        self.saveChangeButton.grid(row=7,column=1)
        self.cancelChangeButton = tk.Button(self.editWindow,text="Cancel",
                                            command=self.editWindow.destroy)
        self.cancelChangeButton.grid(row=7,column=2)
        return

    def deleteEntry(self):
        if self.studentSelected == None:
            messagebox.showwarning("Selection Warning","Please select a student from the list to delete")
            return
        self.confirmDelete = messagebox.askyesno(
            "Confirm Delete","Do you want to delete student %s's details?"%(self.dataCache.peekData(self.studentSelected)['StudentID']))
        if self.confirmDelete == True:
            self.dataCache.deleteData(self.studentSelected)
        else:
            pass
        self.refreshList()
        return
    
    def closeWindow(self):
        self.refreshList()
        self.readWindow.destroy()
        return
            
    def saveEdit(self):
        self.dataCache.deleteData(self.studentSelected)
        self.dataCache.setData(self.nameEdit.get(), {
            'StudentID':self.nameEdit.get(),
            'Class1':self.class1NameEdit.get(),
            'Class2':self.class2NameEdit.get(),
            'Class3':self.class3NameEdit.get(),
            'Marks-Class1':self.class1MarksEdit.get(),
            'Marks-Class2':self.class2MarksEdit.get(),
            'Marks-Class3':self.class3MarksEdit.get(),
            })
        self.refreshList()
        self.editWindow.destroy()
        return
    
    def saveEntry(self):
        self.newStudent = self.newNameEntry.get()
        if self.newStudent != "":
            self.dataCache.setData(self.newNameEntry.get(), {
                        'StudentID':self.newNameEntry.get(),
                        'Class1':self.newClass1Entry.get(),
                        'Class2':self.newClass2Entry.get(),
                        'Class3':self.newClass3Entry.get(),
                        'Marks-Class1':self.newClass1MarksEntry.get(),
                        'Marks-Class2':self.newClass2MarksEntry.get(),
                        'Marks-Class3':self.newClass3MarksEntry.get(),
                        })
        self.refreshList()
        self.createWindow.destroy()
        return
    
    def onselect(self,event):
        self.w = event.widget
        self.index = int(self.w.curselection()[0])
        self.value = self.w.get(self.index)
        self.studentSelected = self.value[0:7]
        #print(self.studentSelected)
        self.studentIndex = self.index
        return

    def quitApp(self):
        self.dataCache.writeToFile()
        root.destroy()
        return
        
    
if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(width=480,height=400)
    root.wm_title("Cache Sim")
    app = initApp(master=root)
    app.mainloop()

    


