# AUTOOS Omega 🚀

**The Next-Generation AI Operating System**

AUTOOS Omega is a revolutionary autonomous AI operating system that orchestrates intelligent agents to execute complex workflows through natural language intent. Built with enterprise-grade security, scalability, and a beautiful modern UI.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

## 🌟 Features

### Core Capabilities
- **Natural Language Intent Processing** - Describe what you want in plain English
- **Autonomous Agent Orchestration** - Multi-agent collaboration with specialized roles
- **Intelligent Workflow Management** - Automatic planning, execution, and verification
- **Real-time Monitoring** - Live metrics, agent status, and workflow tracking
- **Enterprise Security** - JWT authentication, MFA, role-based access control

### Advanced Features
- **Multi-Agent Swarms** - Collaborative agents with specialized capabilities
- **Predictive Intelligence** - ML-powered workflow optimization
- **Context Synthesis** - Advanced memory and learning systems
- **Adversarial Testing** - Built-in security and reliability testing
- **Meta-Learning** - Self-improving agent capabilities

### Authentication & Payment
- **Complete Auth System** - Sign up, sign in, MFA, OAuth, password reset
- **Free Trial** - 30 days, 10 workflows, 2 agents, no credit card required
- **Flexible Pricing** - Student, Employee, Professional, Enterprise tiers
- **Multiple Payment Methods** - Stripe integration + QR code payments (UPI)
- **Subscription Management** - Upgrade, downgrade, cancel anytime

## 🏗️ Architecture

```
AUTOOS Omega
├── Backend (FastAPI + Python)
│   ├── Intent Processing
│   ├── Agent Orchestration
│   ├── Workflow Management
│   ├── Authentication & Authorization
│   ├── Payment Processing
│   └── Real-time Metrics
│
├── Frontend (Next.js + React + TypeScript)
│   ├── Modern UI with Framer Motion
│   ├── Real-time Dashboard
│   ├── Agent Team Visualization
│   ├── Auth Components
│   └── Payment Components
│
└── Infrastructure
    ├── PostgreSQL Database
    ├── Redis Cache
    ├── Prometheus Metrics
    └── Docker Compose
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### 1. Clone the Repository
```bash
git clone https://github.com/VasuOnFire/autoos-omega.git
cd autoos-omega
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/init-db.sql

# Run backend
uvicorn src.autoos.intent.api:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend/web

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Run frontend
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🚂 Deploy to Railway

1. Click the "Deploy on Railway" button above
2. Connect your GitHub repository
3. Set environment variables:
   - `DATABASE_URL` (PostgreSQL)
   - `REDIS_URL`
   - `JWT_SECRET_KEY`
   - `STRIPE_SECRET_KEY` (optional)
   - `OPENAI_API_KEY`
4. Deploy!

Railway will automatically:
- Build and deploy the backend
- Build and deploy the frontend
- Set up PostgreSQL and Redis
- Configure networking

## 📚 Documentation

- [Complete Architecture](COMPLETE_ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Security Implementation](SECURITY_IMPLEMENTATION_COMPLETE.md)
- [Payment Integration](PAYMENT_INTEGRATION_GUIDE.md)
- [Agent Capabilities](AGENT_CAPABILITIES.md)
- [API Documentation](http://localhost:8000/docs)

## 🔐 Security Features

- JWT-based authentication with refresh tokens
- Multi-factor authentication (TOTP)
- Role-based access control (RBAC)
- Subscription-based feature gating
- Rate limiting and DDoS protection
- Encrypted data at rest and in transit
- OAuth integration (Google, GitHub)
- Email verification
- Password reset with secure tokens

## 💳 Pricing Tiers

| Tier | Price | Workflows | Agents | Storage |
|------|-------|-----------|--------|---------|
| **Free Trial** | $0 | 10/month | 2 | 1GB |
| **Student** | $9/mo | 50/month | 5 | 5GB |
| **Employee** | $29/mo | 200/month | 10 | 20GB |
| **Professional** | $99/mo | 1000/month | 50 | 100GB |
| **Enterprise** | Custom | Unlimited | Unlimited | Unlimited |

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Stripe** - Payment processing
- **OpenAI** - LLM integration

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Zustand** - State management
- **React Query** - Data fetching
- **Recharts** - Data visualization

### Infrastructure
- **Docker** - Containerization
- **Prometheus** - Metrics
- **PostgreSQL** - Database
- **Redis** - Cache
- **Nginx** - Reverse proxy

## 📊 System Metrics

- Real-time workflow success rate
- Agent utilization tracking
- LLM latency monitoring
- Cost per workflow analysis
- Active agent count
- Total workflow statistics

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Vasu** - [@VasuOnFire](https://github.com/VasuOnFire)

## 🙏 Acknowledgments

- OpenAI for GPT models
- FastAPI team for the amazing framework
- Next.js team for the React framework
- All open-source contributors

## 📧 Support

For support, email support@autoos.ai or open an issue on GitHub.

---

**Built with ❤️ by Vasu**

⭐ Star this repo if you find it useful!
