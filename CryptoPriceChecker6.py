from os import remove
import winsound
import bitmex
import json
import threading
from datetime import datetime

class Tick():
    def __init__(self, time, price):
        self.time = time
        self.price = price

class PriceChecker():
    # Constructor/Initializer
    def __init__(self):
        self.levelsList = []       #Call the @levelsList.setter method and pass it an empty  list
        self.currentPrice = 0.0    #Call the @currentPrice.setter method and pass it 0.0
        self.BitmexClient = bitmex.bitmex(test=False)
        self.previousPrice = 0.0   # Call the @previousPrice.setter method and pass it 0.0

    # Properties 
    # A property is defined like a method, but you use it in your 
    # code like a variable (no parentheses need to followed it when used in your code)
    # Refer: https://www.youtube.com/watch?v=jCzT9XFZ5bw
    # Refer BP411 slides: Week 2 - Chapter 10 - Slides about Encapsulation and properties 

    @property
    def levelsList(self):
        return self.__levelsList         # Return the value of __levelsList

    @levelsList.setter
    def levelsList(self, newValue):
        self.__levelsList = newValue     # Set the value of __levelsList
    
    @property
    def currentPrice(self): 
        return self.__currentPrice                          # Return the value of __currentPrice             

    @currentPrice.setter
    def currentPrice(self, newValue):    
        self.__currentPrice= newValue                       # Set the value of __currentPrice

    @property
    def previousPrice(self):
        return self.__previousPrice                         # Return the value of __previousPrice


    @previousPrice.setter
    def previousPrice(self, newValue):
        self.__previousPrice = newValue                      # Set the value of __previousPrice
    

    # Class Methods
    # =============

    # Method: Sort and Display the levelsList
    def displayList(self):
        print(chr(27) + "[2J") # Clear the screen
        print("Price Levels In The List")
        print("========================")
        # Sort the list in reverse order
        self.__levelsList.sort(reverse=True)
        for item in self.__levelsList:
            print(f"${item:,}")

        # Print the items in the list (Based on the above sort, numbers should appear from large to small.)

    # Display the menu and get user input about what methods to execute next
    def displayMenu(self):
        min = 0
        max = 5      # execute when the value of 5 is entered.
        errorMsg = "Please enter a valid option between " + str(min) + " and " + str(max)

        print("MENU OPTIONS")
        print("============")
        print("1. Add a price level")
        print("2. Remove a price level")
        print("3. Remove all price levels")
        if(self.currentPrice > 0):
            print("4. Display the current Bitcoin price here: " + f"${self.currentPrice:,}")
        else:
            print("4. Display the current Bitcoin price here")
        print("5. Start the monitoring")
        print("0. Exit the program")
        print(" ")   
        
        # Get user input. Keep on requesting input until the user enters a valid number between min and max 
        selection = 99
        while selection < min or selection > max:
            try:
                selection = int(input("Please enter one of the options: "))
            except:
                print(errorMsg) # user did not enter a number
                continue # skip the following if statement
            if(selection < min or selection > max):
                print(errorMsg) # user entered a number outside the required range
        return selection # When this return is finally reached, selection will have a value between (and including) min and max

    # Method: Append a new price level to the levelsList
    def addLevel(self):
        print("Please enter a valid value")
        try:
            # Let the user enter a new float value and append it to the list
            add_value = int(input("Enter the value you wish to add: "))
            print("The value you chose to add is: ",add_value)
            self.__levelsList.append(add_value)
        
        except:
            # Print and error message if the user entered invalid input
            print("Please enter a valid number as requested")

    # Method: Remove an existing price level from the levelsList
    def removeLevel(self):
        print("Please enter a valid value you want to remove:")
        try:
            # Let the user enter a new float value. If found in the list, remove it from the list
            take_out = int(input("Please enter the value you wish to remove from the list"))
            self.__levelsList.remove(take_out)
        except:
            # Print and error message if the user entered invalid input
            print("Please enter a valid value you want to remove")

    # Method: Set levelsList to an empty list
    def removeAllLevels(self):
        # Set levelsList to an empty list
        self.__levelsList.clear()

    # Method: Load levelsList using data in levelsFile
    def readLevelsFromFile(self):
        try:
            # Set levelsList to an empty list
            self.levelsList = []
            # Open the file
            f = open("levelsFile.txt",'r')

            # Use a loop to read through the file line by line
            for line in f:
                
                # If the last two characters in the line is "\n", remove them
                if line == "\n":
                    remove("\n")
                # remove the line if it is a new line
                
                # Append the line to levelsList
                self.levelsList.append(float(line))
  
            # Close the file
            f.close()
        except:
            print("Something went wrong")
            return self.levelsList



    # Method: Write the levelsList to the levelsFile(overriding the existing file)
    def writeLevelsToFile(self):
        # open the file in a way that will override the existing file (if it already exists)
        f= open("levelsFile.txt","w")

        # use a loop to iterate through the levelsList item by item
        
        for item in self.levelsList:

            # Convert everything in the item to a string and then add \n to it- before writing it to the file
            f.write("%s\n" % item)

        # Close the file
        f.close()

    # Function: Display the Bitcoin price in the menu item - to assist the user when setting price levels
    def updateMenuPrice(self):

        # Get the lastest Bitcoin info (as a Tick object) from getBitmexPrice(). Name it tickObj.
        tickObj = self.getBitMexPrice()

        # Update the currentPrice property with the Bitcoin price in tickObj
        self.currentPrice = tickObj.price


    # Function: Call the Bitmex Exchange
    def getBitMexPrice(self):

        # Send a request to the exchange for Bitcoins data in $USD ('XBTUSD')
        # The json response is converted into a tuple which we name responseTuple.

        responseTuple = self.BitmexClient.Instrument.Instrument_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()

        # The tuple consists of the Bitcoin information (in the form of a dictionary with key>value pairs plus some additional meta data received from the exchange)
        # Extract only the dictionary (Bitcoin information) from the tuple

        responseDictionary = responseTuple[0:1][0][0]

        # Create a Tick object and set its variables to the timestamp and lastPrice data from the dictionary

        return Tick(responseDictionary["timestamp"], responseDictionary["lastPrice"])



    # Once this method has been called, it uses a Timer to execute every 2 seconds
    def monitorLevels(self):
        # Create timer to call this method every 2 seconds

        threading.Timer(2.0, self.monitorLevels).start()

        # Since we will obtain the latest current price from the exchange, store the existing value of currentPrice in previousPrice

        self.previousPrice = self.currentPrice

        # Similar to updateMenuPrice(), call the getBitMexPrice() method to get a Ticker object containing the latest Bitcoin information.
        # Then store the Bitcoin price in currentPrice

        tickObj = self.getBitMexPrice()
        self.currentPrice = tickObj.price


        # During the first loop of this method, previousPrice will still be 0 here, 
        # because it was set to currentPrice above, which also was 0 before we updated 
        # it above via getBitMexPrice().        
        # So, when we reach this point during the first loop, previousPrice will be 0
        # while currentPrice would have just been updated via getBitMexPrice().
        # We don't want to create the impression that the price shot up from 0 to
        # currentPrice. 
        # Therefore, if previousPrice == 0.0, it must be set equal to currentPrice here.

        if self.previousPrice == 0.0:
            self.previousPrice = self.currentPrice

        # Print the current date and time plus instructions for stopping the app while this
        # method is looping. 
        print('')
        print('Price Check at ' + str(datetime.now()) + '   (Press Ctrl+C to stop the monitoring)')
        print('=================================================================================')


        # Each time this method executes, we want to print the items in levelsList together with previousPrice
        # and currentPrice in the right order. However, as we loop through levelsList, how do we know where to
        # insert previousPrice and currentPrice - especially if currentPrice crossed one or two of our price 
        # levels? 
        # We could try to use an elaborate set of IF-statements (I dare you to try this), but a much easier 
        # way is to simply add previousPrice and currentPrice to the list and then sort the list.
        #
        # However, we cannot simply use levelsList for this purpose, because it only stores values, while we
        # also want to print labeling text with these values - such as 'Price Level', 'Current Price' and
        # 'Previous Price'.
        # Therefore, we need to create a temporary list - called displayList - used for displaying purposes only. 
        # This new list must consist of sub-lists. Each sub-List will contain two items. 
        # The first item will be the label we want to print - consisting of the labeling text and the price. 
        # The second item consists of the price only. 
        # We will use the second item to sort the list - since it makes no sense to sort the list based on 
        # the label (the first item). 
        #
        # Example of displayList (containing sub-lists) after it was sorted:
        #
        #       [
        #           ['Price Level:    9700.00',    9700.00],
        #           ['Price Level:    9690.00',    9690.00],
        #           ['Current Price:  9689.08',    9689.08], 
        #           ['Previous Price: 9688.69',    9688.69], 
        #           ['Price Level:    9680.00',    9680.00],
        #       ]


        # Create displayList
        displayList = []

        # Loop through the prices in levelsList.
        # During each loop:
        # - Create a variable called priceLevelLabel consisting of the text 'Price Level:    ' followed 
        #   by the price.        
        # - Add priceLevelLabel and the price as two separate items to a new list (the sub-List).        
        # - Append the sub-List to displayList.

        # created the variable and done the formatting of the values.
        # appended values to the sublist created
        for price in self.levelsList:
            subList = ['Price Level:' "     " +str("%.2f" % price), price]
            displayList.append(subList)


        # Create a variable called previousPriceLabel consisting of the text 'Previous Price: ' followed 
        # by previousPrice. 
        # # Format the background color of previousPriceLabel to be blue. Refer to the following site:
        # http://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
        # Follow the above site to add special text characters to the label, which the console will interpret
        # as background color settings. If the above site's code does not work for your console, research a different way for setting the background.
        # Add previousPriceLabel and previousPrice as two separate items to a new list (the sub-List).        
        # Append the sub-List to displayList.
         
        # Setting the previousPriceLabel to BLUE.
        previousPriceLabel = "Previous Price:"+ str('%.2f' % self.previousPrice)
        subList = ['\x1b[1;34;44m' + previousPriceLabel + '\x1b[0m', self.previousPrice]
        displayList.append(subList)

        # Create a variable called currentPriceLabel consisting of the text 'Current Price:  ' followed
        # by currentPrice.
        # Format the background colour of currentPriceLabel as follows:
        # - If currentPrice > previousPrice: set currentPriceLabel background colour to green.
        # - If currentPrice < previousPrice: set currentPriceLabel background colour to red.
        # - If currentPrice == previousPrice: set currentPriceLabel background colour to blue.
        # Add currentPriceLabel and currentPrice as two separate items to a new list (the sub-List).        
        # Append the sub-List to displayList.

        currentPriceLabel = 'Current Price:'+ str('%.2f' % self.currentPrice)
        
        #GREEN
        if (self.currentPrice > self.previousPrice):
            currentPriceLabel = '\x1b[1;30;42m' + 'Current Price:'+ str('%.2f' % self.currentPrice) + '\x1b[0m'
        
        #RED
        elif (self.currentPrice < self.previousPrice):
            currentPriceLabel = '\x1b[1;30;41m' + 'Current Price:'+ str('%.2f' % self.currentPrice) + '\x1b[0m'
        
        #BLUE
        else: 
            currentPriceLabel = '\x1b[1;30;44m' + 'Current Price:'+ str('%.2f' % self.currentPrice) + '\x1b[0m'
        
        subList = [currentPriceLabel, self.currentPrice]
        displayList.append(subList)


        # Sort displayList using the SECOND item (price) in its sub-lists
        displayList = sorted(displayList, key = lambda x: x[1], reverse=True)

        # For each sub-List in displayList, print only the label (first item) in the sub-List
        for a in range(0, len ( displayList)):
            print(displayList[a][0])


        # Loop through displayList
        for i in range(0,len(displayList)):

            # Test if the first item in the current sub-list contains the text "Price Level"
            # Tip: Remember that each sub-list is a list within a list (displayList). So you have
            #       to access its items via displayList followed by TWO indexes.  

            if("Price Level" in displayList[i][0]):

                # Extract the second item from the current sub-list into a variable called priceLevel

                priceLevel = displayList[i][1]
                # Test if priceLevel is between previousPrice and currentPrice OR
                #         priceLevel == previousPrice OR
                #         priceLevel == currentPrice

                if(
                    (self.previousPrice > priceLevel and self.currentPrice < priceLevel) or
                    (self.previousPrice < priceLevel and self.currentPrice > priceLevel) or
                    (self.previousPrice == priceLevel) or
                    (self.currentPrice == priceLevel)
                ):
                    # Sound the alarm. Pass in the frequency and duration.
                    if self.currentPrice > self.previousPrice:
                        frequency = 800
                        duration = 700                    
                    else:
                        frequency = 400
                        duration = 700
                    winsound.Beep(frequency, duration)

                    # Print the text 'Alarm' with a green background colour, so that the user
                    # can go back into the historical data to see what prices raised the alarm.
                    
                    print('\x1b[1;30;42m'+ 'Alarm' +'\x1b[0m')



# *************************************************************************************************
#                                           Main Code Section
# *************************************************************************************************

# Create an object based on the PriceChecker class
checkerObj = PriceChecker()

# Load levelslist from the records in levelsFile
checkerObj.readLevelsFromFile()


# Display the levelsList and Menu; and then get user input for what actions to take
userInput = 99
while userInput != 0:
    checkerObj.displayList()
    userInput = checkerObj.displayMenu()
    if(userInput == 1):
        checkerObj.addLevel()
        checkerObj.writeLevelsToFile()
        # write levelsList to LevelsFile
    elif(userInput == 2):
        checkerObj.removeLevel()
        checkerObj.writeLevelsToFile()
        # write levelsList to LevelsFile
    elif(userInput == 3):
        checkerObj.removeAllLevels()
        checkerObj.writeLevelsToFile()
        # write levelsList to LevelsFile
    elif(userInput ==4):
        checkerObj.updateMenuPrice()
    elif(userInput ==5):
        userInput = 0 # Prevent the app from continuing if the user pressed Ctrl+C to stop it
        checkerObj.monitorLevels()
    

