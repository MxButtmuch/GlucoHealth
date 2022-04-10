import cv2
import numpy as np
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from colormath.color_objects import LabColor, sRGBColor
from sklearn.cluster import KMeans
from statistics import mode


class ColorFinder:
    def __init__(self, visualize=False):
        self.visualize = visualize
        self.colors = [["0 mg/ml", [49.037, 43.146, 50.657]], ["0 mg/ml", [42.832, 36.156, 44.324]],
                       ["0 mg/ml", [54.301, 45.050, 50.423]],
                       ["2.2 mg/ml", [61.799, 47.709, 69.759]], ["2.2 mg/ml", [73.31, 48.827, 69.335]],
                       ["2.2 mg/ml", [77.089, 60.114, 79.733]],
                       ["2.35 mg/ml", [66.707, 48.81, 66.253]], ["2.35 mg/ml", [78.999, 61.811, 80.432]],
                       ["2.35 mg/ml", [62.625, 44.679, 66.070]],
                       ["2.5 mg/ml", [66.907, 54.399, 64.937]], ["2.5 mg/ml", [91.305, 72.603, 84.315]],
                       ["2.5 mg/ml", [75.136, 60.098, 74.828]],
                       ["2.65 mg/ml", [83.398, 57.803, 66.542]], ["2.65 mg/ml", [82.317, 60.814, 68.704]],
                       ["2.65 mg/ml", [71.47, 50.764, 58.209]],
                       ["2.8 mg/ml", [89.226, 61.02, 75.412]], ["2.8 mg/ml", [63.833, 43.558, 63.545]],
                       ["2.8 mg/ml", [78.229, 56.659, 75.424]],
                       ["3.1 mg/ml", [102.357, 78.851, 86.94]], ["3.1 mg/ml", [109.81, 81.353, 85.919]],
                       ["3.1 mg/ml", [97.2, 70.294, 77.964]]]
        self.distances = []
        self.colorBin = ''

    def findBin(self, filename):
        color = self.find_Color(filename)
        self.distances = []
        for color_bin in self.colors:
            cb = self.convert_to_Lab(color_bin[1])
            dist = self.find_distance(color, cb)
            self.distances.append([color_bin[0], dist])
        self.findKNearest(self.distances)

    def findKNearest(self, distances, k=3):
        try:
            kNearest = []
            for dist in distances:
                kNearest.append(dist)
                #print(f"kNearest = {kNearest}")
                #print(f"dist = {dist}")
                if len(kNearest) > k:
                    neighbors = sorted(kNearest, key= lambda x: x[1])
                    kNearest = neighbors[:-1]
            self.colorBin = mode(kNearest[:][0])    
        except Exception as e:
            print(e)

    @staticmethod
    def find_distance(color, color_bin):
        return delta_e_cie1976(color, color_bin)

    def find_Color(self, filename):
        """This function finds the most dominant color of an image
        returns the color in a Lab value"""
        # Load image and convert to a list of pixels
        reshape = self.convert_image(filename)
        # Find and display most dominant colors
        dominant = self.find_dominant_color(reshape)
        # Converts dominant color to Lab Values
        lab_value = self.convert_to_Lab(dominant)
        return lab_value

    @staticmethod
    def convert_to_Lab(domi):
        """Converts final color to a lab values"""
        rgb = sRGBColor((domi[0]) / 255, (domi[1]) / 255, (domi[2]) / 255)
        lab = convert_color(rgb, LabColor, through_rgb_type=sRGBColor, target_illuminant='d65')
        return lab

    def find_dominant_color(self, reshape):
        """This function finds and displays most dominant colors.
        Visual will only run if self.visualization == True"""
        cluster = KMeans(n_clusters=5).fit(reshape)
        visualize, domi = self.visualize_colors(cluster, cluster.cluster_centers_)
        if self.visualize:
            visualize = cv2.cvtColor(visualize, cv2.COLOR_RGB2BGR)
            cv2.imshow('visualize', visualize)
            cv2.waitKey()
        return domi

    def visualize_colors(self, cluster, centroids):
        # Get the number of different clusters, create histogram, and normalize
        labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
        (hist, _) = np.histogram(cluster.labels_, bins=labels)
        hist = hist.astype("float")
        hist /= hist.sum()

        # Create frequency rect and iterate through each cluster's color and percentage
        rect = np.zeros((50, 300, 3), dtype=np.uint8)
        colors = sorted([(percent, color) for (percent, color) in zip(hist, centroids)])
        start = 0
        for (percent, color) in colors:
            if self.visualize:
                print(color, "{:0.2f}%".format(percent * 100))
            end = start + (percent * 300)
            cv2.rectangle(rect, (int(start), 0), (int(end), 50),
                          color.astype("uint8").tolist(), -1)
            start = end
        return rect, color

    @staticmethod
    def convert_image(filename):
        """This function loads an image and converts it to a list of pixels
        """
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        reshape = image.reshape((image.shape[0] * image.shape[1], 3))

        return reshape

#
# print('### 2.35 Test ###')
# cf = ColorFinder(visualize=False)
# cf.findBin('Amyl_2.35(2).jpg')
#
# print('### 2.5 Test 1 ###')
# cf2 = ColorFinder(visualize=False)
# cf2.findBin('Amyl_2.5(1).jpg')
#
# print('### 2.5 Test 2 ###')
# cf4 = ColorFinder(visualize=False)
# cf4.findBin('Amyl_2.5(2).jpg')
#
# dist = cf4.find_distance(cf4.find_Color('Amyl_2.5(2).jpg'), cf4.convert_to_Lab(cf4.colors[0]))
# print(f'2.5 bin distance is {dist}')
#
# print('### 2.5 Test 3 ###')
# cf5 = ColorFinder(visualize=False)
# cf5.findBin('Amyl_2.5(3).jpg')
#
# dist = cf5.find_distance(cf5.find_Color('Amyl_2.5(3).jpg'), cf5.convert_to_Lab(cf5.colors[0]))
# print(f'2.5 bin distance is {dist}')
#
# print('### 0 Test ###')
# cf3 = ColorFinder(visualize=False)
# cf3.findBin('Amyl_0(1).jpg')
