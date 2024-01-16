# Devon Russo, WGU - Computer Science, Student ID: 010828078
# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.
# The packages will be stored in a hash table with their ID being used as the key.
# The package class stores all relevant information about each package.

# Import the required libraries for the program to run. Built-in python libraries are allowed for the project.
import csv
from datetime import datetime, time, timedelta

starting_time = time(8, 00)
today = datetime.today()
current_time = starting_time
current_datetime = datetime.combine(today, current_time)


# Create package class.
class Package:
    def __init__(self, package_id, address, city, zip_code, deadline, weight, special_notes=""):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.special_notes = special_notes
        self.truck = None
        self.loaded_time = None
        self.delivery_time = None

    def __str__(self):
        if self.deadline != 'EOD':
            return (f"Package: {self.package_id}, Address: {self.address} {self.city},{self.zip_code},"
                    f" deadline: {self.deadline.strftime('%I:%M %p')}, weight: {self.weight}")
        else:
            return (f"Package: {self.package_id}, Address: {self.address} {self.city},{self.zip_code},"
                    f" deadline: {self.deadline}, weight: {self.weight}")

    # Method to format delivered_time with today's date
    def formatted_delivered_time(self):
        if self.delivery_time:
            return self.delivery_time.strftime("%I:%M %p")
        else:
            return "Not delivered yet"


# Create hash table to store packages. Can store/access packages by delivery status as well.
class PackageHashTable:
    def __init__(self):
        self.packages_by_status = {
            "at_hub": {},
            "in_transit": {},
            "delivered": {}
        }

    def add_package(self, package_id, package, status="at_hub"):
        self.packages_by_status[status][package_id] = package

    def get_package(self, package_id, status="at_hub"):
        return self.packages_by_status[status].get(package_id)

    def remove_package(self, package_id, status="at_hub"):
        if package_id in self.packages_by_status[status]:
            del self.packages_by_status[status][package_id]
        else:
            print("Package", package_id, "is not in the", status, "table")

    def get_packages_in_state(self, status="at_hub"):
        return self.packages_by_status[status]


# Create truck class
class Truck:
    def __init__(self, max_capacity=16, speed=18.0, miles_driven=0.0,
                 departure_time=datetime.combine(today, time(8, 0))):
        self.max_capacity = max_capacity
        self.num_packages = 0
        self.speed = speed
        self.miles_driven = miles_driven
        self.departure_time = departure_time

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

packages_at_hub = package_table.get_packages_in_state("at_hub")

# WGUPS has three trucks available
truck1 = Truck()
truck2 = Truck()
truck3 = Truck()

trucks = [truck1, truck2, truck3]


# Define function to parse csv file and create package objects.
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
            package_table.add_package(package_id, new_package, status="at_hub")


def apply_package_restrictions(packages, truck):
    restricted_packages = []

    for pkg in packages:
        if pkg.package_id in [25, 6, 28, 32]:
            # Packages 25, 6, 28, and 32 are delayed and should not be loaded until 9:05 am
            if current_datetime < datetime.combine(today, time(9, 5)):
                continue
        elif pkg.package_id in [36, 18, 38, 3]:
            # Packages 36, 18, 38, and 3 can only be on truck 2
            if truck != truck2:
                continue
        elif pkg.package_id == 9:
            # Package 9 has a wrong address listed. To be corrected at 10:20 AM
            if current_datetime < datetime.combine(datetime.today(), time(10, 20)):
                continue
            else:
                pkg.address = "410 S State St, 84111"

        # Add the package to the list
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

    return distances, local_locations


