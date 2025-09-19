# E-Commerce Platform

A comprehensive Django-based e-commerce platform featuring product management, location-based services, user authentication with Django AllAuth, Stripe payments, and interactive maps using Leaflet.

## Features

- **User Management**: Custom user profiles with seller capabilities, ratings, and location tracking
- **Product Management**: Categories, products with images, ratings, discounts, and condition tracking
- **Location Services**: Store locations, user location history, and geolocation features
- **Marketplace**: Buy/sell functionality with marketplace integration
- **Payment Integration**: Stripe payment processing
- **Interactive Maps**: Leaflet-based maps for location visualization
- **Responsive Design**: Bootstrap 5 styling with Crispy Forms
- **Authentication**: Django AllAuth with email verification

## Tech Stack

- **Backend**: Django 4.2.10
- **Database**: PostgreSQL (SQLite for development)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Maps**: Leaflet, Django-GeoJSON
- **Payments**: Stripe
- **Authentication**: Django AllAuth
- **Forms**: Django Crispy Forms

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite works for development)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ecom.git
   cd ecom
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=postgresql://user:password@localhost:5432/ecom  # Or use SQLite
   STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-email-password
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000` in your browser.

## Usage

- Access the admin panel at `/admin/` using superuser credentials
- Register as a user or seller
- Add products with images and location data
- Browse products by category
- Use the interactive map to find nearby products/stores
- Process payments through Stripe integration

## Configuration

### Database

The project is configured to use SQLite by default. To use PostgreSQL:

1. Install PostgreSQL
2. Create a database
3. Update `DATABASES` in `ecom/settings.py` or use `DATABASE_URL` in `.env`

### Stripe

1. Create a Stripe account
2. Get your publishable and secret keys
3. Add them to your `.env` file

### Email

Configure email settings in `.env` for user verification and notifications.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.# Ecom_Mgt
