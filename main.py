import mysql.connector
from mysql.connector import Error
import json
import matplotlib.pyplot as plotter
from Classes.DataGroup import DataGroup
from Classes.DatabaseHandler import DatabaseHandler
from Classes.LinearAnalyser import LinearAnalyser
from pandas import DataFrame
from sklearn import linear_model
import statsmodels.api as modelling

# Comparisons of data with different numbers of available placings
# e.g. y35 have placings 1 to 35
long35 = DataGroup("x", 35, "longest_block")
block_number35 = DataGroup("x", 35, "block_number")
y35 = DataGroup("y", 35, "succession")
long25 = DataGroup("x", 25, "longest_block")
block_number25 = DataGroup("x", 25, "block_number")
y25 = DataGroup("y", 25, "succession")
long30 = DataGroup("x", 30, "longest_block")
block_number30 = DataGroup("x", 30, "block_number")
y30 = DataGroup("y", 30, "succession")
long20 = DataGroup("x", 20, "longest_block")
block_number20 = DataGroup("x", 20, "block_number")
y20 = DataGroup("y", 20, "succession")
long_all = DataGroup("x", 0, "longest_block")
block_number_all = DataGroup("x", 0, "block_number")
y_all = DataGroup("y", 0, "succession")
DataGroups = [[long35, y35],
              [long25, y25],
              [long30, y30],
              [long20, y20],
              [long_all, y_all],
              [block_number35, y35],
              [block_number25, y25],
              [block_number30, y30],
              [block_number20, y20],
              [block_number_all, y_all]]
prelim_results = []
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
                    if not data_group.data:
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
                        db_interaction.execute("SELECT " + data_group.transform_data() + " FROM data JOIN line ON data.line_id = line.line_id")
                    else:
                        db_interaction.execute("SELECT " + data_group.transform_data() + " FROM data JOIN line ON data.line_id = line.line_id WHERE places = " + str(data_group.spaces))
                    longest_block_results = db_interaction.fetchall()
                    for longest_block in longest_block_results:
                        data_group.data.append(int(longest_block[0]))

        db_interaction.execute("SELECT MAX(line_id) FROM data")
        number_of_lines = db_interaction.fetchall()[0][0]
        line_number = 1

        while line_number <= number_of_lines:
            # ABS() to ensure results are +ive
            db_interaction.execute("SELECT ABS(d2.from_edge - d1.from_edge) AS difference FROM data d1 INNER JOIN data d2 ON d2.data_id = d1.data_id + 1 WHERE d1.line_id = " + str(line_number))
            diff_line_results = db_interaction.fetchall()
            for diff_line_result in diff_line_results:
                prelim_results.append(diff_line_result[0])
            line_number += 1
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
print (prelim_results)

# Clear text files first for each analysis
for text_file in config["result_text_files"]:
    with open(text_file, "w"):
        pass

# Linear regression analysis
linear_analyser = LinearAnalyser()

linear_analyser.recordLinearRegressions(DataGroups)

data = ((long35.data, y35.data),
        (long30.data, y30.data),
        (long25.data, y25.data),
        (long20.data, y20.data))
colors = ("black", "blue", "green", "red")
groups = ("35 places", "30 places", "25 places", "20 places")

# Create plot
figure = plotter.figure()
axis = figure.add_subplot(1, 1, 1)

for data, color, group in zip(data, colors, groups):
    x, y = data
    axis.scatter(x, y, c=color, edgecolors='none', s=30, label=group)

plotter.title("Scatter plot: longest block")
axis.set_xlabel("log(longest block) / length x 100")
axis.set_ylabel("nth solved")
plotter.legend(loc=1)
plotter.savefig("Results/longest_block_scatter.png")

data = ((block_number35.data, y35.data),
        (block_number30.data, y30.data),
        (block_number25.data, y25.data),
        (block_number20.data, y20.data))

figure = plotter.figure()
axis = figure.add_subplot(1, 1, 1)

for data, color, group in zip(data, colors, groups):
    x, y = data
    axis.scatter(x, y, c=color, edgecolors='none', s=30, label=group)

plotter.title("Scatter plot: block number")
axis.set_xlabel("block number / length x 100")
axis.set_ylabel("nth solved")
plotter.legend(loc=1)
plotter.savefig("Results/block_number_scatter.png")

figure = plotter.figure()
x, y = (long_all, block_number_all)
plotter.scatter(long_all.data, block_number_all.data, color="black")
plotter.title("Longest data vs Block number")
plotter.xlabel("log(longest block / length) x 100")
plotter.ylabel("block number / length x 100")
plotter.savefig("Results/block_parameters_scatter.png")

compiled_data = {
    "succession": y_all.data,
    "log(longest block / length) x 100": long_all.data,
    "block number / length x 100": block_number_all.data
    }
data_frame = DataFrame(compiled_data, columns = ["succession", "log(longest block / length) x 100", "block number / length x 100"])
X = data_frame[["log(longest block / length) x 100", "block number / length x 100"]]
Y = data_frame["succession"]

regression = linear_model.LinearRegression()
regression.fit(X, Y)

with open("Results/combined_regression.txt", "w") as data_file:
    data_file.write("Succession = " + str(regression.intercept_) + " + " + str(regression.coef_[0]) + " (log(longest block / length) x 100) + " + str(regression.coef_[1]) + " (block number / length x 100)\n\n")
    X = modelling.add_constant(X)
    model = modelling.OLS(Y, X).fit()
    predictions = model.predict(X) 
    model_stats = model.summary()
    data_file.write(str(model_stats))
