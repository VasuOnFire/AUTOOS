#!/bin/bash

# AUTOOS Private Cloud - Secure Deployment Script
# This script deploys AUTOOS with military-grade security

set -e

echo "🛡️  AUTOOS Private Cloud - Secure Deployment"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ helm not found. Please install helm.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Create namespace
echo "📦 Creating secure namespace..."
kubectl apply -f kubernetes/namespace.yaml
echo -e "${GREEN}✅ Namespace created${NC}"
echo ""

# Deploy Vault
echo "🔐 Deploying HashiCorp Vault..."
kubectl apply -f security/vault-config.yaml
echo "⏳ Waiting for Vault pods to be ready..."
kubectl wait --for=condition=ready pod -l app=vault -n autoos-secure --timeout=300s
echo -e "${GREEN}✅ Vault deployed${NC}"
echo ""

# Initialize Vault
echo "🔑 Initializing Vault..."
echo -e "${YELLOW}⚠️  Save the unseal keys and root token securely!${NC}"
kubectl exec -it vault-0 -n autoos-secure -- vault operator init -key-shares=5 -key-threshold=3 > vault-keys.txt
chmod 600 vault-keys.txt
echo -e "${GREEN}✅ Vault initialized (keys saved to vault-keys.txt)${NC}"
echo ""

# Deploy security policies
echo "🔒 Deploying security policies..."
kubectl apply -f security/security-policies.yaml
echo -e "${GREEN}✅ Security policies deployed${NC}"
echo ""

# Deploy network policies
echo "🌐 Deploying network policies..."
kubectl apply -f kubernetes/network-policy.yaml
echo -e "${GREEN}✅ Network policies deployed${NC}"
echo ""

# Deploy encryption config
echo "🔐 Deploying encryption configuration..."
kubectl apply -f security/encryption-config.yaml
echo -e "${GREEN}✅ Encryption configured${NC}"
echo ""

# Deploy WAF
echo "🛡️  Deploying Web Application Firewall..."
kubectl apply -f security/waf-config.yaml
echo "⏳ Waiting for WAF pods to be ready..."
kubectl wait --for=condition=ready pod -l app=waf -n autoos-secure --timeout=300s
echo -e "${GREEN}✅ WAF deployed${NC}"
echo ""

# Deploy IDS/IPS
echo "👁️  Deploying Intrusion Detection/Prevention System..."
kubectl apply -f security/ids-ips-config.yaml
echo "⏳ Waiting for IDS/IPS to be ready..."
sleep 30
echo -e "${GREEN}✅ IDS/IPS deployed${NC}"
echo ""

# Deploy Zero Trust
echo "🔐 Deploying Zero Trust architecture..."
kubectl apply -f security/zero-trust-config.yaml
echo -e "${GREEN}✅ Zero Trust configured${NC}"
echo ""

# Deploy DDoS protection
echo "🛡️  Deploying DDoS protection..."
kubectl apply -f security/ddos-protection.yaml
echo -e "${GREEN}✅ DDoS protection deployed${NC}"
echo ""

# Deploy security monitoring
echo "📊 Deploying security monitoring..."
kubectl apply -f ../monitoring/security-monitoring.yaml
echo "⏳ Waiting for monitoring to be ready..."
sleep 30
echo -e "${GREEN}✅ Security monitoring deployed${NC}"
echo ""

# Deploy AUTOOS application
echo "🚀 Deploying AUTOOS application..."
kubectl apply -f deployment/secure-deployment.yaml
echo "⏳ Waiting for AUTOOS pods to be ready..."
kubectl wait --for=condition=ready pod -l app=autoos-api -n autoos-secure --timeout=300s
echo -e "${GREEN}✅ AUTOOS deployed${NC}"
echo ""

# Verify deployment
echo "🔍 Verifying deployment..."
echo ""
echo "Pods:"
kubectl get pods -n autoos-secure
echo ""
echo "Services:"
kubectl get svc -n autoos-secure
echo ""
echo "Network Policies:"
kubectl get networkpolicy -n autoos-secure
echo ""

# Security checks
echo "🔒 Running security checks..."
echo ""

# Check pod security
echo "Checking pod security policies..."
INSECURE_PODS=$(kubectl get pods -n autoos-secure -o json | jq -r '.items[] | select(.spec.securityContext.runAsNonRoot != true) | .metadata.name')
if [ -z "$INSECURE_PODS" ]; then
    echo -e "${GREEN}✅ All pods run as non-root${NC}"
else
    echo -e "${RED}❌ Insecure pods found: $INSECURE_PODS${NC}"
fi

# Check read-only filesystem
echo "Checking read-only filesystems..."
WRITABLE_PODS=$(kubectl get pods -n autoos-secure -o json | jq -r '.items[] | select(.spec.containers[].securityContext.readOnlyRootFilesystem != true) | .metadata.name')
if [ -z "$WRITABLE_PODS" ]; then
    echo -e "${GREEN}✅ All pods have read-only root filesystem${NC}"
else
    echo -e "${YELLOW}⚠️  Pods with writable filesystem: $WRITABLE_PODS${NC}"
fi

# Check privilege escalation
echo "Checking privilege escalation..."
PRIVILEGED_PODS=$(kubectl get pods -n autoos-secure -o json | jq -r '.items[] | select(.spec.containers[].securityContext.allowPrivilegeEscalation == true) | .metadata.name')
if [ -z "$PRIVILEGED_PODS" ]; then
    echo -e "${GREEN}✅ No pods allow privilege escalation${NC}"
else
    echo -e "${RED}❌ Privileged pods found: $PRIVILEGED_PODS${NC}"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}🎉 AUTOOS Private Cloud Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo "📝 Next Steps:"
echo "1. Configure DNS to point to the load balancer"
echo "2. Set up SSL certificates"
echo "3. Configure Vault policies and secrets"
echo "4. Set up monitoring dashboards"
echo "5. Configure backup and disaster recovery"
echo ""
echo "📚 Documentation:"
echo "- Security: PRIVATE_CLOUD_SECURITY.md"
echo "- Vault Keys: vault-keys.txt (KEEP SECURE!)"
echo ""
echo "🔐 Access:"
echo "- API: https://autoos.secure/api"
echo "- Vault: https://vault.autoos-secure.svc.cluster.local:8200"
echo "- Grafana: kubectl port-forward -n autoos-secure svc/grafana 3000:3000"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Secure the vault-keys.txt file immediately!${NC}"
echo ""
