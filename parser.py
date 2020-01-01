import requests
import json
import time
import collections
import sys, getopt
from argparse import ArgumentParser
import csv
import tkinter as tk
import threading

def thread_it(func, *args):
    t = threading.Thread(target=func, args=args) 
    t.setDaemon(True) 
    t.start()
    # 阻塞--卡死界面！
    # t.join()

class House_sparse(object):
    """docstring for House_sparse"""
    def __init__(self):
        super(House_sparse, self).__init__()
        #self.arg = arg
        self.total_infomation = {}
        parser = ArgumentParser()
        parser.add_argument("-r", "--rating_b", help="set rating lower bound", dest="rating_lb", default=4.5)
        parser.add_argument("-v", "--review_b", help="set review lower bound", dest="review_lb", default=0)
        parser.add_argument("-f", "--filename", help="set output filename", dest="filename", default="house.json")
        parser.add_argument("-t", "--test", help="run with test mode", dest="is_test", default=False)
        args = parser.parse_args()
        self.rating_lb = args.rating_lb
        self.review_lb = args.review_lb
        self.filename =  args.filename
        self.is_test = args.is_test

        for i in range(13):
            self.total_infomation[i] =collections.defaultdict(dict)
        with open('houseinfo.json','r',encoding="utf8") as file:
            log_entry.insert('end', 'Start parsing houseinfo.json\n')
            self.data = json.load(file)
        self.key=""

        
    def Start_sparse(self):

        if(rate_entry.get()!="" and float(rate_entry.get())>0 and float(rate_entry.get())<=5 ):
            self.rating_lb =float(rate_entry.get())
        #print(rate_entry.get(),self.rating_lb,rate_entry.get().isnumeric(),float(rate_entry.get())>0,float(rate_entry.get())<=5)
        if(comment_entry.get()!="" and comment_entry.get().isnumeric() ):
            self.review_lb = int(comment_entry.get())
        if(filename_entry.get()!="" and filename_entry.get() != ""):
            self.filename = filename_entry.get()


        log_entry.insert('end', 'Start parsing houseinfo.json\n')
        data = self.data
        for listing_id in data:
            if(data[listing_id]["avg_rating"]!=None and data[listing_id]["avg_rating"] > self.rating_lb and data[listing_id]["reviews_count"] > self.review_lb):
                log_entry.insert('end',data[listing_id]['url'] + '\n')
                log_entry.insert('end','Price:%s, Rating:%s, Reviews:%s\n' %(data[listing_id]['price'],data[listing_id]['avg_rating'],data[listing_id]['reviews_count']))
                print(data[listing_id])
                self.parse(self.key,listing_id)
                #time.sleep(0.1)
        self.Output_csv()
        log_entry.insert('end', 'Out put' + self.filename +'\n')
        log_entry.insert('end', 'End\n')
    def Test_sparse(self):
        data = self.data
        t = 4
        for listing_id in data:
            t-=1
            if(t==0):
                break
            if(data[listing_id]["avg_rating"]!=None and data[listing_id]["avg_rating"] > self.rating_lb and data[listing_id]["reviews_count"] > self.review_lb):
                print(data[listing_id])
                self.log_entry('end',data[listing_id])
                self.parse(self.key, listing_id)
                time.sleep(1)
        print(self.total_infomation)

    def parse(self,key,listing_id):
        
        base_url = "https://www.airbnb.com.tw/api/v2/homes_pdp_availability_calendar?currency=TWD&key="
        url_year = time.strftime("%Y", time.localtime())
        url_month = time.strftime("%M", time.localtime())
        calendar_url = '%s%s&locale=zh-TW&listing_id=%s&month=%s&year=%s&count=12' % (base_url, key, listing_id, url_month,url_year)
        html = requests.get(calendar_url)
        data = html.json()
        month_data_list = data.get("calendar_months")
        if (self.is_test == True):
            print(calendar_url)
        #{"calendar_months":[{"month":11,"year":2019,"days":[{"date":"2019-11-01","available":false,"max_nights":45,"min_nights":1,"price":{"local_price_formatted":"$1794"}}
        if month_data_list == None:
            return
        house_url = 'https://www.airbnb.com.tw/api/v2/pdp_listing_details/%s?_format=for_rooms_show&_p3_impression_id=p3_1575989659_RtBMYTzq9a5iHGx5&key=&' % (listing_id)
        html = requests.get(house_url)
        data = html.json()
        house_members_ub = data.get("pdp_listing_detail").get("guest_label")
        house_members_ub = house_members_ub[0:len(house_members_ub)-1]
        if(house_members_ub.isdigit()):
            house_members_ub = int(house_members_ub)
        else:
            return

        datacount = 0
        for month_data in month_data_list:
            day_data_list = month_data.get("days")
            for day_data in day_data_list:
                date = day_data.get("date")
                available = day_data.get("available")
                price = day_data.get("price").get("local_price_formatted")
                price = int(price[1:len(price)])
                if(self.total_infomation[house_members_ub][date]):
                    self.total_infomation[house_members_ub][date]["house_nums"] +=1
                    self.total_infomation[house_members_ub][date]["available_house"]  +=available
                    self.total_infomation[house_members_ub][date]["price"].append(price);
                else:
                    self.total_infomation[house_members_ub][date]["house_nums"]  = 1
                    self.total_infomation[house_members_ub][date]["available_house"]  = int(available)
                    self.total_infomation[house_members_ub][date]["price"] = [price]
                datacount +=1
                if(datacount > 180):
                    break;
    def Output_file(self):
        with open(self.filename, 'w') as file:
            json.dump(self.total_infomation, file)

    def Output_csv(self):
        Time = time.strftime("%Y-%m-%d", time.localtime())
        h = []
        for i in self.total_infomation:
            if(self.total_infomation[i][Time].get('house_nums')):
                h.append(i)
        csvtable = [[0 for i in range(len(h)*3+1)] for j in range(320)]
        csvtable[1][0] = 'people'
        for i in range(len(h)):
            csvtable[0][1+3*i] = 'house_nums'
            csvtable[0][2+3*i] = 'available'
            csvtable[0][3+3*i] = 'avg_price' 
        count = 1        
        for i in self.total_infomation[h[0]]:
            count +=1
            csvtable[count][0] = i
        for i in range(len(h)):
            count = 1 
            csvtable[1][1+i*3] = csvtable[1][2+i*3] = csvtable[1][3+i*3] = h[i]
            for j in self.total_infomation[h[i]]:
                count +=1
                csvtable[count][1+i*3] = self.total_infomation[h[i]][j]['house_nums']
                csvtable[count][2+i*3] = self.total_infomation[h[i]][j]['available_house']
                csvtable[count][3+i*3] = self.total_infomation[h[i]][j]['price'][0]
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csvtable)
    #"33928980"
    #"url":"https://www.airbnb.com/rooms/33928980",
    #"price":275.0,
    #"avg_rating":4.59,
    #"reviews_count":17

