# NFS Export Management

NFS (Network File System) exports are commonly used by Linux and Unix systems
for shared storage and high-performance workloads.

The File Storage Service supports NFS exports for both Production (PROD) and
Non-Production (NON-PROD) environments.

## Creating an NFS Export

To create an NFS export:

1. Log in to the File Storage Admin Portal.
2. Navigate to **Exports → Create Export**.
3. Select **Protocol: NFS**.
4. Choose the target environment (PROD or NON-PROD).
5. Specify the export path and capacity.
6. Define allowed client IP ranges or CIDRs.
7. Configure export options (read/write, root squash).
8. Submit the request.

Once approved, the export becomes available for mounting.

## Mounting an NFS Export (Linux)

Example mount command:

```bash
mount -t nfs <nfs-server>:/export/path /mnt/data
