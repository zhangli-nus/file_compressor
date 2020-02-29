#coding: utf-8
import os
import math


class FileSplitter(object):
    def __init__(self):
        pass

    def get_file_size(self, file_name):
        with open(file_name, 'rb') as fp:
            total_length = fp.seek(0, os.SEEK_END)
        return total_length

    def get_batch_per_size(self, total_length, part_num):
        if total_length<part_num:
            raise ValueError("file length must be larger than part_num")
        avg_length = math.floor(total_length / part_num)
        left_length = total_length - avg_length * part_num
        batch_per_size = [avg_length] * part_num
        batch_per_size[0:left_length] = map(
            lambda x: x + 1, batch_per_size[0:left_length])
        return batch_per_size

    def split(self, input_filename, part_num, output_filename_base, extension):
        input_filename = input_filename
        self.total_length = self.get_file_size(input_filename)
        self.batch_per_size = self.get_batch_per_size(
            self.total_length, part_num)
        fp = open(input_filename, 'rb')
        try:
            idx = 0
            while idx<part_num:
                data = fp.read(self.batch_per_size[idx])
                foutput = open('%s%d.%s' % (output_filename_base, idx, extension), 'wb')
                foutput.write(data)
                foutput.close()
                idx = idx + 1
        finally:
            fp.close()

    def merge(
            self,
            input_filename_base,
            part_num,
            extension,
            output_filename,
            reverse=False):
        '''
        :param input_filename_base: filename base
        :param part_num: part number
        :param extension: file extension
        :param output_filename: output filename
        :param reverse: read from small to large
        :return:
        '''
        input_filename_list = [
            '%s%d.%s' %
            (input_filename_base, idx, extension) for idx in range(part_num)]
        if reverse:
            input_filename_list = input_filename_list[-1::-1]
        data = b''
        with open(output_filename, 'wb') as fp:
            for input_filename in input_filename_list:
                with open(input_filename, 'rb') as finput:
                    data += finput.read()
            fp.write(data)


if __name__ == '__main__':
    a = FileSplitter()
    a.split(
        input_filename='./data/test.zip',
        part_num=3,
        output_filename_base='./data/test',
        extension='zip'
        )

    a.merge(input_filename_base='./data/test',
            part_num=3,
            extension='zip',
            output_filename='data/test_merged.zip',
            reverse=False
            )
