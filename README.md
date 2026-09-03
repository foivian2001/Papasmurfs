# Papasmurfs

Papasmurfs is a Django-based gaming boosting marketplace developed for the Internet Programming final project.

The website allows users to browse rank and level boosting services for several games, filter and search packages, create an account, use a shopping cart, complete a simulated checkout, review completed purchases and receive package recommendations.

The project also includes a custom staff control panel for managing the catalogue, users and customer orders.

## Live Project

Live website:

https://papasmurfs.onrender.com

GitHub repository:

https://github.com/foivian2001/Papasmurfs


## Main Features

### Catalogue

The service catalogue currently contains four games:

- League of Legends
- Counter-Strike 2
- Fortnite
- GTA Online

The catalogue contains five service categories, 73 progression ranks and 365 generated boost packages.

Users can filter packages by:

- Game
- Service category
- Current rank
- Target rank
- Maximum price
- Maximum completion time

Packages can also be sorted by price, completion time, target rank or recommended order.

Featured and inactive packages are also supported.


### Advanced Search

The project includes a separate advanced search feature.

Users can combine keyword searching with catalogue filters to find matching services.


### User Accounts

Users can:

- Register
- Log in and log out
- Edit their profile
- Access their personal dashboard
- View their order history
- Use the shopping cart
- Submit reviews for eligible purchases


### Shopping Cart and Checkout

Authenticated users can:

- Add packages to their cart
- Update quantities
- Remove items
- Review the cart total
- Complete a simulated card transaction

No real payments are processed and card details are not stored.

For testing the simulated checkout:

Approved test card:

`4242424242424242`

Declined test card:

`4000000000000002`

Use a future expiry date in `YYYY-MM` format and any valid three-digit CVV.


### Orders

Successful simulated transactions create an Order and OrderItem records.

Order items preserve a snapshot of important package information including:

- Package name
- Game
- Category
- Current rank
- Target rank
- Unit price
- Quantity


### Reviews

Reviews use AJAX for submission and updating.

A user may review a package only if that user has purchased the package through an order whose status has been marked as Completed.

This restriction is checked on the server as well as in the user interface.


### Recommendations

The recommendation feature uses user activity and catalogue information to suggest relevant boosting packages.


### Custom Staff Control Panel

The project uses a custom in-site control panel rather than relying on the Django administration interface for normal project management.

Staff users can manage:

- Games
- Categories
- Ranks
- Packages
- Users
- Orders

Order management includes:

- Order search
- Status filtering
- Order details
- Completed status
- Cancelled status

Control panel pages are restricted to staff users.


## Security

The project uses Django's built-in security mechanisms including:

- Password hashing
- CSRF protection
- Template escaping
- Authentication checks
- Staff authorization
- Object ownership checks
- POST-only destructive actions
- Django ORM queries instead of raw SQL

Normal users cannot access staff control panel pages.


## Technologies

The project uses:

- Python
- Django 5.2
- HTML
- CSS
- Bootstrap
- JavaScript
- SQLite for local development
- PostgreSQL in production
- Cloudinary for production media
- WhiteNoise for static files
- Gunicorn
- Render


## Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/foivian2001/Papasmurfs.git
cd Papasmurfs
