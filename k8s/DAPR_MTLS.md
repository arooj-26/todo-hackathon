# Dapr mTLS Configuration

This document explains the mTLS (mutual TLS) configuration for Dapr service-to-service communication.

## Overview

mTLS provides:
- **Encryption**: All service-to-service traffic is encrypted
- **Mutual Authentication**: Both client and server verify each other's identity
- **Zero Trust**: Services authenticate every request
- **Automatic Certificate Management**: Dapr handles certificate rotation

## Configuration

mTLS is enabled in `k8s/dapr-components.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: todo-app
spec:
  mtls:
    enabled: true
    workloadCertTTL: "24h"          # Certificate lifetime
    allowedClockSkew: "15m"         # Clock skew tolerance
```

## Settings

- **enabled: true** - Enables mTLS for all Dapr sidecars
- **workloadCertTTL: "24h"** - Certificates are valid for 24 hours and auto-rotated
- **allowedClockSkew: "15m"** - Allows 15 minutes of clock drift between services

## How It Works

1. **Certificate Authority**: Dapr creates a root CA in the namespace
2. **Certificate Issuance**: Each Dapr sidecar gets a unique certificate
3. **Automatic Rotation**: Certificates are rotated before expiry
4. **Mutual Verification**: Every service-to-service call verifies certificates

## Verification

### Check mTLS is Enabled

```bash
# Check Dapr configuration
kubectl get configuration -n todo-app dapr-config -o yaml | grep -A 3 mtls

# Expected output:
# mtls:
#   enabled: true
#   workloadCertTTL: "24h"
#   allowedClockSkew: "15m"
```

### Verify Certificates

```bash
# Check if Dapr sentry (CA) is running
kubectl get pods -n dapr-system | grep dapr-sentry

# View certificate details from a Dapr sidecar
kubectl exec -n todo-app <pod-name> -c daprd -- \
  ls -la /var/run/secrets/dapr.io/tls/

# Should show:
# ca.crt  (CA certificate)
# issuer.crt  (Issuer certificate)
# cert.pem  (Service certificate)
# key.pem  (Private key)
```

### Test Encrypted Communication

```bash
# Capture traffic between Dapr sidecars
kubectl exec -n todo-app <chat-api-pod> -c daprd -- \
  netstat -an | grep 3500

# mTLS traffic should show TLS connections
# You can use tcpdump to verify encrypted traffic
```

## Certificate Rotation

Certificates are automatically rotated by Dapr:

1. New certificate issued when 70% of TTL expires (16.8 hours for 24h TTL)
2. Old certificate remains valid until expiry
3. No downtime during rotation
4. No manual intervention required

Monitor rotation:

```bash
# View Dapr sentry logs for certificate issuance
kubectl logs -n dapr-system -l app=dapr-sentry --tail=100 | grep -i cert
```

## Security Benefits

### Without mTLS
- Traffic unencrypted (visible via network sniffing)
- No service authentication
- Man-in-the-middle attacks possible
- Compromised pod can impersonate any service

### With mTLS
- All traffic encrypted (TLS 1.2+)
- Strong mutual authentication
- Man-in-the-middle attacks prevented
- Certificate-based service identity

## Troubleshooting

### Services Cannot Communicate

If mTLS is misconfigured:

```bash
# Check Dapr sidecar logs
kubectl logs -n todo-app <pod-name> -c daprd | grep -i tls

# Common issues:
# - "certificate verify failed" -> Clock skew or expired cert
# - "connection refused" -> Dapr sidecar not ready
# - "tls handshake timeout" -> Network policy blocking traffic
```

### Certificate Errors

```bash
# Check certificate expiry
kubectl exec -n todo-app <pod-name> -c daprd -- \
  openssl x509 -in /var/run/secrets/dapr.io/tls/cert.pem -noout -dates

# Force certificate rotation (restart pod)
kubectl delete pod -n todo-app <pod-name>
```

### Clock Skew Issues

If services have clock drift > 15 minutes:

```bash
# Check pod time
kubectl exec -n todo-app <pod-name> -- date

# Sync cluster time (if needed)
# This varies by cluster provider
```

## Disabling mTLS (Not Recommended)

Only disable for troubleshooting:

```yaml
spec:
  mtls:
    enabled: false
```

Apply changes:

```bash
kubectl apply -f k8s/dapr-components.yaml
kubectl rollout restart deployment -n todo-app
```

## Performance Impact

mTLS has minimal performance overhead:
- **Latency**: +1-3ms per request (TLS handshake)
- **CPU**: +5-10% (encryption/decryption)
- **Memory**: +10-20MB per sidecar (certificate storage)

Benefits outweigh costs in production environments.

## Best Practices

1. **Always enable mTLS in production**
2. **Monitor certificate rotation** via Dapr sentry logs
3. **Set appropriate TTL** (24h is recommended)
4. **Sync cluster time** to avoid clock skew
5. **Test with mTLS enabled** in staging before production

## Compliance

mTLS helps meet security requirements:
- **PCI-DSS**: Encryption of cardholder data in transit
- **HIPAA**: Encryption of ePHI in transmission
- **SOC 2**: Encryption and authentication controls
- **GDPR**: Security of processing (encryption)

## References

- [Dapr mTLS](https://docs.dapr.io/operations/security/mtls/)
- [Dapr Security](https://docs.dapr.io/concepts/security-concept/)
- [Certificate Management](https://docs.dapr.io/operations/security/mtls/)
