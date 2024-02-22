document.addEventListener('DOMContentLoaded', function () {
            const saleDateInput = document.getElementById('id_settlement_date');

            if (saleDateInput) {
              new Datepicker(saleDateInput, {
                  format: 'dd.mm.yyyy',
                  language: "pl",
                  buttonClass: 'btn'
              });
            }
        });