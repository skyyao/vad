import numpy as np
import wave
import os
import sys

fsize = 256
selgap = 3

def is_cross(x, y) :
	return ((x^y) < 0)

def cal_cross0rate(samp) :
	cross = []
	s = 0
	l = len(samp)

	for i in range(l) :
		if (i+1) % fsize == 0 :
			cross.append(float(s)/(fsize-1))
			s = 0
			continue
		elif i == l - 1 :
			cross.append(float(s)/(fsize-1))
			break
		s = s + is_cross(samp[i], samp[i+1])
	return cross

def cal_energy(samp) :
	energy = []
	s = 0
	l = len(samp)

	for i in range(l) :
		s = s + (int(samp[i]) * int(samp[i]))
		if (i + 1) % fsize == 0 :
			energy.append(s)
			s = 0
		elif i == l - 1 :
			energy.append(s)
	return energy

#get the start and end point of voiced audio
def vad(energy, cross) :
	eg1 = eg2 = cg = 0.0
	s = 0
	v1 = []
	v2 = []
	v = []

	for e in energy :
		s += e
	eg1 = s/(3*len(energy))
	eg2 = eg1/2

	s = 0
	for c in cross :
		s += c
	cg = 2*s/len(cross)

	seq = 0
	#stage 1
	for e in range(len(energy)) :
		if len(v1) == 0 :
			#1st start point
			if seq == False and energy[e] > eg1 :
				v1.append(e)
				seq = True
		#new start point after silence gap
		elif seq == False and energy[e] > eg1 and e - selgap > v1[-1] :
			v1.append(e)
			seq = True
		#with in grace period, joint this point into previous end point
		elif seq == False and energy[e] > eg1 and e - selgap <= v1[-1] :
			v1 = v1[0:-1]
			seq = True

		#end point of voiced audio
		if seq and energy[e] < eg1 :
			v1.append(e)
			seq = False
	print("1st stage points: " + str(v1))

	#stage 2 energy
	for e in range(len(v1)) :
		e1 = v1[e]
		#even index is start point
		if e%2 == 0 :
			while e1 > 0 and energy[e1] > eg2 :
				e1 = e1 - 1
		else :
			while e1 < len(energy) and energy[e1] > eg2 :
				e1 = e1 + 1
		v2.append(e1)
	print("2nd stage end points: " + str(v2))

	#stage 3 cross 0 rate
	for c in range(len(v2)) :
		e2 = v2[c]
		if c%2 == 0 :
			while e2 > 0 and cross[e2] > cg :
				e2 = e2 - 1
		else :
			while e2 < len(cross) and cross[e2] > cg:
				e2 = e2 + 1
		v.append(e2)
	print("vad points: " + str(v))

	return v

def dtw(x, y) :
	xl = len(x)
	yl = len(y)
	D = [[0 for i in range(xl + 1)] for i in range(yl + 1)]

	for i in range(1, xl + 1) :
		D[0][i] = sys.maxsize
	for j in range(1, yl + 1) :
		D[j][0] = sys.maxsize
	for j in range(1, yl + 1) :
		for i in range(1, xl + 1):
			D[j][i] = abs(x[i-1]-y[j-1]) + min(D[j-1][i], D[j][i-1], D[j-1][i-1])
	print(D)
	return D[-1][-1]

def main() :
	fn1 = input("audio wavfile 1: ")
	fn2 = input("audio wavfile 2: ")

	while True:
		if os.path.exists(fn1 + ".wav") and os.path.exists(fn2 + ".wav"):
			break
		else :
			print("ERR: file not exist: " + fn1)

	f1 = wave.open(fn1 + ".wav", "rb")
	samps = f1.readframes(f1.getnframes())
	wav1 = np.frombuffer(samps, dtype = np.short)
	print("got " + str(len(wav1)) + " samples from " + fn1)
	f1.close()

	energy = cal_energy(wav1)
	print(energy)
	cross = cal_cross0rate(wav1)
	print(cross)
	endpoints1 = vad(energy, cross)

	f2 = wave.open(fn2 + ".wav", "rb")
	samps = f2.readframes(f2.getnframes())
	wav2 = np.frombuffer(samps, dtype = np.short)
	print("got " + str(len(wav2)) + " samples from " + fn2)
	f2.close()

	energy = cal_energy(wav2)
	print(energy)
	cross = cal_cross0rate(wav2)
	print(cross)
	endpoints2 = vad(energy, cross)
"""
	xl = endpoints1[0]*fsize
	xr = endpoints1[1]*fsize
	x = wav1[xl:xr]
	yl = endpoints2[0]*fsize
	yr = endpoints2[1]*fsize
	y = wav2[yl:yr]
	d = dtw(x, y)
	print(d)
"""

if __name__ == '__main__':
	main()









