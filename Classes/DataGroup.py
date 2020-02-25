class DataGroup:

    def __init__(self, axis, spaces, column):
        self.type = axis
        self.spaces = spaces
        self.column = column
        self.data = []

    def transform_data(self):
        if self.column == "longest_block":
            return "log(longest_block / length) * 100"
        else:
            return "(block_number / length) * 100"
