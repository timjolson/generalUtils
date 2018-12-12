import time  # import time module


# Create class
class StopWatch():
    # This is an element within the class, you don't need to specify it here.
    # Assigning it within a method will create it, too.
    begin = 0


    # Constructor with default value of 'dec' = 2.
    # If there is no value entered, the default value is assumed.
    # Any method definition has 'self' as the first argument (refers to the instance calling the method)
    def __init__(self, dec=2):

        # Set the instance's 'dec' variable to the 'dec' argument passed in
        self.dec = dec

        # Run start() on the instance just created
        self.start()

    # Define method to start timer
    def start(self):

        # Stores current system time in instance's 'begin' variable
        self.begin = time.time()
        return self.begin

    # Define method to get elapsed time
    def lap(self):

        # Gets elapsed time and rounds to specified 'dec' decimal places, returns it
        return round(time.time() - self.begin, self.dec)

    # Define method to restart the instance
    def restart(self):

        # Store the elapsed time, notice we're using another method.
        # That prevents re-writing of the rounding, meaning it can be changed in one place and affect all cases of it.
        r = self.lap()

        # Restart the stopwatch
        self.start()

        # Return the elapsed time before restart
        return r

__all__ = ['StopWatch']

# If you'd like to run a module or script directly, you can put an example of it's use at the bottom
# The following condition is True when a script is executed directly (not imported or used externally)
if __name__ == "__main__":
    #TODO: move to example file
    SW = StopWatch()
    sw0 = StopWatch(0)
    sw3 = StopWatch(3)

    start = time.time()
    while time.time() - start < 6:
        print('sw0: ' + str(sw0.lap()))
        time.sleep(0.8)
        print('sw3 lap: ' + str(sw3.lap()))
        time.sleep(0.8)
        print('sw3 restart: ' + str(sw3.restart()))
        time.sleep(0.8)
        print('sw3 lap: ' + str(sw3.lap()))
        time.sleep(0.8)
        print('SW: ' + str(SW.lap()))

    print('-------')
    print('sw0: ' + str(sw0.lap()))
    print('sw3: ' + str(sw3.lap()))
    print('SW: ' + str(SW.lap()))