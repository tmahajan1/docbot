# File Storage Service – Overview

The File Storage Service provides managed, highly available file systems
for enterprise workloads running on private, public, and hybrid cloud environments.

The service supports multiple file access protocols to meet different workload needs,
including SMB and NFS. File systems can be created in both Production (PROD) and
Non-Production (NON-PROD) environments and are integrated with enterprise security,
backup, and monitoring systems.

## Supported Protocols

- **SMB (Server Message Block)**
  - Typically used for Windows-based workloads
  - Supports Active Directory integration
  - Provides fine-grained access control

- **NFS (Network File System)**
  - Commonly used for Linux and Unix workloads
  - Optimized for performance and batch workloads
  - Supports multiple NFS versions

## Key Features

- Highly available file systems with replication
- Automated snapshots and backups
- Role-based access control
- Environment isolation between PROD and NON-PROD
- Monitoring and alerting integrations

## Common Use Cases

- Application shared storage
- User home directories
- Data analytics and batch processing
- Lift-and-shift workloads moving to cloud

For protocol-specific details, refer to the SMB and NFS documentation.