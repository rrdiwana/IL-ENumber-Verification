import csv
import getopt
import re
import sys
import urllib

from suds.client import Client


# API calling function
def validate(idToValidate):
    global apiCallFailRetryCount, test
    try:
        url = "https://testmytaxes.illinois.gov/ws/"
        client = Client(url)
        return client.service.EnumberVerify("amazonwsilstest2", "DeNy13R1v3RHazCr0CkoDyLEz1NiT!", idToValidate)
    except urllib.error.URLError as e:
        apiCallFailRetryCount += 1
        if apiCallFailRetryCount > 5:
            print("API call failed for 5 consecutive times, API may be down. Please try later:", e)
            sys.exit()
        else:
            print("API call fails for %s. Retrying... " % row[idIndex])
            return validate(idToValidate)
    except Exception as e:
        print("Unexpected error while calling gov API:", e)
        sys.exit()


# function to format validation
def get_formatted_id_after_format_validation(number):
    # if number == "123":
    #     raise urllib.error.URLError("operational timeout")
    number = number.replace('-', '')
    number = number.replace(' ', '')
    if re.search(regexForValidIdWithoutE, number):
        return "E" + number[0:8]
    elif re.search(regexForValidIdWithE, number):
        return number[0:9]
    else:
        raise ValueError("Invalid format detected for number: %s" % number)


# function to add data for invalid numbers
def append_row_for_valid(details):
    row.append("ValidFormat")
    for elem in details[1:]:
        row.append(elem)
    row.append(str(True))  # appending status as "True"


# function to add data for invalid numbers
def append_row_for_invalid(id_format):
    row.append(id_format)
    row.append("")
    row.append("")
    row.append("")
    row.append(str(False))  # here status will be false always.


# write row to file
def write_to_file(row):
    with open(outputFile, "a") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(row)


# script starting point
if __name__ == '__main__':

    header = []  # Name of columns(The first row of the input file)
    rows = []  # rows with data
    idIndex = 4  # Index for idToValidate column in the input csv

    # The ENumbers are in different format
    # In all of them we ned to:
    #   Remove(-), (" "), remove unwanted numbers(i.e. only consider first 8 numbers)
    #   Add "E" wherever is missing in the beginning.

    regexForValidIdWithE = "^[Ee][0-9]+$"
    regexForValidIdWithoutE = "^[0-9]+$"
    inputFile = ''  # Input file location
    outputFile = ''  # Output file location
    numbersToSkip = 0
    header_added = False
    apiCallFailRetryCount = 0
    typeOfIdToValidate = "ExemptionId"
    test = 1

    try:
        opts, args = getopt.getopt(sys.argv[1:], ":hi:o:s:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('Not sure how to run the script. Try [-h || -help] for help')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('[-i]: input file location')
            print('[-o]: output file location')
            print('[-h]: help')
            sys.exit()
        if opt == "-s":
            numbersToSkip = int(arg) - 1  # decreasing the number by one because of header
            break
        if opt in ("-i", "--ifile"):
            inputFile = arg
        elif opt in ("-o", "--ofile"):
            outputFile = arg
        else:
            print('Required format to run the script: \nscript_name.py -i <inputfile> -o <outputfile>\n')
            sys.exit()

    if int(numbersToSkip) > 0:
        header_added = True  # checking if the header is already added.

    with open(inputFile, "r") as csvFile:
        csvReader = csv.reader(csvFile)
        header = next(csvReader)  # storing the headers
        header.append("numberToBeValidated")  # number after format validation
        header.append("typeOfIdToValidate")   # ExemptionId
        header.append("idFormatInformation")  # Response which we
        header.append("name")  # will receive from
        header.append("date")  # the API
        header.append("type")  # will be
        header.append("status")  # stored in these columns

        for i in range(0, int(numbersToSkip)):
            next(csvReader)  # skipping the required numbers of rows
        counter = numbersToSkip
        for row in csvReader:
            if counter % 500 == 0:
                print("Total Number of records processed:", counter)
            # if limit >= 100:   # DEBUG
            #     break   # DEBUG
            try:
                formattedId = get_formatted_id_after_format_validation(row[idIndex])  # format validation
                result = validate(formattedId)  # checking number against the API
                details = result.EnumberVerifyResult.split(",")
                status = result.ValidExemption
                apiCallFailRetryCount = 0

                row.append(formattedId)     # appending "numberToBeValidated" empty because of it's invalid format
                row.append(typeOfIdToValidate)
                if status:
                    append_row_for_valid(details)
                else:
                    append_row_for_invalid("ValidFormat")

            except ValueError as e:
                row.append("")  # appending "numberToBeValidated" empty because of it's invalid format
                row.append(typeOfIdToValidate)
                append_row_for_invalid("InvalidFormat")

            except Exception as e:
                print("Unexpected error while validating:", e)
                sys.exit()

            if not header_added:
                write_to_file(header)
                header_added = True
            write_to_file(row)
            counter += 1
