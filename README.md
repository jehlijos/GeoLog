# GeoLog
<img src="readme_files/baner.png" alt="GeoLog banner"/> <br>
**User interface for recording tourist-visited municipalities** <br>
<br>
- Tkinter user interface <br>
- Displaying territorial units in a Matplotlib graph (with zoom) <br>
- User account selection, creation, and deletion as tables in a local database <br>
- Manual addition and deletion of visited municipalities <br>
- Support for adding municipalities based on coordinates from the output of the Stopař (tracking module) feature from Mapy.cz (GPX file) <br>
- Visited municipalities filtering based on date of visiting <br>
- Statistics of visited municipalities in state, regions and districts <br>
- Support for all basic windows resolutions <br><br>

## Used Data  <br>
- Spatial data - [ArcČR 4.1](https://www.arcdata.cz/cs-cz/produkty/data/arccr)
- [icon](https://icon-icons.com/icon/nearby-map-location-address/88844)
- Tkinter theme - [Azure-ttk-theme](https://github.com/rdbende/Azure-ttk-theme/)
- [Calendar icon](https://www.iconfinder.com/icons/8664796/calendar_days_icon) , [Statistics icon](https://www.iconfinder.com/icons/2849805/pie_chart_stats_multimedia_statistics_icon) -  [license]( https://creativecommons.org/licenses/by/4.0/)
## Funcionality  <br>
In first combobox in settings panel you can pick a region to zoom to. <br>
![In first combobox in settings panel you can pick a region to zoom to](readme_files/1.png)  <br> <br>
This action will unlock second combobox where you can pick a district to zoom to.   <br>
![second combobox where you can pick a district to zoom to](readme_files/2.png)  <br><br>
In second part od the settings panel you can open user settings window.  <br>
In the combobox there you can select an existing user. <br>
![Clicking the green button in this panel will take you to a new panel where you can create an new user.](readme_files/3.png) <br><br>
Clicking the green button in this panel will take you to a new panel where you can create an new user. <br>
![In second part od the settings panel you can open user settings window.](readme_files/4.png)<br><br>
By clicking on the orange button in the user settings panel will open a window where you can delete an existing user. <br>
![By clicking on the orange button in the user settings panel will open a window where you can delete an existing user.](readme_files/5.png)<br><br>
By clicking on the green button in settings panel, new panel will appear, where you can add visited municipality. <br>
based on region and district where it lays. You can also choose a day of visiting. <br>
![By clicking on the green button in settings panel, new panel will appear, where you can add visited municipality](readme_files/6.png) <br><br>
By clicking on the orange button in settings panel, new panel will appear, where you can remove visited municipality. <br>
![By clicking on the green button in settings panel, new panel will appear, where you can add visited municipality](readme_files/7.png) <br><br>
By clicking on the light green button in settings panel, new panel will appear, where you can load GPX file from Stopař module made by Mapy.cz or any other <br>
![By clicking on the light green button in settings panel, new panel will appear, where you can load GPX file from Stopař module made by Mapy.cz or any other](readme_files/8.png) <br><br>
In this window you can find your GPX file by pressing the grey "Načti soubor" button. <br>
![In this window you can find your GPX file by pressing the grey "Načti soubor" button.](readme_files/9.png) <br><br>
Upon selecting your file, you can confirm your selection by clicking the light green button below and add municipalities that you have visited. <br>
![Upon selecting your file, you can confirm your selection by clicking the light green button below and add municipalities that you have visited.](readme_files/10.png) <br><br>
You can enter date selection window by pressing the calendar icon.<br>
![You can enter date selection window by pressing the calendar icon.](readme_files/11.png) <br><br>
Insert range of dates from you want to filter your visited municipalities and confirm your selection by button below.<br>
You will be able to see your visited municipalities with dates in text window below.<br>
![Insert range of dates from you want to filter your visited municipalities and confirm your selection by button below.](readme_files/12.png) <br><br>
Upon clicking the piechart button, window with statistics will appear.<br>
![Upon clicking the piechart button, window with statistics will appear.](readme_files/13.png) <br><br>
In this statistics window you can se percentages of visited municipalities in the Republic and in its regions.<br>
Use the scrollbar on the right to see all regions or click the button to see district statistic. <br>
![Upon clicking the piechart button, window with statistics will appear.](readme_files/14.png) <br><br>
Now you can see the three most visited districts. Select a district to show its statistics in a new window.<br>
![Now you can see the three most visited districts. Select a district to show its statistics in a new window.](readme_files/15.png)<br>
![The new window.](readme_files/16.png)<br><br>
Upon each addition or removal of a municipality or when a user is changed, the map window updates, and the visited municipalities in the currently selected zoom level are colored in red.<br>
![Upon each addition or removal of a municipality or when a user is changed, the map window updates, and the visited municipalities in the currently selected zoom level are colored in red.](readme_files/17.png) <br> <br>
## How to track your path with Mapy.cz phone app  <br>
To record your route, you will need the mobile application "Mapy.cz". You can download it from Google Play or the App Store. After launching the application, go to the menu and click on the button "Spustit Stopaře" ("Start Hitchhiking").

<img src="readme_files/ST1.png">

To start recording, click on "START". If you want to reduce the size of the resulting file, use the sliders below. Your route is now being recorded.

<img src="readme_files/ST2.png">

Now you can track your route on your phone screen or lock your phone and continue your journey.

<img src="readme_files/ST3.png">

After completing your route, click on the pause button and then on the right arrow.

<img src="readme_files/ST4.png">

Now click on the "UKONČIT A ULOŽIT" ("FINISH AND SAVE") button; there is no need to configure anything on the next screen. Just click on the "DÁLE" ("NEXT") button.

<img src="readme_files/ST5.png">

Click on save, and then again in the main menu, open the "Moje mapy" ("My Maps") tab.

<img src="readme_files/ST6.png">

For your selected (last) route, click on the three dots and choose the option "Exportovat" ("Export").

<img src="readme_files/ST7.png">

Now the route file (.gpx) is saved on your device. After clicking on the "SDÍLET" ("SHARE") button, you can share this file with your computer.

<img src="readme_files/ST8.png">