def nearest_neighbor_algorithm(trucks, distances):
    # Initialize empty route for each truck
    global current_time, current_datetime
    routes = {truck: [] for truck in trucks}

    delivered_packages = 0

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
    def get_nearest_package(current_location, packages, truck):

        # Apply restrictions for specific packages
        all_packages = apply_package_restrictions(packages, truck)

        # Deliver packages with a hard deadline first
        priority_packages = [pkg for pkg in all_packages if pkg.deadline != 'EOD']

        # The following packages must all be delivered together. This works now.
        grouped_packages = [pkg for pkg in all_packages if pkg.package_id in [13, 14, 15, 16, 19, 20]]

        # Combine the two lists together. This might not be the ideal way to do this, but I was struggling to figure
        # out how to force the grouped packages to be loaded together.
        for pkg in grouped_packages:
            if pkg not in priority_packages:
                priority_packages.append(pkg)

        # Packages without a hard deadline
        remaining_packages = [pkg for pkg in all_packages if pkg not in priority_packages]

        # Deliver priority packages first
        while priority_packages:
            return min(priority_packages, key=lambda pkg: distance_between(current_location, pkg.address))

        # There are no priority packages remaining
        else:
            while remaining_packages:
                return min(remaining_packages, key=lambda pkg: distance_between(current_location, pkg.address))

        # There are no packages remaining. Return none.
        if not priority_packages or remaining_packages:
            return None

    # Not using the third truck since there are only two drivers.
    for truck in trucks[:2]:
        # Start at the hub
        current_location = 'HUB'
        truck_string = "Truck 1" if trucks.index(truck) == 0 else "Truck 2"

        loaded_time = datetime.combine(today, starting_time)

        # While there are packages remaining.
        while True:
            nearest_package = get_nearest_package(
                current_location,
                package_table.get_packages_in_state("at_hub").values(),
                truck
            )

            # 50 is an arbitrary limit. I just wanted to make sure both trucks were utilized to trim off some miles.
            if nearest_package is not None and truck.num_packages < truck.max_capacity and truck.miles_driven <= 50:
                # Load the package
                routes[truck].append(nearest_package.address)
                package_table.get_package(nearest_package.package_id, status="at_hub")
                truck.num_packages += 1
                truck.miles_driven += distance_between(current_location, nearest_package.address)

                # Record delivery eta
                eta = truck.departure_time + timedelta(hours=truck.miles_driven / truck.speed)

                # Print information showing that package was delivered.
                print(f"Truck {trucks.index(truck) + 1} - Delivered package {nearest_package.package_id},"
                      f" at {eta.strftime('%I:%M %p')}. "
                      f"Distance to package: {distance_between(current_location, nearest_package.address)} miles, "
                      f"Miles traveled: {truck.miles_driven:.2f},",
                      f"Packages delivered: {delivered_packages + 1}")

                # Mark the package as delivered.
                package_table.add_package(nearest_package.package_id, nearest_package, status="delivered")

                # Record attributes for the new package.
                delivered_package = package_table.get_package(nearest_package.package_id, status="delivered")
                delivered_package.delivery_time = eta
                delivered_package.truck = truck_string
                delivered_package.loaded_time = loaded_time

                package_table.remove_package(nearest_package.package_id, status="at_hub")

                # Update the time.
                if eta >= current_datetime:
                    current_datetime = eta

                # Update the current location
                current_location = nearest_package.address

                delivered_packages += 1

            # The truck is full and will have to return to the hub to get more packages.
            elif truck.num_packages >= truck.max_capacity:
                routes[truck].append('HUB')  # Indicates a return to the hub
                truck.num_packages = 0
                current_location = 'HUB'
                loaded_time = eta

            else:
                # If no valid package is available, exit the loop
                break


delivered_packages = package_table.get_packages_in_state("delivered")


