# HELPER CLASS FOR LINKED LIST
# INSTEAD OF SAVING IMAGES, JUST STORE THE IMAGE PATH AND USE THEM LATER TO DISPLAY THE IMAGES.
class Node:
    def __init__(self, path):
        self.path = path
        self.prev = None
        self.next = None

class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0
        
    def append(self, path):
        newNode = Node(path)
        if self.length == 0:
            self.head = newNode
            self.tail = newNode
        else:
            newNode.prev = self.tail
            self.tail.next = newNode
            self.tail = newNode

        self.tail.next = self.head
        self.head.prev = self.tail
        
        self.length += 1
    
    def __str__(self):
        if self.length == 0:
            return 'This linked list is empty.'
        
        paths = []
        current = self.head
        counter = self.length
        while counter > 0:
            paths.append(current.path)
            current = current.next
            counter -= 1
        return " -> ".join(paths)
