# Fine Tuning Tesseract 4.0 for real world data
## Introduction
This Project was developed by Matthias Leopold for the [RFND AG](http://rfnd.com/).
I was trying to teach [Tesseract](https://github.com/tesseract-ocr/tesseract) to better recognize our scanned Receipts in order to automatically read the VATs.
As Tesseract trains on line-data, I manually cropped some of the important lines from our receipts and labeled them.
Training Tesseract is not possible on windows machines at this point, so I worked with the Ubuntu shell for windows. (They recently patched a possibility to train on Windows aswell)

## Workflow
1) Install Tesseract, following [these](https://github.com/tesseract-ocr/tesseract/wiki/Compiling) instructions (I built from [source](https://github.com/tesseract-ocr/tesseract/wiki/Compiling-%E2%80%93-GitInstallation), but apt packages are now available). Make sure to also install the needed (probably only german) language packages. You might need to add the apt repository before installing:

    ```
    sudo add-apt-repository ppa:alex-p/tesseract-ocr
    sudo apt-get update
    
    sudo apt install tesseract-ocr
    sudo apt install libtesseract-dev 
    ```
2) Create Training Data, as described [here](https://github.com/tesseract-ocr/tesseract/wiki/TrainingTesseract-4.00#building-the-training-tools). Tesseract Training is based on <name>.tif/<name>.box file pairs, where the tif file is the image of a line and the box file contains its String content and the bounding box. The box file needs to consists of a number of lines, where each line follows the convention of:
    <symbol> <left> <bottom> <right> <top> <page>
Where <symbol> is a character and <left><bottom><right><top> describe the bounding box of the line. Pay attention, that the tesseract bouding box starts with (0,0) in the bottom left corner. You can find examples of thes file pairs in the assets\mullerData_training\v2 folder. 

    To create these box files to the corresponding tif file, i used the `create_box_file.py` script. You need to pass the base directory of the tif images as first parameter and an option as second. The option defines the action of the script. 1:= create ground truth (manually enter text to image), 2:= create box_files from the ground truth + image width/height, 3:= preprocess tif images. To sucessfully create the box images, you first need to run option 1 and then option 2. Option 3 is not mandatory. The call to the script may look something like:
    ```
    python create_box_file.py "../assets/mullerData_training/v2" 1
    ...
    python create_box_file.py "../assets/mullerData_training/v2" 2
    ```
3. Copy all tif/box files to your ubuntu filesystem (all pairs into one folder) and combine then them. The file pairs aren't directly being fed to tesseract, but rather combined to a .lstmf file. Navigate to the directory with all the tif/box pairs and run the following command (you might need to be in "su -i" mode):
    ```
    for file in *.tif; do
      echo $file
      base=`basename $file .tif`
      tesseract $file $base lstm.train
    done
    ```
    Now there should be a .lstmf file for every file pair in your file system. 
    Note: I did not use the plain line images for the training process, but performed an image preprocessing to them and fed those "cleaner" images to the training. It seemed like blurring gave the overall best results, but i didn't quantify the results properly. Some kind of binarization might work very well, as the base training data for Tesseract was artificially created and does not contain any grey noise in the background.
4) Create an `all-lstmf.txt` file. This file just contains the locations of the lstmf files that you want to use.
    ```
    ls -1 *.lstmf | sort -R > all-lstmf.txt
    ```
    Afterwards might want to split the data into a training and testing set afterwards, to quantify how good your fine tuned model is:
    ```
    head -n  10 all-lstmf.txt > list_test.txt
    tail -n +11 all-lstmf.txt > list_train.txt
    ```
5) Extract the trained lstm neural network from the standard Tesseract. This lstm will be used as a starting point for our training.
    ```
    tesseract-ocr/src/training/combine_tessdata -e tessdata/deu.traineddata ~/somepath/deu.lstm
    ```
6) Start the actual training process
    ```
    tesseract-ocr/src/training/lstmtraining --model_output somepath/myModel \
      --continue_from somepath/deu.lstm \
      --traineddata tesseract-ocr/tessdata/deu.traineddata \
      --train_listfile somepath/list_train.txt \
      --max_iterations 400
    ```
7) Afterwards you can evaluate, how good your new model ist. Compare this to the performance of the base model aswell:
    ```
     tesseract-ocr/src/training/lstmeval --model somepath/myModel \
    --traineddata tesseract-ocr/tessdata/deu.traineddata \
    --eval_listfile somepath/list_test.txt
    ```
8) The training process outputs various model checkpoints, that contain the neural network parameters. The final or best checkpoint of your model now needs to be combined to a standard `.traineddata` file for tesseract. 
    ```
     tesseract-ocr/src/training/lstmtraining --stop_training \
     --continue_from somepath/myModel_checkpoint \
     --traineddata tesseract-ocr/tessdata/deu.traineddata \
     --model_output somepath/myModel.traineddata
     ```
     This traineddata file can now be used to make predictions with tesseract, after it was put into the tessdata directory (this directory is located at: `echo $TESSDATA_PREFIX`).
9) Now you can start using your fine tuned model to produce output for a full test image. Passing the  `hocr` flag tells tesseract to not only output the text, but more detailed information about the bounding boxes aswell. For best results, preprocessing the receipt image to reduce background noise was found to be effektive.
    ```
    tesseract tx_01.preprocessed.jpeg tx_01.preprocessed -l myModel hocr
    ```
    Running this command will create a `tx_01.preprocessed.hocr` file, which contains the Text and corresponding meta data like its bounding box. 
10) Now in order to use Tesseract's prediction, we need to convert the hocr format to our well known layout json format. This can be achieved by copying all hocr files into a directory, running the `parse_hocr_to_json.py` and passing the root directory of directory containing the hocr files as first and only parameter:
    ```
    python parse_hocr_to_json.py "../assets/Testset_new/result4000"
    ```
