class Node:
    def __init__(self, data, next):
        self.data = data
        self.next = next

class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.sz = 0
    
    def put(self, data):
        if self.head == None:
            self.head = Node(data, None)
            self.tail = self.head
        else:
            self.tail.next = Node(data, None)
            self.tail = self.tail.next
        self.sz += 1
    
    def get(self):
        if self.head == None:
            return None
        buf = self.head
        self.head = self.head.next
        self.sz -= 1
        return buf.data

    def peak(self):
        if self.head == None:
            return None
        return self.head.data

    def empty(self):
        return self.sz == 0
    

