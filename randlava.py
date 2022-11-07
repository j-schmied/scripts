import cv2
import numpy as np
import whirlpool


def hash(s):
    wp = whirlpool.new(s.encode("utf-8"))
    return wp.hexdigest()


# Crop camera image to isolate lava lamp
def crop_frame(img):
    return img[100:900, 200:350]


def img_to_string(img):
    string = np.array2string(img, separator="")
    return string

def generate_secure_hash():
    cv2.namedWindows("Cam")
    cam = cv2.VideoCapture(0)
    
    if not cam.isOpened():
        exit(-1)
        
    works, frame = cam.read()
    
    while works:
        frame = crop_frame(frame)
        
        cv2.imshow("Cam", frame)
        works, frame = cam.read()
        
        string = img_to_string(frame)
        res = hash(string)
        yield res
    
    cam.release()
    cv2.destroyAllWindows()
    

def main():
    generator = generate_secure_hash()
    
    while True:
        print(next(generator))


if __name__ == "__main__":
    main()