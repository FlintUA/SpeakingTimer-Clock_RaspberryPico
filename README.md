# Speaking Timer-Clock on Raspberry Pi Pico
Speaking Timer-Clock on Raspberry Pi Pico (H/W)

Timer-clock with voice communication (1 timer up to 240 minutes, 5 fixed time points) and MP3 player based on Raspberry Pi Pico board, 1602 display with I2C module, RTC Clock DS1302 clock module, DFPlayer Mini MP3 player, 2 encoders with a button and a pull-up resistor 1K each, 5 additional buttons.

One encoder adjusts the volume, and a button on the encoder turns the sound on/off. The second encoder is designed to set the required number of minutes of the timer, the button on the encoder starts/stops the timer. The timer is not too accurate yet - the accuracy is approximate, from one minute, for example, setting the timer for 5 minutes can work after 4 minutes, but not less, because there is no concept of "seconds" in the device. There are 5 additional buttons for various additional functions. The display shows messages in German, voice messages in Russian and German. Every hour the time is announced, every half hour there is a short signal, there are sounds imitating the striking of an ancient clock. There is a silence mode (silent / night mode) from 22.00 to 7.00. While there is no setting mode, all settings are performed in the source code.

Таймер-часы с речевым соообщением (1 таймер до 240 минут, 5 фиксированных временных точек) и проигрывателем MP3 файлов на базе платы Raspberry Pi Pico, дисплей 1602 с модулем I2C, модуль часов RTC Clock DS1302,
проигрыватель MP3 файлов DFPlayer Mini, 2 енкодера с кнопкой и подтягивающим резитором 1кОм каждый, 5 дополнительных кнопок.

Один енкодер регулирует громкость, кнопка на енкодере включает/выключает звук.
Второй енкодер предназначается для установки необходимого количества минут таймера, кнопка на енкодере запускает/останавливает таймер.
Таймер пока не слишком точный - точность примерная, от одной минуты, например, выставив на 5 минут таймер может сработать и через 4 минуты, 
но не меньше, т.к. в устройстве нет понятия "секунд".
Есть 5 дополнительных кнопок для различных дополнительных функций.
На дисплее сообщения выводятся на немецком языке, голосовые сообщения на русском и немецком.
Каждый час проговаривается время, каждые пол-часа - короткий сигнал, есть звуки, имитирующие бой старинных часов.
Есть режим тишины (тихий/ночной режим) с 22.00 до 7.00.
Пока без режима настройки, все настройки выполняются в исходном коде.


