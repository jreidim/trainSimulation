from collections import defaultdict
import numpy
import queue
class Crew:
    max_crew_hours = 12
    crew_remain_hr_interval = (6,11)

    #replacement time counts as part of replacement crews work hours
    hog_crew_remain_hr_interval = (8.5, 9.5)

    def __init__(self):
        self.rem_hrs = self._gen_rem_hrs()

    def _gen_replacement_crew_hours(self):
        return round(numpy.random.uniform(*self.hog_crew_remain_hr_interval),2)

    def _gen_rem_hrs(self):
        return round(numpy.random.uniform(*self.crew_remain_hr_interval),2)

class Train:
    unloading_interval = (2.5, 3.5)
    def __init__(self, arrival_time):
        self.arrival = arrival_time
        self.unload_t = self._gen_unload_time()
        self.crew = Crew() 

    def _gen_unload_time(self):
        return round(numpy.random.uniform(*self.unloading_interval),2)

class TrainSimulation:
    def __init__(self, simulation_hours: float, arrival_average: float):
        #simulation hours + time it takes for all remaining trains to depart
        self.simulation_hours = simulation_hours
        self.arrival_average = arrival_average

        self.line = queue.Queue()

        self.trains = self._gen_trains()
        self.dock = None

    def run(self):
        time = 0
        while time < self.simulation_hours * 100:
            h = time/100
            if not self.dock:
                self.dock = self.trains.get(block=False)
            time+=1

    def _print_arrival(self, ):


    def _gen_trains(self):
        total_time = 0
        t = self._gen_next_arrival()
        final = queue.SimpleQueue()
        count = 0
        while total_time + t < self.simulation_hours:
            total_time = round(total_time + t, 2) 
            train = Train(total_time)
            final.put(train)
            t = self._gen_next_arrival()
        return final

    def _gen_next_arrival(self):
        return numpy.random.exponential(self.arrival_average)

    

