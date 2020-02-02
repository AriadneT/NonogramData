class DataGroup:

   def __init__(self, axis, spaces):
      self.type = axis
      self.spaces = spaces
      self.data = []
   
   def displayGroup(self):
     print (self.type,  " axis with ", self.spaces, "spaces")
