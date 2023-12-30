# Devon Russo

# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.

# The packages will be stored in a hash table with their ID being used as the key.

import csv


# Create package class
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


# Create hash table to store package data
class PackageHashTable:
    def __init__(self):
        self.hash_table = {}

    def add_package(self, package_id, package):
        self.hash_table[package_id] = package

    def get_package(self, package_id):
        return self.hash_table.get(package_id)

    def remove_package(self, package_id):
        if package_id in self.hash_table:
            del self.hash_table[package_id]
            print("Package", package_id, "was deleted")
        else:
            print("Package", package_id, "is not in the table")


# Initialize package hash table
package_table = PackageHashTable()


# Create truck class
class Truck:
    def __int__(self, num_packages=0, speed=18):
        self.num_packages = num_packages
        self.speed = speed


# Define function to parse csv file and create package objects
def create_package_objects():
    with open("files/WGUPS_package_file.csv", "r", encoding='utf-8-sig') as package_file:
        reader_variable = csv.reader(package_file, delimiter=",")
        for row in reader_variable:
            package_id = int(row[0])
            address = row[1]
            city = row[2]
            state = row[3]
            zip_code = row[4]
            deadline = row[5]
            weight = row[6]
            special_notes = row[7]
            new_package = Package(package_id, address, city, state, zip_code, deadline, weight, special_notes)
            package_table.add_package(package_id, new_package)


# TODO: Define function to parse distance files

create_package_objects()

# TODO: Delete before submitting. Check that package objects are created properly.
test = package_table.get_package(1)
print(test.address)
