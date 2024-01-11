# Devon Russo, WGU - Computer Science, Student ID: 010828078
# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.
# The packages will be stored in a hash table with their ID being used as the key.
# The package class stores all relevant information about each package

# Import the required libraries for the program to run. Built-in python libraries are allowed for the project.
import csv
from datetime import datetime, time, timedelta


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
        self.eta = "TBD"
        self.delivered_time = None

    def __str__(self):
        if self.deadline != 'EOD':
            return (f"Package: {self.package_id}, Address: {self.address} {self.city},{self.zip_code},"
                    f" deadline: {self.deadline.strftime('%I:%M %p')}, weight: {self.weight},"
                    f" status: {self.delivery_status})")
        else:
            return (f"Package: {self.package_id}, Address: {self.address} {self.city},{self.zip_code},"
                    f" deadline: {self.deadline}, weight: {self.weight}, status: {self.delivery_status})")

    # Method to format delivered_time with today's date
    def formatted_delivered_time(self):
        if self.delivered_time:
            return self.delivered_time.strftime("%I:%M %p")
        else:
            return "Not delivered yet"


# Create hash table to store packages. Can store/access packages by delivery status as well.
class PackageHashTable:
    def __init__(self):
        self.packages_by_state = {
            "at_hub": {},
            "in_transit": {},
            "delivered": {}
        }

    def add_package(self, package_id, package, state):
        self.packages_by_state[state][package_id] = package

    def get_package(self, package_id, state):
        return self.packages_by_state[state].get(package_id)

    def remove_package(self, package_id, state):
        if package_id in self.packages_by_state[state]:
            del self.packages_by_state[state][package_id]
            # print("Package", package_id, "was deleted from", state)
        else:
            print("Package", package_id, "is not in the", state, "table")

    def get_packages_in_state(self, state):
        return self.packages_by_state[state]


# Create truck class
class Truck:
    def __init__(self, max_capacity=16, speed=18.0, miles_driven=0.0, departure_time_str='08:00 AM'):
        self.max_capacity = max_capacity
        self.num_packages = 0
        self.speed = speed
        self.miles_driven = miles_driven

        # Remove 'AM' or 'PM' from departure_time_str
        departure_time_str = departure_time_str.replace('AM', '').replace('PM', '')

        # Include today's date in the departure time
        today = datetime.today()
        self.departure_time = datetime(today.year, today.month, today.day, *map(int, departure_time_str.split(':')))

    def __str__(self):
        return (f"Truck(max_capacity={self.max_capacity}, num_packages={self.num_packages}, speed={self.speed},"
                f" miles_driven={self.miles_driven})")


# Create location class
class Location:
    def __init__(self, address, distances):
        # Manipulate address into same format as package objects so the strings can be compared.
        self.address = address
        self.distances = distances


package_table = PackageHashTable()

# packages_at_hub = package_table.get_packages_in_state("at_hub")
# delivered_packages = package_table.get_packages_in_state("delivered")

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
            address = "{}, {}".format(row[1], row[4])
            city = row[2]
            zip_code = row[4]
            deadline = row[5]

            if deadline != 'EOD':
                deadline = datetime.combine(datetime.today(), datetime.strptime(deadline, "%I:%M %p").time())

            weight = row[6]
            special_notes = row[7]
            new_package = Package(package_id, address, city, zip_code, deadline, weight, special_notes)
            package_table.add_package(package_id, new_package, state="at_hub")


def apply_package_restrictions(packages, truck, package_table):
    restricted_packages = []
    # packages_at_hub = package_table.get_packages_in_state("at_hub")

    for pkg in packages:
        if pkg.package_id == 14 and not (
                package_table.get_package(15, state="at_hub") and package_table.get_package(19, state="at_hub")):
            continue
        elif pkg.package_id == 16 and not (
                package_table.get_package(13, state="at_hub") and package_table.get_package(19, state="at_hub")):
            continue
        elif pkg.package_id in [25, 6, 28, 32] and datetime.now().time() < time(9, 5):
            # Packages 25, 6, 28, and 32 are delayed and should not be loaded until 9:05 am
            continue
        elif pkg.package_id == 20 and not (
                package_table.get_package(13, state="at_hub") and package_table.get_package(15, state="at_hub")):
            print(f"Package 20 cannot be loaded: Missing package 13 or 15.")
            continue
        elif pkg.package_id in [36, 18, 38, 3] and truck != truck2:
            # Packages 36, 18, 38, and 3 can only be on truck 2
            continue
        elif pkg.package_id == 9 and truck.departure_time >= datetime.combine(datetime.today(), time(10, 20)):
            # Package 9 has a wrong address listed
            pkg.address = "410 S State St"

        # If the package passed all restrictions, add it to the list
        restricted_packages.append(pkg)

    return restricted_packages


