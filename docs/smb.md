# SMB Share Management

SMB (Server Message Block) shares are used primarily for Windows-based workloads
and applications that require integration with Active Directory.

SMB shares can be created in both Production (PROD) and Non-Production (NON-PROD)
environments.

## Creating an SMB Share (PROD)

To create an SMB share in PROD:

1. Log in to the File Storage Admin Portal.
2. Navigate to **Shares → Create Share**.
3. Select **Protocol: SMB**.
4. Choose the appropriate **PROD cluster**.
5. Provide a share name and capacity.
6. Configure access permissions using Active Directory groups.
7. Submit the request for approval.
8. Once approved, the SMB share is provisioned automatically.

## Permissions and Access Control

- SMB shares use Active Directory for authentication.
- Permissions are assigned using AD users or groups.
- Recommended best practice is to use **group-based access** rather than individual users.

## Common Issues

- Access denied errors are usually caused by missing AD group membership.
- Share not visible on Windows systems may indicate DNS or network policy issues.
- Incorrect permissions can result in read-only access.

## Best Practices

- Always request PROD shares with correct capacity planning.
- Follow naming conventions defined by the organization.
- Avoid assigning permissions directly to individual users.

Refer to troubleshooting documentation if access or mount issues persist.