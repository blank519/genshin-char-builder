class DisplayCommand:
    """ Class for checking and displaying objects according to the $display command """

    def display(self, object, object_type):
        if object == None:
            return "No " + object_type + " selected."
        else:
            return object.full_str()