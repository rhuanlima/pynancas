import sqlite3
from sqlite3 import Error
import pandas as pd
import os
from abc import ABC

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

class DB_Manager(ABC):
    def __init__(self):
        pass

    def _fix_file(self, p_file:str, p_file2:str)->None:
        """
        Fix the file to be able to import it into the database
        Args:
            p_file (str): path to the file to be fixed
            p_file2 (str): path to the file to be saved
        """

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

    def read_file(self, p_file:str)->None:
        """
        Read a file and save it into a dataframe
        Args:
            p_file (str): path to the file to be read
        """
        self._fix_file(p_file, 'temp.file')
        self._fix_file('temp.file', 'temp1.file')
        df = pd.read_csv('temp.file', sep=';',encoding='utf-8')
        os.remove('temp.file')
        os.remove('temp1.file')
        return df
