import os
import imagehash
from PIL import Image

def analyseImage(path):
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results

def processImage(path):

    mode = analyseImage(path)['mode']
    
    im = Image.open(path)

    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')
    
    try:
        while True:
            #print("saving %s (%s) frame %d, %s %s" % (path, mode, i, im.size, im.tile))

            if not im.getpalette():
                im.putpalette(p)
            
            new_frame = Image.new('RGBA', im.size)

            if mode == 'partial':
                new_frame.paste(last_frame)
            
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            new_frame.save('./GIF/%d.png' % (i+1), 'PNG')
            #new_frame.save('./GIF/%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i), 'PNG')

            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass

def get_avg_fps(PIL_Image_object):
    PIL_Image_object.seek(0)
    frames = duration = 0
    while True:
        try:
            frames += 1
            duration += PIL_Image_object.info['duration']
            PIL_Image_object.seek(PIL_Image_object.tell() + 1)
        except EOFError:
            print(f"Frames: {frames}")
            print(f"Duration: {duration / 1000}s")
            print(f"Average time per frame: {duration / (frames * 1000)}s")
            return duration / (frames * 1000)
    return None

def is_image_different(img1, img2):
    img1 = f"./GIF/{img1}"
    img2 = f"./GIF/{img2}"
    hash0 = imagehash.average_hash(Image.open(img1)) 
    hash1 = imagehash.average_hash(Image.open(img2)) 
    cutoff = 3 #lol what the fuck is a cutoff

    if hash0 - hash1 <= cutoff: #hash difference compare to cutoff
        return False #false b/c images are similar

    else:
        return True #true b/c images are different

def compare_frames(frame_path): #framepath should be ./GIF
    temp_arr = []
    frame_diff_arr = []
    os_dir = os.listdir(frame_path)

    temp = []
    for i in os_dir:
        split_arr = i.split('.')
        temp.append(int(split_arr[0]))
    temp = sorted(temp)

    os_dir = []
    for j in temp:
        string = f"{j}.png"
        os_dir.append(string)

    for f in os_dir: #f for file
        if len(temp_arr) == 2:
            img_bool = is_image_different(temp_arr[0], temp_arr[1])
            frame_diff_arr.append(img_bool)
            temp_arr = [temp_arr[1]]
            temp_arr.append(f)
        elif len(temp_arr) < 2 and len(temp_arr) == 1:
            temp_arr.append(f)
            img_bool = is_image_different(temp_arr[0], temp_arr[1])
            frame_diff_arr.append(img_bool)
            temp_arr = [temp_arr[1]]
        else:
            temp_arr.append(f)

    t_count = f_count = 0
    for b in frame_diff_arr:
        if b == True:
            t_count += 1
        else:
            f_count += 1
    
    print(f"True Count: {t_count}\nFalse Count: {f_count}")
    
    end_arr = [frame_diff_arr, t_count, f_count]

    return end_arr

def main():
    FILENAME = input("Enter gif file name (exclude .gif extension): ")
    FILENAME += ".gif"
    path = "./GIF/"
    processImage(FILENAME)
    img_obj = Image.open(FILENAME)
    avg_frame_time = get_avg_fps(img_obj)
    c = compare_frames(path)
    
    temp = []
    count = 0
    string = "GIF is most likely alright."
    for i in c[0]:
        if count != 4:
            temp.append(i)
            count += 1

        elif count == 4:
            if (temp[0] == True and (temp[0] == temp[1] == temp[2] == temp[3])): print("GIF has at least 4 frames where frames are too different from each other (cutoff=3).")
            if (avg_frame_time < 0.3333): print("GIF average frame time is faster than set boundary of 0.3333s.")
            if (c[1] / c[2] > 0.34): print(f"GIF True:False ratio: {c[1] / c[2]}, exceeds 34% limit.")
            if (temp[0] == True and (temp[0] == temp[1] == temp[2] == temp[3]) and (avg_frame_time < 0.3333)) or (c[1] / c[2] > 0.34):
                string = "GIF is most likely epileptic. Please proceed with manual evaluation."
                break
            else:
                temp = []
                count = 0
    
    for f in os.listdir(path):
        os.remove(path + f)

    print(string)

if __name__ == "__main__":
    main()