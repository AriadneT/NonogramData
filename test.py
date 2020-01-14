from scipy import stats
import mysql.connector
from mysql.connector import Error

# Test connection to database
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
except Error as error:
    print("Error while connecting to MySQL", error)
finally:
    if (db_connection.is_connected()):
        db_interaction.close()
        db_connection.close()

# Test storing data in file and extracting them
x = [0,2,1,3]
y = [2,3,4,5]

with open('x_values.txt', 'w') as x_file:
    for number in x:
        entry = str(number) + " "
        x_file.write(entry)

x_read = []
with open('x_values.txt', 'r') as x_file:
    for line in x_file:
        line = line.strip() 
        words = line.split(' ')
        for number in words:
            x_read.append(int(number))

# Test linear regression analysis
slope, intercept, r_value, p_value, std_err = stats.linregress(x_read,y)

print ("R-squared:", r_value**2)
