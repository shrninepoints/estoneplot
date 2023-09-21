import os

specific_line = 'ZCURVE	TABLE'
          
folder_path = '/Users/macbookpro/projects/misc/estoneplot/data'


def processing(input_file, output_file, target_line):
    """
    Discard all lines in the input_file before the target_line and write the remaining lines to output_file.
    
    Parameters:
    - input_file: Path to the input file.
    - output_file: Path to the output file.
    - target_line: The line after which the content should be retained.
    """
    with open(input_file, 'r', encoding='ISO-8859-1') as f:
        lines = f.readlines()
        
    # Find the index of the target line
    try:
        start_index = lines.index(target_line + '\n')
    except ValueError:
        print(f"'{target_line}' not found in the file.")
        return
    
    # Write the lines after the target line to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in lines[start_index+1:]:
            f.write(line.lstrip('\t'))
            
for filename in os.listdir(folder_path):
    if filename.endswith('.DTA'):
        file_path = os.path.abspath(os.path.join(folder_path, filename)) # absolute path to the file
        print(f"Processed File: {file_path}")
        
        with open('your_file.txt', 'r') as file:
            # Read the first line
            first_line = file.readline()
            
            # Check if the first line contains a certain string
            if 'EXPLAIN' in first_line:
                output_file_path = file_path[:len(file_path)-4]+"_temp.txt"
                processing(file_path, output_file_path, specific_line)            
            else:
                print("The first line does not contain 'your_string'.")
        
        output_file_path = file_path[:len(file_path)-4]+"_temp.txt"
        processing(file_path, output_file_path, specific_line)
        
  
