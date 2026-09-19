SAKILA_CONTEXT = """
DATABASE: sakila
DIALECT: MySQL

The Sakila database represents a DVD rental business.

TABLE: actor
Purpose: Actors who appear in films.
Columns:
- actor_id [PK]
- first_name
- last_name
- last_update

TABLE: address
Purpose: Addresses used by customers, staff and stores.
Columns:
- address_id [PK]
- address
- address2
- district
- city_id [FK -> city.city_id]
- postal_code
- phone
- location
- last_update

TABLE: category
Purpose: Film categories such as Action, Comedy, Drama, etc.
Columns:
- category_id [PK]
- name
- last_update

TABLE: city
Purpose: Cities associated with addresses.
Columns:
- city_id [PK]
- city
- country_id [FK -> country.country_id]
- last_update

TABLE: country
Purpose: Countries associated with cities.
Columns:
- country_id [PK]
- country
- last_update

TABLE: customer
Purpose: Customers who rent films.
Columns:
- customer_id [PK]
- store_id [FK -> store.store_id]
- first_name
- last_name
- email
- address_id [FK -> address.address_id]
- active
- create_date
- last_update

TABLE: film
Purpose: Films available in the DVD rental business.
Columns:
- film_id [PK]
- title
- description
- release_year
- language_id [FK -> language.language_id]
- original_language_id [FK -> language.language_id]
- rental_duration
- rental_rate
- length
- replacement_cost
- rating
- special_features
- last_update

TABLE: film_actor
Purpose: Many-to-many relationship between films and actors.
Columns:
- actor_id [PK, FK -> actor.actor_id]
- film_id [PK, FK -> film.film_id]
- last_update

TABLE: film_category
Purpose: Many-to-many relationship between films and categories.
Columns:
- film_id [PK, FK -> film.film_id]
- category_id [PK, FK -> category.category_id]
- last_update

TABLE: film_text
Purpose: Full-text-search copy of film titles and descriptions.
Columns:
- film_id [PK]
- title
- description
Note:
- Normally use the film table for film information.
- film_text is maintained from film and is mainly intended for full-text search.

TABLE: inventory
Purpose: Physical copies of films held by individual stores.
Columns:
- inventory_id [PK]
- film_id [FK -> film.film_id]
- store_id [FK -> store.store_id]
- last_update

TABLE: language
Purpose: Languages associated with films.
Columns:
- language_id [PK]
- name
- last_update

TABLE: payment
Purpose: Payments made by customers.
Columns:
- payment_id [PK]
- customer_id [FK -> customer.customer_id]
- staff_id [FK -> staff.staff_id]
- rental_id [FK -> rental.rental_id]
- amount
- payment_date
- last_update

TABLE: rental
Purpose: Individual film rental transactions.
Columns:
- rental_id [PK]
- rental_date
- inventory_id [FK -> inventory.inventory_id]
- customer_id [FK -> customer.customer_id]
- return_date
- staff_id [FK -> staff.staff_id]
- last_update

TABLE: staff
Purpose: Employees who process rentals and payments.
Columns:
- staff_id [PK]
- first_name
- last_name
- address_id [FK -> address.address_id]
- picture
- email
- store_id [FK -> store.store_id]
- active
- username
- password
- last_update

TABLE: store
Purpose: DVD rental stores.
Columns:
- store_id [PK]
- manager_staff_id [FK -> staff.staff_id]
- address_id [FK -> address.address_id]
- last_update


IMPORTANT RELATIONSHIPS:

Actor to Film:
actor
-> film_actor
-> film

Film to Category:
film
-> film_category
-> category

Film to Rental:
film
-> inventory
-> rental

Customer to Rental:
customer
-> rental

Customer to Payment:
customer
-> payment

Rental to Payment:
rental
-> payment

Store to Inventory:
store
-> inventory

Customer Location:
customer
-> address
-> city
-> country

Store Location:
store
-> address
-> city
-> country

Staff Location:
staff
-> address
-> city
-> country

Typical path for determining which films a customer rented:
customer
-> rental
-> inventory
-> film

Typical path for determining categories rented by a customer:
customer
-> rental
-> inventory
-> film
-> film_category
-> category

Typical path for determining actors whose films were rented:
actor
-> film_actor
-> film
-> inventory
-> rental

Typical path for determining revenue by film:
film
-> inventory
-> rental
-> payment

Typical path for determining revenue by category:
category
-> film_category
-> film
-> inventory
-> rental
-> payment
"""