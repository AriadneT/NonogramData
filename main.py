from scipy import stats
import mysql.connector
from mysql.connector import Error
import json
import matplotlib.pyplot as plotter
from Classes.DataGroup import DataGroup
from Classes.DatabaseHandler import DatabaseHandler

# Comparisons of data with different numbers of available placings
# e.g. x35 and y35 have placings 1 to 35
x35 = DataGroup("x", 35, "longest_block")
y35 = DataGroup("y", 35, "succession")
x25 = DataGroup("x", 25, "longest_block")
y25 = DataGroup("y", 25, "succession")
x30 = DataGroup("x", 30, "longest_block")
y30 = DataGroup("y", 30, "succession")
x20 = DataGroup("x", 20, "longest_block")
y20 = DataGroup("y", 20, "succession")
x_all = DataGroup("x", 0, "longest_block")
y_all = DataGroup("y", 0, "succession")
DataGroups = [[x35, y35], [x25, y25], [x30, y30], [x20, y20], [x_all, y_all]]
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
        db_handler = DatabaseHandler(db_interaction)

        #db_handler.createTables()

        db_interaction.execute('USE nonogram;')

        # Entering data via .csv files when table has foreign key does not work
        # unless foreign key ignored, which is not desired

        for data_pair in DataGroups:
            for data_group in data_pair:
                if data_group.type == "y":
                    if data_group.spaces == 0:
                        db_interaction.execute("SELECT succession FROM data JOIN line ON data.line_id = line.line_id")
                    else:
                        db_interaction.execute("SELECT succession FROM data JOIN line ON data.line_id = line.line_id WHERE places = " + str(data_group.spaces))
                    order_results = db_interaction.fetchall()
                    for order in order_results:
                        data_group.data.append(order[0])
                else:
                    if data_group.spaces == 0:
                        # For numbers below 1, multiply by 100 to allow stats.lineregress to work.
                        # Because line lengths vary and therefore affect maximum block size,
                        # Correct for length. Log transformation seems to be more suitable.
                        db_interaction.execute("SELECT log(longest_block / length) * 100 FROM data JOIN line ON data.line_id = line.line_id")
                    else:
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

    with open("Results/" + data_pair[0].column + "_regression.txt", "a") as data_file:
        if data_pair[0].spaces == 0:
            data_file.write("When all data are included:\n\n")
        else:
            data_file.write("When " + str(data_pair[0].spaces) + " lines must be filled:\n\n")
        data_file.write("order = " + str(slope) + "log(" + data_pair[0].column + " / length) x 100 + " + str(intercept) + "\n")
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
plotter.savefig("Results/longest_block_scatter.png")