# Lookup a package by ID and print its status.
def lookup_package(package_id, time):
    # Check if the package exists.
    statuses_to_check = ["at_hub", "in_transit", "delivered"]
    pkg = next((package_table.get_package(package_id, status) for status in statuses_to_check if
                package_table.get_package(package_id, status) is not None), None)

    if pkg is not None:

        deadline = pkg.deadline.strftime('%I:%M %p') if pkg.deadline != 'EOD' else str(
            pkg.deadline)

        # Display package details
        print(f"\nPackage: {package_id}\n"
              f"{pkg.address.split(',')[0].strip()}\n{pkg.city}, {pkg.zip_code}\n"
              f"Deadline: {deadline}\nWeight: {pkg.weight}KG")

        # Check the package status.
        if time < pkg.loaded_time:
            print(f"Package {package_id} is currently at the hub, expected to arrive by {pkg.deadline}")
        elif pkg.loaded_time <= time < pkg.delivery_time:
            print(f"Package {package_id} is currently in transit on {pkg.truck},"
                  f" expected to arrive at {pkg.delivery_time.strftime('%I:%M %p')}")
        else:
            print(f"Package {package_id} was delivered by {pkg.truck} at {pkg.delivery_time.strftime('%I:%M %p')}")

    else:
        print("\nPackage not found. Please try another package ID.")


# Prints a status report of all packages at given time.
def get_status_reports():
    print("Please choose from the following options:")
    print("(1) - Print status of all packages between 8:35 a.m. and 9:25 a.m")
    print("(2) - Print status of all packages between 9:35 a.m. and 10:25 a.m")
    print("(3) - Print status of all packages between 12:03 p.m. and 1:12 p.m")
    print("(4) - Return to main menu\n")

    user_input = int(input("Select an option: "))

    def status_report(start, end):
        for pkg in delivered_packages.values():
            if pkg.delivery_time <= end:
                print(f"Package {pkg.package_id} was delivered by {pkg.truck}"
                      f" at {pkg.formatted_delivered_time()}")
            else:
                print(
                    f"Package {pkg.package_id} will be delivered by {pkg.truck}"
                    f" at {pkg.formatted_delivered_time()}")

    if user_input == 1:
        start_time = datetime.combine(today, time(8, 35))
        end_time = datetime.combine(today, time(9, 25))

        print("Showing status of all packages between 8:35 a.m. and 9:25 a.m\n")
        status_report(start_time, end_time)
    elif user_input == 2:
        start_time = datetime.combine(today, time(9, 35))
        end_time = datetime.combine(today, time(10, 25))

        print("Showing status of all packages between 9:35 a.m. and 10:25 a.m\n")
        status_report(start_time, end_time)
    elif user_input == 3:
        start_time = datetime.combine(today, time(12, 3))
        end_time = datetime.combine(today, time(13, 12))

        print("Showing status of all packages between 12:03 p.m. and 1:12 p.m\n")
        status_report(start_time, end_time)
    elif user_input == 4:
        main_menu()
    else:
        get_status_reports()


# Allows the user to interact with the program.
def main_menu():
    time_input = None

    valid_time = False

    while not valid_time:
        try:
            time_input = input("\nPlease enter the time - (format - HH:MM) : ")
            hour, min = [int(i) for i in time_input.split(":")]

            # Check if the input has both hour and minute values
            if len(time_input.split(":")) != 2:
                raise ValueError("Invalid time format")

            time_input = datetime.combine(today, time(hour, min))
            valid_time = True
        except ValueError as e:
            print(f"Error: {e}")
            print("Please enter a valid time - (format - HH:MM)")

    print("\nPlease choose from the following options:")
    print("(1) - Lookup package by ID")
    print("(2) - Print status of all of today's packages by time")
    print("(3) - Quit the program\n")

    user_selection = int(input("Select an option: "))

    if user_selection == 1:
        package_to_lookup = int(input("Enter package ID: "))
        lookup_package(package_to_lookup, time_input)
        main_menu()
    elif user_selection == 2:
        get_status_reports()
        main_menu()
    elif user_selection == 3:
        print("Quitting program...")
        exit()
    else:
        main_menu()


result = get_location_data()
extracted_distances = result[0]  # Extract the distances dictionary
extracted_locations = result[1]  # Extract the locations list

print(nearest_neighbor_algorithm(trucks, extracted_distances))

print("Miles driven for truck 1:", truck1.miles_driven)
print("Miles driven for truck 2:", truck2.miles_driven)
print("Total miles driven:", truck1.miles_driven + truck2.miles_driven)

packages_in_transit = package_table.get_packages_in_state("in_transit")

main_menu()
