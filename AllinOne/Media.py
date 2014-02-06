import sys
class Media(object):
    def __init__(self, title="", link="", plot="" , pic='/resources/searchers/icons/krasfs.ru.png', source=""):
        self.Link = link
        self.Title = title
        self.Year = ""
        self.Country = ""
        self.Genre = ""
        self.ReleaseDate = ""
        self.Plot = plot
        self.Director = ""
        self.Duration = ""
        self.Cast = ""
        self.PictureLink = pic
        '''Le site Source de cette media'''
        self.Source = source 
        if pic == '/resources/searchers/icons/krasfs.ru.png' :
            self.PictureLink = sys.modules["__main__"].__root__ + pic
        self.tab = [("Title",self.Title),("Year",self.Year),("Country",self.Country),("Genre",self.Genre),("ReleaseDate",self.ReleaseDate),("Plot",self.Plot),("Director",self.Director),("Duration",self.Duration),("Cast",self.Cast),("Link",self.Link)]

    def __getitem__(self, item):
        return self.tab[item]

    @classmethod
    def GetFromTab(self, tab):
        m= Media(tab['Title'],tab['Link'],tab['Plot'],tab['PictureLink'])
        m.Country = tab['Country']
        m.Year = tab['Year']
        m.Director = tab['Director']
        m.Duration = tab['Duration']
        m.Genre = tab['Genre']
        m.ReleaseDate = tab['ReleaseDate']
        m.Cast = tab['Cast']
        return m