def ss():
    log_entry.insert('end','ty')
#@click.command()
#@click.option('-r','--rating','tttt',type=int)

window = tk.Tk()
ybar = tk.Scrollbar(window)
ybar.place(x=560, y=180, anchor='nw',height=320) 
log_entry = tk.Text(width=75,yscrollcommand=ybar.set, wrap='none')
log_entry.place(x=25, y=180, anchor='nw') 


ybar.config(command=log_entry.yview)
if __name__ == "__main__":

    
    #s.Test_sparse()
    #s.Output_csv()
    #window = tk.Tk()
    window.title("Airbnb App")
    window.geometry('600x720')
    #window.configure(background='white')
    line_height =2
    px = 25
    py = 25
    xx = 200
    rate_frame = tk.Frame(window)
    #rate_frame.pack(side = tk.TOP)
    rate_label = tk.Label(text = '評分高於(預設為4.5)　　　　　　：　')
    rate_label.place(x=px, y=py, anchor='nw')
    rate_entry = tk.Entry()
    rate_entry.place(x=px+xx, y=py, anchor='nw')

    comment_label = tk.Label(text = '評論數大於(預設為0)　　　　　  ：　')
    comment_label.place(x=px, y=py*2, anchor='nw')
    comment_entry = tk.Entry()
    comment_entry.place(x=px+xx, y=py*2, anchor='nw')

    filename_label = tk.Label(text = '輸出檔案名稱(預設為output.csv) ：　')
    filename_label.place(x=px, y=py*3, anchor='nw')
    filename_entry = tk.Entry()
    filename_entry.place(x=px+xx, y=py*3, anchor='nw')

    #paint_label = tk.Label(text = '繪製圖表　　　　　　　　　　　：　')
    #paint_label.place(x=px, y=py*4, anchor='nw')
    #paint_b = tk.Checkbutton(text='是')
    #paint_b.place(x=px+xx, y=py*4, anchor='nw')
    s = House_sparse()
    #start_button = tk.Button(text = 'START',font = ("Arial Bold", 16),width = 13,command= s.Start_sparse())
    start_button = tk.Button(text = 'START',font = ("Arial Bold", 16),width = 10,command=lambda :thread_it(s.Start_sparse))
    start_button.place(x=px,y=py*5)
    window.mainloop() 
