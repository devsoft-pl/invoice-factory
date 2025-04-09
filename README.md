## Invoice Factory

Invoicing application for companies and individuals to streamline business processes.
Here's what you can do with the application:

* **Add Your Company:** You can manage multiple companies under one account.

* **Manage Contacts:** Add an unlimited number of contacts, including both business entities and individuals.

* **Create and Edit Invoices:** Generate sales or purchase invoices. Edit or delete invoices as needed.
The application allows you to generate invoices in PDF.

* **Recurring Invoices:** Automate your billing process with recurring invoices. 
The app handles monthly invoice creation and sends email notifications with attachments for generated recurring invoices.

* **Automatic Currency Conversion:** App handle currency conversion when invoicing in foreign currencies. 
It automatically fetches exchange rates from the National Bank of Poland (NBP) for accurate and up-to-date conversion.

* **Month-end Closing:** Specify a day for month-end closing to reconcile invoices effortlessly. 
The app gathers previous month's invoices and sends them to the designated recipient. 
Once closed, invoices cannot be edited, ensuring data integrity.

* **Create a correction for the invoice:** If you spot an error on the invoice, create a correction anytime, even if the month is closed. 
Rectify errors and update accounting records.

* **Revenue Reporting:** The app generates yearly revenue reports and charts from sales invoices, giving users quick access to company revenues.

The app is covered with tests using pytest and unittest, and the coverage is 99% (with some exceptions, such as migrations, configurations).

## Built With

* Python,
* Django,
* DRF,
* Celery,
* JavaScript,
* PostgreSQL,
* Bootstrap,
* Docker,
* Kubernetes,

## How to run the application (docker-compose)

To run the application, you need to have docker and docker-compose installed on your machine. If you don't have it installed, 
you can download it from [here](https://www.docker.com/products/docker-desktop).

After you have docker and docker-compose installed, you can clone the repository with:

```bash
clone: git@github.com:w-wajda/invoice_manager.git
```
Then you can run the application with:

```bash
  docker compose up
  make migrate-docker  # run migrations
```

And that's it! The application is running on [http://localhost:8000](http://localhost:8000). 

To **stop** the application, you can run:

```bash
  docker compose down
```

### Running the application with local with python manage.py runserver

```bash
    python manage.py runserver
```

Be sure that postgres is up before:

```bash
    docker compose up postgres -d
```

## Application Link

Link: https://invoice-factory.devsoft.pl/

## Contact

LinkedIn : https://www.linkedin.com/in/wioletta-wajda/







