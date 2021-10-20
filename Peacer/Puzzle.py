import requests
import cv2 as cv
import json
import numpy as np
import os
from pathlib import Path
MEDIA_FOLDER = os.path.abspath(os.path.join( os.path.dirname( __file__ ), '../media' ))
class PuzzleGame:
    collectionName = "moonshotbotsv3";
    baseUrl = 'https://gateway.pinata.cloud/ipfs/QmShqhZzwkoEM1wcrWjG7HTvPUgvBaknRqaFhBUNMvis1T/nfts/'
    src = None
    name = ''
    Lowhsv = [0,180,0]
    Highhsv = [255,255,60] 
    kernel = 7
    size=(1000,1000)

    def __init__(self, name, imgURL = None, baseUrl = None):
        if baseUrl is not None:
            self.baseUrl = baseUrl
        if imgURL is not None:
            self.imgURL = imgURL
        else:
            self.imgURL = name + ".png"
        self.name = name
        imgPath = os.path.join(MEDIA_FOLDER, self.collectionName, self.name , self.imgURL)
        img = cv.imread(imgPath, cv.IMREAD_UNCHANGED)
        self.src = img
        if self.src is None:
            try:            
                self.downloadImg(self.baseUrl + self.imgURL)
                img = cv.imread(imgPath, cv.IMREAD_UNCHANGED)
                self._setup(img)
            except Exception as e:
                raise RuntimeError('Download error')
        else:
            self._setup(img)
        if self.src is None:
            raise RuntimeError('Src is empty')
 

    def _setup(self, img):
        self.src = cv.resize(img, self.size, fx=0.5, fy=0.5) 

    def downloadImg(self, url):  
        folderPath = os.path.abspath(os.path.dirname(os.path.join(MEDIA_FOLDER, self.collectionName, self.name, self.imgURL)))
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        with open(os.path.join(MEDIA_FOLDER, self.name,  self.imgURL), 'wb') as f:
            f.write(requests.get(url).content)

    def onThreshholdChange(self, *value):
        if value and value[0] is not None:
            self.thresholdValue = value[0]
        self.threshold()

    def onErodeChange(self, *value):
        if value and value[0] is not None:
            self.erodeValue = value[0]
        self.threshold()

    def hElement(self):
        element = cv.getStructuringElement(cv.MORPH_RECT, (1, 40))
        return element

    def threshold(self, img, iter = 1):
        _, thresh = cv.threshold(img, 100, 255, 0)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, 
                                   (7, 7))
        thresh = cv.erode(thresh, kernel, iter)
        return thresh

    def grayScale(self, img):
        return cv.cvtColor(img, cv.COLOR_RGB2GRAY)

    def erode(self, img, k =(7,7)):
        element = cv.getStructuringElement(cv.MORPH_RECT, k)
        return cv.erode(img, element)
    def dilate(self, img, k =(7,7)):
        element = cv.getStructuringElement(cv.MORPH_RECT, k)
        return cv.dilate(img, element)
    def houghGrad(self, img, k = (15,15)):
        kernel = cv.getStructuringElement(cv.MORPH_RECT,
                                k)
        return cv.morphologyEx(img, 
                            cv.HOUGH_GRADIENT,
                            kernel)  
    def close(self, img, k = (1,13)):
        kernel = cv.getStructuringElement(cv.MORPH_RECT,
                                k)
        return cv.morphologyEx(img, 
                            cv.MORPH_CLOSE,
                            kernel)  
    def open(self, img, k = (1,13)):
        kernel = cv.getStructuringElement(cv.MORPH_RECT,
                                k)
        return cv.morphologyEx(img, 
                            cv.MORPH_OPEN,
                            kernel)
    def colorFilter(self, img, low, high):
        frame = img.copy()
        img =   cv.cvtColor(img, cv.COLOR_BGR2HSV)
        img = cv.inRange(img,  np.array(self.Lowhsv), np.array(self.Highhsv))
        return img
    
    def getContour(self, img, minArea = 3000):
        x = []
        contours, hierarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_NONE )
        if hierarchy is None:
            return x
        c = sorted(contours,  key=lambda x: cv.contourArea(x))
        for i in range(len(c)):
            cnt = contours[i]
            area= cv.contourArea(cnt)
            h = hierarchy[0][i]
            if h[3] == -1 :
                if(area > 10000 and area < 100000):
                    x.append(cnt)
                    break
            else:
                if(area > 5000 and area < 100000):
                    x.append(cnt)
                    break
        return x

    def getPeaces(self,  max = 15):
        

        if self.src is None:
            raise RuntimeError('Src is empty')
        ext = '.' + self.imgURL.split('.')[-1]
        for p in Path(os.path.abspath(os.path.join(MEDIA_FOLDER, self.name))).glob(self.name + '_*' + ext):
            p.unlink()    
        for p in Path(os.path.abspath(os.path.join(MEDIA_FOLDER, self.name))).glob('metadata*.json'):
            p.unlink()
        img = self.src.copy()
        filtered = img.copy()
     
        mask = self.colorFilter(img, self.Lowhsv, self.Highhsv)
        binary_mask = cv.bitwise_or(filtered, filtered, mask =  cv.bitwise_not(mask))
        binary_mask = self.grayScale(binary_mask)
        binary_mask = self.threshold(binary_mask)
        binary_mask = self.erode(binary_mask, (1,1))
        binary_mask = self.close(binary_mask, (3,3))
        # binary_mask = self.dilate(binary_mask, (1,1))
        binary_mask = cv.bitwise_not(binary_mask)
        binary_mask = cv.Canny(binary_mask, 100 , 200)
        mask = np.zeros(filtered.shape[:2], np.uint8)
        metadata = {"Peaces": []}
        peaces = []
        contours = []
        for i in range(max):
            cnt = self.getContour(binary_mask)
            if len(cnt) == 0  :
                break
            contours.append(cnt[0])
            cMask = np.zeros(filtered.shape[:2], np.uint8) 
            cv.fillPoly(binary_mask, pts = cnt, color=(0,0,0))
            cv.fillPoly(mask, pts = cnt, color=255)
            cv.fillPoly(cMask, pts = cnt, color=255)
            x,y,w,h = cv.boundingRect(cnt[0])
            padding = 4
            ROI = img[y:y+h,x:x+w]
            ROI = cv.cvtColor(ROI, cv.COLOR_BGR2BGRA)
            row, col = ROI.shape[:2]
            roiFrame = np.zeros((row + (padding*2), col + (padding*2), 4) , np.uint8)
            roiFrame[padding:-padding, padding: -padding] = ROI
            ROI = roiFrame
            roiMask = np.zeros(ROI.shape[:2] , np.uint8)
            cv.fillPoly(roiMask, pts = cnt, color=(255,) * ROI.shape[2], offset=(-x,-y))
            peace = cv.bitwise_and(ROI, ROI, mask = roiMask)
            M = cv.moments(cnt[0])
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            peaces.append(peace)
            metadata['Peaces'].append({
                "Id": self.name + '_' + str(i),
                "Url": self.name + '_' + str(i) + ".png",
                "Center": {"x":cx, "y":cy},
                "Dim": {'x':x,'y':y,'w':w,'h':h,}
            })
        metadata["Name"] = self.name
        metadata["HoledUrl"] = self.name + "_holed" + ext
        metadata["Url"] = self.imgURL
        metadata["BaseUrl"] = self.baseUrl
        metaPath = os.path.abspath(os.path.join(MEDIA_FOLDER, self.name , 'metadata.json'))
        if not os.path.exists(os.path.dirname(metaPath)):
            os.makedirs(os.path.dirname(metaPath))
        with open(metaPath, 'w+', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

      
        for i in  range(len(metadata['Peaces'])):
            peace = metadata['Peaces'][i]
            cv.imwrite(os.path.abspath(os.path.join(MEDIA_FOLDER, self.name  , peace['Id'] + ext)), peaces[int(i)])
        mask = cv.bitwise_not(mask)
        holey = cv.bitwise_and(filtered, filtered, mask = mask)
        holey = cv.drawContours(holey.copy(), contours, -1, (0,0,0, 255), 5)  
        holey = cv.drawContours(holey.copy(), contours, -1, (255,255,255, 255), 4)  
        holey = cv.drawContours(holey.copy(), contours, -1, (66,11,230, 255), 2)  
        # cv.imshow("holey", holey)
        # cv.waitKey(0)
        cv.imwrite(os.path.abspath(os.path.join(MEDIA_FOLDER, self.name  , self.name + "_holed" + ext)), holey)
        return True
        q



    

# p = [
#     'bot00.png',
#     'bot3.png',
#     'Average_Platform.png',
#     'Ashamed_Backup.png',
#     'Blushing_Malware.png',
# ]
# game = PuzzleGame("Massive_Browser")
# game.getPeaces()
