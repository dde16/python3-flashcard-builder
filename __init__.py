import os
import sys
import argparse
import json
import numpy as np
import cv2
import math
import collections

FontInfo = collections.namedtuple("FontInfo", ["name", "scale", "colour", "thickness"])

class Page:
    ppi       = None
    image     = None
    height    = None
    width     = None
    fontInfo  = None

    def __init__(self, ppi, fontInfo, intervals):
        self.ppi = ppi
        self.fontInfo = fontInfo
        self.intervals = intervals
        self.height, self.width = A4.GetDimensions(self.ppi)

        self.image = np.zeros((self.height, self.width, 3), np.uint8)
        self.image.fill(255)

    def draw(self, items: list):
        intervalsAdjusted = self.intervals - 1
        intervalsVerticalCount = 1 if self.intervals < 4 else 2
        intervalsHorizontalCount = math.floor(self.intervals / intervalsVerticalCount)

        intervalsVerticalSize = math.floor(self.height / intervalsVerticalCount)
        intervalsHorizontalSize = math.floor(self.width / intervalsHorizontalCount)

        for intervalVertical in range(intervalsVerticalCount-1):
            intervalVerticalSize = (intervalVertical+1) * intervalsVerticalSize
            cv2.line(
                self.image,
                (0, intervalVerticalSize),
                (self.width, intervalVerticalSize),
                (0,0,0),
                1
            )

        for intervalHorizontal in range(intervalsHorizontalCount-1):
            intervalHorizontalSize = (intervalHorizontal+1) * intervalsHorizontalSize
            cv2.line(
                self.image,
                (intervalHorizontalSize,0),
                (intervalHorizontalSize,self.height),
                (0,0,0),
                1
            )

        for index, item in enumerate(items):
            itemNumber = index + 1
            itemHorizontalIndex = itemNumber % intervalsHorizontalCount

            if itemHorizontalIndex == 0:
                itemHorizontalIndex = intervalsHorizontalCount

            itemVerticalIndex = math.ceil(itemNumber / intervalsHorizontalCount)

            itemLines = list(
                map(
                    lambda line: [
                        line.strip(),
                        cv2.getTextSize(
                            line.strip(),
                            self.fontInfo.name,
                            self.fontInfo.scale,
                            self.fontInfo.thickness
                        )[0]
                    ],
                    item.split("\n")
                )
            )

            itemPositionX = round(
                (intervalsHorizontalSize * (itemHorizontalIndex - 1)) + intervalsHorizontalSize/2
            )

            itemPositionY = round(
                (intervalsVerticalSize * (itemVerticalIndex - 1)) + intervalsVerticalSize/2
            )

            itemLinesTotalHeight = 0
            itemLinesCount = len(itemLines)

            for itemLineIndex, itemLineInfo in enumerate(itemLines):
                itemLineText = itemLineInfo[0]
                itemLineSize = itemLineInfo[1]

                itemLineWidth = itemLineSize[0]
                itemLineHeight = itemLineSize[1]

                if itemLineIndex != itemLinesCount:
                    itemLinesTotalHeight += itemLineHeight

            fontGap = round(
                itemLinesTotalHeight / itemLinesCount
            )

            itemPositionY -= round(
                (itemLinesTotalHeight / itemLinesCount) +
                (itemLinesCount * fontGap)
            )

            for itemLineIndex, itemLineInfo in enumerate(itemLines):
                itemLineText = itemLineInfo[0]
                itemLineSize = itemLineInfo[1]

                itemLineWidth = itemLineSize[0]
                itemLineHeight = itemLineSize[1]

                itemPositionY += itemLineHeight
                itemPositionY += fontGap

                cv2.putText(
                    self.image,
                    itemLineText,
                    (
                        itemPositionX - round(itemLineWidth / 2),
                        itemPositionY
                    ),
                    self.fontInfo.name,
                    self.fontInfo.scale,
                    self.fontInfo.colour,
                    self.fontInfo.thickness
                )

        return self.image

class Utility:
    @staticmethod
    def ImageRotate(image, angle, center = None, scale = 1.0):
        (height, width) = image.shape[:2]

        if center is None:
            center = (height / 2, width / 2)

        # Perform the rotation
        rotationMatrix = cv2.getRotationMatrix2D(center, angle, scale)
        rotatedImage = cv2.warpAffine(image, rotationMatrix, (height, width))

        return rotatedImage

    @staticmethod
    def SliceInterval(source, interval):
        interval = interval - 1
        slices = []

        for index in range(interval+1):
            if index % interval == 0:
                start = index

                if index > 0: start += 1

                end = start + interval + 1

                slices.append(
                    source[start:end]
                )

        return slices

class A4:
    base = [8.2639, 11.695]

    @staticmethod
    def GetDimensions(ppi: int):
        return list(map(lambda d: math.ceil(d * ppi), A4.base))

class Program:
    @staticmethod
    def Main(arguments):
        cwd = os.getcwd()

        source = arguments.source
        source = cwd + "/" + source

        outputDirectory = cwd + "/sheets"

        ppi = arguments.ppi
        fontInfo = FontInfo(
            name=cv2.FONT_HERSHEY_SIMPLEX,
            scale=ppi/arguments.text_scale,
            colour=(0,0,0),
            thickness=1
        )

        intervals = 4
        intervalsAdjusted = intervals - 1

        with open(source, "r") as sourceIO:
            questions = json.load(sourceIO)
            questionsLength = len(questions)

            if not os.path.exists(outputDirectory):
                os.mkdir(outputDirectory)

            for intervalIndex, intervalQuestions in enumerate(Utility.SliceInterval(questions, intervals)):
                intervalQuestionPrompts = list(
                    map(
                        lambda question: question["prompt"],
                        intervalQuestions
                    )
                )

                intervalQuestionAnswers = list(
                    map(
                        lambda question: question["answer"],
                        intervalQuestions
                    )
                )

                intervalQuestionPromptPage = Page(ppi, fontInfo, intervals)
                intervalQuestionPromptPageImage = intervalQuestionPromptPage.draw(intervalQuestionPrompts)

                intervalQuestionAnswerPage = Page(ppi, fontInfo, intervals)
                intervalQuestionAnswerPageImage = intervalQuestionAnswerPage.draw(intervalQuestionAnswers)

                intervalFolder = cwd + "/sheets/" + str(intervalIndex)

                if not os.path.exists(intervalFolder):
                    os.mkdir(intervalFolder)

                intervalPromptsPath = intervalFolder + "/prompts.png"
                intervalAnswersPath = intervalFolder + "/answers.png"

                cv2.imwrite(intervalPromptsPath, intervalQuestionPromptPageImage)
                cv2.imwrite(intervalAnswersPath, intervalQuestionAnswerPageImage)

    @staticmethod
    def AddArguments(parser):
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            required=True
        )

        parser.add_argument(
            "-r",
            "--ppi",
            type=int,
            choices=[72,96,150,300],
            default=72
        )

        parser.add_argument(
            "-x",
            "--text-scale",
            type=int,
            default=120
        )

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()

        Program.AddArguments(parser)
        Program.Main(parser.parse_args())
    except KeyboardInterrupt:
        pass