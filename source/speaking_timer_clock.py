# Version 1.16
# button 1 - проигрывание случайной мелодии повторное нажатие - стоп
# button 2 - проговаривание текущего времени, даты и года
# button 3 - "выбор" ()
# button 4 - "минус" ()
# button 5 - "плюс" ()
# button левого енкодера - вкл/выкл звука
# button правого енкодера - старт/отмена таймера
#
import time
import random
from machine import Pin, I2C
from pico_i2c_lcd import I2cLcd
from picozero import Button
from picodfplayer import DFPlayer
from ds1302 import DS1302
from rotary import Rotary

I2C_ADDR = 0x3F
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
player = DFPlayer(
    0, 16, 17, 18
)  # Initialising DFPlayer (UART, TX-Pin, RX-Pin, Busy-Pin)
DFPlayer_busy = machine.Pin(18)
time.sleep(0.5)
player.pause()
vol_sound = 5
player.setVolume(vol_sound)  # громкость: von 0 bis 30
# Variables for random playback
play_on = False  # Flag to indicate if playback should be active
playing = False  # Flag to indicate if a track is currently playing
playlist = list(
    range(1, 46)
)  # Assuming you have 45 music files named 1.mp3, 2.mp3, ..., 45.mp3
current_track_index = 0  # Index of the current track in the playlist
ds = DS1302(Pin(2), Pin(5), Pin(4))  # CLK DAT RST
i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
time.sleep(1)

clear_spisok = [0, 1, 2, 3, 4, 5, 6]
hour_dict = dict(zip(clear_spisok, ds.date_time()))
current_minute = hour_dict.get(5)
current_hour = hour_dict.get(4)
old_minute = current_minute - 1
old_hour = current_hour - 1
sp_month = {
    1: "Jan",
    2: "Feb",
    3: "Mär",
    4: "Apr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Okt",
    11: "Nov",
    12: "Dez",
}
sp_dayname = {
    1: "Montag",
    2: "Dienstag",
    3: "Mittwoch",
    4: "Donnerstag",
    5: "Freitag",
    6: "Samstag",
    7: "Sonntag",
}
# Определение выводов для энкодера
rotary1 = Rotary(14, 15, 20)  # DATA CLK SW пины инициализации енкодера 1
rotary2 = Rotary(11, 10, 19)  # DATA CLK SW пины инициализации енкодера 2

# Установка начального значения
s_volume = 10  # начальное значение громкости
# флаги
alarm_trigger = False  # флаг срабатывания будильника
time_spoken = False  # флаг срабатывания проговаривания
flag_update = True  # флаг обновления экрана
# таймер, который сработает следующим для показа
num_alarm = 1  # номер будильника, который сработает следующим
# флаг  10- на определенную дату 11- на каждый день
num_alarm_spisok = {1: 1149, 2: 1235, 3: 1400, 4: 1600, 5: 1700}  # время таймеров
# Инициализация переменных для проверки таймера
timer_running = False
remaining_minutes = 0
minutes = 1  # на сколько минут установлен таймер по умолчанию
# период действия речевых сообщений - имеет приоритет перед проговариванием таймеров
work_time_start = 7
work_time_end = 22
volume_on = True  # флаг звука
timer_hour = 0
current_timer_hour = 0
total_minutes = 0
boom_hour = 0


# Функция для обработки вращения энкодера 1
def rotary_changed1(change1):
    global s_volume
    global flag_update
    if change1 == Rotary.ROT_CW:
        if s_volume <= 29:
            s_volume = s_volume + 1
            flag_update = True
            print("Флаг_ОЭ: ", flag_update)
            player.playTrack(9, s_volume)  # из папки 09 проговариваем цифры
            time.sleep(0.6)
            player.playTrack(12, s_volume)  # из папки 12 проговариваем цифры

    elif change1 == Rotary.ROT_CCW:
        if s_volume > 0:
            s_volume = s_volume - 1
            flag_update = True
            print("Флаг_ОЭ: ", flag_update)
            player.playTrack(9, s_volume)  # из папки 09 проговариваем цифры
            time.sleep(0.6)
            player.playTrack(12, s_volume)  # из папки 12 проговариваем цифры


