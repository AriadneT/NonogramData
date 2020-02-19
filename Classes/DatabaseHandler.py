class DatabaseHandler:

    def __init__(self, interaction):
        self.interaction = interaction

    def createTables(self):
        self.interaction.execute('CREATE DATABASE IF NOT EXISTS nonogram;')
        self.interaction.execute('USE nonogram;')
        self.interaction.execute('CREATE TABLE IF NOT EXISTS line (line_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, length TINYINT(4) NOT NULL, places TINYINT(4) NOT NULL);')
        # From_edge refers to blocks from top or left end
        self.interaction.execute('CREATE TABLE IF NOT EXISTS data (data_id INTEGER(11) AUTO_INCREMENT PRIMARY KEY, line_id INTEGER(11) NOT NULL, succession TINYINT(4) NOT NULL, from_edge TINYINT(4) NOT NULL, block_number TINYINT(4) NOT NULL, longest_block TINYINT(4) NOT NULL, FOREIGN KEY (line_id) REFERENCES line(line_id));')
