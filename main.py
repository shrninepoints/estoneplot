import os
import numpy as np
import matplotlib.pyplot as plt

directory = '/Users/macbookpro/projects/misc/estoneplot/t'
path_to_config = ''


def list_txt_files(directory):
    """
    List all the .txt files in the given directory and its sub-directories.
    txt_files is the absolute path to every txt file.
    """
    txt_files = []
    
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.txt'):
                txt_files.append(os.path.join(foldername, filename))
    txt_files.sort()
    return txt_files
        
def processing_type1(input_file):
    """
    Discard all lines in the input_file for TYPE 1 data. 
    Return a np.array containing interested data
    
    Parameters:
    - input_file: Path to the input file.
    - output_file: Path to the output file.
    """
    file_name = os.path.basename(input_file)
    if 'eis' in file_name: # TYPE 1 EIS
        data = np.genfromtxt(input_file, delimiter="\t", encoding='utf-16le', skip_header=102)
        extracted_data = data[:,[3,4,5]] # Frequency, Zreal, Zimg
    elif 'lsv' in file_name: # TYPE 1 LSV
        data = np.genfromtxt(input_file, delimiter="\t", encoding='utf-16le', skip_header=85)
        extracted_data = data[:,[3,4]]  # V, I
    else:
        print(f'Warning: The file {file_name} is of unknown format.')
        return None
    return extracted_data

def processing_type2(input_file):
    """
    Discard all lines in the input_file for TYPE 1 data. 
    Return a np.array containing interested data
    
    Parameters:
    - input_file: Path to the input file.
    - output_file: Path to the output file.
    """
    file_name = os.path.basename(input_file)
    if 'eis' in file_name: # TYPE 1 EIS
        data = np.genfromtxt(input_file, delimiter="\t", encoding='utf-16le', skip_header=2)
        extracted_data = data[:,[4,1,2]] # Frequency, Zreal, Zimg
    elif 'lsv' in file_name: # TYPE 1 LSV
        data = np.genfromtxt(input_file, delimiter="\t", encoding='utf-16le', skip_header=2)
        extracted_data = data[:,[1,2]]  # V, I
    else:
        print(f'Warning: The file {file_name} is of unknown format.')
        return None
    return extracted_data
 
def cleanup_data(data):
    '''
    Input is a 2d np.array of data.
    This is only for eis data.
    '''
    # Compute Q1 and Q3
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)

    # Compute IQR
    IQR = Q3 - Q1

    # Determine bounds
    k = 3
    lower_bound = Q1 - k * IQR
    upper_bound = Q3 + k * IQR
    filtered_data = data[(data[:,1] > lower_bound) & (data[:,1] < upper_bound)]
    return filtered_data

def load_data():
    txt_files = list_txt_files(directory) # a list contain absolute path to all txt files
    data_list = []
    
    eis = all('eis' in os.path.basename(s) for s in txt_files)
    lsv = all('lsv' in os.path.basename(s) for s in txt_files)
    
    if eis and not lsv: 
        print('EIS plot processing...')
    elif not eis and lsv:
        print('LSV plot processing...')
    else:
        raise ValueError('Incorrect eis/lsv type of file.')
            
    
    for txt_file in txt_files:
        file_name = os.path.basename(txt_file)

        with open(txt_file, 'r', encoding='utf-16le') as f:
            first_line = f.readline()
            if 'EXPLAIN' in first_line:  # If the file is in format of TYPE 1, first line start with "EXPLAIN"
                data = processing_type1(input_file=txt_file)
                data = cleanup_data(data)
                data_list.append(data)
            elif 'Segment' in first_line: # If the file is in format of TYPE 2, first line start with "Segment"
                data = processing_type2(input_file=txt_file)
                data = cleanup_data(data)
                data_list.append(data)
            else:
                raise ValueError(f'The file {txt_file} is of unknown format.')
        print(f'{file_name} successfully loaded.')
    return data_list

def plot(data_list):
    data = data_list[0]
    num_column = len(data[0])
    if num_column == 2:
        plot_lsv(data_list)
    elif num_column == 3:
        plot_eis(data_list)
        
