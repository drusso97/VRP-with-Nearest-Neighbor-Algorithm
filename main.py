# Devon Russo, WGU - Computer Science, Student ID: 010828078
# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.
# The packages will be stored in a hash table with their ID being used as the key.
# The package class stores all relevant information about each package.

# Import the required libraries for the program to run. Built-in python libraries are allowed for the project.
import csv
from datetime import datetime, time, timedelta

current_time = time(8, 00)
today = datetime.today()
current_datetime = datetime.combine(today, current_time)


# Create package class.
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
        self.truck = None
        self.loaded_time = None
        self.delivery_time = None
        self.status = "at_hub"

    # Method to format delivered_time with today's date
    def formatted_delivered_time(self):
        if self.delivery_time:
            return self.delivery_time.strftime("%I:%M %p")
        else:
            return "Not delivered yet"


# The Package Hash Table is implemented using linked lists.
class PackageHashTable:
    def __init__(self, size=10):
        self.size = size
        self.buckets = [LinkedList() for _ in range(size)]

    # The package ID is used as the key for the hash table. In our case, each package has a unique ID,
    # so there is no risk of hash collisions
    def _hash_function(self, package_id):
        return package_id % self.size

    # Adds a package to the hash table.
    def add_package(self, package):
        index = self._hash_function(package.package_id)
        self.buckets[index].insert(package)

    # Returns a package from the hash table.
    def get_package(self, package_id):
        index = self._hash_function(package_id)
        return self.buckets[index].find(package_id)

    # Removes a package from the hash table.
    def remove_package(self, package_id):
        index = self._hash_function(package_id)
        self.buckets[index].delete(package_id)

    # Gets all packages in a given status, "at_hub", "in_transit", or "delivered".
    def get_packages_in_state(self, status):
        result = []
        for bucket in self.buckets:
            current = bucket.head
            while current:
                if current.package.status == status:
                    result.append(current.package)
                current = current.next
        return result

    # Changes the package status.
    def update_package_status(self, package_id, new_status):
        index = self._hash_function(package_id)
        self.buckets[index].update_status(package_id, new_status)


# Our node class for the linked list.
class Node:
    def __init__(self, package):
        self.package = package
        self.next = None


# Our linked list class.
class LinkedList:
    def __init__(self):
        self.head = None

    # Insert a new node.
    def insert(self, package):
        new_node = Node(package)
        new_node.next = self.head
        self.head = new_node

    # Find a node in the linked list.
    def find(self, package_id):
        current = self.head
        while current:
            if current.package.package_id == package_id:
                return current.package
            current = current.next
        return None

    # Delete a node from the linked list. Updates the head as necessary.
    def delete(self, package_id):
        current = self.head
        if current and current.package.package_id == package_id:
            self.head = current.next
            return

        prev = None
        while current and current.package.package_id != package_id:
            prev = current
            current = current.next

        if current is None:
            return

        prev.next = current.next

    # Gets all packages in a given status, "at_hub", "in_transit", or "delivered".
    def find_by_status(self, status):
        result = []
        current = self.head
        while current:
            if current.package.status == status:
                result.append(current.package)
            current = current.next
        return result

    # Change package status.
    def update_status(self, package_id, new_status):
        current = self.head
        while current:
            if current.package.package_id == package_id:
                current.package.status = new_status
                return
            current = current.next


# Initialize Package List
package_table = PackageHashTable()


# Create truck class
class Truck:
    def __init__(self, max_capacity=16, speed=18.0, miles_driven=0.0,
                 departure_time=datetime.combine(today, time(8, 0))):
        self.max_capacity = max_capacity
        self.num_packages = 0
        self.speed = speed
        self.miles_driven = miles_driven
        self.departure_time = departure_time
        self.packages_delivered = 0


# WGUPS has three trucks available
truck1 = Truck()

# Truck 2 does not depart until 9:05am since some of the packages are delayed.
truck2 = Truck(departure_time=datetime.combine(today, time(9, 5)))

# WGUPS has three trucks available, but we will not use the third since there are only two drivers available.
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
            state = row[3]
            zip_code = row[4]
            deadline = row[5]

            if deadline != 'EOD':
                deadline = datetime.combine(datetime.today(), datetime.strptime(deadline, "%I:%M %p").time())

            weight = row[6]
            special_notes = row[7]
            new_package = Package(package_id, address, city, state, zip_code, deadline, weight, special_notes)
            package_table.add_package(new_package)


# Fill the package hash table
get_package_data()


# Parse distance csv file to get the distances between the different locations.
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


