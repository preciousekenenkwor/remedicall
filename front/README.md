<img width="959" alt="image" src="https://github.com/user-attachments/assets/ee229a9e-6203-4395-ad12-3241dbdd5066" />

# 💊 MediGuard - Smart Medication Management Platform

A comprehensive digital health platform designed to help users maintain consistent medication schedules and improve treatment adherence through intelligent reminders and tracking.

## 🌟 Features

### Core Functionality

- **Smart Medication Scheduling** - Set up complex dosing schedules with custom intervals
- **Intelligent Reminders** - Push notifications, email alerts, and SMS reminders
- **Medication Tracking** - Visual progress tracking and adherence analytics
- **Drug Information Database** - Comprehensive medication details and interactions
- **Prescription Management** - Upload and manage prescriptions digitally
- **Refill Alerts** - Automatic notifications when medications are running low

### Advanced Features

- **Multi-User Support** - Caregivers can manage medications for family members
- **Healthcare Provider Dashboard** - Monitor patient adherence remotely
- **Interaction Checker** - Alerts for potential drug interactions
- **Side Effect Tracking** - Log and monitor adverse reactions
- **Medication History** - Complete timeline of medication usage
- **Export Reports** - Generate adherence reports for healthcare visits

## 🏗️ Technology Stack

### Frontend

- **TypeScript** - Type-safe JavaScript development
- **React** - Modern component-based UI framework
- **Tailwind CSS** - Utility-first styling
- **PWA Support** - Offline functionality and native app experience
- **Push Notifications** - Web push API for reminders

### Backend

- **FastAPI** - High-performance Python web framework
- **UV** - Ultra-fast Python package installer and resolver
- **PostgreSQL** - Robust relational database
- **Redis** - In-memory caching and session management
- **Celery** - Distributed task queue for notifications
- **JWT Authentication** - Secure user authentication

### DevOps & Infrastructure

- **Docker** - Containerized deployment
- **GitHub Actions** - CI/CD pipeline
- **Nginx** - Reverse proxy and static file serving
- **SSL/TLS** - End-to-end encryption

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **UV** package manager
- **PostgreSQL** 14+
- **Redis** 6+

### Frontend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/mediguard.git
cd mediguard

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev

# For production build
npm run build
npm start
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment using UV
uv venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate     # On Windows

# Install dependencies with UV (blazing fast!)
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Configure your database, Redis, and API keys

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# For production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
mediguard/
├── frontend/                 # TypeScript React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   ├── types/          # TypeScript type definitions
│   │   ├── utils/          # Utility functions
│   │   └── store/          # State management
│   ├── public/             # Static assets
│   └── package.json
├── backend/                 # FastAPI Python application
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database models and migrations
│   │   ├── services/       # Business logic services
│   │   ├── schemas/        # Pydantic models
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── main.py            # Application entry point
├── docker-compose.yml      # Development environment
├── .github/workflows/      # CI/CD pipelines
└── README.md
```

## 🔧 Configuration

### Environment Variables

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_vapid_public_key
NEXT_PUBLIC_FIREBASE_CONFIG=your_firebase_config
```

#### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@localhost/mediguard
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_super_secret_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🧪 Testing

### Frontend Tests

```bash
cd frontend
npm run test              # Run unit tests
npm run test:e2e         # Run end-to-end tests
npm run test:coverage    # Generate coverage report
```

### Backend Tests

```bash
cd backend
pytest                   # Run all tests
pytest --cov=app        # Run with coverage
pytest -v tests/        # Verbose test output
```

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up --build

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up --scale backend=3
```

## 📊 API Documentation

Once the backend is running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## 🔐 Security Features

- **Data Encryption** - All sensitive data encrypted at rest
- **HIPAA Compliance** - Healthcare data protection standards
- **Rate Limiting** - API endpoint protection
- **Input Validation** - Comprehensive request validation
- **Audit Logging** - Complete activity tracking

## 🚀 Performance Optimizations

- **UV Package Manager** - 10-100x faster Python package installation
- **TypeScript** - Compile-time error detection and better IDE support
- **Database Indexing** - Optimized query performance
- **Redis Caching** - Reduced database load
- **CDN Integration** - Fast static asset delivery
- **Image Optimization** - Automatic image compression and WebP conversion

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Write comprehensive tests
- Update documentation
- Follow conventional commit messages
- Ensure code passes all linting checks

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.mediguard.com](https://docs.mediguard.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/mediguard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mediguard/discussions)
- **Email**: <support@mediguard.com>

## 🗺️ Roadmap

- [ ] **Mobile App** - Native iOS and Android applications
- [ ] **Wearable Integration** - Apple Watch and Fitbit support
- [ ] **AI-Powered Insights** - Personalized medication recommendations
- [ ] **Telemedicine Integration** - Connect with healthcare providers
- [ ] **Pharmacy Integration** - Direct prescription refill ordering
- [ ] **Multi-language Support** - Internationalization

## 🏆 Acknowledgments

- Healthcare professionals who provided domain expertise
- Open source community for amazing tools and libraries
- Beta testers who helped refine the user experience

---

**Made with ❤️ for better health outcomes**
