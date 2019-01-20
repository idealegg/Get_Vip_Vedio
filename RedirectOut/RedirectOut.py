# -*- coding:utf-8 -*-
import sys


class __redirection__:

    def __init__(self, file):
        self.buff=""
        self.file=file
        self.__console__=sys.stdout
        self.fd=open(self.file, 'w')
        sys.stdout = self

    def write(self, output_stream):
        sys.__stdout__.write(output_stream)
        self.fd.write(output_stream)

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
  print 'hello'
  print 'there'
  del robj


if __name__=="__main__":
    # redirection
    test()
    print "123"