from scipy import stats
import mysql.connector
from mysql.connector import Error
import os.path

x = []
y = []

# Test connection to database
# Test extraction of data
try:
    db_connection = mysql.connector.connect(host='host',
                                         database='database',
                                         user='user',
                                         password='password')

    if db_connection.is_connected():
        db_interaction = db_connection.cursor()

        db_interaction.execute('CREATE DATABASE IF NOT EXISTS nonogram;')

        db_interaction.execute('USE nonogram;')

        create_line_table = 'CREATE TABLE IF NOT EXISTS line (line_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, length TINYINT(4) NOT NULL);'
        db_interaction.execute(create_line_table)
        # from_edge refers to blocks from top or left end
        create_data_table = 'CREATE TABLE IF NOT EXISTS data (data_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, line_id INTEGER(11) NOT NULL, succession TINYINT(4) NOT NULL, from_edge TINYINT(4) NOT NULL, block_number TINYINT(4) NOT NULL, longest_block TINYINT(4) NOT NULL, FOREIGN KEY (line_id) REFERENCES line(line_id));'
        db_interaction.execute(create_data_table)

        db_interaction.execute("SELECT line_id FROM line")
        line_results = db_interaction.fetchall()
        for line_id in line_results:
            x.append(line_id[0])

        second_db_interaction = db_connection.cursor()
        second_db_interaction.execute("SELECT length FROM line")
        length_results = second_db_interaction.fetchall()
        for length in length_results:
            y.append(length[0])
except Error as error:
    print("Error while connecting to MySQL", error)
finally:
    if (db_connection.is_connected()):
        db_interaction.close()
        second_db_interaction.close()
        db_connection.close()

# Test storing data in file and extracting them
if os.path.isfile('x_values.txt'):
    with open('x_values.txt', 'w') as x_file:
        for number in x:
            entry = str(number) + " "
            x_file.write(entry)
"""
x_read = []
with open('x_values.txt', 'r') as x_file:
    for line in x_file:
        line = line.strip() 
        words = line.split(' ')
        for number in words:
            x_read.append(int(number))
"""

# Test linear regression analysis
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print ("R-squared:", r_value**2)
print ("P-value:", p_value)
