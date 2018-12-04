#!/usr/bin/env python3
#compare csv files

import sys
import csv

def checkInputExists(csvfile):
    try:
        with open(csvfile) as file:
            pass
    except IOError as e:
        print("Unable to open " + csvfile)
        raise SystemExit(22)

def readFile(csvfile):
    #Return a list of values in csv_file, len of rows, len of columns
    #if the number of columns is not consistent, raise an error
    val_list = []
    len_col = 0
    header = []
    with open(csvfile, 'r') as file:
        reader = csv.reader(file, dialect='excel')
        for row in reader:
            row = list(filter(lambda x: x != '', row))
            for col in range(len(row)):
                try:
                    row[col] = int(row[col])
                except ValueError:
                    try:
                        row[col] = float(row[col])
                    except ValueError:
                        row[col] = str(row[col])
            val_list.append(row)
    len_col = len(row)
    for row in val_list:
        if len(row) != len_col:
            #check that the number of cols is always same
            print("Error - Inconsistent number of columns in " + csvfile)
            raise SystemExit(22)
    return val_list, len(val_list), len_col

def compareFileSizes(csv1_row, csv2_row, csv1_col, csv2_col):
    if csv1_row == csv2_row:
        print('Common number of rows: ' + str(csv1_row))
    else:
        print('Error - The number of rows are different: '
        + str(csv1_row) + '<>' + str(csv2_row))
        raise SystemExit(99)

    if csv1_col == csv2_col:
        print('Common number of columns: ' + str(csv1_col))
    else:
        print('Error - The number of columns are different: '
        + str(csv1_col) + '<>' + str(csv2_col))
        raise SystemExit(99)

def computeDif(len_row, len_col, csv1_vals, csv2_vals):
    print("Compute relative and absolute difference")
    rdif_max = float(0)
    adif_max = float(0)
    for r in range(len_row):
        for c in range(len_col):
            if type(csv1_vals[r][c]) is str:
                if csv1_vals[r][c].strip() == csv2_vals[r][c].strip():
                    adif = 0
                    rdif = 0
                else:
                    print("Error in comparison of strings: "
                    + csv1_vals[r][c] + " differs from "
                    + csv2csv1_vals[r][c])
                    raise SystemExit(99)
            else:
                adif = abs(csv1_vals[r][c] - csv2_vals[r][c])
                if adif == 0:
                    rdif = 0
                else:
                    rdif = 2 * adif / abs(csv1_vals[r][c] + csv2_vals[r][c])
            if adif > adif_max:
                adif_max = adif
            if rdif > rdif_max:
                rdif_max = rdif

    print("Max Relative Difference  :" + str(rdif_max))
    print("Max Absolute Difference  :" + str(adif_max))
    return adif_max, rdif_max

if __name__ == "__main__":
    #Get command line arguments
    '''
    1: csv_file 1
    2: csv_file 2
    3: relative tolerance
    4: absolute tolerance
    5: variables you want to check
    '''
    len_arg = len(sys.argv)
    if len_arg < 3 or len_arg > 5:
        print("Error - A minimum 2 and a maximum 4 arguments can be used")
        raise SystemExit(22)
    csv1 = sys.argv[1]
    csv2 = sys.argv[2]

    if len_arg > 3:
        relative = float(sys.argv[3])
    else:
        relative = float(0)

    if len_arg > 4:
        absolute = float(sys.argv[4])
    else:
        absolute = float(0)

    #Print current variables
    print("---------------------------------------------")
    print("Comparing CSV files")
    print("1st CSV file         :" + csv1)
    print("2nd CSV file         :" + csv2)
    print("Relative tolerance   :" + str(relative))
    print("Absolute tolerance   :" + str(absolute))
    print("---------------------------------------------")

    print("Test if input files exist")
    checkInputExists(csv1)
    checkInputExists(csv2)
    print("Success -- input files exist")

    print("Read all files")
    csv1_vals, csv1_row, csv1_col = readFile(csv1)
    csv2_vals, csv2_row, csv2_col = readFile(csv2)

    compareFileSizes(csv1_row, csv2_row, csv1_col, csv2_col)
    print("File Sizes are the same")

    adif_max, rdif_max = computeDif(csv1_row, csv1_col, csv1_vals, csv2_vals)
    if rdif_max > relative:
        print("Unacceptable relative difference")
        raise SystemExit(99)
    if adif_max > absolute:
        print("Unacceptable relative difference")
        raise SystemExit(99)

    print("CSV files similar!")
    print("Passed All Tests!")
