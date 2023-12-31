# Devon Russo, WGU - Computer Science, Student ID: 010828078
# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.
# The packages will be stored in a hash table with their ID being used as the key.
# The package class stores all relevant information about each package.

import csv


# Create package class.
class Package:
    def __init__(self, package_id, address, city, zip_code, deadline, weight, special_notes="",
                 delivery_status="at the hub"):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.special_notes = special_notes
        self.delivery_status = delivery_status


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


# Create truck class
class Truck:
    def __int__(self, num_packages=0, speed=18.0, miles_driven=0.0):
        self.num_packages = num_packages
        self.speed = speed
        self.miles_driven = miles_driven


# Create location class
class Location:
    def __init__(self, address, distances):
        # Manipulate address into same format as package objects so the strings can be compared.
        self.address = address.replace('(', '').replace(')', '').strip().replace('\n', ', ')
        self.distances = distances


locations = []

# Initialize package hash table
package_table = PackageHashTable()

# WGUPS has three trucks available
truck1 = Truck()
truck2 = Truck()
truck3 = Truck()

trucks = [truck1, truck2, truck3]


# Define function to parse csv file and create package objects.
# The address is stored in the same format as the location objects.
def create_package_objects():
    with open("files/WGUPS_package_file.csv", "r", encoding='utf-8-sig') as package_file:
        reader_variable = csv.reader(package_file, delimiter=",")
        for row in reader_variable:
            package_id = int(row[0])
            address = row[1]
            city = row[2]
            zip_code = row[4]
            deadline = row[5]
            weight = row[6]
            special_notes = row[7]
            new_package = Package(package_id, address, city, zip_code, deadline, weight, special_notes)
            package_table.add_package(package_id, new_package)


# Fill the package hash table
create_package_objects()


# Define function to parse distance file and create location objects.
def create_location_objects():
    with open("files/distance_table.csv", "r", encoding='utf-8-sig') as distance_file:
        reader_variable = csv.reader(distance_file, delimiter=",")

        for row in reader_variable:
            address = row[1]
            distances = row[slice(2, 29)]
            distances = [float(i) for i in distances if i != '']
            new_location = Location(address, distances)
            locations.append(new_location)


def nearest_neighbor_algorithm(trucks, packages, distances):
    # Initialize empty route for each truck
    routes = {truck: [] for truck in trucks}

    # Define function to calculate the distance between two locations
    def distance_between(location1, location2):
        return distances[location1][location2]

    # Define function to get the nearest package for a given location
    def get_nearest_package(current_location, remaining_packages):
        return min(remaining_packages, key=lambda package: distance_between(current_location, package.address))

    # Start at the hub
    for truck in trucks:
        current_location = 'Hub'

        # While there are still packages remaining
        while packages:
            nearest_package = get_nearest_package(current_location, packages)

            # Load the package
            routes[truck].append(nearest_package)
            package_table.get_package(nearest_package.package_id).delivery_status = "in transit"

            # Mark the package as loaded
            packages.remove_package(nearest_package)

            # Update the current location
            current_location = nearest_package['address']

    return routes


# Define unction to lookup package by ID
def lookup_package(package_id):
    package_to_lookup = package_table.get_package(package_id)

    print("Delivery address: " + package_to_lookup.address, package_to_lookup.city + ", " + package_to_lookup.zip_code)
    print("Delivery deadline: " + package_to_lookup.deadline)
    print("Package weight: " + package_to_lookup.weight + "KG")
    print("Package", package_id, "is", package_to_lookup.delivery_status)
    print()


def time_function():
    # Enter a time. Format must be "00:00 AM/PM"
    user_time = input("Enter current time (Format 12:00 AM/PM): ")
    print("Status report for", user_time, )
    print('...\n' * 3)
    print("This feature has not been added yet\n")

    # Print status of all packages at that time.

    return


def get_user_input():
    print("Please choose from the following options:")
    print("(1) - Lookup package by ID")
    print("(2) - Print status of all of today's packages by time - Does not work yet")
    print("(3) - Enter a different time - Does not work yet")
    print("(4) - Quit the program\n")

    user_input = int(input("Enter your selection: "))

    if user_input == 1:
        id_input = int(input("Enter package ID: "))
        lookup_package(id_input)
        get_user_input()
    elif user_input == 2:
        print("This feature has not yet been added\n")
        time_function()
        get_user_input()
    elif user_input == 3:
        print("This feature has not yet been added\n")
        get_user_input()
    elif user_input == 4:
        print("Quitting program...")
        exit()
    else:
        get_user_input()


print(nearest_neighbor_algorithm(trucks, package_table.hash_table, locations))

get_user_input()