# Fill the package hash table
get_package_data()


# Define function to parse distance file and create location objects.
def get_location_data():
    distances = {}

    with open("files/distance_table.csv", "r", encoding='utf-8-sig') as distance_file:
        reader_variable = csv.reader(distance_file, delimiter=",")

        header = next(reader_variable)  # Skip the header row
        local_locations = [location.strip() for location in header[2:]]  # Remove extra spaces

        for row in reader_variable:
            current_location = row[1].strip().replace('(', '').replace(')', '')
            distances[current_location] = {}

            for i, distance_str in enumerate(row[2:]):
                destination_location = local_locations[i].strip().replace('(', '').replace(')', '')
                try:
                    if distance_str:
                        distance = float(distance_str)
                        distances[current_location][destination_location] = distance
                    else:
                        # Ignore empty distances
                        continue
                except ValueError:
                    distances[current_location][destination_location] = float('inf')

        # Set distances from each location to itself as 0
        distances[current_location][current_location] = 0.0

    # print("Locations:", local_locations)
    # print("Distances:")
    # for location, dist_dict in distances.items():
    #     print(f"{location}: {dist_dict}")

    return distances, local_locations


def nearest_neighbor_algorithm(trucks, distances, max_total_miles=140.0):
    # Initialize empty route for each truck
    routes = {truck: [] for truck in trucks}

    delivered_packages = 0

    # TODO: Find a way to track delivered packages and the time that they were delivered.

    # Define function to calculate the distance between two locations
    def distance_between(location1, location2):

        # Access distances using the locations as keys
        if location1 in distances and location2 in distances[location1]:
            return distances[location1][location2]
        elif location2 in distances and location1 in distances[location2]:
            return distances[location2][location1]
        else:
            print(f"Distance between {location1} and {location2} not available.")
            return float('inf')  # or any other appropriate value for missing distances

    # Define function to get the nearest package for a given location and truck
    def get_nearest_package(current_location, remaining_packages, truck):
        valid_packages = [pkg for pkg in remaining_packages if truck.num_packages + 1 < truck.max_capacity]

        # Apply restrictions for specific packages
        valid_packages = apply_package_restrictions(
            valid_packages,
            truck,
            package_table
        )

        if not valid_packages:
            return None  # No valid packages available

        return min(valid_packages, key=lambda pkg: distance_between(current_location, pkg.address))

    # Start at the hub
    # TODO: We want to make sure two of the trucks are utilized.
    # TODO: Track miles and ensure that the miles traveled do not exceed 140 miles between the two trucks.
    # There is no good reason to use the third truck since there are only two drivers.
    while any(package_table.get_packages_in_state("at_hub") for truck in trucks[:2]):
        for truck in trucks[:2]:

            # TODO: This may be causing issues. The current location is being rewritten as HUB every time
            #  the algorithm is called
            current_location = 'HUB'

            nearest_package = get_nearest_package(
                current_location,
                package_table.get_packages_in_state("at_hub").values(),
                truck
            )

            if nearest_package is not None:
                # Load the package
                routes[truck].append(nearest_package.address)
                package_table.get_package(nearest_package.package_id, state="at_hub")
                truck.num_packages += 1
                truck.miles_driven += distance_between(current_location, nearest_package.address)

                # After loading the package in the nearest_neighbor_algorithm function
                print(f"Truck {trucks.index(truck) + 1} - Loaded package {nearest_package.package_id}, "
                      f"Distance to package: {distance_between(current_location, nearest_package.address)} miles, "
                      f"Total miles traveled: {truck.miles_driven:.2f} miles",
                      f"Packages delivered: {delivered_packages + 1}")

                # Mark the package as loaded
                package_table.add_package(nearest_package.package_id, nearest_package, state="in_transit")
                package_table.remove_package(nearest_package.package_id, state="at_hub")

                # Record the eta
                eta = truck.departure_time + timedelta(hours=truck.miles_driven / truck.speed)
                package_table.get_package(nearest_package.package_id,
                                          state="in_transit").eta = eta

                # Update the current location
                current_location = nearest_package.address
                get_nearest_package(current_location, package_table.get_packages_in_state("at_hub").values(), truck)

                delivered_packages += 1

            else:
                # Break out of the loading loop when no valid package is available
                break

            # Break out of the main loop if there are no more packages at the hub or in transit for any truck
            if not any(package_table.get_packages_in_state("at_hub") for truck in trucks):
                break

            if truck.num_packages == truck.max_capacity:
                routes[truck].append('HUB')
                current_location = 'HUB'
                truck.num_packages = 0
                get_nearest_package(current_location, package_table.get_packages_in_state("at_hub").values(), truck)

        # Print all packages in transit or at the hub at the end of the algorithm
        print("Packages in Transit or at the Hub after the algorithm:")
        for state in ["at_hub"]:
            packages = package_table.get_packages_in_state(state)
            for package_id, package in packages.items():
                print(f"Package {package_id} - Delivery Status: {package.delivery_status}, State: {state}")
                print(f"  Address: {package.address}, Deadline: {package.deadline}")
                if state == "in_transit":
                    print(f"  ETA: {package.eta}, Delivered Time: {package.formatted_delivered_time()}")
                print()

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
        # Display package details
        print("\nAddress:", package_to_lookup.address,
              package_to_lookup.city + ", " + package_to_lookup.zip_code)
        if package_to_lookup.deadline != 'EOD':
            print("Deadline:", package_to_lookup.deadline.strftime('%I:%M %p'))
        else:
            print("Deadline:", package_to_lookup.deadline)
        print("Weight:", package_to_lookup.weight + "KG")
        print("Package", package_id, "is", package_to_lookup.delivery_status, "due at", package_to_lookup.eta)

        # Display actual delivery time
        print("Actual Delivery Time:", package_to_lookup.formatted_delivered_time())
        if package_to_lookup.eta != 'TBD':
            estimated_delivery_time = starting_time + timedelta(hours=package_to_lookup.eta)
            print("Estimated Delivery Time:", estimated_delivery_time)

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
    # Print status, ETA, truck.

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

    # Returns the current status of the package if the package exists.
    if user_input == 1:
        id_input = int(input("Enter package ID: "))
        lookup_package(id_input)
        get_user_input()
    # TODO: This will eventually return the status of all packages at any given user selected time
    elif user_input == 2:
        print("This feature has not yet been added\n")
        time_function()
        get_user_input()
    # TODO: Not sure if this will end up getting used. Will change the departure time of the trucks.
    elif user_input == 3:
        set_departure_time()
        get_user_input()
    # Quits the program
    elif user_input == 4:
        print("Quitting program...")
        exit()
    else:
        get_user_input()


