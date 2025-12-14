#!/usr/bin/python

# This script finds and list duplicate files.

# USAGE: finddup.py [dir1] [dir2] ... [dirN],
#        where dir1, dir2, dirN are the directories to search for duplicate
#        files. If no directories are given, current directory is used as the
#        starting point


from sys import argv
import os
import hashlib



BUFFER_SIZE = 1024

if __name__ == '__main__':
   
   args = []
   if len(argv) == 1:
      print 'Using current directory'
      args = '.'
   else:
      args = argv[1:]

   filelist = []
   for topdir in args:
      for root, dirs, files in os.walk(topdir):
         for name in files:
            filelist.append(os.path.join(root, name))


   # Hash dictionary
   hashDict = {}
   
   # Open each file
   for filename in filelist:
      # do not look at 0 bytes files - they are all the same
      # do not look at .DS_Store - those are frequently the same
      if ('.DS_Store' == os.path.basename(filename) or 
          0 == os.path.getsize(filename)):
         continue
      
      # Create hash object for calculating SHA 256 over each file
      hashObj = hashlib.sha256()

      # open each file in binary, read only
      try:
         fileObj = open(filename, 'rb')    
      except IOError as e:
         print 'Unable to open %s: %s' % (filename, e)
         continue
         

      fileSize = 0
      try:
         while True:
            buf = fileObj.read(BUFFER_SIZE)

            if not buf:
               break                       # finished file

            # if have valid data in buffer, update hash
            hashObj.update(buf)
            
            # update file size
            fileSize += len(buf)

      finally:
         fileObj.close()

      # get generated digest
      hexdigest = hashObj.hexdigest()

      # Check if the file with the same checksum already exists
      # add checksum and file info to dictionary if its does not
      if not hexdigest in hashDict:
         hashDict[hexdigest] = (filename, fileSize)
      else:
         # file with the same checksum already exists. Most likely found a
         # duplicate file.
         # Print information about the dup files
         print "Duplicates:"
         print '%s: %s (%s bytes)' % (hashDict[hexdigest][0], hexdigest,
            hashDict[hexdigest][1])
         print '%s: %s (%s bytes)' % (filename, hexdigest, fileSize)
