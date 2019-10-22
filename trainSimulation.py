from collections import defaultdict
import numpy
import myQueue
class Crew:
    max_crew_hours = 12
    crew_remain_hr_interval = (6,11)

    #replacement time counts as part of replacement crews work hours
    hog_crew_remain_hr_interval = (2.5, 3.5)

    count = 0

    def __init__(self, arrival):
        self.rem_hrs = self._gen_rem_hrs()
        self.clocks_out = round(arrival + self.rem_hrs, 2)
        self.count = Crew.count
        self.hogged = False
        self.rep_arrival = None
        Crew.count += 1
    
    def replace_crew(self, call_time):
        self.count = Crew.count
        Crew.count += 1

        rep_t = self._gen_replacement_crew_hours()
        self.rep_arrival = round(rep_t + call_time,2)
        self.clocks_out = call_time + Crew.max_crew_hours - rep_t

    def _gen_replacement_crew_hours(self):
        return round(numpy.random.uniform(*self.hog_crew_remain_hr_interval),2)

    def _gen_rem_hrs(self):
        return round(numpy.random.uniform(*self.crew_remain_hr_interval),2)

class Train:
    unloading_interval = (3.5, 4.5)
    count = 0
    def __init__(self, arrival_time):
        self.arrival = arrival_time
        self.unload_t = self._gen_unload_time()
        self.crew = Crew(arrival_time)
        self.count = Train.count
        Train.count += 1 

    def _gen_unload_time(self):
        return round(numpy.random.uniform(*self.unloading_interval),2)

class TrainSimulation:
    def __init__(self, simulation_hours: float, arrival_average: float):
        #simulation hours + time it takes for all remaining trains to depart
        self.simulation_hours = simulation_hours
        self.arrival_average = arrival_average

        self.line = myQueue.Queue()

        self.train_times = self._gen_train_times()
        self.dock = None

    def run(self):
        time = 0
    
        print("runnning")
        while time < self.simulation_hours * 100 or (self.line.sz > 0 and self.dock != None):
            h = time/100
            
            if self.train_times.peak() == h:

                next_train = Train(self.train_times.get())
                self.line.put(next_train)
                self._print_arrival(next_train)

            if self.dock == None:
                if not self.line.empty() and not self.line.peak().crew.hogged:
                    self.dock = self.line.get()
                    if self.dock:
                        self._print_docking(h)
                        self.dock.unload_t = round(self.dock.unload_t - 0.01, 2)

            else:
                if self.dock.crew.hogged and self.dock.crew.rep_arrival == h:
                    self.dock.crew.hogged = False
                    
                    self._print_dock_unhogged(h)
                if not self.dock.crew.hogged:
                    self.dock.unload_t = round(self.dock.unload_t - 0.01, 2)
                    if self.dock.unload_t <= 0.0:
                        self._print_departure(self.dock, h)
                        if self.line.empty() or self.line.peak().crew.hogged:
                            self.dock = None
                        else:
                            self.dock = self.line.get()
                            if self.dock:
                                self._print_docking(h)
                        
                    elif self.dock.crew.clocks_out == h:
                        self.dock.crew.hogged = True
                        self._print_dock_hogged(h)
                        self.dock.crew.replace_crew(h)

            p = self.line.head
            while p != None:
                crew = p.data.crew
                if crew.hogged and crew.rep_arrival == h:
                    crew.hogged = False
                    self._print_line_unhogged(h, p.data)
                
                elif not crew.hogged:
                    if crew.clocks_out == h:
                        crew.hogged = True
                        self._print_line_hogged(h, p.data)
                        crew.replace_crew(h)

                p = p.next    

            time+=1

    def _print_line_hogged(self, time, train):
        print("Time {:.2f}: train {} crew {} hogged out in queue".format(
            time, train.count, train.crew.count
        ))

    def _print_line_unhogged(self, time, train):
        print("Time {:.2f}: train {} replacement crew {} arrives (SERVER UNHOGGED)".format(
            time, train.count, train.crew.count
        ))

    def _print_dock_hogged(self, time):
        print("Time {:.2f}: train {} crew {} hogged out during service (SERVER HOGGED)".format(
            time, self.dock.count, self.dock.crew.count
        ))

    def _print_dock_unhogged(self, time):
        print("Time {:.2f}. train {} replacement crew {} arrives (SERVER UNHOGGED)".format(
            time, self.dock.count, self.dock.crew.count
        ))

    def _print_arrival(self, train):
        s = "Time {:.2f}: train {} arrival for {}h of unloading\n\t\t"+\
            "crew {} with {}h before hogout (Q={})"
        print(s.format(train.arrival, train.count, train.unload_t,
         train.crew.count, train.crew.rem_hrs, self.line.sz))
    
    def _print_departure(self, train, time):
        print("Time {:.2f}: train {} departing (Q={})".format(
            time,
            train.count,
            self.line.sz
        ))

    def _print_docking(self, time):
        s = "Time {:.2f}: train {} entering dock for {}h of unloading\n\t\t" +\
            "crew {} with {}h before hogout (Q={})"
        print(s.format(
            time,
            self.dock.count,
            self.dock.unload_t,
            self.dock.crew.count,
            round(self.dock.crew.clocks_out - time,2),
            self.line.sz
        ))
        

    def _gen_train_times(self):
        total_time = 0
        t = self._gen_next_arrival()
        final = myQueue.Queue()
        count = 0
        while total_time + t < self.simulation_hours:
            total_time = round(total_time + t, 2) 
            final.put(total_time)
            t = self._gen_next_arrival()
        return final

    def _gen_next_arrival(self):
        return numpy.random.exponential(self.arrival_average)
    

if __name__ == '__main__':
    simulation = TrainSimulation(720.0, 10.0)
    simulation.run()