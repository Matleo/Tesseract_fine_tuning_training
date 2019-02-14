import xml.etree.ElementTree as ET
import sys
import glob
import json
import io
from pprint import pprint
from PIL import Image, ImageDraw
from random import randint


def showImage(imgPath, jsonPath, select):
    print(jsonPath)
    with open(jsonPath, "r", encoding="utf8") as read_file:
        data = json.load(read_file)
    im = Image.open(imgPath)
    draw = ImageDraw.Draw(im)
    if(select=="rows"):
        for line in data["lines"]:
            pprint(line)
            bounding = line["bbox"].split(" ")

            x0 = bounding[0]
            y0 = bounding[1]
            x1 = bounding[2]
            y1 = bounding[3]
            coordinates = [int(x0), int(y0), int(x1), int(y1)]

            rndColor = (randint(0, 255), randint(0, 255), randint(0, 255))
            draw.rectangle(coordinates, outline=rndColor)
            print()
    elif(select=="words"):
        for line in data["lines"]:
            for word in line["words"]:
                pprint(word)
                bounding = word["BoundingBox"].split(" ")

                x0 = bounding[0]
                y0 = bounding[1]
                x1 = bounding[2]
                y1 = bounding[3]
                coordinates = [int(x0), int(y0), int(x1), int(y1)]

                rndColor = (randint(0, 255), randint(0, 255), randint(0, 255))
                draw.rectangle(coordinates, outline=rndColor)
                print()

    im.show()


def convert2json(filename):
    json_lines = []
    tree = ET.parse(filename)
    html = tree.getroot()
    for span in html.iter("{http://www.w3.org/1999/xhtml}span"):
        sClass = span.get("class")
        if sClass == "ocr_line":
            json_line = {}
            line_bbox = span.get("title").split(";")[0][5:]
            #json_line["bbox"] = line_bbox
            json_words = []
            for word in span:
                json_word = {}
                bbox = word.get("title").split(";")[0][5:]
                json_word["BoundingBox"] = bbox
                json_word["Text"] = word.text
                json_word["Confidence"] = int(word.get("title").split(";")[1][9:]) / 100
                json_words.append(json_word)
            json_line["Words"] = json_words
            json_lines.append(json_line)
    data = {"Lines": json_lines}
    json_filename = filename.replace("hocr","json")
    print(json_filename)
    with io.open(json_filename, "w", encoding="utf8") as write_file:
        json.dump(data, write_file, ensure_ascii=False, indent=1)


def main(baseDir):
    files = glob.glob(baseDir + "/*.hocr")
    print(files)
    for file in files:
        convert2json(file)



if __name__ == "__main__":
    baseDir = "../assets/Testset_new/result4000"
    if len(sys.argv) == 2:
        baseDir = sys.argv[1]
    main(baseDir)
    #imgPath = "../assets/tx_68_2.jpg"
    #path = "C:/Users/test/PycharmProjects/Teseract/assets/tesseract_recognitions/muller2_1000/tx_163_2.hocr"
    #convert2json(path)
    #showImage(imgPath, jsonPath, "rows")