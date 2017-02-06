import openpyxl.reader.excel
from datetime import date

class oldZooDataExtractor:


    # Names that match the sheet names in the source Excel workbook for month collection
    month_dict = ["Yht1", "Yht2", "Yht3", "Yht4", "Yht5", "Yht6", "Yht7", "Yht8", "Yht9", "Yht10", "Yht11", "Yht12"]
    headers = ["day","month","year","visitors","datetime","weekday"]
    weekdays = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    output = []
    output_filename = "../data/oldVisitorCounts.csv"

    def __init__(self):
        # data_only reads only evaluated values and never returns formulas
        file = "../data/Kävijätilasto_2015.xlsx"
        # Which months to be included 1-12
        months_included = [1,2,3]
        #Which years to be included 2016-2011
        years = [2016, 2015, 2014, 2013, 2012, 2011, 2010]

        for year in years:
            self.output.append(self.read_one_year_statistics(months_included,year))

        self.write_to_file()

    def read_one_year_statistics(self, months_included, year):
        file = "../data/Kävijätilasto_" + str(year) + ".xlsx"
        workbook = openpyxl.reader.excel.load_workbook(file, read_only=True, data_only=True)
        result = []
        for month in months_included:
            result.append(self.read_month_statistics(month, workbook, year))

        return result

    def read_month_statistics(self,month, workbook,year):
        month_sheet = workbook[self.month_dict[month-1]]
        values = list(month_sheet.iter_rows())[4:]
        valueList = []

        for item in values:
            if item[0].value != None :
                valueList.append([item[0].value, month, year, item[29].value])

        return valueList

    def write_to_file(self):
        file = open(self.output_filename,"w")
        file.write(",".join(self.headers) + "\n")
        for year in self.output:
            for month in year:
                for day in month:
                    currentDate = date(day=day[0],month=day[1],year=day[2])
                    file.write(str(day[0])+ ","+str(day[1])+","+ str(day[2]) +","+str(day[3]) +","+ currentDate.isoformat() + "," + self.weekdays[currentDate.weekday()]+"\n")
        file.close()

test = oldZooDataExtractor()

