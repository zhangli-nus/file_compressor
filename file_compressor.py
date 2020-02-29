#coding: utf-8

import numpy as np
import cv2
import os
import math
import struct
import sys


def get_encode_endian():
    # 不管大端还是小段，均从低位读向高位
    # big-endian则高bytes写1, 四个字节
    # 高bytes写1, 四个字节\x00 \x00 \x00 \x01；
    # 如果是small-endian写1, 四个字节
    # 低bytes写1, 四个字节\x01 \x00 \x00 \x00
    # 网络传输默认是大端模式
    res = sys.byteorder  # 'little' or 'big'
    return res

class File2Image(object):
    def __init__(self):
        pass

    def get_file_size(self, input_filename):
        with open(input_filename, 'rb') as fp:
            total_length = fp.seek(0, os.SEEK_END)
        return total_length

    def get_img_width(self, total_length):
        img_width = math.ceil(math.sqrt(total_length))
        img_width = img_width + 2 #to append image size at the top two bytes
        return img_width

    # def get_encode_endian_in_c(self):
    #     int i=1;
    #     if(*(char*)&i == 1) //if i=1, little-endian第一个字节是0x01；big-endian则为1
    #         return "little";
    #     else
    #         return "big";

    def int_to_bytes(self, a, byteorder):
        #option1
        res = a.to_bytes(length=4, byteorder=byteorder) #效率最慢
        # #option2
        # if byteorder == 'little':
        #     res = struct.pack('<i', a)  # 效率最快，>表示大端，<表示小端
        # else:
        #     res = struct.pack('>i', a)
        # #option3
        # res = bytes([a]) #只能表示255以内的数
        return res

    def bytes_to_int(self, a, byteorder):
        if byteorder == 'little':
            res = struct.unpack('<i', a)[0]
        else:
            res = struct.unpack('>i', a)[0]
        #option2
        # res = int.from_bytes(a, byteorder=byteorder)
        return res

    def convert_file2image(self, input_filename, output_filename, endian_format='little'):
        total_length = self.get_file_size(input_filename) #4 bytes
        img_width = self.get_img_width(total_length)
        img_mat = np.zeros((img_width, img_width), dtype=np.uint8)
        # endian_format = self.get_encode_endian()
        size_binary = self.int_to_bytes(total_length, endian_format)
        print("total length: %d"%(total_length))
        img_mat[0, 0] = size_binary[0]
        img_mat[0, 1] = size_binary[1]
        img_mat[0, 2] = size_binary[2]
        img_mat[0, 3] = size_binary[3]
        with open(input_filename, 'rb') as fp:
            for idx in range(total_length):
                data = fp.read(1)
                # print("%#x"%(struct.unpack('<B', data)[0]))
                pos = idx+4
                x = math.floor(pos/img_width)
                y = pos%img_width
                img_mat[x, y] = struct.unpack('<B', data)[0]
        cv2.imwrite(output_filename, img_mat)

    def convert_image2file(self, input_filename, output_filename, endian_format='little'):
        img = cv2.imread(input_filename, cv2.IMREAD_GRAYSCALE)
        img_width, img_height = tuple(img.shape)
        x1, x2, x3, x4 = tuple(img[0, 0:4])
        data1 = int(x1).to_bytes(length=1, byteorder=endian_format)
        data2 = int(x2).to_bytes(length=1, byteorder=endian_format)
        data3 = int(x3).to_bytes(length=1, byteorder=endian_format)
        data4 = int(x4).to_bytes(length=1, byteorder=endian_format)
        data = data1+data2+data3+data4
        recovery_size = self.bytes_to_int(data, endian_format)
        print("recoveryed size: %d"%recovery_size)
        raw_data = [b'0']*recovery_size
        for idx in range(recovery_size):
            if idx % 500000 == 0:
                print("iteration: %d, total: %d"%(idx, recovery_size))
            pos = idx+4
            x = math.floor(pos / img_width)
            y = pos % img_width
            # data += int(img[x, y]).to_bytes(length=1, byteorder=endian_format)
            raw_data[idx] = struct.pack('<B', int(img[x,y]))
        with open(output_filename, 'wb') as fp:
            for idx in range(recovery_size):
                fp.write(raw_data[idx])
        print("recoveryed file: %s" % output_filename)


if __name__ == '__main__':
    import time
    start_time = time.time()
    t = File2Image()
    endian_format = get_encode_endian()
    # t.convert_file2image('./data/test.zip', './data/res.png', endian_format=endian_format)
    # print("convert to image: %0.3f"%(time.time()/60.0-start_time/60.0))
    t.convert_image2file('./data/res.png', './data/test_recovery.zip', endian_format=endian_format)
    print("recovery to file: %0.3f" % (time.time() / 60.0 - start_time / 60.0))
    pass