def plot_eis(data_list):
    # Settings
    prefactor_Zreal = 1
    prefactor_Zimg = 1
    colors = ['r', 'b', 'g', 'y', 'c', 'm', 'k']

    # Initialize
    experiment_index = 0
    table_data = []
    F_data = []

    plt.figure()
    for data in data_list:
        # Extract F data
        filtered_rows = data[data[:, 2] < 0]
        i = np.argmin(filtered_rows[:, 1])
        F1 = filtered_rows[i, 0] # the frequency for smallest Zreal with Zimg > 0
        i = np.argmin(data[:, 2])
        F2 = data[i, 0] # the frequency for largest Zimg
        F3 = min(data[:,0]) # the smallest frequency
        print(F1,F2,F3)
        F_data.append([experiment_index+1, F1, F2, F3])
        
        # Make scatter plot

        # Split the data into x and y for plotting
        x = filtered_rows[:, 1] * prefactor_Zreal
        y = filtered_rows[:, 2] * prefactor_Zimg
        # Plot the data
        plt.scatter(x, -y, marker='o', edgecolor=colors[experiment_index], facecolor='none', s=25, label = experiment_index + 1)  # s controls the size of the circles
        experiment_index += 1
        
        # Extract table data
        print("experiment_index ", experiment_index)    
        print('Ohm: ',min(x), '\nPolarization: ', max(x)-min(x))
        table_data.append([experiment_index, round(min(x),4), round(max(x)-min(x),4)])
        
        
    # Continue make scatter plot        
    plt.xlabel('Z\'')
    plt.ylabel('-Z\'\'')
    plt.title('Some title')
    plt.grid(False)
    plt.legend()  # Display legend

    # Manually set the range for x and y axes
    x_min, x_max = 0, 1  # Change these values as needed
    y_min, y_max = 0, 0.4  # Change these values as needed

    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    plt.gca().set_aspect('equal', adjustable='box')

    # Make small table inside the scatter plot
    ax = plt.gca()
    column_labels = ["", "Ohm", "Polarization"]
    table = ax.table(cellText=table_data, colLabels=column_labels, loc='center', cellLoc='center', bbox=[0.1, 0.5, 0.2, 0.4]) # bbox = [left, bottom, width, height]
    linewidth = 0.5  # Adjust this value as needed
    for key, cell in table.get_celld().items():
        cell.set_linewidth(linewidth)
    table.auto_set_font_size(False)
    table.set_fontsize(5)
    table.set_transform(ax.transAxes)
    plt.savefig(directory+'/eis_plot.pdf')

    plt.show()
    plt.close('all')

    # Make F table
    plt.figure()
    F_labels = ['', 'F1', 'F2', 'F3']
    ax = plt.gca()
    ax.axis('off')  # Turn off the axis
    table = plt.table(cellText=F_data, colLabels=F_labels, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(column_labels))))  # Adjust column width to fit the content
    plt.title("Second Plot - Table")
    plt.savefig(directory+'/eis_plot_table.pdf')
    plt.show()

def plot_lsv(data_list):
    colors = ['r', 'b', 'g', 'y', 'c', 'm', 'k']
    
    prefactor_power = 1/Users/macbookpro/projects/misc/estoneplot/preprocessing_new.py
    
    experiment_index = 0
    table_data = []

    # Function to plot series and the modified series [x, x*y]
    def plot_series(data, experiment_index):
        x = data[:, 1]
        y = data[:, 0]
        ax1.plot(-x, y, color = colors[experiment_index-1], label='V'+ str(experiment_index))  # Original data
        ax2.plot(-x, abs(x*y)*prefactor_power, '--',color = colors[experiment_index-1], label='P' + str(experiment_index))  # Modified series
        
        ppd = max(abs(x*y)*prefactor_power) # peak power density
        i = np.argmin(abs(data[:, 1]))        
        ocv = data[i,0]# open circuit voltage
        return ppd, ocv
        
    # Plotting
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    for data in data_list: 
        experiment_index += 1   
        print("experiment_index ", experiment_index)    
        ppd, ocv = plot_series(data,experiment_index)
        
        # Extract table data
        print('PPD: ',ppd, '\nOCV: ', ocv)
        table_data.append([experiment_index,round(ocv,4),round(ppd,4)])

    ax1.legend(loc='upper left')
    ax1.set_xlabel('I')
    ax1.set_ylabel('V', color='black')
    ax2.set_ylabel('P', color='black')
    ax1.grid(True)
    plt.title('Multiple Series Plot')
    plt.grid(False)
    
    # Make small table inside the scatter plot
    ax = plt.gca()
    column_labels = ["", "OCV", "PPD"]
    table = ax.table(cellText=table_data, colLabels=column_labels, loc='center', cellLoc='center', bbox=[0.15, 0.1, 0.3, 0.2]) # bbox = [left, bottom, width, height]

    linewidth = 0.5  # Adjust this value as needed
    for (i,j), cell in table.get_celld().items():
        cell.set_linewidth(linewidth)
        if j == 0:  # If it's the first column
            cell.set_width(0.1)

    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.set_transform(ax.transAxes)
    plt.savefig(directory+'/lsv_plot.pdf')
    print("Plot saved to "+directory+'/lsv_plot.pdf')
    plt.show()



if __name__ == "__main__":
    plot(load_data())
