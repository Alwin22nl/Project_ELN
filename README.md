[Project LIMSELN.txt](https://github.com/user-attachments/files/30976133/Project.LIMSELN.txt)
Project LIMS/ELN

Goal of v1.0: 
the Goal of V1 is to replace the excel-based lab records for quality control for a basic data management system to record and display the results.

*In scope V1.0*:
authentication and authorisation:
	- user login using user_id and password

User:
	- create and manage users (basic)
	- electronic signatures for tests

Samples:
	- Register samples
	- link samples to products

Test Results:
	- Register test results per sample
	- store measured values, units, timestamps and users.
	- multiple test results per sample supported

Display results: 
	- dislpay results per product group
	- Filter by batch_number and date
	- search batchnumber to get more detailed results

*out of scope (for V1)*	
	-audit trails and change history
	- regulatory complience
	- advanced reporting statistics
	- external system intergrations

*Assumptions and Simplifications
	- single lab environment
	- limited number of users
	- no regulatory validation needed
	- basic UI, focus on backend functionality