# Функция для обработки вращения энкодера 2
def rotary_changed2(change2):
    global flag_update, minutes

    if change2 == Rotary.ROT_CW:
        if minutes != 180:
            minutes += 1

    elif change2 == Rotary.ROT_CCW:
        if minutes != 0:
            minutes -= 1

    flag_update = True
    print("Таймер на: ", minutes)


rotary1.add_handler(rotary_changed1)
rotary2.add_handler(rotary_changed2)


def speak_frase(
    x,
):  # 1- время, 2 - день недели, 3 - месяц и число, 4 - год, 1 впереди - на втором языке
    if volume_on:
        if x == 1:
            player.playTrack(1, hour_dict.get(4))  # из папки 01 проговариваем часы
            time.sleep(0.7)
            player.playTrack(2, hour_dict.get(5))  # из папки 02 проговариваем минуты
            time.sleep(1)
        # на немецком
        if x == 11:
            player.playTrack(11, hour_dict.get(4))  # из папки 01 проговариваем часы
            time.sleep(0.7)
            player.playTrack(12, hour_dict.get(5))  # из папки 02 проговариваем минуты
            time.sleep(1)
        elif x == 2:
            player.playTrack(
                6, hour_dict.get(3)
            )  # из папки 01 проговариваем день недели
            time.sleep(1)
        # на немецком
        elif x == 12:
            player.playTrack(
                16, hour_dict.get(3)
            )  # из папки 01 проговариваем день недели
            time.sleep(1)
        elif x == 3:
            player.playTrack(3, hour_dict.get(2))  # из папки 03 проговариваем число
            time.sleep(1)
            player.playTrack(4, hour_dict.get(1))  # из папки 04 проговариваем месяц
            time.sleep(1)
        # на немецком
        elif x == 13:
            player.playTrack(13, hour_dict.get(2))  # из папки 03 проговариваем число
            time.sleep(1.6)
            player.playTrack(14, hour_dict.get(1))  # из папки 04 проговариваем месяц
            time.sleep(1)
        elif x == 4:
            player.playTrack(
                5, hour_dict.get(0) - 2020
            )  # из папки 05 проговариваем год
            time.sleep(1)
        # на немецком
        elif x == 14:
            player.playTrack(
                15, hour_dict.get(0) - 2020
            )  # из папки 05 проговариваем год
            time.sleep(1)

        else:
            time.sleep(1)


# button на енкодере 1 - включение и выключение звука
def vol_onoff():
    print(
        "button енкодера 2: Громкость on/off"
    )  # текущая громкость меняется на 0, предыдущее значение сохраняется
    global volume_on
    if volume_on:
        volume_on = False
        player.playTrack(7, 9)  # из папки 07 фраза "Звук включен"
        time.sleep(1)
        # на немецком
        player.playTrack(17, 9)  # из папки 07 фраза "Звук включен"
    else:
        player.playTrack(7, 8)  # из папки 07 фраза "Звук выключен"
        time.sleep(1)
        # на немецком
        player.playTrack(17, 8)  # из папки 07 фраза "Звук выключен"
        volume_on = True


#    speak_frase(4)
# returns the current datetime
# ds.date_time()
# print(ds.date_time())
# ds.date_time([2023, 10, 22, 7, 13 , 5, 0, 0]) # set datetime YYYY MM DD NN HH MM.


