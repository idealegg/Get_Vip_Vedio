from Crypto.Cipher import AES
import os
fs=os.listdir('.')
fs1=filter(lambda x: x.startswith('3_') and x.endswith('.ts'), fs)
def dec(ff, key):
  c = AES.new(key, AES.MODE_CBC, key)
  ffd=open(ff, 'rb')
  ffe=ffd.read()
  ffd.close()
  fff=c.decrypt(ffe)
  ffd=open(ff+'tmp', 'wb')
  ffd.write(fff)
  ffd.close()
def enc(ff, key):
  c = AES.new(key, AES.MODE_CBC, key)
  ffd=open(ff, 'rb')
  ffe=ffd.read()
  ffd.close()
  fff=c.encrypt(ffe)
  ffd=open(ff+'tmp', 'wb')
  ffd.write(fff)
  ffd.close()
  