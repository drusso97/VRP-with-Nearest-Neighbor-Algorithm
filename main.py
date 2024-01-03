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

# Create hash table to store packages. Can store/access packages by delivery status as well.
class PackageHashTable:
    def __init__(self):
        self.packages_by_state = {
            "at_hub": {},
            "in_transit": {},
            "delivered": {}
        }

    def add_package(self, package_id, package, state="at_hub"):
        self.packages_by_state[state][package_id] = package

    def get_package(self, package_id, state="at_hub"):
        return self.packages_by_state[state].get(package_id)

    def remove_package(self, package_id, state="at_hub"):
        if package_id in self.packages_by_state[state]:
            del self.packages_by_state[state][package_id]
            print("Package", package_id, "was deleted from", state)
        else:
            print("Package", package_id, "is not in the", state, "table")

    def get_packages_in_state(self, state="at_hub"):
        return self.packages_by_state[state]


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

package_table = PackageHashTable()

packages_at_hub = package_table.get_packages_in_state("at_hub")
packages_in_transit = package_table.get_packages_in_state("in_transit")
delivered_packages = package_table.get_packages_in_state("delivered")


# WGUPS has three trucks available
truck1 = Truck()
truck2 = Truck()
truck3 = Truck()

trucks = [truck1, truck2, truck3]


# Define function to parse csv file and create package objects.
# The address is stored in the same format as the location objects.
def get_package_data():
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
            package_table.add_package(package_id, new_package, state="at_hub")


# Fill the package hash table
get_package_data()


# Define function to parse distance file and create location objects.
def get_location_data():
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
        while delivered_packages < len(package_table.get_packages_in_state("at_hub")):
            nearest_package = get_nearest_package(
                current_location,
                package_table.get_packages_in_state("at_hub").values(),
                truck
            )

            if nearest_package is not None:
                # Load the package
                routes[truck].append(nearest_package)
                package_table.get_package(nearest_package.package_id, state="at_hub").delivery_status = "in transit"
                truck.num_packages += 1

                # Mark the package as loaded
                # TODO: add package to packages_in_transit list
                # TODO: Record their delivery time, truck they are on, and ETA
                package_table.add_package(nearest_package.package_id, nearest_package, state="in_transit")
                package_table.remove_package(nearest_package.package_id, state="at_hub")

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
    package_to_lookup = None

    if package_table.get_package(package_id, state="at_hub") is not None:
        package_to_lookup = package_table.get_package(package_id, state="at_hub")
    elif package_table.get_package(package_id, state="in_transit") is not None:
        package_to_lookup = package_table.get_package(package_id, state="in_transit")
    elif package_table.get_package(package_id, state="delivered") is not None:
        package_to_lookup = package_table.get_package(package_id, state="delivered")

    if package_to_lookup is not None:
        print("\nDelivery address:", package_to_lookup.address,
              package_to_lookup.city + ", " + package_to_lookup.zip_code)
        print("Delivery deadline:", package_to_lookup.deadline)
        print("Package weight:", package_to_lookup.weight + "KG")
        print("Package", package_id, "is", package_to_lookup.delivery_status)
        print()
    else:
        print("\nPackage not found. Please try another package ID.")


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


distances = get_location_data()
print(nearest_neighbor_algorithm(trucks, packages_at_hub, distances))

get_user_input()
