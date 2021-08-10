import sqlite3
from sqlite3 import Error
import pandas as pd
import os

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return conn


def fix_file(p_file, p_file2):
    file = open(p_file,'r')
    file2 = open(p_file2,'w')

    save_line = ''
    for line in file:
        if save_line != '':
            file2.write(save_line + line)
            save_line = ''
        elif 'sep=;' in line:
            pass
        elif '"Nome"' in line:
            file2.write(line[:-1]+';""\n')
        elif line[-2] != '\"':
            save_line = line[:-1]
        else:
            file2.write(line)
    file.close()
    file2.close()

fix_file('data/import/data.csv','data/import/data2.csv')
fix_file('data/import/data2.csv','data/import/data3.csv')

df = pd.read_csv('data/import/data3.csv', sep=';', encoding='utf-8')

os.remove('data/import/data3.csv')
os.remove('data/import/data2.csv')

df