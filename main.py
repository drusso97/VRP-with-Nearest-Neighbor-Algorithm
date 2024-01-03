# Devon Russo, WGU - Computer Science, Student ID: 010828078
# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.
# The packages will be stored in a hash table with their ID being used as the key.
# The package class stores all relevant information about each package.

import csv

current_time = "8:00 AM"


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


# Create hash table to store packages at the Hub
class HubHashTable:
    def __init__(self):
        self.packages_at_hub = {}

    # TODO: create three separate hash tables, one to store packages at the hub, one to store packages in transit,
    #  and one to store packages that are delivered.
    #  Record the time the package was loaded and the time the package was delivered.
    #  The remove_package function could be replaced with a move_package function that deletes the package from its
    #  current hash table and inserts it into the correct one,

    def add_package(self, package_id, package):
        self.packages_at_hub[package_id] = package

    def get_package(self, package_id):
        return self.packages_at_hub.get(package_id)

    def remove_package(self, package_id):
        if package_id in self.packages_at_hub:
            del self.packages_at_hub[package_id]
            print("Package", package_id, "was deleted")
        else:
            print("Package", package_id, "is not in the table")


class TransitHashTable:
    def __init__(self):
        self.packages_in_transit = {}

    def add_package(self, package_id, package):
        self.packages_in_transit[package_id] = package

    def get_package(self, package_id):
        return self.packages_in_transit.get(package_id)

    def remove_package(self, package_id):
        if package_id in self.packages_in_transit:
            del self.packages_in_transit[package_id]
            print("Package", package_id, "was deleted")
        else:
            print("Package", package_id, "is not in the table")


class DeliveredHashTable:
    def __init__(self):
        self.delivered_packages = {}

    def add_package(self, package_id, package):
        self.delivered_packages[package_id] = package

    def get_package(self, package_id):
        return self.delivered_packages.get(package_id)

    def remove_package(self, package_id):
        if package_id in self.delivered_packages:
            del self.delivered_packages[package_id]
            print("Package", package_id, "was deleted")
        else:
            print("Package", package_id, "is not in the table")

# Create truck class
class Truck:
    def __init__(self, max_capacity=16, speed=18.0, miles_driven=0.0):
        self.max_capacity = max_capacity
        self.num_packages = 0
        self.speed = speed
        self.miles_driven = miles_driven


# Create location class
class Location:
    def __init__(self, address, distances):
        # Manipulate address into same format as package objects so the strings can be compared.
        self.address = address.replace('(', '').replace(')', '').strip().replace('\n', ', ')
        self.distances = distances


locations = []

# Initialize package hash tables
package_table = HubHashTable()
transit_table = TransitHashTable()
delivered_table = DeliveredHashTable()

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
    distances = {}

    with open("files/distance_table.csv", "r", encoding='utf-8-sig') as distance_file:
        reader_variable = csv.reader(distance_file, delimiter=",")

        for row in reader_variable:
            address = row[1].strip()
            distances[address] = {locations[i].address: float(row[i + 2]) for i in range(len(locations))}
            new_location = Location(address, distances[address])
            locations.append(new_location)

    if 'Hub' not in distances:
        distances['Hub'] = {location.address: 0.0 for location in locations}

    return distances


def nearest_neighbor_algorithm(trucks, packages, distances):
    # Initialize empty route for each truck
    routes = {truck: [] for truck in trucks}

    delivered_packages = 0

    # TODO: Find a way to track delivered packages and the time that they were delivered.

    # Define function to calculate the distance between two locations
    def distance_between(location1, location2):
        location1 = location1.strip()
        location2 = location2.strip()

        if location1 in distances and location2 in distances[location1]:
            return distances[location1][location2]
        else:
            return float('inf')  # or any other appropriate value for missing distances

    # Define function to get the nearest package for a given location
    def get_nearest_package(current_location, remaining_packages, truck):
        # Sort packages by distance and filter out packages that exceed truck capacity
        valid_packages = [pkg for pkg in remaining_packages if truck.num_packages + 1 <= truck.max_capacity]

        if not valid_packages:
            return None  # No valid packages available

        return min(valid_packages, key=lambda pkg: distance_between(current_location, pkg.address))

    # Start at the hub
    for truck in trucks:
        current_location = 'Hub'

        # While there are still packages remaining
        while delivered_packages < len(packages):
            nearest_package = get_nearest_package(current_location, packages.values(), truck)

            if nearest_package is not None:
                # Load the package
                routes[truck].append(nearest_package)
                package_table.get_package(nearest_package.package_id).delivery_status = "in transit"
                truck.num_packages += 1

                # Mark the package as loaded
                # TODO: add package to packages_in_transit list
                # TODO: Record their delivery time, truck they are on, and ETA
                package_table.get_package(nearest_package.package_id)
                package_table.remove_package(nearest_package.package_id)

                # Update the current location
                current_location = nearest_package.address

                if nearest_package.package_id == 9 and current_time >= "10:20 AM":
                    nearest_package.address = "410 S State St"

            else:
                # If no valid package is available, return to the hub to load more packages
                routes[truck].append('Hub')  # Indicates a return to the hub
                truck.num_packages = 0
                current_location = 'Hub'

                # Increment the number of delivered packages for this truck
                delivered_packages += len(routes[truck])

    return routes


# Define function to lookup package by ID
def lookup_package(package_id):
    package_to_lookup = package_table.get_package(package_id)

    if package_table.get_package(package_id) is not None:
        print("Delivery address: " + package_to_lookup.address,
              package_to_lookup.city + ", " + package_to_lookup.zip_code)
        print("Delivery deadline: " + package_to_lookup.deadline)
        print("Package weight: " + package_to_lookup.weight + "KG")
        print("Package", package_id, "is", package_to_lookup.delivery_status)
        print()
    else:
        print("The package does not exist")


def time_function():
    # Enter a time. Format must be "00:00 AM/PM"
    user_time = input("Enter current time (Format 12:00 AM/PM): ")
    print("Status report for", user_time, )
    print('...\n' * 3)
    print("This feature has not been added yet\n")

    # Print status of all packages at that time.

    return


def set_departure_time():
    for truck in trucks:
        departure_time = input(f"Enter departure time for Truck {trucks.index(truck) + 1} (Format 12:00 AM/PM): ")
        # Set the departure time for the truck
        # You may want to store this information in the Truck class
        print(f"Truck {trucks.index(truck) + 1} will depart at {departure_time}")


def get_user_input():
    print("Please choose from the following options:")
    print("(1) - Lookup package by ID")
    print("(2) - Print status of all of today's packages by time - Does not work yet")
    print("(3) - Enter departure time for trucks")
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
        set_departure_time()
        get_user_input()
    elif user_input == 4:
        print("Quitting program...")
        exit()
    else:
        get_user_input()


distances = create_location_objects()
print(nearest_neighbor_algorithm(trucks, package_table.packages_at_hub, distances))

get_user_input()
