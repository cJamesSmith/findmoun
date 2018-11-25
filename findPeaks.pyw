"""
Author: Chen xianwei
Chukochen Honor College & Control Science And Engineering College ,Zhejiang University
Date: 2018/11/10
Version: 1.0
Function: Analyzing texts which include large amount of moun data. This program can not only identify the moun, but calculate the lifetime of each moun and do statistical analysis.
"""
#coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import peakutils
import os
import sys

def main():

    #statistical array
    distribute = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #average lifetime 
    ave_time = 0.0

    #number of moun 
    num_of_moun = 0

    #folder that contains the texts
    #PLEASE INPUT THE FILENAME WITH QUOTATION MARKS ON EACH SIDE
    #eg.
    #python .\peakutilsFindPeaks.py "C:\Users\chenb\Documents\Tencent Files\706499321\FileRecv\500M\\"
    if len(sys.argv) < 2:
        print('Sorry! Please input the foldername.')
        exit()

    elif len(sys.argv) > 2:
        print('Sorry! Please input only one foldername.')
        exit()

    else:
        folder = sys.argv[1]

    try:
        num_of_file = len(os.listdir(folder))

    except:
        print('Sorry! Please input the right form of the folder.\n' + 'eg.\n' +
             '#python peakutilsFindPeaks.py "C:\\Users\\chenb\\Documents\\Tencent Files\\706499321\\FileRecv\\500M\\\\\"')
    else:
        for i in range(1, 1000):
            filename = folder + str(i) + ".txt"

            try:
                #read x coordinate from the text
                x = np.loadtxt(filename,  delimiter='\t',  usecols = (0,),  dtype = float)
                #read y coordinate from the text
                y = np.loadtxt(filename,  delimiter='\t',  usecols = (1,),  dtype = float)

            except IOError:
            #    print('file not found')
                continue

            else:

                #fourier filtering 
                y = np.fft.rfft(y)

                #change the level of filtering
                for j in range(len(y)):
                    y[j] = -y[j]
                    if abs(y[j]) < 30:
                        y[j] = 0

                #fourier filtering 
                y = np.fft.irfft(y)

                #using peakutils to find the peaks, change the parameter when needed
                indexes = peakutils.indexes(y, thres=0.2, min_dist=20)

                #confirm if it is a moun, change the condition when needed 
                #if (len(indexes) == 2 and indexes[1] - indexes[0] > 60 and
                #   abs((y[indexes[0]] - y[indexes[1]]) / (x[indexes[0]] - x[indexes[1]])) < 1070000 and
                #   y[int((indexes[0] + indexes[1]) / 2)] < (0.9 * min(y[indexes[0]], y[indexes[1]]))):

                if (len(indexes) >= 2 and
                   y[int((indexes[0] + indexes[1]) / 2)] < (0.9 * min(y[indexes[0]], y[indexes[1]]))):

                #if True:
            
                    #画图
                    #print(filename, indexes, x[indexes[1]] - x[indexes[0]])
                    plt.plot(x, y)
                    plt.plot(x[indexes], y[indexes], 'o-r')
                    plt.savefig(folder + str(i) + '.jpg')
                    plt.close()
                    #plt.show()
                    #print(x[indexes[1]] - x[indexes[0]])

                    #if it is a moun, do statistical things
                    if x[indexes[1]] - x[indexes[0]] < 1e-6:
                        distribute[0] += 1
                    elif 1e-6 <= x[indexes[1]] - x[indexes[0]] < 2e-6:
                        distribute[1] += 1
                    elif 2e-6 <= x[indexes[1]] - x[indexes[0]] < 3e-6:
                        distribute[2] += 1
                    elif 3e-6 <= x[indexes[1]] - x[indexes[0]] < 4e-6:
                        distribute[3] += 1
                    elif 4e-6 <= x[indexes[1]] - x[indexes[0]] < 5e-6:
                        distribute[4] += 1
                    elif 5e-6 <= x[indexes[1]] - x[indexes[0]] < 6e-6:
                        distribute[5] += 1
                    elif 6e-6 <= x[indexes[1]] - x[indexes[0]] < 7e-6:
                        distribute[6] += 1
                    elif 7e-6 <= x[indexes[1]] - x[indexes[0]] < 8e-6:
                        distribute[7] += 1
                    elif 8e-6 <= x[indexes[1]] - x[indexes[0]] < 9e-6:
                        distribute[8] += 1
                    elif 9e-6 <= x[indexes[1]] - x[indexes[0]] < 10e-6:
                        distribute[9] += 1
                    else:
                        distribute[10] += 1

                    print(distribute)
                    ave_time += x[indexes[1]] - x[indexes[0]]

        #how many mouns were found
        for item in distribute:
            num_of_moun += item

        try:
            ave_time /= num_of_moun

        except ZeroDivisionError:
            #show the statistical result
            plt.bar(range(len(distribute)), distribute)
            plt.title('Sorry! No moun!')
            plt.savefig(folder + 'finalDistribution.jpg')

        else:
            #show the statistical result
            plt.bar(range(len(distribute)), distribute)
            plt.title('The number of moun is ' + str(num_of_moun) + '\n' + 'The average lifetime is ' + str(ave_time))
            plt.savefig(folder + 'finalDistribution.jpg')
            plt.close()

if __name__ == '__main__':
    main()