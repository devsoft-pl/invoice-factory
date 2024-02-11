document.addEventListener("DOMContentLoaded", function () {
    const createCompanyButton = document.getElementById('createCompanyButton');

    const companyModalElement = document.getElementById('companyModal');
    const companyModalContentElement = document.getElementById('companyModalContent');

    const url = createCompanyButton.getAttribute("href");

    companyModalElement.addEventListener('hidden.bs.modal', function (event) {
      companyModalContentElement.innerHTML = ''
    })

    createCompanyButton.addEventListener("click", async (e) => {
        e.preventDefault();

        const response = await fetch(url);
        const data = await response.text();

        companyModalContentElement.innerHTML = data;

        const modal = new bootstrap.Modal(companyModalElement, {});
        modal.show();

        const selectCountryElement = document.getElementById("id_country");

        const optionCountryElement = createCountryOptionElement("new_country", "Dodaj nowy kraj", true);
        selectCountryElement.appendChild(optionCountryElement);

        const cancelCountryElement = document.getElementById("cancelCountryButton");
        const saveCountryElement = document.getElementById("saveCountryButton");

        const newCountryInput = document.createElement("input");
        newCountryInput.classList.add("form-control");

        selectCountryElement.addEventListener("change", () => {
            if (selectCountryElement.value === "new_country") {
                cancelCountryElement.classList.remove("d-none");
                saveCountryElement.classList.remove("d-none");
                selectCountryElement.classList.add("d-none");
                selectCountryElement.parentElement.appendChild(newCountryInput);
                newCountryInput.classList.remove("d-none");
            }
        });

        const hideCountryEditMode = () => {
            cancelCountryElement.classList.add("d-none");
            saveCountryElement.classList.add("d-none");
            newCountryInput.classList.add("d-none")
            selectCountryElement.classList.remove("d-none");
        };

        cancelCountryElement.addEventListener("click", (e) => {
            e.preventDefault();
            hideCountryEditMode();
            selectCountryElement.value = "";
            newCountryInput.value = "";
        });

        saveCountryElement.addEventListener("click", async (e) => {
            e.preventDefault();
            hideCountryEditMode();

            const urlCountry = saveCountryElement.getAttribute("href");
            const csrfCountryElement = document.getElementsByName("csrfmiddlewaretoken")[0];

            const data = new FormData();
            data.set("country", newCountryInput.value)
            data.set("csrfmiddlewaretoken", csrfCountryElement.value)

            const response = await fetch(urlCountry, {
                method: "POST",
                body: data
            });
            const json = await response.json();

            const newCountryOption = createCountryOptionElement(json.id, json.name);
            selectCountryElement.appendChild(newCountryOption);

            selectCountryElement.value = json.id.toString();
            newCountryInput.value = "";
        });

        const createCompanySaveButton = document.getElementById('createCompanySaveButton');

        createCompanySaveButton.addEventListener("click", async (e) => {
            e.preventDefault();

            const form = companyModalContentElement.getElementsByTagName('form')[0]

            const data = new FormData(form)

            const response = await fetch(url, {
                method: "POST",
                body: data
            });

            const json = await response.json();

            if (json.success) {
                const selectElement = document.getElementById('id_client');

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