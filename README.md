## About The Project

This user-friendly invoicing application is designed to streamline your business processes, offering an intuitive interface and robust features that make managing invoices easier than ever. 
With its comprehensive features, it simplifies financial management tasks, allowing you to focus on growing your business. 
Experience efficiency and convenience with our intuitive invoicing solution.
Here's what you can do with the application:

<ul>
    <li>
        <b>Add Your Company:</b> Easily add your company details to the system. 
        You can manage multiple companies under one account.
    </li>
    <li>
        <b>Manage Contacts:</b> Add an unlimited number of contacts, including both business entities (client) and individuals (person).
    </li>
    <li>
        <b>Create and Edit Invoices:</b> Generate sales or purchase invoices with ease. 
        Enjoy the flexibility of editing or deleting invoices as needed. 
        The application allows you to generate invoices in PDF.
    </li>
    <li>
        <b>Recurring Invoices:</b> Automate your billing process with recurring invoices for clients. 
        The app handles monthly invoice creation and sends email notifications with attachments for generated recurring invoices.
    </li>
    <li>
        <b>Automatic Currency Conversion:</b> Let the app handle currency conversion when invoicing in foreign currencies. 
        It automatically fetches exchange rates from the National Bank of Poland (NBP) for accurate and up-to-date conversion.
    </li>
    <li>
        <b>Month-end Closing:</b> Specify a day for month-end closing to reconcile invoices effortlessly. 
        The app gathers previous month's invoices and sends them to the designated recipient. 
        Once closed, invoices cannot be edited, ensuring data integrity.
    </li>
    <li>
        <b>Create a correction for the invoice:</b> If you spot an error on the invoice, create a correction anytime, even if the month is closed. 
        Rectify errors and update accounting records.
    </li>
    <li>
        <b>Revenue Reporting:</b> The app generates yearly revenue reports and charts from sales invoices, giving users quick access to company revenues.
    </li>
</ul>

The app is covered with tests using pytest and unittest, and the coverage is 99% (with some exceptions, such as migrations, configurations).

## Built With
<ul>
<li>Python 3+</li>
<li>Django 4+, DRF</li>
<li>Celery, Redis</li>
<li>JavaScript</li>
<li>PostgreSQL, MySQL</li>
<li>HTML, CSS, Bootstrap</li>
<li>Docker, Docker-compose</li>
<li>Git</li>
</ul>

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

## Application View

Project Link and Application View: in progress

## Contact

LinkedIn : https://www.linkedin.com/in/wioletta-wajda/







