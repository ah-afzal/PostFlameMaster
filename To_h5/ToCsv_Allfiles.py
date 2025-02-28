
import os
from ToCsv_Onefile import onefile_csv

def allfile_csv():
    directory = 'OutSteady'
    new_directory = 'flamelets'
    
    os.makedirs(new_directory,exist_ok=True)
    directs=os.listdir(directory)
    os.chdir(directory)
    
    for filename in directs:
        print(filename)
        
        onefile_csv(filename)
    os.chdir('..')
if __name__ == "__main__":
    allfile_csv()
