import mysql.connector

import datetime # To get the current date and time

# con: The primary connection to the existing up and running MySQL server.
# cur: The primary cursor used to interact with the MySQL server.
Con = mysql.connector.connect(user='root', password='root', database='courier', host='localhost')
if not Con.is_connected():
    print("Error connecting to MySQL database! Please check your environment setup.")
Cur = Con.cursor()

# CourierCount: Used to track the count of the number of couriers and assign IDs automatically.
# Initial value is the count of the couriers in the database.

CourierCount = 0

def setup():
    TABLE_BUILD_CMDS = [
        # Users table
        "CREATE TABLE users(Username CHAR(30) PRIMARY KEY, Password CHAR(30))",

        # Couriers table
        "CREATE TABLE couriers(CourierID CHAR(5) PRIMARY KEY, CustomerID CHAR(30) NOT NULL,"\
            "FromLoc TEXT, ToLoc TEXT,"\
            "ServiceTier CHAR(10), RequestDate DATE, FOREIGN KEY(CustomerID) REFERENCES users(Username))"
    ]
    for cmd in TABLE_BUILD_CMDS:
        try:
            Cur.execute(cmd)
        except mysql.connector.Error as err:
            print(err.msg)
            pass
    Con.commit()

    global CourierCount
    Cur.execute("SELECT COUNT(*) FROM couriers;")
    CourierCount = int(Cur.fetchone()[0])

def cleanup():
    TABLE_DESTROY_CMDS = [
        "DROP TABLE couriers;",
        "DROP TABLE users;",
    ]
    for CMD in TABLE_DESTROY_CMDS:
        try:
            Cur.execute(CMD)
        except mysql.connector.Error:
            pass
    Con.commit()

def rebuild():
    if input("Rebuilding the database destroys all the tables and rebuilds them.\n"
        "If the data stored is not backed up, loss of data is imminent.\n"
        "Do you still wish to continue? (yes/no): ").strip().lower() == "yes":
        cleanup()
        setup()

def _getUsers():
    Cur.execute("SELECT * FROM users")
    return Cur.fetchall()

def signUp():
    while True:
        print('-'*30)
        print("SIGNUP")
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        for user in _getUsers():
            if user[0] == username:
                print("Username already taken! Please enter a different username and try again!")
                continue
        Cur.execute("INSERT INTO users VALUES(%s, %s)", (username, password))
        break
    Con.commit()

LoginInformation = None

def login():
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()
    Cur.execute("SELECT Username FROM users WHERE Username=%s AND Password=%s", (username, password))
    if Cur.fetchall() == []:
        print("Invalid username/password combo!")
    else:
        global LoginInformation
        print("Successfully logged in as", username, "!")
        LoginInformation = {"Username": username, "Password": password}

def sendCourier():
    global LoginInformation, CourierCount
    if LoginInformation == None:
        print("You need to login before sending a courier! Please login!")
        return
    print("Sending courier as", LoginInformation["Username"])
    fromLoc = input("Enter from location: ")
    toLoc = input("Enter to location: ")
    requestDate = datetime.date.today().isoformat()
    print("Enter the service tier you would like to opt:"\
        " 1) Standard - Basic courier service with International shipping.",\
        " 2) Prime - Faster delivery ( + INR 1500.00 )",\
        " 3) PrimePlus - Fastest delivery and 5\% off of your next 3 couriers! ( + INR 2500.00 )", sep="\n")
    serviceTierChoice = int(input("Enter your choice: ").strip())
    serviceTier = None
    if serviceTierChoice == 1:
        serviceTier = "Standard"
    elif serviceTierChoice == 2:
        serviceTier = "Prime"
    elif serviceTierChoice == 3:
        serviceTier = "PrimePlus"
    else:
        print("Invalid service tier choice", serviceTierChoice, "! Cancelling last request!")
        return
    print("Selecting service tier", serviceTier)
    CourierCount += 1
    courierId = CourierCount
    Cur.execute("INSERT INTO couriers VALUES(%s, %s, %s, %s, %s, %s)", \
        (courierId, LoginInformation["Username"], fromLoc, toLoc, serviceTier, requestDate))
    print("Successfully sent courier! Your courier ID is", courierId)
    Con.commit()

def _getAllCouriers():
    global LoginInformation
    Cur.execute("SELECT * FROM couriers WHERE CustomerID=%s;", (LoginInformation["Username"],))
    couriers = Cur.fetchall()
    if couriers == []:
        print("You haven't sent out any couriers yet. Try sending one now! :D")
    return couriers

def printCouriers(couriers):
    if couriers == []:
        return
    print('-' * 67)
    print("| {} | {} | {} | {} | {} |".format(\
        "SlNo".rjust(4), "From".rjust(10), "To".rjust(10), \
            "Date of Sending", "Service Tier"))
    print('-' * 67)
    for courier in couriers:
        print("| {} | {} | {} | {} | {} |".\
            format(courier[0].rjust(4), \
                courier[2].rjust(10), courier[3].rjust(10), \
                str(courier[5]).rjust(15), courier[4].rjust(12)))
    print('-' * 67)


def trackCourier():
    courierId = int(input("Enter your courier ID: ").strip())
    Cur.execute("SELECT * FROM couriers WHERE CourierID=%s", (courierId,))
    dat = Cur.fetchone()
    if dat == ():
        print("No courier with the given ID!")
    else:
        global LoginInformation
        if dat[1] != LoginInformation["Username"]:
            print("Mismatch between currently logged in user and the user who sent the courier!",
            "Please login as the user who sent the courier to track it!")
        else:
            print(("Courier ID: {}\nService Tier: {}\nFrom location: " +\
                "{}\nTo location: {}\nDate of sending: {}")\
                    .format(dat[0], dat[4], dat[2], dat[3], dat[5]))

def searchCourier():
    global LoginInformation
    couriers = []
    choice = int(input("Would you like to search by"+\
        "(1) from location or (2) to location? (1/2): "))
    if choice == 1:
        fromLoc = input("Enter from location: ").strip()
        Cur.execute("SELECT * FROM couriers WHERE CustomerID=%s AND FromLoc LIKE %s",\
            (LoginInformation["Username"], fromLoc))
        couriers = Cur.fetchall()
    elif choice == 2:
        toLoc = input("Enter to location: ").strip()
        Cur.execute("SELECT * FROM couriers WHERE CustomerID=%s AND ToLoc LIKE %s", \
            (LoginInformation["Username"], toLoc))
        couriers = Cur.fetchall()
    else:
        return
    if couriers == []:
        print("Search results empty :(")
    else:
        printCouriers(couriers)

def manageCouriers():
    if LoginInformation == None:
        print("You need to login in order manage your couriers!")
        return
    while True:
        print('#' * 25)
        print("Manage your couriers")
        print(" 1) View all your couriers")
        print(" 2) Track a courier")
        print(" 3) Search courier by from or to location")
        print(" *) Go back")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            printCouriers(_getAllCouriers())
        elif choice == 2:
            trackCourier()
        elif choice == 3:
            searchCourier()
        else:
            break

#################### Main logic ####################

setup()

while True:
    print('\n', ('#' * 30))
    print("Welcome to control panel!")
    print(" 1) Sign up")
    print(" 2) Log in")
    print(" 3) Send a courier")
    print(" 4) Manage your couriers")
    print(" 5) Admin tools: Rebuild the database")
    print(" *) Exit")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        signUp()
    elif choice == 2:
        login()
    elif choice == 3:
        sendCourier()
    elif choice == 4:
        manageCouriers()
    elif choice == 5:
        rebuild()
    else:
        break

Con.close()
            
####################################################
