import matplotlib.pyplot as plt
import numpy as np
import os

folder_path = '/Users/macbookpro/projects/misc/estoneplot/data'

prefactor_Zreal = 1
prefactor_Zimg = 1


colors = ['blue', 'red', 'green', 'purple', 'black', 'orange']
experiment_index = 0

table_data = []
F_data = []

plt.figure()

for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.abspath(os.path.join(folder_path, filename)) # absolute path to the file
        print(f"Plotted File: {file_path}")
        data = np.genfromtxt(file_path, delimiter="\t", skip_header=2)
                
        # Extract F data
        #arr[np.argmax(arr[:, 1])]
        filtered_rows = data[data[:, 4] < 0]
        i = np.argmin(filtered_rows[:, 3])
        F1 = filtered_rows[i, 2]
        i = np.argmin(data[:, 4])
        F2 = data[i, 2]
        F3 = min(data[:,2])
        print(F1,F2,F3)
        F_data.append([experiment_index+1, F1, F2, F3])
        
        # Make scatter plot
        extracted_data = data[:, [3, 4]]
        # Filter the data where y values are <= 0
        mask = extracted_data[:, 1] <= 0
        filtered_data = extracted_data[mask]
        # Split the data into x and y for plotting
        x = filtered_data[:, 0] * prefactor_Zreal
        y = filtered_data[:, 1] * prefactor_Zimg
        # Plot the data
        plt.scatter(x, -y, marker='o', edgecolor=colors[experiment_index], facecolor='none', s=25, label = experiment_index + 1)  # s controls the size of the circles
        experiment_index += 1
        
        # Extract table data
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

# Add the table to the plot
table = ax.table(cellText=table_data, colLabels=column_labels, loc='center', cellLoc='center', bbox=[0.1, 0.5, 0.2, 0.4]) # bbox = [left, bottom, width, height]
linewidth = 0.5  # Adjust this value as needed
for key, cell in table.get_celld().items():
    cell.set_linewidth(linewidth)
table.auto_set_font_size(False)
table.set_fontsize(5)
table.set_transform(ax.transAxes)
plt.savefig(folder_path+'/temp1.pdf')

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
plt.savefig(folder_path+'/temp2.pdf')
plt.show()