# Devon Russo

# C950 PA Task 2
# Created on 12/30/2023

# This program uses the nearest neighbor algorithm to design an efficient route to deliver packages.

# The packages will be stored in a hash table with their ID being used as the key.

import csv


# Creating package class
class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, special_notes):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.special_notes = special_notes
