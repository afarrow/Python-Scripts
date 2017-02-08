## Miscellaneous Useful Python Scripts
### mergepdfs.py
A simple script for merging pdfs together. The script looks for pdfs that share the same base filename and combines them together based on the page number indicated in the filename. For example:
```
folder
├── folder1
│   ├── notesp1.pdf
│   ├── notesp2.pdf
│   ├── slidesp1.pdf
│   └── slidesp2.pdf
├── folder2
│   ├── git.pdf
│   ├── letter.pdf
│   ├── pythonp1.pdf
│   └── pythonp2.pdf
├── instructionsp1.pdf
├── instructionsp2.pdf
├── instructionsp3.pdf
└── instructionsp4.pdf
```
Could be combined using the script into:
```
folder
├── folder1
│   ├── notes.pdf
│   └── slides.pdf
├── folder2
│   ├── git.pdf
│   ├── letter.pdf
│   └── python.pdf
└── instructions.pdf
```
The script can also send the old pdf files to the trash and/or run recursively.

#### Requirements:
* Python 3
* [PyPDF2](https://pypi.python.org/pypi/PyPDF2/1.26.0)
  * It can be installed using [pip](https://pypi.python.org/pypi/pip/) with: `pip install PyPDF2`
* [Send2Trash](https://pypi.python.org/pypi/Send2Trash)
  * It can be installed using pip with: `pip install Send2Trash`

#### To Run:
In the folder where the script is located, run:
```
python3 mergepdfs.py /path/to/folder/
```
where /path/to/folder/ is the location of the folder containing the pdfs. The script will prompt the user for decisions on trashing and recursion during runtime.