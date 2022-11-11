import mysql.connector

# con: The primary connection to the existing up and running MySQL server.
# cur: The primary cursor used to interact with the MySQL server.
con = mysql.connector.connect(user='root', password='root', database='courier', host='localhost')
if not con.is_connected():
    print("Error connecting to MySQL database! Please check your environment setup.")
cur = con.cursor()

def setup():
    TABLE_BUILD_CMDS = [
        "CREATE TABLE couriers(CourierID CHAR(5) PRIMARY KEY, FromLoc TEXT, ToLoc TEXT)",
        "CREATE TABLE transportations(TransportID CHAR(5) PRIMARY KEY, Transport CHAR(10), Capacity INT)",
        "CREATE TABLE shipments(TransportID CHAR(5) NOT NULL,\
        CourierID CHAR(5) NOT NULL,\
        ShippingTime DATE,\
        FOREIGN KEY(TransportID) REFERENCES transportations(TransportID),\
        FOREIGN KEY(CourierID) REFERENCES couriers(CourierID))"
    ]
    for cmd in TABLE_BUILD_CMDS:
        try:
            cur.execute(cmd)
        except mysql.connector.Error:
            pass
    cur.execute("COMMIT")

def cleanup():
    TABLE_DESTROY_CMDS = [
        "DROP TABLE shipments;",
        "DROP TABLE couriers;",
        "DROP TABLE transportations;"
    ]
    for CMD in TABLE_DESTROY_CMDS:
        try:
            cur.execute(CMD)
        except mysql.connector.Error:
            pass
    cur.execute("COMMIT")

def addTransportation():
    transportID = input("Enter transport ID (5 characters): ").strip()
    transport = input("Enter transport type (Air/Water/Land): ").strip()
    capacity = input("Enter capacity (couriers): ").strip()
    cur.execute("INSERT INTO transportations VALUES (%s, %s, %s)", (transportID, transport, capacity))
    cur.execute("COMMIT")

def viewTransportation(transportID = None):
    if transportID == None:
        transportID = input("Enter transport ID: ").strip()
    cur.execute("SELECT * FROM transportations WHERE TransportID=%s", (transportID,))
    data = cur.fetchone()
    if data == None:
        print(" No transport with the given ID!")
    else:
        print('#'*30, "\nTransportation details:")
        print(" Transport ID: {}\n Transport type: {}\n Capacity (Couriers): {}".format(data[0], data[1], data[2]))
    return data

def editTransportation():
    transportID = input("Enter transport ID: ").strip()
    data = viewTransportation(transportID)
    print('#' * 30)
    if data == None:
        return
    (transportID, transport, capacity) = data
    while True:
        print("Edit transport", transportID)
        print(" 1) Change transport ID")
        print(" 2) Change transport type")
        print(" 3) Change transport capacity")
        print(" *) Continue")
        choice = int(input("Enter your choice: ").strip())
        if choice==1:
            transportID = input("Enter new transport ID: ").strip()
        elif choice==2:
            transport = input("Enter new transport type: ").strip()
        elif choice==3:
            capacity = input("Enter new transport capacity: ").strip()
        else:
            break
    cur.execute("UPDATE transportations SET TransportID=%s, Transport=%s, Capacity=%s", (transportID, transport, capacity))
    cur.execute("COMMIT")
    print("Successfully updated the data!\n")

def manageTransportations():
    while True:
        print('#' * 30)
        print("Manage transportations:")
        print(" 1) Add new transportation")
        print(" 2) View transportation details")
        print(" 3) Edit transportation details")
        print(" 4) Return")
        choice = int(input("Enter your choice: ").strip())
        if choice == 1:
            addTransportation()
        elif choice == 2:
            viewTransportation()
        elif choice == 3:
            editTransportation()
        elif choice==4:
            break

def addCourier():
    courierID = input("Enter courier ID (5 characters max): ").strip()
    fromLoc = input("Enter from location: ").strip().capitalize()
    toLoc = input("Enter to location: ").strip().capitalize()
    cur.execute("INSERT INTO couriers VALUES (%s, %s, %s)", (courierID, fromLoc, toLoc))
    cur.execute("COMMIT")

