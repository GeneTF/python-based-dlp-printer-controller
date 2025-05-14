# python-based-dlp-printer-controller

This is a Python based application to control DLP printers. The application is tailored to the Gaharwar Laboratory customized DLP printer. Feel free to make changes to the code to tailor to your build.

The application uses PySerial for serial USB connection, PyQt6 for the user interface, pyqtdarktheme for the UI style, PySLM and Trimesh for slicing and image generation, and Pillow and OpenCV for image manipulation. I reused code from the pyCrafter4500 package to be able to change the UV intensity; credits to SivyerLab for providing the code available on their page.

I plan to update this Read Me and create a YouTube playlist showcasing how to build a DLP printer and how to use this code for printing.

I appreciate any help in correcting and optimizing any code I have already written.

Python 3.13 recommended. A requirements.txt file is provided to show the requirements needed using pip and a virtual environment. The fork of pyqtdarktheme is recommended for the latest Python version.

