'''
This module contains a perceptual image has algorithm for comparing two images
to see if they are identical or not. 

@author: Cory Banack
'''
import clr
clr.AddReference('System')
from System import Array, Single

clr.AddReference('System.Drawing')
from System.Drawing import Bitmap, Graphics, GraphicsUnit, Rectangle
from System.Drawing.Imaging import ColorMatrix, ImageAttributes
from System.Drawing.Drawing2D import CompositingQuality, \
   SmoothingMode, InterpolationMode


#==============================================================================
def perceptual_hash(image):
   ''' 
   Returns an image hash for the given Image. 
   '''
   
   if image is not None:
   
      SIZE = 8
         
      # create ImageAttributes for converting image to greyscale
      # see: http://tech.pro/tutorial/660/
      #              csharp-tutorial-convert-a-color-image-to-grayscale
      attr = ImageAttributes()
      attr.SetColorMatrix(
         ColorMatrix(Array[Array[Single]](( \
            (0.3, 0.3, 0.3, 0.0, 0.0),   
            (.59, .59, .59, 0.0, 0.0),
            (.11, .11, .11, 0.0, 0.0),        
            (0.0, 0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 0.0, 1.0)         
         )))
      )
      
      with Bitmap(SIZE,SIZE, image.PixelFormat ) as small_image:
         with Graphics.FromImage(small_image) as g:
            
            # draw image in greyscale in a tiny square
            # see:  https://www.memonic.com/user/aengus/folder/coding/id/1qVeq
            g.CompositingQuality = CompositingQuality.HighQuality
            g.SmoothingMode = SmoothingMode.HighQuality
            g.InterpolationMode = InterpolationMode.HighQualityBicubic
            g.DrawImage(image, Rectangle(0,0,SIZE,SIZE), 0, 0,
               image.Width, image.Height, GraphicsUnit.Pixel, attr)
            
            # convert image pixels into bits, where 1 means pixel is greater
            # than image average, and 0 means pixel is less than average.
            # return bits as a single long value
            pixels = [small_image.GetPixel(x,y).R 
                      for x in range(SIZE) for y in range(SIZE)];
            average = reduce(lambda x,y: x+y, pixels) / float(len(pixels))
            bits = map(lambda x: 1 if x > average else 0, pixels ) 
            return reduce(lambda x, (i, val): x | (val<<i), enumerate(bits), 0)
         
   else:
      return long(0);
         
         
#==============================================================================
def similarity(hash1, hash2):
   ''' 
   Returns the 'similarity' between two perceptual hash values as
   a value between 0.0 and 1.0, with 1.0 meaning 'very similar'
   and 0.0 meaning 'very different'. 
   '''
   if hash1 == None or hash2 == None:
      return 0.0;
   else:
      xor = hash1 ^ hash2
      hamming_distance = sum( b == '1' for b in bin(xor)[2:])
      return 1.0 - ( hamming_distance / float(len(bin(xor))) )