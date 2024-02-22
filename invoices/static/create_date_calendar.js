document.addEventListener('DOMContentLoaded', function () {
            const saleDateInput = document.getElementById('id_create_date');

            if (saleDateInput) {
              new Datepicker(saleDateInput, {
                  format: 'dd.mm.yyyy',
                  language: "pl",
                  buttonClass: 'btn'
              });
            }
        });