# Applies the package restrictions found in the package special notes.
def apply_package_restrictions(packages, truck):
    restricted_packages = []

    for pkg in packages:
        if pkg.package_id in [25, 6, 28, 32]:
            # Packages 25, 6, 28, and 32 are delayed and should not be loaded until 9:05 am
            # These packages technically don't need to be loaded on truck 2,
            # but it solved the problem of them being delivered late.
            if current_datetime < datetime.combine(today, time(9, 5)) or truck != truck2:
                continue
        elif pkg.package_id in [36, 18, 38, 3]:
            # Packages 36, 18, 38, and 3 can only be on truck 2
            if truck != truck2:
                continue
        elif pkg.package_id == 9:
            pkg.address = "410 S State St, 84111"
            # Package 9 has a wrong address listed. To be corrected at 10:20 AM
            if current_datetime < datetime.combine(datetime.today(), time(10, 20)):
                continue

        # Add the package to the list
        restricted_packages.append(pkg)

    return restricted_packages


# This algorithm will continuously return the next nearest package while there are packages remaining.
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
            pkg = min(priority_packages, key=lambda pkg: distance_between(current_location, pkg.address))
            if pkg.status == "at_hub":
                return pkg

        # There are no priority packages remaining
        else:
            while remaining_packages:
                pkg = min(remaining_packages, key=lambda pkg: distance_between(current_location, pkg.address))
                if pkg.status == "at_hub":
                    return pkg

        # There are no packages remaining. Return none.
        return None

    # Not using the third truck since there are only two drivers.
    for truck in trucks[:2]:
        # Start at the hub
        current_location = 'HUB'
        truck_string = "Truck 1" if trucks.index(truck) == 0 else "Truck 2"

        loaded_time = truck.departure_time

        # While there are packages remaining.
        while True:
            nearest_package = get_nearest_package(
                current_location,
                package_table.get_packages_in_state("at_hub"),
                truck
            )

            # I decided to divide the packages between the two trucks to ensure both trucks were used.
            if nearest_package is not None and truck.num_packages < truck.max_capacity and truck.packages_delivered < 20:
                # Load the package
                routes[truck].append(nearest_package.address)
                package_table.get_package(nearest_package.package_id)
                truck.num_packages += 1
                truck.packages_delivered += 1
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
                package_table.update_package_status(nearest_package.package_id, "delivered")

                # Record attributes for the new package.
                delivered_package = package_table.get_package(nearest_package.package_id)
                delivered_package.delivery_time = eta
                delivered_package.truck = truck_string
                delivered_package.loaded_time = loaded_time

                # Update the current location
                current_location = nearest_package.address

                delivered_packages += 1

            # The truck is full. Deliver packages, then return to hub to get more packages.
            elif truck.num_packages >= truck.max_capacity and nearest_package is not None:

                # Update the time.
                if eta >= current_datetime:
                    current_datetime = eta

                routes[truck].append('HUB')  # Indicates a return to the hub
                truck.num_packages = 0
                distance_to_hub = distance_between(current_location, 'HUB')
                truck.miles_driven += distance_to_hub
                eta = truck.departure_time + timedelta(hours=truck.miles_driven / truck.speed)
                print(f"{truck_string} - Returned to HUB at {eta.strftime('%I:%M %p')}"
                      f" - Distance to hub: {distance_to_hub}, Miles traveled: {round(truck.miles_driven, 2)}")
                current_location = 'HUB'
                loaded_time = eta

            # There are no packages remaining, return to the hub and break the loop.
            else:
                routes[truck].append('HUB')  # Indicates a return to the hub
                distance_to_hub = distance_between(current_location, 'HUB')
                truck.miles_driven += distance_to_hub
                eta = truck.departure_time + timedelta(hours=truck.miles_driven / truck.speed)

                print(f"Route for {truck_string} completed - Returned to HUB at {eta.strftime('%I:%M %p')}"
                      f" - Distance to hub: {distance_to_hub}, Miles traveled: {round(truck.miles_driven, 2)}\n")
                break


# Prints the miles driven for each truck and the total miles between all the trucks.
def get_miles_for_all_trucks():
    total_miles = 0
    for truck in trucks:
        print(f"Miles driven for Truck {trucks.index(truck) + 1}: {truck.miles_driven}")
        total_miles += truck.miles_driven
    print(f"Miles driven by all trucks: {total_miles}")


# Lookup a package by ID and print its status.
def lookup_package(package_id, time):
    # Check if the package exists.
    pkg = package_table.get_package(package_id)

    if pkg is not None:

        deadline = pkg.deadline.strftime('%I:%M %p') if pkg.deadline != 'EOD' else str(
            pkg.deadline)

        # Display package details.
        print(f"\nPackage: {package_id}\n"
              f"{pkg.address.split(',')[0].strip()}\n{pkg.city} {pkg.state}, {pkg.zip_code}\n"
              f"Deadline: {deadline}\nWeight: {pkg.weight}KG")

        # Check the package status.
        if time < pkg.loaded_time:
            print(f"Package {package_id} is currently at the hub, expected to arrive by {deadline}")
        elif pkg.loaded_time <= time < pkg.delivery_time:
            print(f"Package {package_id} is currently in transit on {pkg.truck},"
                  f" expected to arrive at {pkg.delivery_time.strftime('%I:%M %p')}")
        else:
            print(f"Package {package_id} was delivered by {pkg.truck} at {pkg.delivery_time.strftime('%I:%M %p')}")

    else:
        print("\nPackage not found. Please try another package ID.")


