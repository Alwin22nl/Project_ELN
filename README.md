[Project LIMSELN.txt](https://github.com/user-attachments/files/30976133/Project.LIMSELN.txt)
Project LIMS/ELN

Goal of v1.0: 
the Goal of V1 is to replace the excel-based lab records with a minimal structured system for managing samples, results and raw materials.

*In scope V1.0*:
authentication and authorisation:
	- user login using user_id and password
 	- role based accescontroll (eg researcher/admin)
	- permission enforced at API level

User:
	- create and manage users (basic)
	- assign roles and permissions

Samples:
	- Register samples
	- link sample to experiment results
	- add tekst notes to sample

Test Results:
	- Register test results per sample
	- store measured values, units and timestamps
	- multiple results per sample supported

Raw materials
	- register raw materials
	- track current stock quantities
	- store SDS document reference
	- store physical storage location 

*out of scope (for V1)*	
	-audit trails and change history
	- electronic signatures
	- regulatory complience
	- advanced reporting statistics
	- automated stock consumption based on experiments
	- external system intergrations

*Assumptions and Simplifications
	- single lab environment
	- limited number of users
	- no regulatory validation needed
	- basic UI, focus on backend functionality

