from Crypto.Cipher import AES
import os


def decode(key, s):
  cryptor = AES.new(key, AES.MODE_CBC, key)
  return cryptor.decrypt(s)


if __name__ == "__main__":
  os.chdir(r'C:\Downloads\store\movies')
  key = '3583be23a99ac9ae'
  for file in os.listdir('.'):
    if file.endswith('ts'):
      fd=open(file, 'rb')
      s=fd.read()
      fd.close()
      s2 = decode(key, s)
      fd = open(file.replace('ts', 'tmp'), 'wb')
      fd.write(s2)
      fd.close()