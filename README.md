# Parallel NFS with RAID 5 Redundancy

## Summary

This repository contains files relating to the final project in the course [Principles of Computer System Design](https://www.ece.ufl.edu/wp-content/uploads/syllabi/Fall2019/EEL4736_Prin_Comp_Sys_Figueiredo_Fall_2019.pdf). During the first 2 months of the course, each student implemented a Python model of several core features in a UNIX-style filesystem on top of provided basic IO control files. Some features we implemented include an inode layer for storing and retrieving data in data blocks,  an absolute path name layer for resolving filenames, and a filesystem interface that uses lower-level layers to implement common UNIX commands like mkdir, write, read, rm, and mv. Additionally, we implemented a client interface to the filesystem to model a client/server architecture. 

During the last 2 weeks of the class, my team of two students had the following goals for our final project:
- Upgrade the client/server architecture to work with a cluster of 4 servers using **virtual memory**.
- Modify the client stub for **load distribution** across all servers, to minimize response time and avoid overloading of a single component.
- Implement **RAID 5 redundancy** so that corruption of data due to a single server failure could be fully recovered.
- Add a 16-byte **checksum** to the end of a data block, so that the server can check for data decay before returning data to the client.
- Add a back channel that allows users to "destroy" a server or incorrectly modify a piece of stored memory to model data decay. The back channel allows for testing the RAID 5 and checksum features added for the project.

An in-depth report of our final result and the final project prompt can be found in the docs folder or by clicking on the links below.

## Contributors

- Daniel Hamilton [**(@sweatpantsdanny)**](https://github.com/sweatpantsdanny)
- Jacob Crain [**(@Jake16000)**](https://github.com/Jake16000)
