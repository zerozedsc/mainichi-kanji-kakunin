from tkinter import *
from tkinter import filedialog,messagebox,font
from configparser import ConfigParser
import json, random, os, time, threading, sys, wmi, re
import getpass, traceback, pythoncom

DEBUG = True
USER_NAME = getpass.getuser()
config = ConfigParser()

def WindowManager(window):
    config.read("config.ini")
    get_PID = os.getpid()
    run_config = config["Run"]
    run_config["PID"] = str(get_PID)
    run_config["window"] = str(window)
    with open('config.ini', 'w') as conf:
        config.write(conf)
        conf.close()


class MAIN_GUI():
    # WINDOW = MAIN
    def __init__(self, master):
        self.window = master
        self.window.title("Mainichi Kanji Kakunin")
        self.window.geometry("862x519")
        self.window.configure(bg="#3A7FF6")

        #SELF VAR DECLARE
        self.kanji_canvas = None
        self.s, self.m, self.h = 0,0,0
        self.get_timer = ""
        self.kanji_data = []
        self.counter = 1
        self._run, self._options, self._skip = True, True, True
        self._exe = False

        #CHECK FILE AT STARTUP


        with open("kanji.json", "r", encoding="utf8") as read:
            self.test_load = json.load(read)
            read.close()
        self.kanji = list(self.test_load.keys())

        #Config file
        self.config = config
        self.config.read("config.ini")
        self.kanji_config = self.config["Option"]
        self.FIX_N = self.kanji_config["mainichi_count"]
        if self.FIX_N == "0":
            self.FIX_N = random.randint(1, 20)

        self.setup_jlpt = [k for k in self.kanji_config["jlpt"].split(",")]
        self.setup_stroke = [k for k in self.kanji_config["strokes"].split(",")]
        self.startup_check = bool(self.config["Run"]["startup"])

        self.inStartup()

        if not DEBUG:
            self.window.protocol("WM_DELETE_WINDOW", self.__callback)

        #RUN SPLASH splashScreen
        self.splashScreen()

        canvas = Canvas(master=self.window,bg="#3A7FF6",height=519,width=862,bd=0, highlightthickness=0,relief="ridge")
        canvas.place(x=0,y=0)
        canvas.create_rectangle(431, 0, 431 + 431, 0 + 519, fill="#F3F1FC",outline="")
        canvas.create_rectangle(40, 160, 40 + 60, 160 + 5, fill="#FCFCFC",outline="")

        text_box_bg = PhotoImage(file=f"images/TextBox_Bg.png")
        kun_entry_img = canvas.create_image(650.5,167.5,image=text_box_bg)
        on_entry_img = canvas.create_image(650.5,248.5,image=text_box_bg)
        imi_entry_img = canvas.create_image(650.5,329.5,image=text_box_bg)

        self.kun_entry = Entry(master=self.window,bd=0,bg="#F6F7F9",highlightthickness=0)
        self.kun_entry.place(x=490.0,y=137+25,width=321.0,height=35)

        self.on_entry = Entry(master=self.window, bd=0,bg="#F6F7F9",highlightthickness=0)
        self.on_entry.place(x=490.0,y=218+25,width=321.0,height=35)

        self.imi_entry = Entry(master=self.window, bd=0,bg="#F6F7F9",highlightthickness=0)
        self.imi_entry.place(x=490.0,y=299+25,width=321.0,height=35)
        # self.path_entry.bind("<1>", select_path)


        canvas.create_text(548.5,154.0,text="訓読み(hiragana)",fill="#515486",font=("Arial-BoldMT",int(13.0)))
        canvas.create_text(548.5,232.5,text="音読み(hiragana)",fill="#515486",font=("Arial-BoldMT",int(13.0)))
        canvas.create_text(558.5,312.5,text="意味(English/英語)",fill="#515486",font=("Arial-BoldMT",int(13.0)))
        canvas.create_text(646.5,426.5,text="確認",fill="#FFFFFF",font=("Arial-BoldMT",int(13.0)))
        canvas.create_text(573.5,88.0,text="答え?",fill="#515486",font=("Arial-BoldMT",int(22.0)))

        title = Label(master=self.window, text="毎日漢字", bg="#3A7FF6",fg="white",font=("Arial-BoldMT",int(35.0)))
        title.place(x=27.0,y=100.0)

        self.counter_label = Label(master=self.window, text=f"1/{self.FIX_N}", bg="#3A7FF6",fg="white",font=("Times New Roman",int(20.0)))
        self.counter_label.place(x=370.0,y=200.0)

        def checkOptions(*args):
            if self._options:
                self.options()

        self.option = Label(master=self.window, text="option?",font=("Arial-BoldMT",int(10.0)), bg="#3A7FF6",fg="white", cursor="hand2")
        self.option.place(x=27,y=450)
        self.option.bind('<Button-1>', checkOptions)

        def skipKanji(*args):
            if self._skip:
                self.showInfoKanji()

        self.skip_kanji = Label(master=self.window, text="skip",font=("Arial-BoldMT",int(10.0)), bg="#3A7FF6",fg="white", cursor="hand2")
        self.skip_kanji.place(x=100,y=450)
        self.skip_kanji.bind('<Button-1>', skipKanji)



        #LOAD IMAGE FIRST FOR BUTTON
        self.next_btn_img = PhotoImage(file="./images/next.png")
        self.true_img = PhotoImage(file="./images/true.png")
        self.false_img = PhotoImage(file="./images/false.png")
        kakunin_btn_img = PhotoImage(file="./images/generate.png")

        self.kakunin_btn = Button(master=self.window, image=kakunin_btn_img, borderwidth=0, highlightthickness=0, command=self.kanjiKakunin, relief="flat")
        self.kakunin_btn.place(x=557, y=401, width=180, height=55)


        self.window.resizable(False, False)
        self.kanjiGenerate()
        self.window.mainloop()

    @staticmethod
    def __callback():
        return

    def splashScreen(self):
        #Instruction Window
        #RUN TERMINATING SCRIPT
        if not DEBUG:
            self.run_check = threading.Thread(target=self.checkAppBg)
            self.run_check.start()

        splash = Toplevel(self.window)
        def txt():
            return'''WELCOME TO MAINICHI KANJI KAKUNIN,\nThis app is for who having a problem and want to find a way to memorize kanji.\nTHIS APP STILL IN DEVELOPING,
            \nSO A LOT OF PROBLEM WILL OCCUR.\nFeel Free to contact me for some improvement or issue for me to fix it.
            楽しみ練習しましょう。。頑張れ'''

        Label(master=splash, text=txt(), bg="#3A7FF6",fg="white",font=("Arial-BoldMT",int(15.5))).grid()

        splash.focus_force()
        splash.after(5000, lambda:splash.destroy())

    def timer_func(self):
        if self.option_pane is not None:
            self.timer = Label(master=self.window, text="TIMER: 0:00:00",font=("Arial-BoldMT",int(10.0)), bg="#3A7FF6",fg="white", cursor="hand2")
            self.timer.place(x=300,y=450)

        if self.h > 0:
            messagebox.showerror("END", "Times Up go for next kanji")
            self.get_timer = "TIMES UP"
            self.h = 0
            self.showInfoKanji()

        else:
            self.s += 1

            if self.s > 60:
                self.m += 1
                self.s = 0
            if self.m > 60:
                self.h +=1
                self.m = 0
            self.timer.configure(text=f"TIMER: {self.h}min:{self.m}s:{self.s}")


            self.timer.after(10,self.timer_func)

            self.get_timer = f"{self.h}m : {round(((float(self.s)+float(self.m)*60)/60),2)}s"

    def showInfoKanji(self,*args):
        #DISABLE Button
        self._options, self._skip = False, False
        self.kakunin_btn.config(state="disabled")

        self.skip_kanji.bind('<Button-1>', None)
        self.skip_kanji.update()
        self.option.bind('<Button-1>', None)
        self.option.update()
        self.kakunin_btn.config(state="disabled")

        self.window_info = Toplevel(master=self.window)
        self.window_info.title("Kanji INFO")
        self.window_info.geometry("862x519")
        self.window_info.configure(bg="#77DD77")
        self.window_info.resizable(False, False)
        self.window_info.protocol("WM_DELETE_WINDOW", self.__callback)

        # destroy timer_func
        self.timer.destroy()
        self.timer = None

        #BACKGROUND
        canvas = Canvas(master=self.window_info,bg="#77DD77",height=519,width=862,bd=0, highlightthickness=0,relief="ridge")
        canvas.place(x=0,y=0)
        canvas.create_rectangle(431, 0, 431 + 431, 0 + 519, fill="#CCE6CC",outline="")

        #KANJI Canvas
        kanji_canvas = Canvas(self.window_info, width=250, height=250, bg = 'white')
        kanji_canvas.create_text(250/2,250/2,fill="black",font="Times 130 bold",text=str(self.get_kanji))
        kanji_canvas.place(x=0,y=0)
        number_kanji = self.rand_choice + 1
        kanji_canvas.create_text(40,10,fill="black",font="Times 20 bold",
                        text=f"{number_kanji}.")

        #KUNYOMI ONYOMI Label
        kunyomi_get = "訓読み:\n"
        kun_len = len(self.kun_reading)
        if kun_len > 6:
            for k in range(0,5):
                kunyomi_get += self.kun_reading[k] + ",\n"
        else:
            for k in self.kun_reading:
                kunyomi_get += k + ",\n"

        onyomi_get = "音読み:\n"
        for o in self.on_reading:
            onyomi_get += o + ",\n"
        yomi_text = kunyomi_get+"\n"+onyomi_get
        yomi_label = Label(self.window_info,text= f"{yomi_text}",fg="black",font=("Bahnschrift SemiCondensed" ,23 ,"bold"))
        yomi_label.place(x=255.5,y=5)

        #YOMI CHECK
        #TO GET A REAL VALUE OF X AND Y NEED TO UPDATE TK
        self.window_info.update()
        yomi_label_x = 260.5 + float(yomi_label.winfo_width()) #LETAK SEBELAH KANAN TAMBAH DENGAN x:yomi_label
        if self._kunyomi:
            kun_check = self.true_img
        else:
            kun_check = self.false_img
        Button(master=self.window_info, image=kun_check, borderwidth=0, highlightthickness=0, command=None, relief="flat").place(x=yomi_label_x, y=10, width=21, height=20)
        if self._onyomi:
            on_check = self.true_img
        else:
            on_check = self.false_img
        yomi_label_y = 5 + float(yomi_label.winfo_height()) # LETAK SEBELAH BAWAH
        Button(master=self.window_info, image=on_check, borderwidth=0, highlightthickness=0, command=None, relief="flat").place(x=yomi_label_x, y=kun_len*10 + yomi_label_y/2 , width=21, height=20)
        # print(f"yomi_label = x:{yomi_label_x}, y:{yomi_label_y}")


        #stroke show info
        canvas.create_text(250/2,300,text= f"STROKE:\n   > {self.stroke} <  ",fill="black",font="Times 20 bold")
        #JLPT showinfo
        canvas.create_text(250/2,370,text= f"JLPT:\n> {self.jlpt} < ",fill="black",font="Times 20 bold")

        #TIMER showInfo
        Label(self.window_info,text= f"YOUR TIME:{self.get_timer}<<",fg="black",font=("Bahnschrift SemiCondensed" ,23 ,"bold")).place(relx=0,rely=0.9)

        #MEANING showInfoKanji
        meaning = ""
        g = 1
        for m in self.meaning:
            if len(m) > 10:
                m = m + ",\n"
            else:
                m += ", "

            if len(self.meaning) < 2:
                meaning += m
            else:
                if g == 4:
                    if "\n" not in m:
                        meaning += "\n"
                    g=1
                meaning += m
                g+=1
        # print(meaning)
        imi_label = Label(self.window_info,text= f"MEANING:\n{meaning}",fg="black",font=("Bahnschrift SemiCondensed" ,18 ,"bold"))
        imi_label.place(x=460,y=10)

        #MEANING Check
        self.window_info.update()
        if self._imi:
            imi_check = self.true_img
        else:
            imi_check = self.false_img
        imi_label_x = 400 + float(imi_label.winfo_width())  #LETAK SEBELAH KANAN
        Button(master=self.window_info, image=imi_check, borderwidth=0, highlightthickness=0, command=None, relief="flat").place(x=imi_label_x, y=10, width=21, height=20)
        # imi_label_y = 260.5 + float(imi_label.winfo_height()) >> xpayah sebab nk letak sebelah atas

        #Sentence EXAMPLE

        #NEXT Button
        def next():
            self._options, self._skip = True, True
            self.kakunin_btn.config(state="normal")
            self.on_entry.delete(0, 'end')
            self.kun_entry.delete(0, 'end')
            self.imi_entry.delete(0, 'end')
            self.window_info.destroy()
            self.timer = Label(master=self.window, text="TIMER: 0:00:00",font=("Arial-BoldMT",int(10.0)), bg="#3A7FF6",fg="white", cursor="hand2")
            self.timer.place(x=300,y=450)
            self.kanjiGenerate()
        next_btn = Button(master=self.window_info, image=self.next_btn_img, borderwidth=0, highlightthickness=0, command=next, relief="flat")
        next_btn.place(x=730, y=430, width=128, height=80)

    def kanjiGenerate(self, *args):
        self._onyomi, self._kunyomi, self._imi = False, False, False
        self.on_entry.config(state="normal")
        self.kun_entry.config(state="normal")
        self.imi_entry.config(state="normal")
        #CHECK IF N IS true
        if int(self.counter) > int(self.FIX_N):
            # run_config not use
            self.run_config["run"] = str(False)
            with open('config.ini', 'w') as conf:
                self.config.write(conf)
                conf.close()

            try:
                messagebox.showinfo("Nice", "You have done fukushu for kanji. Ganbattane")
                self._run = False
                self.run_check.join()
                WindowManager("CLOSE")
                self.window.destroy()
            except Exception as e:
                print(e)

        if self.s > 0 and self.timer is not None:
            self.s,self.m,self.h = 0,0,0
            self.timer.destroy()
            self.timer = Label(master=self.window, text="TIMER: 0:00:00",font=("Arial-BoldMT",int(10.0)), bg="#3A7FF6",fg="white", cursor="hand2")
            self.timer.place(x=300,y=450)

        if self.kanji_canvas is not None:
            self.kanji_canvas.destroy()

        #call timer
        self.option_pane = None
        self.timer = Label(master=self.window, text="TIMER: 0:00:00",font=("Arial-BoldMT",int(10.0)), bg="#3A7FF6",fg="white", cursor="hand2")
        self.timer.place(x=300,y=450)
        self.timer_func()


        total_kanji = len(self.kanji)
        pick = True
        old_number = []
        while pick:
            #CHECK SAME KANJI
            self.rand_choice = random.randint(0, total_kanji-1)
            if self.rand_choice in old_number:
                pass

            else:
                #GET KANJI DATA
                ALL = "ALL"
                self.get_kanji = self.kanji[self.rand_choice]
                self.get_data_kanji = self.test_load[self.kanji[self.rand_choice]]
                self.stroke = str(self.get_data_kanji["strokes"])
                self.jlpt = "n" + str(self.get_data_kanji["jlpt_new"])
                # print(f"{self.jlpt},{self.setup_jlpt} >{(self.jlpt in self.setup_jlpt) or (ALL in self.setup_jlpt)}")
                reading_on,reading_kun,meaning  = [],[],[]
                punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
                for j in self.get_data_kanji["readings_on"]:
                    j = re.sub(r'[^\w\s]','',j)
                    reading_on.append(j)
                for k in self.get_data_kanji["readings_kun"]:
                    k = re.sub(r'[^\w\s]','',k)
                    reading_kun.append(k)
                for l in self.get_data_kanji["meanings"]:
                    l = re.sub(r'[^\w\s]',' ',l)
                    meaning.append(l)



                if ((self.setup_stroke[1] != 0) and (int(self.stroke) in range(int(self.setup_stroke[0]),int(self.setup_stroke[1]))) or \
                ("0" == self.setup_stroke[0] or self.stroke == self.setup_stroke[0]))\
                 and ((self.jlpt in self.setup_jlpt) or (ALL in self.setup_jlpt)):
                    self.on_reading = reading_on
                    if self.on_reading == []:
                        self.on_entry.config(state="disabled")
                    self.kun_reading = reading_kun
                    if self.kun_reading == []:
                        self.kun_entry.config(state="disabled")
                    self.meaning = meaning
                    if self.meaning == []:
                        self.imi_entry.config(state="disabled")
                    self.kanji_data = [self.get_kanji, self.on_reading, self.kun_reading, self.jlpt, self.meaning]
                    pick = False


            old_number.append(self.rand_choice)

        self.kanji_canvas = Canvas(self.window, width=250, height=250, bg = 'white')
        self.kanji_canvas.create_text(250/2,250/2,fill="black",font="Times 130 bold",
                        text=str(self.get_kanji))
        self.kanji_canvas.place(x=27.0,y=180.0)

    def kanjiKakunin(self, *args):
        kun_get = str(self.kun_entry.get())
        on_get = str(self.on_entry.get())
        imi_get = str(self.imi_entry.get())

        #Check
        message_check = f"""kun_get>{kun_get} = {self.kanji_data[2]} ;{kun_get in self.kanji_data[2]}
        on_get>{on_get} = {self.kanji_data[1]} ; {on_get in self.kanji_data[1]}
        imi_get>{imi_get} = {self.kanji_data[4]}; {imi_get.capitalize() in self.kanji_data[4]} """

        self._onyomi = bool(on_get in self.kanji_data[1])
        self._kunyomi = bool(kun_get in self.kanji_data[2])
        self._imi = bool(imi_get.capitalize() in self.kanji_data[4])

        print(len(self.kanji_data[1]), len(self.kanji_data[1]))
        if self.kanji_data[2] == []:
            self._kunyomi = True
        elif self.kanji_data[1] == []:
            self._onyomi = True

        if self._onyomi and self._kunyomi and self._imi:
            self.counter += 1
            self.counter_label.configure(text=f"{self.counter}/{self.FIX_N}")
            messagebox.showinfo("True", "You input a correct answer")
            self.showInfoKanji()
        else:
            messagebox.showerror("Wrong", "Wrong answer")
            self.get_timer = "WRONG"
            self.showInfoKanji()    #check True or False

    def options(self, *args):
        #Pause Timer and disable option
        self.timer.destroy()
        self._options, self._skip = False, False
        self.option.update()
        self.kakunin_btn.config(state="disabled")

        self.skip_kanji.bind('<Button-1>', None)
        self.skip_kanji.update()
        self.option.bind('<Button-1>', None)
        self.option.update()
        self.kakunin_btn.config(state="disabled")

        self.option_pane = Toplevel(self.window)
        self.option_pane.protocol("WM_DELETE_WINDOW", self.__callback)
        self.option_pane.configure(bg="#000080")
        self.option_pane.resizable(False, False)


        Label(self.option_pane, text="OPTION",font="Times 10 bold").grid(row = 0, column = 1, sticky = W, pady = 5)
        label_frame = Frame(self.option_pane)
        entry_frame = Frame(self.option_pane)

        Label(label_frame, text="Kanji Count",font="Times 20 bold").grid(row = 1, column = 0, sticky = W, pady = 2)
        kanji_count = Entry(entry_frame, textvariable=0)
        kanji_count.grid(row = 1, column = 1, sticky = W, pady = 3,ipady=5,ipadx=5)


        Label(label_frame, text="JLPT",font="Times 20 bold").grid(row = 2, column = 0, sticky = W, pady = 2)
        cbVariables=[0,0,0,0,0,0]
        jlpt_frame = Frame(entry_frame)

        for k in range(6):
            cbVariables[k] = IntVar()
            if k == 5:
                Checkbutton(jlpt_frame, text=f"ALL",variable=cbVariables[k]).grid(row = 0, column = k, sticky = W, pady = 2)
            else:
                Checkbutton(jlpt_frame, text=f"N{k+1}",variable=cbVariables[k]).grid(row = 0, column = k, sticky = W, pady = 2)

        jlpt_frame.grid(row = 2, column = 3, sticky = W, pady = 5)

        Label(label_frame, text="Stroke",font="Times 20 bold").grid(row = 3, column = 0, sticky = W, pady = 2)
        stroke_entry1 = Entry(entry_frame)
        stroke_entry1.grid(row = 3, column = 1, sticky = W, pady = 3,ipady=5,ipadx=5)
        Label(entry_frame, text="~").grid(row = 3, column = 2, sticky = W, ipady = 2,ipadx=5)
        stroke_entry2 = Entry(entry_frame,state="disabled")
        stroke_entry2.grid(row = 3, column = 3, sticky = W, pady = 3,ipady=5,ipadx=5)

        label_frame.grid(row = 1, column = 0, sticky = W, pady = 5)
        entry_frame.grid(row = 1, column = 2, sticky = W, pady = 5,ipady=5,ipadx=5)


        def check_number(*args):
            if not str(kanji_count.get()).isnumeric():
                kanji_count.delete(0, 'end')
            if not str(stroke_entry1.get()).isnumeric():
                stroke_entry1.delete(0, 'end')
            if str(stroke_entry1.get()) == "":
                stroke_entry2.config(state="disabled")
            else:
                stroke_entry2.config(state="normal")
            if not str(stroke_entry2.get()).isnumeric():
                stroke_entry2.delete(0, 'end')

        kanji_count.bind("<KeyRelease>", check_number)
        stroke_entry1.bind("<KeyRelease>", check_number)
        stroke_entry2.bind("<KeyRelease>", check_number)
        #exit Button
        def optionsExit():
            self.kanji_config
            #JLPT
            jlpt_set = ""
            translate_var = []
            for i in range(len(cbVariables)):
                translate_var.append(cbVariables[i].get())

            if 1 in translate_var:
                if translate_var[5] == 1:
                    jlpt_set = "ALL,ALL"
                else:
                    for j in range(len(translate_var)-1):
                        if translate_var[j] == 1:
                            jlpt_set += f"n{j+1},"

                self.kanji_config["jlpt"] = jlpt_set
                self.setup_jlpt = [k for k in jlpt_set.split(",")]


            #NUMBER OF Kanji
            if kanji_count.get() != "":
                self.kanji_config["mainichi_count"] = kanji_count.get()
                self.FIX_N = kanji_count.get()
                self.counter_label.configure(text=f"{self.counter}/{self.FIX_N}")
                self.counter = 1

            #STROKE
            if stroke_entry1.get() != "":
                stroke_range = ""
                if str(stroke_entry2.get()) == "":
                    stroke_range = str(stroke_entry1.get()) + ",0"

                else:
                    stroke_range = str(stroke_entry1.get()) + "," + str(stroke_entry2.get())

                self.kanji_config["strokes"] = stroke_range
                self.setup_stroke = [k for k in stroke_range.split(",")]


            with open('config.ini', 'w') as conf:
                self.config.write(conf)
                conf.close()

            self._options, self._skip = True, True
            self.kakunin_btn.config(state="normal")
            self.on_entry.delete(0, 'end')
            self.kun_entry.delete(0, 'end')
            self.imi_entry.delete(0, 'end')

            self.timer_func()
            self._options = True
            self.option_pane.destroy()

        Button(master=self.option_pane,text="EXIT",font="Times 12 bold", borderwidth=0, highlightthickness=0, command=optionsExit, relief="flat").grid(row = 4, column = 2, sticky = W, pady = 2)

        # print(self.FIX_N, self.setup_jlpt, self.jlpt)
        # with open('config.ini', 'w') as conf:
        #     self.config.write(conf)
        #     conf.close()

    def checkAppBg(self):
        pythoncom.CoInitialize()
        self.f = wmi.WMI()
        #NOT USING
        config = ConfigParser()
        config.read("config.ini")
        main_bool = config["Run"]["run"]
        main_PID = config["Run"]["PID"]

        # print("pid   Process name")
        self.get_startup_id = []
        self.pid_list = []
        self.get_exceptional_id = []
        self.check_round = 1
        # Iterating through all the running processes
        for process in self.f.Win32_Process():
            # Displaying the P_ID and P_Name of the process
            self.get_startup_id.append(str(process.ProcessId))
            # print(f"{process.ProcessId:<10} {process.Name}")

        while self._run:
            print(f"RUNNING>> {self.check_round}")
            for next in self.f.Win32_Process():
                get_new_id = next.ProcessId
                get_new_name = next.Name
                if str(get_new_id) not in self.get_startup_id and str(get_new_id) not in self.get_exceptional_id and ".exe" in str(get_new_name):
                    try:
                        print(next.Name,get_new_id)
                        next.terminate()
                    except Exception as e:
                        print("EXCEPT>> ", e)
                        if str(get_new_id) not in self.get_exceptional_id:
                            self.get_exceptional_id.append(str(get_new_id))


            self.check_round += 1
            time.sleep(1)
            os.system("cls")

    def inStartup(self):
        startup_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME

        if not DEBUG:
            if not self._exe :
                #THIS BAT FILE WILL SAVE AT STARTUP
                #TESTING PURPOSE ONLY, WHEN EXE FILE DONE, THIS WILL NOT BE USE
                startup_name = "mainichi_start.bat"
                if not os.path.exists(os.path.abspath(f"{startup_path}\{startup_name}")):
                    file_path = os.path.dirname(os.path.realpath("main.py"))
                    bat_code = f'''cd /\ncd /d {file_path}\npython.exe main.py'''

                    with open(startup_path + '\\' + startup_name , "w+") as bat_file:
                        bat_file.write(r'%s' % f"{bat_code}")
                        bat_file.close()
                else:
                    print(f"{startup_path}\{startup_name} >>> exists")

            else:
                #FOR EXE FILE
                #PLEASE MAKE self._exe = True to create exe file to startup
                startup_name = "mainichi-kanji-kakunin.exe"
                exe_file = "mainichi.exe"
                if not os.path.exists(os.path.abspath(f"{startup_path}\{startup_name}")):
                    file_path = os.path.dirname(os.path.realpath(exe_file))
                    from pyshortcuts import make_shortcut
                    make_shortcut(file_path, name=startup_name,folder=startup_path)
                else:
                    print(f"{startup_path}\{startup_name} >>> exists")
                pass



        #NEXT TIME MAYBE I WILL CONSIDER PUT IN REG
        #FOR NOW JUST IN STARTUP FOLDER

class LEARN_GUI():
    # WINDOW = LEARN
    def __init__(self, master):
        self.window = master
        self.window.title("Mainichi Kanji Kakunin")
        self.window.geometry("862x519")
        self.window.configure(bg="#3A7FF6")
        self.window.resizable(False, False)


        self.window.mainloop()


if __name__ == "__main__":
    try:
        #WindowManager
        process = True
        while process:
            window = Tk()
            config.read("config.ini")
            run_config = config["Run"]
            window_get = str(run_config["window"])
            if window_get == "MAIN":
                MAIN_GUI(window)
            elif window_get == "LEARN":
                LEARN_GUI(window)
            else:
                run_config["window"] = "MAIN"
                with open('config.ini', 'w') as conf:
                    config.write(conf)
                    conf.close()
                print("close")
                process = False
                sys.exit()

    except Exception as e:
        if not DEBUG:
            with open("ERROR LOG.txt", "a") as log:
                log.write(f"{e}\n{traceback.format_exc()}\n")
        else:
            print(f"{e}\n{traceback.format_exc()}\n")