# button на енкодере 2 - включение и выключение таймера
def timer_onoff():
    global minutes, timer_running, remaining_minutes, current_timer_hour, total_minutes, current_minute

    if timer_running:
        # Отмена текущего таймера
        timer_running = False
        print("Таймер отменен.")
        player.playTrack(7, 14)  # таймер установлен
        time.sleep(0.7)
        # немецкий
        player.playTrack(17, 14)  # таймер установлен
        time.sleep(0.7)
        remaining_minutes = 0
    else:
        # Добавление установленного количества минут к текущему времени
        current_timer_hour = hour_dict.get(4)
        current_minute = hour_dict.get(5)
        total_minutes = current_minute + minutes
        print("*: ", current_timer_hour, total_minutes)

        if total_minutes >= 60:
            current_timer_hour += 1
            total_minutes -= 60
        print("Установленное время:", current_timer_hour, total_minutes)
        player.playTrack(7, 7)  # таймер установлен
        time.sleep(0.7)
        player.playTrack(2, minutes)  # таймер установлен
        time.sleep(0.6)
        # немецкий
        player.playTrack(17, 7)  # таймер установлен
        time.sleep(1.3)
        player.playTrack(12, minutes)  # таймер установлен
        time.sleep(0.6)
        player.playTrack(17, 15)  # minuten
        time.sleep(0.6)
        # Включение таймера для срабатывания
        timer_running = True
        flag_update = True
        remaining_minutes = minutes


# громкость
btn_enc1 = Button(20)
btn_enc1.when_pressed = vol_onoff  # button енкодера 1 - громкость
# таймер
btn_enc2 = Button(19)
btn_enc2.when_pressed = timer_onoff  # button енкодера 2 - таймер


# на немецком
#        speak_frase(11)
#        speak_frase(12)
#        speak_frase(13)
# 1 button - проигрывание случайной мелодии
# def set_btn01():
#    global volume_on, play_mus
#    if volume_on:
#        num_comp = random.randint(1, 45) # номер трека
#        player.playTrack(8, num_comp) #из папки 08 музыка
#        print('Кнопка 1: Проигрывание трека: ', num_comp)
#        time.sleep(1)
# Fisher-Yates shuffle algorithm
def fisher_yates_shuffle(lst):
    n = len(lst)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]


# Shuffle the playlist
fisher_yates_shuffle(playlist)


# Function to check if DFPlayer is busy
def is_dfplayer_busy():
    return (
        not DFPlayer_busy.value()
    )  # Pin is low when DFPlayer is busy, so we invert the value


def play_track():
    global current_track_index, play_on, playing
    if volume_on:
        print("playing:", playing)
        print("play_on:", play_on)
        print("Busy:", is_dfplayer_busy())

        if not is_dfplayer_busy() and play_on and not playing:
            print("***Play track:", current_track_index)
            current_track_index += 1
            if current_track_index >= len(playlist):
                fisher_yates_shuffle(
                    playlist
                )  # Reset the playlist when all tracks have been played
                current_track_index = 0
            num_comp = playlist[current_track_index]
            player.playTrack(8, num_comp)  # из папки 08 музыка
            print("Проигрывание трека:", num_comp)
            print("***Busy:", is_dfplayer_busy())
            playing = True
        time.sleep(1)  # Adjust the sleep duration as needed


# button 1 - проигрывание случайной мелодии
def set_btn01():
    global play_on, playing
    if playing:
        player.pause()  #
        print("***Stopped")
        play_on = False
        playing = False
    else:
        play_on = True  # играть трек
        print("Play track button pressed")
        print("play_on:", play_on)


# button 2 - проговаривание текущего времени, даты и года
def set_btn02():
    if volume_on:
        speak_frase(1)
        speak_frase(2)
        speak_frase(3)
        print("Кнопка 2 - проговаривание текущего времени, даты и года")
        # на немецком
        speak_frase(11)
        speak_frase(12)
        speak_frase(13)


#    speak_frase(4)
#    in_current_year = input ("Input Year: ")
#    in_current_month = input ("Input Month: ")
#    in_current_day = input ("Input Day: ")
#    in_current_num_day = input ("Input NumDay: ")
#    in_current_hour = input ("Input Hour: ")
#    in_current_minute = input ("Input Min: ")

#    current_year = int(in_current_year)
#    current_month = int(in_current_month)
#    current_day = int(in_current_day)
#    current_num_day = int(in_current_num_day)
#    current_hour = int(in_current_hour)
#    current_min = int(in_current_minute)

