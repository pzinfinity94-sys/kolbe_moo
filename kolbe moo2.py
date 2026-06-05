import requests
import time
import json
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")


class kolbe_moo:

    def __init__(self,token):

        self.token=token
        self.base_url=f"https://tapi.bale.ai/bot{self.token}"
        self.last_update_id=0
        self.user_state={}
        self.barber_chat_id=2123079534

        self.buttons={
            "inline_keyboard":[
                [{"text":"فشیال","callback_data":"k_1"}],
                [{"text":"کوتاهی بچه","callback_data":"k_2"}],
                [{"text":"اصلاح سر و سایه ریش","callback_data":"k_3"}],
                [{"text":"شیو صورت","callback_data":"k_4"}],
                [{"text":"هیرکات مدرن","callback_data":"k_5"}]
            ]
        }
    def time_keyboard(self,selected_date):
        reservations=self.load_reservation()
        reserved_times=[]
        for r in reservations:
            if r["date"]==selected_date:
                reserved_times.append(
                    r["time"]
                )
        all_times=[
                ("09:00","t1"),
                ("10:30","t2"),
                ("12:00","t3"),
                ("13:30","t4"),
                ("18:00","t5"),
                ("19:30","t6"),
                ("21:00","t7"),
                ("22:00","t8")
            ]
        keyboard=[]
        for time_text,callback in all_times:
                if time_text not in reserved_times:
                    keyboard.append([
                        {
                            "text":time_text,
                            "callback_data":callback
                        }
                    ])    

        return{
            "inline_keyboard":keyboard
        }
    def calender_keyboard(self):
        return{
            "inline_keyboard":[
                [
                    {"text":"شنبه","callback_data":"d1"},
                    {"text":"یکشنبه","callback_data":"d2"}
                ],
                [
                    {"text":"دوشنبه","callback_data":"d3"},
                    {"text":"سه شنبه","callback_data":"d4"}
                ],
                [
                    {"text":"چهارشنبه","callback_data":"d5"},
                    {"text":"پنجشنبه","callback_data":"d6"}
                ]
            ]
        }
    def get_updates(self,offset=None):
        url=self.base_url+"/getUpdates"
        params={}

        if offset is not None:
            params["offset"]=offset
            try:
                response=requests.get(url,params=params,timeout=10)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"error:{e}")
                return{"ok":False}
    def send_message(self,chat_id,text,reply_markup=None):
        url=self.base_url+"/sendMessage"
        payload={
            "chat_id":chat_id,
            "text":text,
            "reply_markup":reply_markup
        }
        requests.post(url,json=payload,timeout=10)

    def load_reservation(self):

        if not os.path.exists("reservations.json"):
            return[]
        
        with open("reservations.json","r",encoding="utf-8") as f:
            return json.load(f)
    def save_reservations(self,reservations):
        with open("reservations.json","w",encoding="utf-8") as f:
            json.dump(
                reservations,
                f,
                ensure_ascii=False,
                indent=4
            )
        
    def run(self):
        print("kolbe moo is runiing....")
        print(self.load_reservation())
        while True:
            updates=self.get_updates(self.last_update_id+1)
            if updates.get("ok"):
                for item in updates.get("result",[]):
                    self.last_update_id=item["update_id"]
                    if "message"in item:
                        chat_id=item["message"]["chat"]["id"]
                        text=item["message"].get("text","")
                        if text=="/start":
                            
                            self.send_message(chat_id,"لطفا یکی از گزینه هارا انتخاب کنید:",self.buttons)

                        
                            
                        elif chat_id in self.user_state:

                            state = self.user_state[chat_id]
                            if state.get("step")=="waiting_lastname":
                                state["lastname"]=text
                                state["step"]="waiting_phone"

                                self.send_message(
                                    chat_id,
                                    "لطفا شماره تماس خود را وارد نمایید:"
                                )

                            elif state.get("step")=="waiting_phone":

                                state["phone"]=text

                                reservations = self.load_reservation()

                                reservations.append({
                                    "service":state.get("service",""),
                                    "date":state.get("date",""),
                                    "time":state.get("t",""),
                                    "lastname":state.get("lastname",""),
                                    "phone":state.get("phone","")
                                })
                                self.save_reservations(reservations)
                                print("saved")
                                print(reservations)
                                

                                self.send_message(
                                    chat_id,
                                    f"رزرو شما ثبت شد \n\n"
                                    f"خدمات:{state.get('service','')}\n"
                                    f"ساعت:{state.get('t','')}\n"
                                    f"روز:{state.get('date','')}\n"
                                    f"نام خانوادگی:{state.get('lastname','')}\n"
                                    f"شماره تماس:{state.get('phone','')}"
                                )
                                self.send_message(
                                    self.barber_chat_id,
                                    f"رزرو جدید\n\n"
                                    f"خدمت:{state.get('service','')}\n"
                                    f"رزرو:{state.get('date','')}\n"
                                    f"ساعت:{state.get('t','')}\n"
                                    f"نام خانوادگی:{state.get('lastname','')}\n"
                                    f"تلفن:{state.get('phone','')}"
                                )
                                del self.user_state[chat_id]
                    elif "callback_query" in item:

                        callback=item["callback_query"]

                        chat_id=callback["message"]["chat"]["id"]
                        data=callback["data"]

                        services={
                            "k_1":"فشیال",
                            "k_2":"کوتاهی بچه",
                            "k_3":"اصلاح سر و سایه ریش",
                            "k_4":"شیو صورت",
                            "k_5":"هیرکات مدرن"
                        }
                        times={
                            "t1":"09:00",
                            "t2":"10:30",
                            "t3":"12:00",
                            "t4":"13:30",
                            "t5":"18:00",
                            "t6":"19:30",
                            "t7":"21:00",
                            "t8":"22:00",
                        }
                        calender={
                            "d1":"شنبه",
                            "d2":"یکشنبه",
                            "d3":"دوشنبه",
                            "d4":"سه شنبه",
                            "d5":"چهارشنبه",
                            "d6":"پنجشبه",
                        }

                        if data in services:
                            self.user_state[chat_id]={
                                "service":services[data],
                                "step":"waiting_data"
                            }
                            self.send_message(
                                chat_id,
                                "لطفا روز مورد نظر را انتخاب کنید:",
                                self.calender_keyboard()
                            )
                        elif data.startswith("d"):
                            if chat_id not in self.user_state:
                                self.send_message(
                                    chat_id,
                                    "ابتدا یک خدمت را انتخاب کنید",
                                )
                                continue
                            self.user_state[chat_id]["date"]=calender[data]
                            self.user_state[chat_id]["step"]="waiting_time"
                            self.send_message(
                                chat_id,
                                "لطفا ساعت مورد نظر را انتخاب کنید:",
                                self.time_keyboard(
                                    self.user_state[chat_id]["date"]
                                )
                            )
                        elif data.startswith("t"):
                            if chat_id not in self.user_state:
                                self.send_message(chat_id,"ابتدا یک خدمت را انتخاب کنید")
                                continue

                            selected_time=times[data]
                            reservations=self.load_reservation()
                            selected_date=self.user_state[chat_id]["date"]
                            reserved=False
                            for r in reservations:
                               if(
                                   r["date"]==selected_date and
                                   r["time"]==selected_time
                               ):
                                   reserved=True
                                   break
                                
                            if reserved:
                                self.send_message(
                                    chat_id,
                                    "این ساعت قبلا رزرو شده است"
                                )
                            else:
                                 self.user_state[chat_id]["t"]=selected_time
                                 self.user_state[chat_id]["step"]="waiting_lastname"

                                 self.send_message(
                                chat_id,
                                "لطفا نام خانوادگی خود را وارد نمایید:"
                                 )
            time.sleep(1)

if __name__=="__main__":

 TOKEN="611480532:q9ODKZ-Thj0dUlBJ3mm2suHWDc4jluGaF2c"

 bot=kolbe_moo(TOKEN)
 bot.run()

        
