# Kubernetes Network Policies

Network policies implement least-privilege access for the Todo Application.

## Quick Start

Apply network policies:
```bash
kubectl apply -f k8s/network-policies.yaml
```

Verify:
```bash
kubectl get networkpolicies -n todo-app
```

## Policy Overview

- **default-deny-ingress**: Denies all ingress by default
- **postgres-netpol**: PostgreSQL access from authorized services only
- **kafka-netpol**: Kafka access from publishers/subscribers only
- **chat-api-netpol**: Chat API ingress/egress rules
- **frontend-netpol**: Frontend access rules
- **recurring-tasks-netpol**: Recurring tasks service rules
- **notifications-netpol**: Notifications service rules
- **audit-netpol**: Audit service rules

## Testing

Test default deny:
```bash
kubectl run -n todo-app test-pod --image=busybox --rm -it -- nc -zv postgres 5432
# Should fail
```

Test allowed access from Chat API:
```bash
kubectl exec -n todo-app -l app=chat-api -- nc -zv postgres 5432
# Should succeed
```

## Security Benefits

1. Prevents lateral movement between pods
2. Reduces attack surface
3. Enforces least-privilege access
4. Meets compliance requirements (PCI-DSS, HIPAA)

## Prerequisites

Requires a CNI plugin that supports Network Policies:
- Calico
- Cilium
- Weave Net

For Minikube:
```bash
minikube start --network-plugin=cni --cni=calico
```

## Troubleshooting

If pods cannot communicate:
1. Check pod labels match policy selectors
2. Verify policy allows the specific port
3. Check Dapr sidecar ports (3500, 50001)
4. Ensure DNS egress rules are present

Temporarily disable for debugging:
```bash
kubectl delete networkpolicy default-deny-ingress -n todo-app
```

## References

- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Network Policy Recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes)
