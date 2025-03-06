import pandas as pd
import numpy as np
import os
def onefile_csv(file_path):
    if(file_path=='speciestranslated'):#it's not required
        return
    if(file_path[-4:].isdigit()):
        
     T_st=float(file_path[-4:])
    else:
     T_st=float(file_path[-3:])   
     #stores the stoichiometric T
    
    c_vars=["H2O"]#progress variable list
    
    
    data = {} #dictionary to store values of each variable
    current_variable = None
    
    
    # Read the file and store all the lines
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    # get the stoichiometrix mixture fraction   
    parts =lines[1].split()[-2]
    z_st=float(parts)
    
    i=5 #current line(skipped first 5)
    while i < len(lines): #loop till last line
        if lines[i].startswith('\t'): 
            float_values = [float(value) for value in lines[i].split('\t') if value.strip()]#if to skip empty
            for each_val in float_values:
                data[current_variable].append(each_val) 
            
        else: #initialiing each key in dictionary
            if lines[i][:4]=='mass':
                current_variable = lines[i][13:-1] #extracts chemical formula
            elif lines[i][-2]==']':#remove units from variable name
                current_variable = lines[i].split()[0]                
            else:    
                current_variable = lines[i][:-1]
            
            
            data[current_variable] = []  # Create a new list if the key doesn't exist
        
            
        i+=1
    
    
    #finds the values of progVar at Z_st
    z_diff=[x - z_st for x in data['Z'] ]
    ind = np.argmax([num for num in z_diff if num < 0])
    sum=0
    
    for vars in c_vars:
            
          sum+=np.interp(z_st,[data['Z'][ind],data['Z'][ind+1]],[data[vars][ind],data[vars][ind+1]])
        
    data['T'] = data.pop('temperature')
    data['rho'] = data.pop('density')
    
    progVar = np.zeros(len(data['rho']))
    prodRateProgVar = np.zeros(len(data['rho']))
    for vars in c_vars:
        progVar+=data[vars]
        prodRateProgVar+=data["ProdRate"+vars]        
    data['ProgressVariable']=progVar
    data['ProdRateProgressVariable']=prodRateProgVar
    
    #data['ProgressVariable']=data.pop('ProgVar')
    #data['ProdRateProgressVariable']=data.pop('ProdRateProgVar')
    
    data['D'] = []

    
    for n in range(len(data['Z'])):
        data['D'].append(data['mu'][n]/data['rho'][n])
    
    data['SquareProgVar'] = np.array(data['ProgressVariable'])**2
    data['ProgVarProdRate']=np.array(data['ProdRateProgressVariable'])*np.array(data['ProgressVariable'])
    
    df = pd.DataFrame(data)
    
    
    var_names=list(data.keys())
    
    folder_name = 'flamelets'

# Get the parent directory path
    os.chdir('..')
    parent_folder = os.path.join(os.getcwd(), os.pardir)[:-2]
    output_folder = os.path.join(parent_folder, folder_name)
    output_file = os.path.join(output_folder, 'Tst_' + str(T_st) + '_c_st_' + str(round(sum, 7)) + '.csv')
    os.chdir('OutSteady')
    np.savetxt(output_file,
                  df,
                  fmt = '%12.6e',
                  delimiter = ',',header = ','.join(var_names),
                  comments='')
    return
        
    
  