result = get_location_data()
extracted_distances = result[0]  # Extract the distances dictionary
extracted_locations = result[1]  # Extract the locations list

print(nearest_neighbor_algorithm(trucks, extracted_distances))

print("Miles driven for truck 1:", truck1.miles_driven)
print("Miles driven for truck 2:", truck2.miles_driven)
print("Total miles driven:", truck1.miles_driven + truck2.miles_driven)

# get_user_input()

packages_at_hub = package_table.get_packages_in_state("at_hub")

num_restricted_pkgs = 0
restricted_pkgs = []

for package_id, package in packages_at_hub.items():
    if package.special_notes != '':
        num_restricted_pkgs += 1
        print("Package:", package.package_id, "-", package.special_notes)
        restricted_pkgs.append(package.package_id)

print(restricted_pkgs)

# Check delivery status of all packages
for package_id, package in package_table.get_packages_in_state("in_transit").items():
    print(f"Package {package_id} - Delivery Status: {package.delivery_status}")

for package_id, package in package_table.get_packages_in_state("delivered").items():
    print(f"Package {package_id} - Delivered at: {package.formatted_delivered_time()}")

# Check detailed delivery status of packages in transit
for package_id, package in package_table.get_packages_in_state("in_transit").items():
    print(f"Package {package_id} - Delivery Status: {package.delivery_status}")
    print(f"  Address: {package.address}, Deadline: {package.deadline}")
    print(f"  Distance traveled: {truck1.miles_driven:.2f} miles")
    print(f"  ETA: {package.eta}, Delivered Time: {package.formatted_delivered_time()}")
    print()
