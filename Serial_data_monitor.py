import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox,filedialog
import pandas as pd
import os
import serial
from serial.tools import list_ports
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import time

class App:
    def __init__(self):      
        #CREATE ROOT WINDOW
        self.root=tk.Tk()
        self.root.title("SERIAL DATA MONITOR")
        self.root.iconbitmap("Images/logo256x256_transparent.ico")
        self.root.resizable(0,0)
        screen_width=self.root.winfo_screenwidth()
        screen_height=self.root.winfo_screenheight()
        self.width=900
        self.height=800
        x=int((screen_width/2)-(self.width/1.8))
        y=int((screen_height/2)-(self.height/1.8))
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.root.protocol("WM_DELETE_WINDOW",self.close_app)

        #LOAD IMAGES
        self.img_title=tk.PhotoImage(file="Images/title.png")
        self.img_refresh=tk.PhotoImage(file="Images/refresh16x16.png")
        self.img_clear=tk.PhotoImage(file="Images/clear32x32.png")
        self.img_export=tk.PhotoImage(file="Images/export32x32.png")
        self.img_stop=tk.PhotoImage(file="Images/stop50x50.png")
        self.img_record=tk.PhotoImage(file="Images/record50x50.png")
        self.img_info=tk.PhotoImage(file="Images/info32x32.png")

        #TTK WIDGETS STYLES
        style=ttk.Style()
        style.configure("TMenubutton",background='#d4d3d2',font=('arial',12))  #style for ttk.OptionMenu widget
        style.configure("Treeview",font=('arial',12))

        #"TITLE" SECTION
        title_frame=tk.Frame(self.root,relief='groove',borderwidth=3)
        title_frame.grid(row=0,column=0,columnspan=2,sticky="nsew")
        self.root.rowconfigure(0,weight=70)
        self.root.columnconfigure(0,weight=1)

        title_label=ttk.Label(title_frame,image=self.img_title)
        title_label.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

        #MESSAGE SECTION
        message_frame=tk.Frame(self.root,relief='groove',borderwidth=3)
        message_frame.grid(row=1,column=0,sticky="nsew")
        self.root.rowconfigure(1,weight=100)
        self.root.columnconfigure(0,weight=1)
        self.message_label=ttk.Label(message_frame,text="SET COM PORTS, BAUDRATE AND LOG INTERVAL",font=('arial',10,'bold'))
        self.message_label.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

        #"MENU" SECTION
        menu_frame=tk.LabelFrame(self.root,relief='groove',borderwidth=3)
        menu_frame.grid(row=2,column=0,sticky="nsew")
        self.root.rowconfigure(2,weight=220)
        self.root.columnconfigure(0,weight=1)

        self.COMports=list_ports.comports()
        self.COMports_list=[]
        for port in self.COMports:
            self.COMports_list.append(port.device) #return available COM ports list
        self.COMport=tk.StringVar()
        self.COMports_optionmenu=ttk.OptionMenu(menu_frame,self.COMport,"COM ports",*self.COMports_list,command=self.connection_readiness)
        self.COMports_optionmenu.config(width=10)
        self.COMports_optionmenu.place(relx=0.21,rely=0.17,anchor=tk.CENTER)

        self.baudrate_list=[4800,9600,19200,38400,57600,115200,230400,460800,500000,576000]
        self.baudrate=tk.StringVar()
        self.baudrate_optionmenu=ttk.OptionMenu(menu_frame,self.baudrate,"Baudrate",*self.baudrate_list,command=self.connection_readiness)
        self.baudrate_optionmenu.config(width=10)
        self.baudrate_optionmenu.place(relx=0.21,rely=0.45,anchor=tk.CENTER)

        interval_frame=tk.LabelFrame(menu_frame,font=('arial',9),width=self.width*2.7/12,height=self.height*1.2/10,text="LOG INTERVAL",relief='groove',borderwidth=2,labelanchor='n')
        interval_frame.place(relx=0.72,rely=0.3,anchor=tk.CENTER)
        self.interval=tk.IntVar()
        self.interval_scale=tk.Scale(interval_frame,font=('arial',11),length=160,from_=0,to=60,orient=tk.HORIZONTAL,troughcolor='#d4d3d2',variable=self.interval,command=self.connection_readiness)
        self.interval_scale.place(relx=0.5,rely=0.3,anchor=tk.CENTER)
        self.intervalunit=tk.IntVar()
        self.intervalunitSEC_radiobutton=ttk.Radiobutton(interval_frame,text="sec",value=0,variable=self.intervalunit)
        self.intervalunitSEC_radiobutton.place(relx=0.32,rely=0.8,anchor=tk.CENTER)
        self.intervalunitMIN_radiobutton=ttk.Radiobutton(interval_frame,text="min",value=1,variable=self.intervalunit)
        self.intervalunitMIN_radiobutton.place(relx=0.7,rely=0.8,anchor=tk.CENTER)

        self.refresh_button=ttk.Button(menu_frame,image=self.img_refresh,command=self.refresh)
        self.refresh_button.place(relx=0.4,rely=0.17,anchor=tk.CENTER)

        self.info_button=ttk.Button(menu_frame,image=self.img_info,comman=self.info)
        self.info_button.place(relx=0.12,rely=0.8,anchor=tk.CENTER)
        
        self.clear_button=ttk.Button(menu_frame,image=self.img_clear,state=tk.DISABLED,command=self.clear)
        self.clear_button.place(relx=0.24,rely=0.8,anchor=tk.CENTER)

        self.export_button=ttk.Button(menu_frame,image=self.img_export,state=tk.DISABLED,command=self.export)
        self.export_button.place(relx=0.36,rely=0.8,anchor=tk.CENTER)

        self.stop_button=ttk.Button(menu_frame,image=self.img_stop,state=tk.DISABLED,command=self.stop)
        self.stop_button.place(relx=0.62,rely=0.8,anchor=tk.CENTER)
        
        self.record_button=ttk.Button(menu_frame,image=self.img_record,state=tk.DISABLED,command=self.record)
        self.record_button.place(relx=0.82,rely=0.8,anchor=tk.CENTER)

        #"DISPLAY" SECTION
        display_frame=tk.LabelFrame(self.root,relief='groove',borderwidth=3)
        display_frame.grid(row=3,column=0,sticky="nsew")
        self.root.rowconfigure(3,weight=120)
        self.root.columnconfigure(0,weight=1)

        time_frame=tk.LabelFrame(display_frame,text="TIME",labelanchor='n',relief='groove',borderwidth=2)
        time_frame.grid(row=0,column=0,sticky="nsew")
        display_frame.rowconfigure(0,weight=1)
        display_frame.columnconfigure(0,weight=3)

        timecur_frame=tk.Frame(time_frame,relief='groove',borderwidth=2)
        timecur_frame.grid(row=0,column=0,sticky="nsew")
        time_frame.rowconfigure(0,weight=1)
        time_frame.columnconfigure(0,weight=1)
        self.timecur_label=ttk.Label(timecur_frame,text="--:--:--",font=('arial',18,'bold'))
        self.timecur_label.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

        timeelap_frame=tk.LabelFrame(time_frame,text="ELAPSED TIME",labelanchor='n',relief='groove',borderwidth=2)
        timeelap_frame.grid(row=1,column=0,sticky="nsew")
        time_frame.rowconfigure(1,weight=1)
        time_frame.columnconfigure(0,weight=1)
        self.timeelap_label=ttk.Label(timeelap_frame,text="--:--:--",font=('arial',11))
        self.timeelap_label.place(relx=0.5,rely=0.5,anchor=tk.CENTER)
 
        ds1_frame=tk.LabelFrame(display_frame,text="DS1",labelanchor='n',relief='groove',borderwidth=2)
        ds1_frame.grid(row=0,column=1,sticky="nsew")
        display_frame.rowconfigure(0,weight=1)
        display_frame.columnconfigure(1,weight=7)

        ds1cur_frame=tk.Frame(ds1_frame,relief='groove',borderwidth=2)
        ds1cur_frame.grid(row=0,column=0,columnspan=3,sticky="nsew")
        ds1_frame.rowconfigure(0,weight=1)
        ds1_frame.columnconfigure(0,weight=1)
        self.ds1cur_label=ttk.Label(ds1cur_frame,text="----",font=('arial',18,'bold'))
        self.ds1cur_label.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

        ds1min_frame=tk.LabelFrame(ds1_frame,text="MIN",labelanchor='n',relief='groove',borderwidth=2)
        ds1min_frame.grid(row=1,column=0,sticky="nsew")
        ds1_frame.rowconfigure(1,weight=1)
        ds1_frame.columnconfigure(0,weight=1)
        self.ds1min_label=ttk.Label(ds1min_frame,text="----",font=('arial',11))
        self.ds1min_label.place(relx=0.48,rely=0.5,anchor=tk.CENTER)

        ds1avg_frame=tk.LabelFrame(ds1_frame,text="AVG",labelanchor='n',relief='groove',borderwidth=2)
        ds1avg_frame.grid(row=1,column=1,sticky="nsew")
        ds1_frame.rowconfigure(1,weight=1)
        ds1_frame.columnconfigure(1,weight=1)
        self.ds1avg_label=ttk.Label(ds1avg_frame,text="----",font=('arial',11))
        self.ds1avg_label.place(relx=0.48,rely=0.5,anchor=tk.CENTER)

        ds1max_frame=tk.LabelFrame(ds1_frame,text="MAX",labelanchor='n',relief='groove',borderwidth=2)
        ds1max_frame.grid(row=1,column=2,sticky="nsew")
        ds1_frame.rowconfigure(1,weight=1)
        ds1_frame.columnconfigure(2,weight=1)
        self.ds1max_label=ttk.Label(ds1max_frame,text="----",font=('arial',11))
        self.ds1max_label.place(relx=0.48,rely=0.5,anchor=tk.CENTER)
        
        ds2_frame=tk.LabelFrame(display_frame,text="DS2",labelanchor='n',relief='groove',borderwidth=2)
        ds2_frame.grid(row=0,column=2,sticky="nsew")
        display_frame.rowconfigure(0,weight=1)
        display_frame.columnconfigure(2,weight=7)

        ds2cur_frame=tk.Frame(ds2_frame,relief='groove',borderwidth=2)
        ds2cur_frame.grid(row=0,column=0,columnspan=3,sticky="nsew")
        ds2_frame.rowconfigure(0,weight=1)
        ds2_frame.columnconfigure(0,weight=1)
        self.ds2cur_label=ttk.Label(ds2cur_frame,text="----",font=('arial',18,'bold'))
        self.ds2cur_label.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

        ds2min_frame=tk.LabelFrame(ds2_frame,text="MIN",labelanchor='n',relief='groove',borderwidth=2)
        ds2min_frame.grid(row=1,column=0,sticky="nsew")
        ds2_frame.rowconfigure(1,weight=1)
        ds2_frame.columnconfigure(0,weight=1)
        self.ds2min_label=ttk.Label(ds2min_frame,text="----",font=('arial',11))
        self.ds2min_label.place(relx=0.48,rely=0.5,anchor=tk.CENTER)

        ds2avg_frame=tk.LabelFrame(ds2_frame,text="AVG",labelanchor='n',relief='groove',borderwidth=2)
        ds2avg_frame.grid(row=1,column=1,sticky="nsew")
        ds2_frame.rowconfigure(1,weight=1)
        ds2_frame.columnconfigure(1,weight=1)
        self.ds2avg_label=ttk.Label(ds2avg_frame,text="----",font=('arial',11))
        self.ds2avg_label.place(relx=0.48,rely=0.5,anchor=tk.CENTER)
    
        ds2max_frame=tk.LabelFrame(ds2_frame,text="MAX",labelanchor='n',relief='groove',borderwidth=2)
        ds2max_frame.grid(row=1,column=2,sticky="nsew")
        ds2_frame.rowconfigure(1,weight=1)
        ds2_frame.columnconfigure(2,weight=1)
        self.ds2max_label=ttk.Label(ds2max_frame,text="----",font=('arial',11))
        self.ds2max_label.place(relx=0.48,rely=0.5,anchor=tk.CENTER)
        
        #"TREEVIEW" SECTION
        treeview_frame=tk.LabelFrame(self.root,width=400,relief='groove',borderwidth=3)
        treeview_frame.grid(row=1,column=1,rowspan=3,sticky="nsew")
        treeview_frame.propagate(0)
        self.root.rowconfigure(1,weight=40)

        self.columns=("No","Time","DS1","DS2")
        scrollbary = tk.Scrollbar(treeview_frame,orient=tk.VERTICAL)
        self.tree=ttk.Treeview(treeview_frame,columns=self.columns,yscrollcommand=scrollbary.set)
        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=tk.RIGHT, fill=tk.Y)
        for col in self.columns:
            self.tree.heading(col,text=col)
        self.tree.column('#0',stretch=tk.NO,minwidth=0,width=0)
        self.tree.column('#1',width=35,anchor=tk.CENTER)
        self.tree.column('#2',width=100,anchor=tk.CENTER)
        self.tree.column('#3',width=100,anchor=tk.CENTER)
        self.tree.column('#4',width=100,anchor=tk.CENTER)
        self.tree.pack(fill='both',expand=True)

        #"PLOT" SECTION 
        self.plot_frame=tk.LabelFrame(self.root,relief='groove',borderwidth=3)
        self.plot_frame.grid(row=4,column=0,columnspan=2,sticky="nsew")
        
        self.fig=plt.figure(figsize=(9,4),dpi=100,facecolor='#ededeb')
        self.fig.subplots_adjust(top=0.92,right=0.92,left=0.08,bottom=0.08)
        
        self.ax=self.fig.add_subplot(1,1,1,facecolor='white')
        self.ax.grid()

        self.ax2=self.ax.twinx()
        self.ax2.tick_params(right=False, labelright=False)
        self.ax2.spines['right'].set_color("black")

        self.canvas=FigureCanvasTkAgg(self.fig,self.plot_frame)
        self.canvas.get_tk_widget().pack()

        self.toolbar=NavigationToolbar2Tk(self.canvas,self.plot_frame,pack_toolbar=False) 

        self.ax2_status=tk.IntVar()
        self.ax2_checkbox=tk.Checkbutton(self.plot_frame,variable=self.ax2_status,text="Second axe",font=("Arial",9),state=tk.DISABLED)
        self.ax2_checkbox.place(relx=0.01,rely=0)

        self.ax1_color="black"
        self.ax2_color="blue"
                 
        #FLAG VARIABLES
        self.data={self.columns[0]:[],self.columns[1]:[],self.columns[2]:[],self.columns[3]:[]}
        self.data_point=0
        self.stop_status=0
        self.stop_time=0
        self.start_time=0
        self.current_time=""
        self.elapsed_time=0
        self.ser=serial.Serial()
        self.serial_data=""
        self.serial_data_list=[]

    def info(self):
        information="""
App that allows user to monitor in real-time data sent through the serial port and export them to a file.
              
Before run the program set the correct COM port, baudrate and log interval.
                             
Important!
Each data point sent to the program must be placed in new line (separated by a newline character)

App allows to monitor max. 2 datasets (DS) at the same time - in that case they have to be separated by a comma.

Example of correct data frame sended to app:
1) One dataset: "DS1\\nDS1\\nDS1..."
2) Two datasets: "DS1,DS2\\nDS1,DS2\\nDS1,DS2..."

"""
        messagebox.showinfo(title="Information",message=information)        
        
    def refresh(self):
        self.COMports=list_ports.comports()
        self.COMports_list=[]
        for port in self.COMports:
            self.COMports_list.append(port.device) #return available COM ports list
        self.COMports_optionmenu.set_menu("COM ports",*self.COMports_list)

        self.message_label['text']="COM PORTS HAS BEEN REFRESHED"
   
    def export(self):
        try:
            export_filedialog=filedialog.asksaveasfilename(initialdir=os.getcwd(),title="Export to CSV",defaultextension=".csv",filetypes=(("CSV files","*.csv"),("All files","*.*")))

            df=pd.DataFrame(self.data)
            df.to_csv(export_filedialog,index=False)

            self.message_label['text']="DATA HAS BEEN EXPORTED"
        except:
            pass
        
    def clear(self):
        #Add warning message box with 'yes'-'no' question
        warning=messagebox.askquestion("Warning","Are you sure you want to clear a data?", icon='warning')
        
        if warning=="yes":
            #Reset variables
            self.data={self.columns[0]:[],self.columns[1]:[],self.columns[2]:[],self.columns[3]:[]}
            self.data_point=0
            self.stop_time=0
            self.start_time=0
            self.elapsed_time=0

            #Clear display labels
            self.timecur_label['text']="--:--:--"
            self.timeelap_label['text']="--:--:--"        

            self.ds1cur_label['text']="----"
            self.ds1min_label['text']="----"
            self.ds1avg_label['text']="----"
            self.ds1max_label['text']="----"   

            self.ds2cur_label['text']="----"
            self.ds2min_label['text']="----"
            self.ds2avg_label['text']="----"
            self.ds2max_label['text']="----"

            #Clear treeview
            self.tree.delete(*self.tree.get_children())

            #Remove plot
            self.ax.cla()
            self.ax2.cla()
            self.ax.grid()
            self.ax2.tick_params(colors='black')
            self.ax2.spines['right'].set_color('black')
            self.fig.canvas.draw()
            
            #Hide graph toolbar section
            self.toolbar.pack_forget()
            self.root.geometry(f"{self.width}x{self.height}")

            #Change button status
            self.clear_button['state']=tk.DISABLED
            self.export_button['state']=tk.DISABLED
            
            #Update message status
            self.message_label['text']="DATA HAS BEEN REMOVED"

    def stop(self):
        self.stop_status=1
        self.ser.close()
        
        #Change widgets status 
        self.record_button['state']=tk.ACTIVE
        self.stop_button['state']=tk.DISABLED
        self.interval_scale['state']=tk.ACTIVE
        self.intervalunitSEC_radiobutton['state']=tk.ACTIVE
        self.intervalunitMIN_radiobutton['state']=tk.ACTIVE
        self.COMports_optionmenu['state']=tk.ACTIVE
        self.baudrate_optionmenu['state']=tk.ACTIVE
        self.refresh_button['state']=tk.ACTIVE
        self.clear_button['state']=tk.ACTIVE
        self.export_button['state']=tk.ACTIVE
        self.ax2_checkbox['state']=tk.DISABLED
        
        #Expand graph toolbar section
        self.root.geometry(f"{self.width}x{self.height+42}")
        self.toolbar.update()
        self.toolbar.pack(fill=tk.X)

        #Update message status
        self.message_label['text']="STOP DATA LOGGING"
       
    def connection_readiness(self,arg):
        #Method responsible for checking if all settings has been selected
        if "COM ports" in self.COMport.get() or self.interval.get()==0 or "Baudrate" in self.baudrate.get():
            self.record_button['state']=tk.DISABLED
        else:
            self.record_button['state']=tk.ACTIVE

    def stream_data(self):
        self.final_interval=self.interval.get()
        if self.intervalunit.get()==1: #interval time in min
            self.final_interval=self.interval.get()*60 #conversion to sec
        
        try:            
            self.ser=serial.Serial(port=self.COMport.get(),baudrate=self.baudrate.get(),timeout=self.final_interval*0.75) #open serial port
            if self.stop_time==0:
                self.start_time=time.time() #return elapsed time in sec from epoch to the start of streaming
            if self.stop_status==1:
                self.stop_time=time.time()-self.elapsed_time-self.start_time #return elapsed time during pause
            self.ser.reset_input_buffer() #erase data in input buffer
            self.message_label.config(foreground="black")
            self.stop_status=0     
        except:
            self.stop_status=1 

            #Change widgets status
            self.record_button['state']=tk.ACTIVE
            self.stop_button['state']=tk.DISABLED
            self.interval_scale['state']=tk.ACTIVE
            self.intervalunitSEC_radiobutton['state']=tk.ACTIVE
            self.intervalunitMIN_radiobutton['state']=tk.ACTIVE
            self.COMports_optionmenu['state']=tk.ACTIVE
            self.baudrate_optionmenu['state']=tk.ACTIVE
            self.refresh_button['state']=tk.ACTIVE

            #Update message status
            self.message_label['text']="CONNECTION NOT FOUND" 
            self.message_label.config(foreground="red")        
       
        while self.stop_status==0:
            self.current_time=time.strftime('%H:%M:%S',time.localtime()) #format current time                
            self.elapsed_time=time.time()-self.start_time-self.stop_time #return elapsed time of streaming
            try:
                if self.ser.inWaiting(): #check data in buffer
                    buffer_byte=self.ser.read(self.ser.inWaiting()) #getting byte data from buffer
                    self.data_point+=1 #'No' counter
                    
                    if b'\n' in buffer_byte:
                        buffer_list=buffer_byte.split(b"\n") #split buffer data by newline character
                        buffer_latest=buffer_list[-2] #getting latest data
                        
                        self.serial_data=buffer_latest.decode("utf-8").rstrip("\n\r") #decode latest buffer data

                    #Update dictionary data base
                    self.data[self.columns[0]].append(self.data_point) #add 'No' to dict data base
                    self.data[self.columns[1]].append(self.current_time) #add 'Time' to dict data base
                    if "," in self.serial_data:
                        self.serial_data_list=self.serial_data.split(",") #split buffer data by a comma
                        self.data[self.columns[2]].append(float(self.serial_data_list[0])) #add 'DS1' to dict data base
                        self.data[self.columns[3]].append(float(self.serial_data_list[1])) #add 'DS2' to dict data base
                    else:
                        self.data[self.columns[2]].append(float(self.serial_data)) #add 'DS1' to dict data base

                    self.update_display()
                    self.update_treeview()
                    self.update_plot()

                    self.message_label['text']="MONITORING IN PROGRESS" #update message status
            except:
                self.ser.reset_input_buffer()

                self.message_label['text']="WAITING FOR DATA..." #update message status

                #Reset variables
                self.data={self.columns[0]:[],self.columns[1]:[],self.columns[2]:[],self.columns[3]:[]}
                self.data_point=0 
                self.elapsed_time-=self.final_interval

            time.sleep(self.final_interval) #add delay

    def update_display(self):
        self.timecur_label['text']=self.current_time
        self.timeelap_label['text']=time.strftime('%H:%M:%S',time.gmtime(self.elapsed_time))
                        
        if "," in self.serial_data:
            self.ds1cur_label['text']=self.serial_data_list[0]
            
            self.ds2cur_label['text']=self.serial_data_list[1]
            min_ds2=str(round(min(self.data[self.columns[3]]),2))
            self.ds2min_label['text']=min_ds2
            avg_ds2=str(round(sum(self.data[self.columns[3]])/len(self.data[self.columns[3]]),2))
            self.ds2avg_label['text']=avg_ds2
            max_ds2=str(round(max(self.data[self.columns[3]]),2))
            self.ds2max_label['text']=max_ds2
        else:
            self.ds1cur_label['text']=self.serial_data

        min_ds1=str(round(min(self.data[self.columns[2]]),2))
        self.ds1min_label['text']=min_ds1
        avg_ds1=str(round(sum(self.data[self.columns[2]])/len(self.data[self.columns[2]]),2))
        self.ds1avg_label['text']=avg_ds1
        max_ds1=str(round(max(self.data[self.columns[2]]),2))
        self.ds1max_label['text']=max_ds1

    def update_treeview(self):
        if "," in self.serial_data:
            self.tree.insert('',0,values=(self.data_point,self.current_time,self.serial_data_list[0],self.serial_data_list[1]))
        else:
            self.tree.insert('',0,values=(self.data_point,self.current_time,self.serial_data))

    def update_plot(self):
        x_arg=self.data[self.columns[0]]
        y1_arg=self.data[self.columns[2]]
        self.ax.clear()
        self.ax.grid()
        self.ax.margins(x=0)
        
        if "," in self.serial_data:
            self.ax2_checkbox['state']=tk.ACTIVE
            y2_arg=self.data[self.columns[3]]
            if self.ax2_status.get()==0:
                self.ax2.tick_params(right=False, labelright=False)
                self.ax2.spines['right'].set_color("black")
                self.ax2.cla()
                self.ax.plot(x_arg,y1_arg,label="DS1",color=self.ax1_color)
                self.ax.plot(x_arg,y2_arg,label="DS2",color=self.ax2_color)
                self.ax.legend(bbox_to_anchor=(0.6,1.1),ncol=2,frameon=False)
            else:
                self.ax.plot(x_arg,y1_arg,label="DS1",color=self.ax1_color)
                self.ax2.clear()
                self.ax2.plot(x_arg,y2_arg,label="DS2",color=self.ax2_color)
                self.ax2.margins(x=0)
                self.ax2.tick_params(colors=self.ax2_color,right=True, labelright=True)
                self.ax2.spines['right'].set_color(self.ax2_color)
                self.ax.legend(bbox_to_anchor=(0.473,1.1),frameon=False)
                self.ax2.legend(bbox_to_anchor=(0.6,1.1),frameon=False)
            
        else:
            self.ax2_checkbox['state']=tk.DISABLED
            self.ax.plot(x_arg,y1_arg,label="DS1",color=self.ax1_color)
            self.ax.legend(bbox_to_anchor=(0.55,1.1),frameon=False)
            
        self.fig.canvas.draw()

    def record(self):
        #Change widgets status 
        self.record_button['state']=tk.DISABLED
        self.stop_button['state']=tk.ACTIVE
        self.interval_scale['state']=tk.DISABLED
        self.intervalunitSEC_radiobutton['state']=tk.DISABLED
        self.intervalunitMIN_radiobutton['state']=tk.DISABLED
        self.COMports_optionmenu['state']=tk.DISABLED
        self.baudrate_optionmenu['state']=tk.DISABLED
        self.refresh_button['state']=tk.DISABLED
        self.clear_button['state']=tk.DISABLED
        self.export_button['state']=tk.DISABLED

        #Thread init 
        t1=threading.Thread(target=self.stream_data,daemon=True)
        t1.start()

        #Hide graph toolbar section
        self.toolbar.pack_forget()
        self.root.geometry(f"{self.width}x{self.height}")

    def close_app(self):
        #Method responsible for 'clean' exit from the program
        self.root.destroy()
        self.stop_status=1
        self.ser.close()

        

if __name__=="__main__":
    SerialDataMonitor=App()
    SerialDataMonitor.root.mainloop()