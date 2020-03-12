from scipy import stats

class LinearAnalyser:

    def __init__(self):
        pass

    def recordLinearRegressions(self, data_groups):
        for data_pair in data_groups:
            slope, intercept, r_value, p_value, std_err = stats.linregress(data_pair[0].data,data_pair[1].data)

            with open("Results/" + data_pair[0].column + "_regression.txt", "a") as data_file:
                if data_pair[0].spaces == 0:
                    data_file.write("When all data are included:\n\n")
                else:
                    data_file.write("When " + str(data_pair[0].spaces) + " lines must be filled:\n\n")
                data_file.write("order = " + str(slope) + " " + data_pair[0].transform_data() + " + " + str(intercept) + "\n")
                data_file.write("Standard error: " + str(std_err) + "\n")
                data_file.write("R-squared: " + str(r_value**2) + "\n")
                data_file.write("P-value: " + str(p_value) + "\n\n")
