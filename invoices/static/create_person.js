document.addEventListener("DOMContentLoaded", function () {
    const createPersonButton = document.getElementById('createPersonButton');

    const personModalElement = document.getElementById('personModal');
    const personModalContentElement = document.getElementById('personModalContent');

    const url = createPersonButton.getAttribute("href");

    personModalElement.addEventListener('hidden.bs.modal', function (event) {
      personModalContentElement.innerHTML = ''
    })

    createPersonButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const response = await fetch(url);
        const data = await response.text();

        personModalContentElement.innerHTML = data;

        const modal = new bootstrap.Modal(personModalElement, {});
        modal.show();

        const selectCountryAjaxElement = document.getElementById("id_country");

        const optionCountryAjaxElement = createCountryOptionElement("new_country", "Dodaj nowy kraj", true);
        selectCountryAjaxElement.appendChild(optionCountryAjaxElement);

        const cancelCountryAjaxElement = document.getElementById("cancelCountryButton");
        const saveCountryAjaxElement = document.getElementById("saveCountryButton");

        const newCountryAjaxInput = document.createElement("input");
        newCountryAjaxInput.classList.add("form-control");

        selectCountryAjaxElement.addEventListener("change", () => {
            if (selectCountryAjaxElement.value === "new_country") {
                cancelCountryAjaxElement.classList.remove("d-none");
                saveCountryAjaxElement.classList.remove("d-none");
                selectCountryAjaxElement.classList.add("d-none");
                selectCountryAjaxElement.parentElement.appendChild(newCountryAjaxInput);
                newCountryAjaxInput.classList.remove("d-none");
            }
        });

        const hideCountryEditMode = () => {
            cancelCountryAjaxElement.classList.add("d-none");
            saveCountryAjaxElement.classList.add("d-none");
            newCountryAjaxInput.classList.add("d-none")
            selectCountryAjaxElement.classList.remove("d-none");
        };

        cancelCountryAjaxElement.addEventListener("click", (e) => {
            e.preventDefault();
            hideCountryEditMode();
            selectCountryAjaxElement.value = "";
            newCountryAjaxInput.value = "";
        });

         saveCountryAjaxElement.addEventListener("click", async (e) => {
            e.preventDefault();

            const countryAjaxErrors = document.getElementById('id_country_errors');
            if (countryAjaxErrors) {
                    countryAjaxErrors.parentElement.removeChild(countryAjaxErrors);
                }

            const urlCountryAjax = saveCountryAjaxElement.getAttribute("href");
            const csrfCountryAjaxElement = document.getElementsByName("csrfmiddlewaretoken")[0];

            const data = new FormData();
            data.set("country", newCountryAjaxInput.value)
            data.set("csrfmiddlewaretoken", csrfCountryAjaxElement.value)

            const response = await fetch(urlCountryAjax, {
                method: "POST",
                body: data
            });
            const json = await response.json();

            if (json['success'] === false) {

                const rowAjaxContainer = selectCountryAjaxElement.parentElement.parentElement;

                const errorAjaxElement = document.createElement('div');
                errorAjaxElement.setAttribute('id', 'id_country_errors');
                errorAjaxElement.setAttribute('class', 'row');

                const errorAjaxContainer = document.createElement('div');
                errorAjaxContainer.setAttribute('class', 'col-12 col-md-6 offset-md-6 text-danger');
                errorAjaxElement.appendChild(errorAjaxContainer);

                const errorUlAjaxContainer = document.createElement('ul');
                errorUlAjaxContainer.setAttribute('class', 'errorlist');
                errorAjaxContainer.appendChild(errorUlAjaxContainer);

                const countryAjaxErrors = json['errors']['country'];

                countryAjaxErrors.forEach((value) => {
                    const errorLiAjaxElement = document.createElement('li');
                    const errorAjaxLabel = document.createTextNode(value);
                    errorLiAjaxElement.appendChild(errorAjaxLabel);

                    errorUlAjaxContainer.appendChild(errorLiAjaxElement);
                });

                rowAjaxContainer.parentElement.insertBefore(errorAjaxElement, rowAjaxContainer.nextSibling);
            } else {
                hideCountryEditMode();

                const newCountryAjaxOption = createCountryOptionElement(json.id, json.name);
                selectCountryAjaxElement.appendChild(newCountryAjaxOption);

                selectCountryAjaxElement.value = json.id.toString();
                newCountryAjaxInput.value = "";
            }
        });

        const createPersonSaveButton = document.getElementById('createPersonSaveButton');

        createPersonSaveButton.addEventListener("click", async (e) => {
            e.preventDefault();

            const form = personModalContentElement.getElementsByTagName('form')[0]
            const data = new FormData(form)

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

            if (json.success) {
                const selectElement = document.getElementById('id_person');

                const optionElement = document.createElement('option');
                optionElement.setAttribute('value', json.id);

                const optionNameElement = document.createTextNode(json.name);

                optionElement.appendChild(optionNameElement)
                selectElement.appendChild(optionElement);

                selectElement.value = json.id.toString()

                modal.hide();
            }
        })
    });
});