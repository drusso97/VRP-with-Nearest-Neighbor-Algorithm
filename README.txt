This program uses the nearest neighbor algorithm to find an efficient solution to the Vehicle Routing Problem.
It uses various functions and classes to store and manipulate package and vehicle data. There are several checks in place
to ensure that various delivery restrictions are met and that the total miles traveled does not exceed 140.

    A hash table is implemented using linked lists since dictionaries are not allowed to be used for the project. The
package ID was chosen as the hash key since it is an integer, and it is unique to each package.

    The program has an intuitive UI to check the status of any package at any time. The user can also check the status
of all packages at three different time intervals and print the total miles driven by all three trucks after the routes
have completed.

The program considers the following assumptions:

    * Each truck can carry no more than 16 packages
    * The trucks travel at a constant speed of 18 mph and have no need to stop
    * Three trucks and two drivers are available
    * The address for package 9 is incorrect and will be updated at 10:20 am
    * Package loading and delivery is instantaneous

This program was developed and tested in Python 3.10 with Pycharm. It was not tested in any other environments.