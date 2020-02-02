from scipy import stats
import mysql.connector
from mysql.connector import Error
import json
#import os
import matplotlib.pyplot as plotter
from Classes.DataGroup import DataGroup

# Comparisons of data with different numbers of placings
# e.g. x35 and y35 have placings 1 to 35
x35 = []
y35 = []
x25 = []
y25 = []
x30 = DataGroup("x", 30)
y30 = []
x20 = []
y20 = []
config = []

with open('Configuration/config.json') as config_file:
    config = json.load(config_file)

try:
    db_connection = mysql.connector.connect(host=config["mysql"]["host"],
                                         database=config["mysql"]["db"],
                                         user=config["mysql"]["user"],
                                         password=config["mysql"]["password"])

    if db_connection.is_connected():
        db_interaction = db_connection.cursor()

        db_interaction.execute('CREATE DATABASE IF NOT EXISTS nonogram;')

        db_interaction.execute('USE nonogram;')

        create_line_table = 'CREATE TABLE IF NOT EXISTS line (line_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, length TINYINT(4) NOT NULL, places TINYINT(4) NOT NULL);'
        db_interaction.execute(create_line_table)
        # from_edge refers to blocks from top or left end
        create_data_table = 'CREATE TABLE IF NOT EXISTS data (data_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, line_id INTEGER(11) NOT NULL, succession TINYINT(4) NOT NULL, from_edge TINYINT(4) NOT NULL, block_number TINYINT(4) NOT NULL, longest_block TINYINT(4) NOT NULL, FOREIGN KEY (line_id) REFERENCES line(line_id));'
        db_interaction.execute(create_data_table)

        # Entering data via .csv files when table has foreign key does not work
        # unless foreign key ignored, which is not desired

        # Lines vary from 20 to 35 in length, so limit results to first 20 solved
        #db_interaction.execute("SELECT succession FROM data WHERE succession < 21")
        db_interaction.execute("SELECT succession FROM data JOIN line ON data.line_id = line.line_id WHERE places = 35")
        order_results = db_interaction.fetchall()
        for order in order_results:
            y35.append(order[0])

        second_db_interaction = db_connection.cursor()
        # For numbers below 1, multiply by 100 to allow stats.lineregress to work.
        # Because line lengths vary and therefore affect maximum block size,
        # correct for length. Log transformation seems to be more suitable.
        #db_interaction.execute("SELECT log(longest_block / length) * 100 FROM data JOIN line ON data.line_id = line.line_id WHERE succession < 21")
        db_interaction.execute("SELECT log(longest_block / length) * 100 FROM data JOIN line ON data.line_id = line.line_id WHERE places = 35")
        longest_block_results = db_interaction.fetchall()
        for longest_block in longest_block_results:
            x35.append(int(longest_block[0]))

        db_interaction.execute("SELECT succession FROM data JOIN line ON data.line_id = line.line_id WHERE places = 25")
        order_results = db_interaction.fetchall()
        for order in order_results:
            y25.append(order[0])

        db_interaction.execute("SELECT log(longest_block / length) * 100 FROM data JOIN line ON data.line_id = line.line_id WHERE places = 25")
        longest_block_results = db_interaction.fetchall()
        for longest_block in longest_block_results:
            x25.append(int(longest_block[0]))
except Error as error:
    print("Error while connecting to MySQL", error)
finally:
    if (db_connection.is_connected()):
        db_interaction.close()

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
# Linear regression analysis
slope35, intercept35, r_value35, p_value35, std_err35 = stats.linregress(x35,y35)

print ("When 35 lines must be filled:")
print ("order =", slope35 ,"log(longest_block / length) x 100 +", intercept35)
print ("R-squared:", r_value35**2)
print ("P-value:", p_value35)

"""
plotter.scatter(x35, y35, c="black")
plotter.title('Scatter plot')
plotter.xlabel('log(longest_block / length) x 100')
plotter.ylabel('order')
plotter.show()
"""
# Second linear regression analysis
slope25, intercept25, r_value25, p_value25, std_err25 = stats.linregress(x25,y25)

print ("When 25 lines must be filled:")
print ("order =", slope25 ,"log(longest_block / length) x 100 +", intercept25)
print ("R-squared:", r_value25**2)
print ("P-value:", p_value25)
"""
plotter.scatter(x25, y25, c="red")
plotter.title('Scatter plot')
plotter.xlabel('log(longest_block / length) x 100')
plotter.ylabel('order')
plotter.show()
"""
data = ((x35,y35),(x25,y25),(x20,y20))
colors = ("red", "black","green")
groups = ("35 places", "25 places", "20 places")

# Create plot
figure = plotter.figure()
axis = figure.add_subplot(1, 1, 1)

for data, color, group in zip(data, colors, groups):
    x, y = data
    axis.scatter(x, y, c=color, edgecolors='none', s=30, label=group)

plotter.title("Scatter plot")
plotter.legend(loc=1)
plotter.savefig("scatter_plot.png")
