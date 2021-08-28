import requests

class GeneralTransformer:
    """ Class with a set of methods to transform HTML into usable data. """

    def table_to_text(self, table):
        """ Turns a list of 'tr' objects into a 2D-array of text. """
        for i in range(len(table)):
            table[i] = table[i].find_all('td')
            for j in range(len(table[i])):
                table[i][j] = table[i][j].text.strip()

    def url_to_png(self, icon_name, img_url, folder):
        """ Turns an image url into a png that is saved accordingly. """
        image = requests.get(img_url)
        file = open(folder + "/" + icon_name, "wb")
        file.write(image.content)
        file.close()