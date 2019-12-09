"""
In java exists a subclass of FloatProcessor. In python do not (or at least I did not find it). I translate the code that
I need here.


"""
from numpy import zeros,sum
from math import pi,cos,sin

def btst(x, bit):
    return x & (1 << bit) != 0

def log2(x):
    cont=31
    while btst(x,cont) is False:
        cont = cont-1
    return cont

def bitRevX(x,bitLen):
    temp =0
    for i in range(bitLen+1):
        if (x & (1<<i)) !=0:
            temp |= (1<<(bitLen-i-1))
    return temp

class FHT:
    """
    Fast Hartley Transform
    """

    def __init__(self, img=None):
        # i have to see which kind of values i have to init... img always a numpy?
        #see pag 44 FHT.class
        self.img=img
        self.width=0
        self.height = 0
        self.maxN=0
        self.S = None
        self.C=None
        self.isFrequencyDomain = None
        self.bitrev=None
        self.tempArr = None

    def add(self, value=0):
        #shold be the standard FloatProcess.add
        sum(self.img,value, out=self.img)


    def initializeTables(self, maxN):
        if self.maxN > 0x40000000:
            print(f"ERROR: Too large for FHT: maxN(={maxN}) > 2^30")
            exit(-1)
        self.makeSinCosTables(maxN)
        self.makeBitReverseTable(maxN)
        self.tempArr = zeros(maxN)

    def makeSinCosTables(self,maxN):
        n=maxN
        self.C = zeros(n, dtype=float)
        self.S = zeros(n, dtype=float)
        theta = 0
        dtheta=2*pi/maxN
        for i in range(n):
            self.C = cos(theta)
            self.S = sin(theta)
            theta+=dtheta

    def makeBitReverseTable(self,maxN):
        self.bitrev=zeros(maxN, dtype=int)
        nLog2 = log2(maxN)
        for i in self.bitrev.shape[0]:
            self.bitrev[i] = bitRevX(i, nLog2)


    def powerOf2Size(self):
        """
        :return: true of this FHT contains a square image with a width that is a power of two
        """
        if self.width!=self.height or self.width%2!=0:
            return False
        i = 2
        while i<self.width:
            i*=2
        return i==self.width

    def transform(self,inverse):
        """
        Trasform from space domain to frequency domain and viceversa
        :param inverse: True to transofrm in frequency domain. false viceversa
        :return:
        """
        if self.powerOf2Size() is False:
            print(f"ERROR: Image not power of 2 size or not square. width={self.width}\theight={self.height}")
            exit(-1)
        self.maxN=self.width
        if self.S is None:
            self.initializeTables(self.maxN)
        self.rc2DFHT(self.img,inverse,self.maxN)    # see ln 196. it should be the pixel matrix of the img
        self.isFrequencyDomain = not inverse
        pass

    def rc2DFHT(self, img,inverse,maxN):
        """Performs a 2D FHT (Fast Hartley Transform)"""
        #todo: implementala
        pass

    def transform_to_freq_domain(self):
        """
        Performs a forward transform, converting this image into the frequency domain.
		The image contained in this FHT must be square and its width must be a power of 2
        :return:
        """
        self.transform(False)

    def transform_to_space_domain(self):
        """
        Performs a forward transform, converting this image into the space domain.
		The image contained in this FHT must be square and its width must be a power of 2.
        :return:
        """
        self.transform(True)