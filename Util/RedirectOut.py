# -*- coding:utf-8 -*-
import sys
import chardet


class __redirection__:

    def __init__(self, file):
        self.buff=""
        self.file=file
        self.__console__=sys.stdout
        self.fd=open(self.file, 'w')
        sys.stdout = self

    def write(self, output_stream):
        sys.__stdout__.write(output_stream)
        #if type(output_stream) is not unicode: # py2
        if isinstance(output_stream, bytes):
          self.fd.write(output_stream.decode(chardet.detect(output_stream)['encoding']).encode('utf-8'))
        else:
          self.fd.write(output_stream.encode('utf-8'))

    def flush(self):
        sys.__stdout__.flush()
        self.fd.flush()

    def __del__(self):
        try:
          sys.stdout=self.__console__
          self.fd.close()
        except :
          pass


def test():
  robj=__redirection__('out.log')
  # get output stream
  print('hello')
  print('there')
  del robj


if __name__=="__main__":
    # redirection
    test()
    print("123")