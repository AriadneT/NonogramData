from scipy import stats
import mysql.connector
from mysql.connector import Error
import json
import matplotlib.pyplot as plotter
from Classes.DataGroup import DataGroup

# Comparisons of data with different numbers of placings
# e.g. x35 and y35 have placings 1 to 35
x35 = DataGroup("x", 35)
y35 = DataGroup("y", 35)
x25 = DataGroup("x", 25)
y25 = DataGroup("y", 25)
x30 = DataGroup("x", 30)
y30 = DataGroup("y", 30)
x20 = DataGroup("x", 20)
y20 = DataGroup("y", 20)
DataGroups = [[x35, y35], [x25, y25], [x30, y30], [x20, y20]]
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

        #db_interaction.execute('CREATE DATABASE IF NOT EXISTS nonogram;')

        db_interaction.execute('USE nonogram;')

        #create_line_table = 'CREATE TABLE IF NOT EXISTS line (line_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, length TINYINT(4) NOT NULL, places TINYINT(4) NOT NULL);'
        #db_interaction.execute(create_line_table)
        # From_edge refers to blocks from top or left end
        #create_data_table = 'CREATE TABLE IF NOT EXISTS data (data_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, line_id INTEGER(11) NOT NULL, succession TINYINT(4) NOT NULL, from_edge TINYINT(4) NOT NULL, block_number TINYINT(4) NOT NULL, longest_block TINYINT(4) NOT NULL, FOREIGN KEY (line_id) REFERENCES line(line_id));'
        #db_interaction.execute(create_data_table)

        # Entering data via .csv files when table has foreign key does not work
        # unless foreign key ignored, which is not desired

        # Lines vary from 20 to 35 in length
        for data_pair in DataGroups:
            for data_group in data_pair:
                if data_group.type == "y":
                    db_interaction.execute("SELECT succession FROM data JOIN line ON data.line_id = line.line_id WHERE places = " + str(data_group.spaces))
                    order_results = db_interaction.fetchall()
                    for order in order_results:
                        data_group.data.append(order[0])
                else:
                    # For numbers below 1, multiply by 100 to allow stats.lineregress to work.
                    # Because line lengths vary and therefore affect maximum block size,
                    # correct for length. Log transformation seems to be more suitable.
                    db_interaction.execute("SELECT log(longest_block / length) * 100 FROM data JOIN line ON data.line_id = line.line_id WHERE places = " + str(data_group.spaces))
                    longest_block_results = db_interaction.fetchall()
                    for longest_block in longest_block_results:
                        data_group.data.append(int(longest_block[0]))
except Error as error:
    print("Error while connecting to MySQL", error)
finally:
    if (db_connection.is_connected()):
        db_interaction.close()

"""
# Test storing data in file and extracting them
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
for data_pair in DataGroups:
    slope, intercept, r_value, p_value, std_err = stats.linregress(data_pair[0].data,data_pair[1].data)

    with open('Results/linear_regressions.txt', 'a') as data_file:
        data_file.write("When " + str(data_pair[0].spaces) + " lines must be filled:\n\n")
        data_file.write("order = " + str(slope) + "log(longest_block / length) x 100 + " + str(intercept) + "\n")
        data_file.write("Standard error: " + str(std_err) + "\n")
        data_file.write("R-squared: " + str(r_value**2) + "\n")
        data_file.write("P-value: " + str(p_value) + "\n\n")

data = ((x35.data, y35.data), (x30.data, y30.data), (x25.data, y25.data), (x20.data, y20.data))
colors = ("black", "blue", "green", "red")
groups = ("35 places", "30 places", "25 places", "20 places")

# Create plot
figure = plotter.figure()
axis = figure.add_subplot(1, 1, 1)

for data, color, group in zip(data, colors, groups):
    x, y = data
    axis.scatter(x, y, c=color, edgecolors='none', s=30, label=group)

plotter.title("Scatter plot: longest block")
axis.set_xlabel("log(longest block)/length")
axis.set_ylabel("nth solved")
plotter.legend(loc=1)
plotter.savefig("Results/scatter_plot.png")
