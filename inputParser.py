def trainParser(filename):
    arrivals = []
    unloading = []
    remaining = []
    with open(filename, "r") as file:
        for line in file:
            L = line.split()
            arrivals.append(float(L[0]))
            unloading.append(float(L[1]))
            remaining.append(float(L[2]))
    return (arrivals, unloading, remaining)


def crewParser(filename):
    final = []
    with open(filename, "r") as file:
        for line in file:
            L = line.split()
            final.append(float(L[0]))
    return final