#    ds.date_time([current_year, current_month, current_day, current_num_day, current_hour, current_min, 0, 0]) # set datetime.
#    date_list = ds.date_time()


# button 3 - "выбор"
def set_btn03():
    if volume_on:
        # на немецком
        speak_frase(11)
        speak_frase(12)
        speak_frase(13)
        # на русском
        #        speak_frase(1)
        #        speak_frase(2)
        #        speak_frase(3)
        player.playTrack(18, 0)  # музыка боя
        time.sleep(17)
        boom_hour = hour_dict.get(4)
        if boom_hour > 12:
            boom_hour = boom_hour - 12
        player.playTrack(18, boom_hour)  # музыка боя
        time.sleep(1)
        print("3 button - выбор")


# button 4 - "минус"
def set_btn04():
    if volume_on:
        speak_frase(1)
        speak_frase(2)
        speak_frase(3)
        print("4 button - минус")


# на немецком
#        speak_frase(11)
#        speak_frase(12)
#        speak_frase(13)


# button 5 - "плюс"
def set_btn05():
    if volume_on:
        speak_frase(1)
        speak_frase(2)
        speak_frase(3)
        print("5 button - плюс")


# установка назначения кнопок с 1 по 5
# button 1 - проигрывание случайной мелодии
btn01 = Button(28)
btn01.when_pressed = set_btn01  # резерв
# button 2 проговаривание текущего времени
btn02 = Button(21)
btn02.when_pressed = set_btn02  # проговаривание текущего времени
# button 3 - "выбор"
btn03 = Button(22)
btn03.when_pressed = set_btn03  # button редактирования "выбор"
# button 4 - "минус"
btn5 = Button(26)
btn5.when_pressed = set_btn04  # button редактирования "минус"
# button 5 - "плюс"
btn05 = Button(27)
btn05.when_pressed = set_btn05  # button редактирования "плюс"

