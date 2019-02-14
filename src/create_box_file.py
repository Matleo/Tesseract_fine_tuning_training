from PIL import Image
import glob
import cv2
import os
import shutil
import sys

def create_ground_truth(tx_folder):
    files = glob.glob(tx_folder+"*.tif")
    for imageFile in files:
        Image.open(imageFile).show()
        text = input("Text of ("+imageFile+"): ")
        textFile = imageFile.replace(".tif",".gt.txt")
        if os.path.exists(textFile):
            os.remove(textFile)
        with open(textFile,"w") as f:
            f.write(text)

def create_box_files(tx_folder):
    imageFiles = glob.glob(tx_folder + "*.tif")
    for imageFile in imageFiles:
        print(imageFile)
        with open(imageFile, "rb") as f:
            width, height = Image.open(f).size

        # load ground truth
        textFile = imageFile.replace(".tif", ".gt.txt")
        with open(textFile, "r", encoding='iso-8859-1') as f:
            line = f.read()

        # write box file
        boxFile = imageFile.replace(".tif", ".box")
        if os.path.exists(boxFile):
            os.remove(boxFile)
        with open(boxFile, "w", encoding='utf-8') as f:
            for char in line:
                f.write(u"%s %d %d %d %d 0" % (char, 0, 0, width, height))
                f.write("\n")
            f.write(u"%s %d %d %d %d 0" % ("\t", width, width, width + 1, height + 1))

def preprocess_images(tx_folder):
    tx_folder = tx_folder.replace("\\", "/")

    GRAY_FOLDER = tx_folder+"gray/"
    BIN_FOLDER = tx_folder+"bin/"
    BLUR_FOLDER = tx_folder+"blur/"
    if os.path.exists(GRAY_FOLDER):
        shutil.rmtree(GRAY_FOLDER)
    os.makedirs(GRAY_FOLDER)
    if os.path.exists(BIN_FOLDER):
        shutil.rmtree(BIN_FOLDER)
    os.makedirs(BIN_FOLDER)
    if os.path.exists(BLUR_FOLDER):
        shutil.rmtree(BLUR_FOLDER)
    os.makedirs(BLUR_FOLDER)

    imageFiles = glob.glob(tx_folder + "*.tif")
    for imageFile in imageFiles:
        imageFile = imageFile.replace("\\","/")
        filename = imageFile.replace(tx_folder,"")
        print(imageFile)
        img = cv2.imread(imageFile)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_file = GRAY_FOLDER + filename
        pil_im = Image.fromarray(gray)
        pil_im.save(gray_file,dpi=(200,200))
        #cv2.imwrite(gray_file, gray)

        bin = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        bin_file = BIN_FOLDER + filename
        pil_im = Image.fromarray(bin)
        pil_im.save(bin_file,dpi=(200,200))
        #cv2.imwrite(bin_file, bin)

        blur = cv2.medianBlur(gray, 3)
        blur_file = BLUR_FOLDER + filename
        pil_im = Image.fromarray(blur)
        pil_im.save(blur_file,dpi=(200,200))
        #cv2.imwrite(blur_file, blur)


def main(tx_folders, option):
    for tx_folder in tx_folders:
        if option == 1:
            create_ground_truth(tx_folder)
        elif option == 2:
            create_box_files(tx_folder)
        elif option == 3:
            preprocess_images(tx_folder)
if __name__ == "__main__":
    baseDir = "../assets/mullerData_training/v1"
    option = 1
    if len(sys.argv) == 3:
        baseDir = sys.argv[1]
        option = sys.argv[2]
    tx_folders = glob.glob(baseDir + "/*/")
    main(tx_folders, int(option))
