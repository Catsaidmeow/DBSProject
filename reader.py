import csv


def checkUser(user):
        global invalid_names
        global invalid_Screennames
        global invalid_location
        global invalid_verified

        if isEmpty(user["id"]) or (not user["id"].isdigit()):
                #print("ID", user["id"])
                return False

        if isEmpty(user["name"]):
                #print("Name", user["name"])
                # return False
                invalid_names += 1
                return False

        if isEmpty(user["screenName"]):
                #print("ScreenName", user["screenName"])
                invalid_Screennames += 1
                return False

        if isEmpty(user["location"]):
                #print("Location", user["location"])
                invalid_location += 1
                # return False


        if isEmpty(user["verified"]) or (not isStringBool(user["verified"])):
                #print("Verified", user["verified"])
                invalid_verified += 1
                return False

        return True

def checkUsers():

        i,j = 0,0
        with open('prj_user.csv', "r") as csv_file:
                users = csv.DictReader(csv_file, delimiter=';')
                for user in users:
                        i += 1
                        if checkUser(user):
                                # User is valid
                                j += 1
                                insertUser(user)
                print("Von",i,"Usern sind",j,"gültig.")

def insertUser(user):
    # TODO
    # print(user["screenName"])
    pass

def isEmpty(string):
        return (not string) or string == "None"

def isStringBool(string):
        if(string == "True" or string == "False"):
                return True
        else:
                return False


if __name__ == "__main__":
        invalid_names = 0
        invalid_Screennames = 0
        invalid_location = 0
        invalid_verified = 0

        checkUsers()

        print(f"Invalid Names {invalid_names}")
        print(f"Invalid ScreenNames {invalid_Screennames}")
        print(f"Invalid Locations {invalid_location}")
        print(f"Invalid Verified {invalid_verified}")