# Fault Injection Simulator

For our Master Qualifying Project at WPI, we created an application to automate fault injection when there is a glitch. to collect information on a low level. This enabled us to then see if glitching would occur and the registers stay the same.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Files
* gui.py
  * main function to run
* gui.tcl
  * program to open with PAGE
* backend.py
  * helper file for backend functions
* Import Documents
  * .XML and .C Files

### Installations

```
install untangle
```

## Running the Application

$ python gui.py

### Running the Fault Injection Simulator

```
1. Open XML File located in xml_documents directory
```
```
2. Open C File located in c_documents directory
```
```
3. Press Enter Button
```

## Built With

* [PAGE]() - gui development
* [Sublime 2]() - text editor
* [Ubuntu]() - operating system
* [ChipWhisperer]() - information from chips to feed into the application

## History v1.x

### Version 1.1
* Upload C file
* seperated GUI and Backend
* Output on GDB from C file
* Update User Interface

### Version 1.0
* User Interface
* Title, Open Buttons
* XML Table, Registers, GDB Output, Breakpoints
* Open XML insert into table and prints file name

## Tasks
- [x] Complete GUI Layout
- [x] Import XML file onto XML table
- [x] Import C file onto "GDB Output"
- [x] Seperate into Frontend and Backend
- [x] Connect button when both XML and C files are present with connect button
- [ ] Enter button working
- [ ] Registers printed
- [ ] Ready for Claypool (Thursday)
- [ ] Ready for Vincent and Andrew (Monday)
- [ ] Valid information for testing

- [ ] Task

## Authors

Jon Metzger
Himanjal Sharma
Maryann O'Connell

## License

This project was completed under WPI and NVIDIA and cannot be used without permission from the authors.

## Acknowledgments

* NVIDIA - Vincent Chen and Andrew Tran
* WPI - Professor Claypool
* Oakwood Apartments

Template taken from: https://gist.github.com/PurpleBooth/109311bb0361f32d87a2#file-readme-template-md

