import numpy

#: experimental setup constants
NUMBER_OF_PARTICIPANTS = 50
NUMBER_OF_UNIQUE_RUNS = 8
NUMBER_OF_SHARED_RUNS = 1
UNIQUE_IMAGES_PER_UNIQUE_RUN = 56
SHARED_IMAGES_PER_UNIQUE_RUN = 8
SHARED_IMAGES_PER_SHARED_RUN = 64

DIM_REDUCE_TO = 10
NUMBER_OF_BIN = 10

class Subject():
    def __init__(self):
        self.histgram_normalized = numpy.zeros(shape=(DIM_REDUCE_TO, NUMBER_OF_BIN), dtype=float)
        self.histgram = numpy.zeros(shape=(DIM_REDUCE_TO, NUMBER_OF_BIN))
        self.assigned = []
        self.this_class_assigned = 0

    def difference(self, template, hist_all_normalized):
        return sum(sum(template * (hist_all_normalized - self.histgram_normalized)))

    def assign(self, file, template):
        self.assigned.append(file)
        self.histgram += template
        self.histgram_normalized = self.histgram/sum(sum(self.histgram))
        self.this_class_assigned += 1