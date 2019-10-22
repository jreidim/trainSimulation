import trainSimulation as ts
import pdSim as pts
import sys
import inputParser
def main():
    if len(sys.argv) == 3:
        simulation = ts.TrainSimulation(float(sys.argv[1]), float(sys.argv[2]))
        simulation.run()
    
    elif len(sys.argv) == 4 and sys.argv[1] == "-s":
        a = inputParser.trainParser(sys.argv[2])
        b = inputParser.crewParser(sys.argv[3])
        simulation = pts.TrainSimulation(a[0],a[1],a[2], b)
        simulation.run()

    else:
        print("error: invalid input")

if __name__ == "__main__":
    main()