# Prints status of all packages between two user-selected times.
def print_packages_on_trucks():
    print("Please choose from the following options:")
    print("(1) - Print status of all packages between 8:35 a.m. and 9:25 a.m")
    print("(2) - Print status of all packages between 9:35 a.m. and 10:25 a.m")
    print("(3) - Print status of all packages between 12:03 p.m. and 1:12 p.m")
    print("(4) - Return to main menu\n")

    user_input = int(input("Select an option: "))

    # Iterates through the delivered packages list and outputs all packages
    # that were in transit during the interval specified.
    def print_packages(start_time, end_time):
        for pkg in package_table.get_packages_in_state("delivered"):
            # The package has not been loaded yet.
            if end_time <= pkg.loaded_time:
                print(f"Package {pkg.package_id} is currently at the hub, due by {pkg.deadline.strftime('%I:%M %p') if pkg.deadline != 'EOD' else pkg.deadline}, loaded at {pkg.loaded_time}")
            # The package is still in transit.
            elif end_time >= pkg.loaded_time and pkg.delivery_time >= end_time:
                print(f"Package {pkg.package_id} is currently on {pkg.truck}"
                      f", due by {pkg.formatted_delivered_time()}")
            # The package was delivered.
            else:
                print(f"Package {pkg.package_id} was delivered by {pkg.truck} at {pkg.formatted_delivered_time()}")

    if user_input == 1:
        start_time = datetime.combine(today, time(8, 35))
        end_time = datetime.combine(today, time(9, 25))

        print("\nStatus of all packages between 8:35 a.m. and 9:25 a.m\n")
        print_packages(start_time, end_time)
    elif user_input == 2:
        start_time = datetime.combine(today, time(9, 35))
        end_time = datetime.combine(today, time(10, 25))

        print("\nStatus of all packages 9:35 a.m. and 10:25 a.m\n")
        print_packages(start_time, end_time)
    elif user_input == 3:
        start_time = datetime.combine(today, time(12, 3))
        end_time = datetime.combine(today, time(13, 12))

        print("\nStatus of all packages 12:03 p.m. and 1:12 p.m\n")
        print_packages(start_time, end_time)
    elif user_input == 4:
        main_menu()
    else:
        print_packages_on_trucks()


# Allows the user to interact with the program.
def main_menu():
    print("\nWelcome to WGUPS. Please choose from the following options:")
    print("(1) - Lookup package by ID")
    print("(2) - Print status of all of today's packages by time")
    print("(3) - Print mileage driven by all trucks")
    print("(4) - Quit the program\n")

    try:
        user_selection = int(input("Select an option: "))

        if user_selection == 1:
            time_input = None
            valid_time = False

            while not valid_time:
                try:
                    time_input = input("\nPlease enter the time to continue - (format - HH:MM) : ")
                    hour, minute = [int(i) for i in time_input.split(":")]

                    # Check if the input has both hour and minute values
                    if len(time_input.split(":")) != 2:
                        raise ValueError("Invalid time format")

                    time_input = datetime.combine(today, time(hour, minute))
                    valid_time = True
                except ValueError as e:
                    print(f"Error: {e}")
                    print("Please enter a valid time - (format - HH:MM)")

            package_to_lookup = int(input("Enter package ID: "))

            lookup_package(package_to_lookup, time_input)

            main_menu()
        elif user_selection == 2:
            print_packages_on_trucks()
            main_menu()
        elif user_selection == 3:
            print("\nMiles driven for all trucks today.\n")
            get_miles_for_all_trucks()
            main_menu()
        elif user_selection == 4:
            print("Quitting program...")
            exit()
        else:
            print("\nInput must be one of the following:")
            main_menu()
    except ValueError:
        print("\nInput must be one of the following:")
        main_menu()


# Get location data.
location_data = get_location_data()
extracted_distances = location_data[0]  # Extract the distances dictionary
extracted_locations = location_data[1]  # Extract the locations list

# Run algorithm to deliver packages.
nearest_neighbor_algorithm(trucks, extracted_distances)

# Run algorithm to deliver packages.
nearest_neighbor_algorithm(trucks, extracted_distances)

# Output total miles driven
get_miles_for_all_trucks()

# Launch main menu
main_menu()