# main loop
while True:
    clear_spisok = [0, 1, 2, 3, 4, 5, 6]
    hour_dict = dict(zip(clear_spisok, ds.date_time()))
    current_hour = hour_dict.get(4)
    current_minute = hour_dict.get(5)
    current_year = hour_dict.get(0)
    current_month = hour_dict.get(1)
    current_day = hour_dict.get(2)
    current_dayname = hour_dict.get(3)
    curr_hour = str(current_hour)
    curr_min = str(current_minute)
    curr_day = str(current_day)
    curr_year = str(current_year)

    # установка громкости
    player.setVolume(s_volume)  # начальное 15, громкость: от 0 до 30
    time.sleep_ms(50)
    current_time = int(curr_hour + curr_min)  # текущее время в формате 'HHMM'
    print("Текущее время: ", "%02d:%02d" % (current_hour, current_minute))
    print("Громкость: ", s_volume)
    print("Номер будильника: ", num_alarm)
    print("Текущий будильник: ", num_alarm_spisok.get(num_alarm))
    print("Время таймера: ", current_timer_hour, total_minutes)
    print("Осталось минут: ", remaining_minutes)
    print("Таймер включен: ", timer_running)
    print("------------------------")
    # ===============
    # обработка проигрывания музыки
    # если играет - ничего не делать, если не играет - проверить должно ли играть
    # если да - включить следующий трек, если нет - ничего не делать
    play_track()
    # индикация звукового режима - звук вкл - курсор мигает
    if timer_running:
        lcd.move_to(15, 1)
        lcd.putstr("T")
    else:
        lcd.move_to(15, 1)
        lcd.putstr("S")

    if volume_on:
        lcd.move_to(2, 0)
        lcd.blink_cursor_on()
        lcd.show_cursor
    else:
        lcd.move_to(2, 0)
        lcd.blink_cursor_off()
        lcd.hide_cursor

    if current_minute != old_minute or flag_update:
        # выводим время
        print(
            f"{curr_hour:.2}"
            + ":"
            + f"{curr_min:.2}"
            + " Next Timer: "
            + "%02d" % (num_alarm_spisok.get(num_alarm))
        )
        print(
            f"{curr_day:.2}"
            + "-"
            + sp_month.get(current_month)
            + "-"
            + f"{curr_year:02}"
            + " "
            + sp_dayname.get(current_dayname)
        )
        print(num_alarm)
        num_day_len_spisok = {
            1: 10,
            2: 8,
            3: 8,
            4: 6,
            5: 9,
            6: 9,
            7: 9,
        }
        # позиции для вывода дня недели
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("%02d:%02d" % (current_hour, current_minute))
        lcd.move_to(
            num_day_len_spisok.get(current_dayname), 0
        )  # позиция вывода дня недели
        lcd.putstr(sp_dayname.get(current_dayname))
        lcd.move_to(0, 1)
        lcd.putstr(
            f"{curr_day:.2}"
            + "-"
            + sp_month.get(current_month)
            + "-"
            + f"{curr_year:4}"
            + " "
            + "%02d" % (minutes)
        )
        old_minute = current_minute  # флаг смены минуты
        time_spoken = False  # восстанавливаем флаг проговаривания каждого часа
        alarm_trigger = False  # восстанавливаем флаг срабатывания будильника
        flag_update = False  # сбросили флаг обновления экрана
    else:
        if current_hour != old_hour:
            # говорим время каждый час
            if (
                (current_hour >= work_time_start and current_hour <= work_time_end - 1)
                and current_minute == 0
                and not time_spoken
            ):
                # время, в течении которого разрешается говорить время каждый час
                speak_frase(1)
                # на немецком
                speak_frase(11)
                # бой курантов
                #                player.playTrack(18, 0) # музыка боя
                #                time.sleep(17)
                #                boom_hour = hour_dict.get(4)
                #                if boom_hour > 12:
                #                        boom_hour = boom_hour - 12
                #                player.playTrack(18, boom_hour) # бой количества часов
                #                time.sleep(1)

                old_minute = current_minute  # флаг смены минуты
                time_spoken = True

            if (
                (current_hour >= work_time_start and current_hour <= work_time_end - 1)
                and current_minute == 30
                and not time_spoken
            ):
                # время, в течении которого разрешается говорить время каждые пол-часа
                speak_frase(1)
                # на немецком
                speak_frase(11)
                # бой курантов один раз
                #                player.playTrack(18, 1) # бой один раз
                #                time.sleep(1)

                old_minute = current_minute  # флаг смены минуты
                time_spoken = True

        # таймер 1
        if current_time == num_alarm_spisok.get(num_alarm) and not alarm_trigger:
            # будильник совпал
            time.sleep(0.6)
            print("Будильник " + str(num_alarm) + "совпал")
            # выводим сообщение будильника и устанавливаем флаг срабатывания будильника
            alarm_trigger = True

        if alarm_trigger and not time_spoken:
            # проговаривание времени при совпадении будильника и первый раз
            player.playTrack(7, num_alarm)  # фраза "сработал будильник номер "
            time.sleep(1.5)
            speak_frase(1)  # время рус
            time.sleep(0.7)
            # на немецком
            player.playTrack(7, num_alarm)  # фраза "сработал будильник номер "
            time.sleep(1.5)
            speak_frase(11)  # время нем
            time_spoken = True
            num_alarm = num_alarm + 1
            if num_alarm > 5:
                num_alarm = 1

        if (
            current_hour == current_timer_hour
            and current_minute == total_minutes
            and timer_running
        ):
            # время таймера
            print("Сработал таймер!")
            player.playTrack(7, 11)  # сработал будильник номер
            time.sleep(0.7)
            player.playTrack(7, 13)  # сигнал
            #            time.sleep(0.6)
            timer_running = False

        elif alarm_trigger and current_time == num_alarm_spisok.get(num_alarm):
            # будильник сработал, но время еще не изменилось
            time.sleep(0.1)
        else:
            # время не совпадает, цикл
            time.sleep(0.1)
