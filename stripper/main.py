from datetime import datetime
from  stripper.helper import getTransformedMasks

def run():
    a= getTransformedMasks(32, 1, 1, 4, 0)
    print("START:",datetime.now())
    print("END:", datetime.now())

if __name__ == "__main__":
    run()