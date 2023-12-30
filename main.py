# Devon Russo

# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.

# The packages will be stored in a hash table with their ID being used as the key.

import csv

# Initialize empty list to store package objects
packages = []


# Creating package class
class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, special_notes=""):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.special_notes = special_notes


# Define function to parse csv file and create package objects
def create_package_objects():
    with open("files/WGUPS_package_file.csv", "r") as package_file:
        reader_variable = csv.reader(package_file, delimiter=",")
        for row in reader_variable:
            package_id = row[0]
            address = row[1]
            city = row[2]
            state = row[3]
            zip_code = row[4]
            deadline = row[5]
            weight = row[6]
            special_notes = row[7]
            package = Package(package_id, address, city, state, zip_code, deadline, weight, special_notes)
            packages.append(package)


create_package_objects()

for package in packages:
    print(package.package_id, package.address, package.city, package.zip_code, package.deadline, package.weight,
          package.special_notes)
