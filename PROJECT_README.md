# QuickPost - Django Ninja API

A modern, high-performance blog API built with Django Ninja, featuring user authentication, posts, comments, and real-time interactions.

## 📖 About This Project

This project is part of the book **"Django Ninja In Action"** - a comprehensive guide to building modern APIs with Django Ninja.

## ✨ Features

### 🔐 Authentication & User Management
- User registration with email verification
- JWT-based authentication (access & refresh tokens)
- Google OAuth integration
- Password reset with OTP verification
- Profile management with avatar upload
- Multi-device logout support

### 📝 Blog Functionality
- Create, read, update, delete posts
- Image upload for posts
- Auto-generated slugs for SEO-friendly URLs
- Post filtering and pagination

### 💬 Interactive Comments System
- Hierarchical comments (replies to comments)
- Like/dislike system for posts and comments
- Real-time engagement tracking
- Pagination for comments and replies

### 🛠️ Technical Features
- **Django Ninja** for fast, modern API development
- **Async/await** support for better performance
- **PostgreSQL** database with optimized queries
- **Cloudinary** integration for media storage
- **Docker** containerization
- **Comprehensive test suite** with pytest

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kayprogrammer/quickpost.git
   cd quickpost
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # OR using make
   make req
   ```

3. **Environment Setup**
   Create a `.env` file with the necessary values as stated in .env.example:
   ```env
   DJANGO_SETTINGS_MODULE=quickpost.settings.dev
   ...
   ```

4. **Database Setup**
   ```bash
   python manage.py migrate
   # OR using make
   make mig
   
   python manage.py createsuperuser
   # OR using make
   make suser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   # OR using uvicorn with make
   make run
   ```

### 🐳 Docker Setup

```bash
docker-compose up -d
# OR using make
make up

# Build and run (first time)
docker-compose up --build -d
# OR using make
make build
```

## 🔧 Make Commands

This project includes convenient Make commands for common tasks:

```bash
make req          # Install requirements
make mig          # Run migrations
make mmig         # Make migrations (add app='app_name' for specific app)
make suser        # Create superuser
make run          # Run development server with uvicorn
make shell        # Django shell
make test         # Run tests
make up           # Start Docker containers
make build        # Build and start Docker containers
make down         # Stop Docker containers
make show-logs    # Show Docker logs
```

## 📚 API Documentation

Once running, visit:
- **Interactive API Docs**: `http://localhost:8000/`
- **Admin Interface**: `http://localhost:8000/admin/`

## 🏗️ Project Structure

```
quickpost/
├── apps/
│   ├── accounts/          # User authentication & profiles
│   ├── blog/             # Posts, comments, likes
│   ├── common/           # Shared utilities & base models
│   └── api.py           # Main API router configuration
├── quickpost/
│   ├── settings/        # Environment-specific settings
│   └── urls.py         # URL configuration
├── templates/          # Email templates
├── static/            # Static files
└── docker-compose.yml # Docker configuration
```

## 🧪 Testing

Run the test suite:

```bash
pytest
# OR using make
make test
```

Run with coverage:
```bash
pytest --cov=apps
```

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/google-login` - Google OAuth
- `POST /api/v1/auth/refresh` - Refresh tokens
- `GET /api/v1/auth/logout` - Logout current device
- `GET /api/v1/auth/logout-all` - Logout all devices

### Profiles
- `GET /api/v1/profiles` - Get user profile
- `PUT /api/v1/profiles` - Update profile

### Blog
- `GET /api/v1/blog/posts` - List posts (with pagination & filters)
- `POST /api/v1/blog/posts` - Create post
- `GET /api/v1/blog/posts/{slug}` - Get single post
- `PUT /api/v1/blog/posts/{slug}` - Update post
- `DELETE /api/v1/blog/posts/{slug}` - Delete post

### Comments & Replies
- `GET /api/v1/blog/posts/{slug}/comments` - Get comments
- `POST /api/v1/blog/posts/{slug}/comments` - Create comment
- `GET /api/v1/blog/comments/{id}/replies` - Get replies
- `POST /api/v1/blog/comments/{id}/replies` - Create reply

### Likes/Dislikes
- `GET /api/v1/blog/likes/{obj_id}/toggle` - Toggle like/dislike

## 🛠️ Technologies Used

- **Backend**: Django 5.2, Django Ninja 1.4
- **Database**: PostgreSQL with async support
- **Authentication**: JWT tokens, Google OAuth
- **Media Storage**: Cloudinary
- **Email**: SMTP with HTML templates
- **Testing**: pytest, pytest-django
- **Containerization**: Docker & Docker Compose
- **Code Quality**: Black formatting, Type hints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📚 Learn More

This project demonstrates the concepts covered in **"Django Ninja In Action"**. The book provides detailed explanations of:

- Building high-performance APIs with Django Ninja
- Implementing async/await patterns in Django
- JWT authentication strategies
- API design best practices
- Testing modern Django applications
- Production deployment techniques

## 🙋‍♂️ Support

If you have questions about this project or the book, feel free to:
- Open an issue in this repository
- Contact the author through the book's website

---

**Happy coding!** 🚀