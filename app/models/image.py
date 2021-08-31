import sys
import cv2
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt


class Convert:

    @staticmethod
    def remove_background(source, destination):
        img = Image.open(source)
        img = img.convert("RGBA")
        datas = img.getdata()
        new_data = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        img.putdata(new_data)
        img.save(destination, "PNG")
        print("Successful")

    @staticmethod
    def remove3(source, destination):
        image = Image.open(source)
        image = image.convert('RGBA')
        new_image = []
        for item in image.getdata():
            if item[:3] == (255, 255, 255):
                new_image.append((255, 255, 255, 0))
            else:
                new_image.append(item)

        image.save(destination)
        print(image.mode, image.size)

    @staticmethod
    def remove4(source, destination):
        img = cv2.imread(source)

        mask = np.zeros(img.shape[:2], np.uint8)

        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        rect = (10, 10, 45, 45)
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img = img * mask2[:, :, np.newaxis]
        cv2.imshow('Imagem', img)
        cv2.waitKey(0)
        cv2.imwrite(destination, img)
        plt.imshow(img), plt.colorbar(), plt.show()

        pass
