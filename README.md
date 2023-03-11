# SERIAL DATA MONITOR

## 1. Description
App that allows user to monitor in real-time data sent through the serial port and export them to a CSV file. The main goal of the project was to provide a simply tool which will collect data from the sensors connected to the MCU (ex. as a ESP or Arduino boards) and save them for further analyze. 

## 2. Functionality
* establishing connection via serial port by setting COM port, baudrate and time interval,
* collecting and presenting data in tabular and graph form,
* displaying current data points and highlight their extremum and avarage values,
* recording time tracking with possibility to stop and resume program,
* ability to receive and compare two different datasets,
* export collected data to a CSV file.

## 3. Used technology
Python 3 with specified libraries:  
* Tkinter,  
* pySerial,  
* pandas,  
* matplotlib.

## 4. Important notes
Each data point sent to the program must be placed in new line (separated by a newline character).

App allows to monitor max. 2 datasets (DS) at the same time - in that case they should be separated by a comma.

Example of correct data frame sent to the app:
1) One dataset: "DS1\\nDS1\\nDS1..."
2) Two datasets: "DS1,DS2\\nDS1,DS2\\nDS1,DS2..."

## 5. Showcase
![Alt text](Images/GIF/SDM_GIF.gif)