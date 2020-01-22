from scipy import stats
import mysql.connector
from mysql.connector import Error
import os
import matplotlib.pyplot as plotter

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

        # Entering data via .csv files when table has foreign key does not work
        # unless foreign key ignored, which is not desired

        # Lines vary from 20 to 35 in length, so limit results to first 20 solved
        db_interaction.execute("SELECT succession FROM data WHERE succession < 21")
        order_results = db_interaction.fetchall()
        for order in order_results:
            y.append(order[0])

        second_db_interaction = db_connection.cursor()
        # For numbers below 1, multiply by 100 to allow stats.lineregress to work.
        # Because line lengths vary and therefore affect maximum block size,
        # correct for length. Log transformation seems to be more suitable.
        second_db_interaction.execute("SELECT log(longest_block / length) * 100 FROM data JOIN line ON data.line_id = line.line_id WHERE succession < 21")
        longest_block_results = second_db_interaction.fetchall()
        for longest_block in longest_block_results:
            x.append(int(longest_block[0]))
except Error as error:
    print("Error while connecting to MySQL", error)
finally:
    if (db_connection.is_connected()):
        db_interaction.close()
        second_db_interaction.close()
        db_connection.close()

"""
# Test storing data in file and extracting them
if os.path.isfile('x_values.txt'):
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
"""
# Test linear regression analysis
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print ("order =", slope ,"log(longest_block / length) x 100 +", intercept)
print ("R-squared:", r_value**2)
print ("P-value:", p_value)

plotter.scatter(x, y, c="black")
plotter.title('Scatter plot')
plotter.xlabel('log(longest_block / length) x 100')
plotter.ylabel('order')
plotter.show()