def findCouriers(courierID = None, fromLoc = None, toLoc = None):
    if courierID == None and fromLoc == None and toLoc == None:
        print("Find couriers:")
        print(" 1) Find courier by ID")
        print(" 2) Find courier by from location")
        print(" 3) Find courier by to location")
        choice = int(input("Enter your choice: ").strip())
        if choice == 1:
            courierID = input("Enter courier ID to find: ").strip()
        elif choice == 2:
            fromLoc = input("Enter from location to find: ")
        elif choice == 3:
            toLoc = input("Enter to location to find: ")
        else:
            return
    courierID = "%" if courierID == None else courierID
    fromLoc = "%" if fromLoc == None else fromLoc
    toLoc = "%" if toLoc == None else toLoc
    cur.execute("SELECT * FROM couriers WHERE \
        CourierID LIKE %s AND FromLoc LIKE %s AND ToLoc LIKE %s", (courierID, fromLoc, toLoc))
    data = cur.fetchall()
    print("Search results: ")
    if len(data) == 0:
        print("Nothing to show :(")
    else:
        print("[ CourierID | From Location | To Location ]")
        for d in data:
            print("  {} | {} | {} ".format(d[0].rjust(9), d[1].rjust(13), d[2].rjust(11)))


def manageCouriers():
    while True:
        print('\n' + '#' * 30)
        print("Manage couriers: ")
        print(" 1) Add courier")
        print(" 2) Find couriers")
        print(" 3) Return")
        choice = int(input("Enter your choice: ").strip())
        if choice == 1:
            addCourier()
        elif choice == 2: 
            findCouriers()
        elif choice == 3:
            break

def deployShipment():
    print('#' * 30)
    transportID = input("Select transportation by ID: ")
    courierID = input("Select courier by ID: ")
    shippingTime = input("Enter shipping time (yyyy-mm-dd format): ")
    cur.execute("INSERT INTO shipments VALUES(%s, %s, %s)", (transportID, courierID, shippingTime))
    cur.execute("COMMIT")

def findShipment(transportID = "", courierID = "", shippingDate = ""):
    if transportID == "" and courierID == "" and shippingDate == "":
        transportID = input("Enter transport ID: ").strip()
        courierID = input("Enter courierID: ").strip()
        shippingDate = input("Enter shipping date (yyyy-mm-dd format): ").strip()
    transportID = "%" if transportID == "" else transportID
    courierID = "%" if courierID == "" else courierID
    shippingDate = "%" if shippingDate == "" else shippingDate
    cur.execute("SELECT * FROM shipments WHERE\
        TransportID LIKE %s, CourierID LIKE %s, ShippingDate LIKE %s", (transportID, courierID, shippingDate))
    data = cur.fetchall()
    print("Search results: ")
    if len(data) == 0:
        print("Nothing to show :(")
    else:
        print("[ TransportID | CourierID | Shipping Date ]")
        for d in data:
            print("  {} | {} | {}".format(d[0].rjust(11), d[1].rjust(9), d[2].rjust(13)))

def rebuild():
    if input("Rebuilding the database destroys all the tables and rebuilds them.\n"
        "If the data stored is not backed up, loss of data is imminent.\n"
        "Do you still wish to continue? (yes/no): ").strip().lower() == "yes":
        cleanup()
        setup()

#################### Main logic ####################

setup()

while True:
    print('\n' + ('#' * 30))
    print("Welcome to control panel!")
    print(" 1) Manage transportations")
    print(" 2) Manage couriers")
    print(" 3) Deploy shipment")
    print(" 4) Cleanup and recreate the database")
    print("Anything else will close the prompt.")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        manageTransportations()
    elif choice == 2:
        manageCouriers()
    elif choice == 3:
        deployShipment()
    elif choice == 4:
        rebuild()
    else:
        break

con.close()
            
####################################################