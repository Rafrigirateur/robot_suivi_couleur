import sys
import os
import cv2 as cv

# Ensure project root is importable when running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Hardware.camera import Camera


def main():
	cam = Camera(camId=1, width=640, height=480, fps=30)

	try:
		while True:
			frame = cam.get_frame()
			if frame is None:
				print('No frame received, exiting.')
				break

			cv.imshow('Video', frame)

			if cv.waitKey(1) & 0xFF == 27:  # ESC to quit
				break
	finally:
		cam.release()
		cv.destroyAllWindows()


if __name__ == '__main__':
	main()

