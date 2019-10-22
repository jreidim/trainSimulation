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
        self.clocks_out = round(call_time + Crew.max_crew_hours - rep_t,2)

    def _gen_replacement_crew_hours(self):
        return round(TrainSimulation.new_crew_travel_time.get(),2)

    def _gen_rem_hrs(self):
        return round(TrainSimulation.remaining_crew_hr.get(),2)

class Train:
    unloading_interval = (3.5, 4.5)
    count = 0
    def __init__(self, arrival_time):
        self.arrival = arrival_time
        self.unload_t = self._gen_unload_time()
        self.crew = Crew(arrival_time)
        self.count = Train.count
        self.entered_dock_t = 0
        self.departure = 0
        self.hogout_count = 0
        Train.count += 1 

    def _gen_unload_time(self):
        return round(TrainSimulation.unloading_times.get(),2)

class TrainSimulation:
    #constructor:
    unloading_times = myQueue.Queue()
    remaining_crew_hr = myQueue.Queue()
    new_crew_travel_time = myQueue.Queue()
    def __init__(self, arrivals, unloading, remaining, crew_travel):

        self.line = myQueue.Queue()
        self.train_times = myQueue.Queue()
        for t in arrivals:
            self.train_times.put(round(t,2))

        for t in unloading:
            self.unloading_times.put(round(t,2))
        
        for t in remaining:
            self.remaining_crew_hr.put(round(t,2))
        
        for t in crew_travel:
            self.new_crew_travel_time.put(round(t,2))

        self.dock = None

        #data-structure used for stats
        self.processed = set()

    #public:
    def run(self):
        time = 0

        idle_c = 0
        hog_c = 0


        #Run simulation until the time is up, the line reaches 0, and the dock is empty
        while not self.train_times.empty() or self.line.sz > 0 or self.dock != None:
            h = time/100 #hours
            #print(self.train_times.sz)
            #if the time matches the next train's arrival time, add to line
            if self.train_times.peak() == h:
                next_train = Train(self.train_times.get())
                self.line.put(next_train)
                self._print_arrival(next_train)

            #if the dock is empty and the line isnt empty and the next in line is
            #not hogged, then move the next train in line to the dock for unloading
            if self.dock == None:
                idle_c += 1
                if not self.line.empty() and not self.line.peak().crew.hogged:
                    self.dock = self.line.get()
                    if self.dock:
                        self.dock.entered_dock_t = h
                        self._print_docking(h)
                        self.dock.unload_t = round(self.dock.unload_t - 0.01, 2)

            #otherwise, the dock is occupied
            else:
                #if the train in the dock is hogged and the crew arrives, unhog 
                if self.dock.crew.hogged:
                    hog_c += 1
                    if self.dock.crew.rep_arrival == h:
                        self.dock.crew.hogged = False
                        self._print_dock_unhogged(h)
                
                #if the train in the dock is not hogged, continue unloading
                if not self.dock.crew.hogged:
                    self.dock.unload_t = round(self.dock.unload_t - 0.01, 2)
                    
                    #if the train is finished unloading, remove train from dock 
                    if self.dock.unload_t <= 0.0:
                        self._print_departure(self.dock, h)
                        self.dock.departure = h
                        self.processed.add(self.dock)
                        #if there is no one in line or the next in line is hogged,
                        #the dock will be empty
                        if self.line.empty() or self.line.peak().crew.hogged:
                            self.dock = None
                        #otherwise, the next in line gets docked for unloading
                        else:
                            self.dock = self.line.get()
                            if self.dock:
                                self.dock.entered_dock_t = h
                                self._print_docking(h)
                    #if the crew on the dock reaches their max hours, hog the train
                    #and request a replacement crew
                    elif self.dock.crew.clocks_out == h:
                        self.dock.crew.hogged = True
                        self.dock.hogout_count += 1
                        self._print_dock_hogged(h)
                        self.dock.crew.replace_crew(h)

            #for every train in line, manage the hours of the crews, if a crew
            #has reached its max hours, hog in line and request a replacement crew.
            p = self.line.head
            while p != None:
                crew = p.data.crew
                if crew.hogged and crew.rep_arrival == h:
                    crew.hogged = False
                    self._print_line_unhogged(h, p.data)
                
                elif not crew.hogged:
                    if crew.clocks_out == h:
                        crew.hogged = True
                        p.data.hogout_count += 1
                        self._print_line_hogged(h, p.data)
                        crew.replace_crew(h)

                p = p.next    

            time+=1

        #print simulation stats
        self._print_simulation_end(time, idle_c, hog_c)
        self._print_histogram()


    #private:
    def _print_histogram(self):
        print("Histogram of hogout count per train:")
        dd = defaultdict(int)
        for train in self.processed:
            dd[train.hogout_count] += 1
        
        for k in sorted(dd.keys()):
            print("[{}]: {}".format(k, dd[k]))

    def _print_simulation_end(self, time, idle_c, hog_c):
        if Train.count == 0:
            average_time, max_time, queue_ave = 0
        else:
            average_time = sum([t.departure-t.arrival for t in self.processed])/Train.count
            max_time = max([t.departure-t.arrival for t in self.processed])
            queue_ave = sum([t.entered_dock_t-t.arrival for t in self.processed])/Train.count
        end  = "Time {:.2f}: simulation ended\n\n".format(time/100)
        end += "Statistics\n"
        end += "----------\n"
        end += "Total number of trains served: {}\n".format(Train.count)
        end += "Average time-in-system per train: {:.6f}h\n".format(average_time)
        end += "Maximum time-in-system per train: {:.6f}h\n".format(max_time)
        end += "Dock idle percentage: {:.2f}%\n".format(idle_c/time * 100)
        end += "Dock busy percentage: {:.2f}%\n".format((time-idle_c)/time * 100)
        end += "Dock hogged-out percentage: {:.2f}%\n".format(hog_c/time * 100)
        end += "Time average of trains in queue: {:.4f}h\n".format(queue_ave)
        end += "Maximum number of trains in queue: {}".format(self.line.max)
        print(end)  

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